from __future__ import annotations

import re
import time
import uuid
from contextlib import contextmanager

import pytest

from tests.helpers import (
    REPO_ROOT,
    container_path_exists,
    docker_available,
    docker_exec,
    docker_volume,
    ensure_pytest_image,
    reserve_host_port,
    run_command,
)

IMAGE_TAG = "sure-aio:pytest"
ALPHA_IMAGE_TAG = "sure-aio-alpha:pytest"
pytestmark = pytest.mark.integration
SECRET_KEY_BASE = (
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"  # nosec B105
)


def pinned_upstream_version(dockerfile_name: str = "Dockerfile") -> str:
    dockerfile = (REPO_ROOT / dockerfile_name).read_text()
    match = re.search(r"^ARG UPSTREAM_VERSION=(?P<version>\S+)$", dockerfile, re.M)
    assert match is not None  # nosec B101
    return match.group("version")


def logs(name: str) -> str:
    result = run_command(["docker", "logs", name], check=False)
    return result.stdout + result.stderr


def wait_for_http(name: str, host_port: int, timeout: int = 420) -> None:
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{host_port}/up"

    while time.time() < deadline:
        status = run_command(
            ["docker", "inspect", "-f", "{{.State.Status}}", name],
            check=False,
        ).stdout.strip()
        if status != "running":
            raise AssertionError(f"{name} stopped before becoming ready.\n{logs(name)}")

        if run_command(["curl", "-fsS", url], check=False).returncode == 0:
            return
        time.sleep(2)

    raise AssertionError(f"{name} did not become ready.\n{logs(name)}")


def assert_no_https_redirect(host_port: int) -> None:
    result = run_command(
        [
            "curl",
            "-sS",
            "-D",
            "-",
            "-o",
            "/dev/null",
            f"http://127.0.0.1:{host_port}/",
        ]
    )
    assert "location: https://" not in result.stdout.lower()  # nosec B101


def rails_runner_output(container_name: str, code: str) -> str:
    result = docker_exec(container_name, f"bin/rails runner {code!r}")
    lines = result.stdout.strip().splitlines()
    return lines[-1] if lines else ""


def login_form_token(host_port: int, cookie_path: str) -> str:
    result = run_command(
        [
            "curl",
            "-fsS",
            "-c",
            cookie_path,
            "-b",
            cookie_path,
            "-H",
            "Host: sure.domain.com",
            "-H",
            "X-Forwarded-Host: sure.domain.com",
            "-H",
            "X-Forwarded-Port: 443",
            "-H",
            "X-Forwarded-Proto: https",
            "-H",
            "X-Forwarded-Ssl: on",
            f"http://127.0.0.1:{host_port}/sessions/new",
        ]
    )
    match = re.search(r'name="authenticity_token" value="([^"]+)"', result.stdout)
    assert match is not None  # nosec B101
    return match.group(1)


def post_login_with_null_origin(host_port: int, cookie_path: str, token: str):
    return run_command(
        [
            "curl",
            "-sS",
            "-D",
            "-",
            "-o",
            "-",
            "-c",
            cookie_path,
            "-b",
            cookie_path,
            "-H",
            "Host: sure.domain.com",
            "-H",
            "X-Forwarded-Host: sure.domain.com",
            "-H",
            "X-Forwarded-Port: 443",
            "-H",
            "X-Forwarded-Proto: https",
            "-H",
            "X-Forwarded-Ssl: on",
            "-H",
            "Origin: null",
            "-H",
            "Content-Type: application/x-www-form-urlencoded",
            "--data-urlencode",
            f"authenticity_token={token}",
            "--data-urlencode",
            "email=missing@example.com",
            "--data-urlencode",
            "password=bad-password",
            f"http://127.0.0.1:{host_port}/sessions",
        ],
        check=False,
    )


def get_service_worker(host_port: int):
    return run_command(
        [
            "curl",
            "-sS",
            "-D",
            "-",
            "-o",
            "-",
            "-H",
            "Host: sure.domain.com",
            "-H",
            "X-Forwarded-Host: sure.domain.com",
            "-H",
            "X-Forwarded-Port: 443",
            "-H",
            "X-Forwarded-Proto: https",
            "-H",
            "X-Forwarded-Ssl: on",
            f"http://127.0.0.1:{host_port}/service-worker",
        ],
        check=False,
    )


def assert_alpha_import_and_webauthn_config(
    container_name: str,
    expected: str,
) -> None:
    result = rails_runner_output(
        container_name,
        "config = Rails.application.config.x.webauthn; "
        "puts [SureImport::MAX_NDJSON_SIZE, SureImport.max_ndjson_size, "
        "SureImport.max_row_count, SureImport.allocate.max_row_count, "
        'config.rp_id, config.allowed_origins.join("|")].join(":")',
    )
    assert result == expected  # nosec B101


def assert_alpha_import_preflight_blocks_dirty_target(container_name: str) -> None:
    result = rails_runner_output(
        container_name,
        "association = Struct.new(:names) { def pluck(_column); names; end }; "
        "family = Struct.new(:categories, :tags, :merchants).new("
        "association.new(['Groceries']), association.new([]), association.new([])); "
        "content = ["
        "{ type: 'Category', data: { id: 'cat-1', name: 'Groceries' } }, "
        "{ type: 'MysteryType', data: { id: 'bad-1' } }"
        "].map(&:to_json).join(10.chr); "
        "result = SureImport::Preflight.new(family: family, content: content).call; "
        "counts = SureImport.dry_run_totals_from_line_type_counts("
        "{ 'Transfer' => 1, 'RejectedTransfer' => 1, 'Holding' => 1 }); "
        "puts [result.valid?, result.errors.map { |error| error[:code] }.join('|'), "
        "result.error_message.include?('Groceries'), counts[:transfers], "
        "counts[:rejected_transfers], counts[:holdings]].join(':')",
    )

    valid, codes, collision_message, transfers, rejected_transfers, holdings = (
        result.split(":")
    )
    assert valid == "false"  # nosec B101
    assert set(codes.split("|")) == {  # nosec B101
        "existing_taxonomy_collision",
        "unsupported_record_type",
    }
    assert collision_message == "true"  # nosec B101
    assert (transfers, rejected_transfers, holdings) == ("1", "1", "1")  # nosec B101


def assert_alpha_admin_reset_task_available(container_name: str) -> None:
    result = rails_runner_output(
        container_name,
        "require 'rake'; Rails.application.load_tasks; "
        "routes = Rails.application.routes; "
        "preview_route = routes.recognize_path('/settings/hosting/financial_data_reset', method: :get); "
        "destroy_route = routes.recognize_path('/settings/hosting/financial_data_reset', method: :delete); "
        "views = %w["
        "app/views/settings/hostings/_danger_zone_settings.html.erb "
        "app/views/settings/hostings/financial_data_reset.html.erb "
        "app/views/settings/hostings/financial_data_reset_complete.html.erb "
        "app/views/settings/securities/show.html.erb"
        "].all? { |path| Rails.root.join(path).exist? }; "
        "puts [defined?(Family::FinancialDataReset).present?, "
        "Rake::Task.task_defined?('sure:admin:reset_financial_data'), "
        "Family::FinancialDataReset::COUNT_KEYS.include?(:imports), "
        "Family::FinancialDataReset::COUNT_KEYS.include?(:merchants), "
        "Family::FinancialDataReset.const_defined?(:CONFIRMATION_PHRASE), "
        "preview_route[:controller] == 'settings/hostings', "
        "preview_route[:action] == 'financial_data_reset', "
        "destroy_route[:action] == 'destroy_financial_data_reset', "
        "views].join(':')",
    )

    assert result == "true:true:true:true:true:true:true:true:true"  # nosec B101


@contextmanager
def container(
    storage_volume: str,
    pgdata_volume: str,
    redis_volume: str,
    *,
    image_tag: str = IMAGE_TAG,
    name_prefix: str = "sure-aio-pytest",
    extra_env: dict[str, str] | None = None,
):
    name = f"{name_prefix}-{uuid.uuid4().hex[:10]}"
    host_port = reserve_host_port()
    v0_7_runtime_env = {
        "ALPHA_VANTAGE_MAX_REQUESTS_PER_DAY": "25",
        "BINANCE_EGRESS_IP": "127.0.0.1",
        "BINANCE_PUBLIC_URL": "https://data-api.binance.vision",
        "EODHD_MAX_REQUESTS_PER_DAY": "20",
        "GCS_BUCKET": "sure-aio-pytest",
        "GCS_KEYFILE_JSON": '{"type":"service_account","project_id":"sure-aio-pytest"}',
        "GCS_PROJECT": "sure-aio-pytest",
        "LLM_CONTEXT_WINDOW": "4096",
        "LLM_MAX_HISTORY_TOKENS": "2048",
        "LLM_MAX_ITEMS_PER_CALL": "10",
        "LLM_MAX_RESPONSE_TOKENS": "512",
        "LLM_SYSTEM_PROMPT_RESERVE": "256",
        "MFAPI_URL": "https://api.mfapi.in",
        "OPENAI_SUPPORTS_RESPONSES_ENDPOINT": "false",
        "SECURITIES_PROVIDERS": "yahoo_finance,binance_public",
        "SMTP_TLS_SKIP_VERIFY": "false",
        "TIINGO_MAX_REQUESTS_PER_HOUR": "500",
        "TWELVE_DATA_MAX_REQUESTS_PER_MINUTE": "7",
        "TWELVE_DATA_MIN_REQUEST_INTERVAL": "1.0",
    }
    command = [
        "docker",
        "run",
        "-d",
        "--platform",
        "linux/amd64",
        "--name",
        name,
        "-p",
        f"{host_port}:3000",
        "-e",
        f"SECRET_KEY_BASE={SECRET_KEY_BASE}",
        "-e",
        "SELF_HOSTED=true",
        "-e",
        "EXCHANGE_RATE_PROVIDER=yahoo_finance",
        "-e",
        "SECURITIES_PROVIDER=yahoo_finance",
        "-e",
        "ONBOARDING_STATE=open",
        "-e",
        "RAILS_ASSUME_SSL=false",
        "-e",
        "RAILS_FORCE_SSL=false",
        "-v",
        f"{storage_volume}:/rails/storage",
        "-v",
        f"{pgdata_volume}:/var/lib/postgresql/data",
        "-v",
        f"{redis_volume}:/var/lib/redis",
    ]
    runtime_env = {**v0_7_runtime_env, **(extra_env or {})}
    for key, value in runtime_env.items():
        command.extend(["-e", f"{key}={value}"])
    command.append(image_tag)
    run_command(command)
    try:
        yield name, host_port
    finally:
        run_command(["docker", "rm", "-f", name], check=False)


@pytest.fixture(scope="session")
def build_image() -> None:
    if not docker_available():
        pytest.skip("Docker is unavailable; integration tests require Docker/OrbStack.")
    ensure_pytest_image(IMAGE_TAG)


@pytest.fixture(scope="session")
def build_alpha_image() -> None:
    if not docker_available():
        pytest.skip("Docker is unavailable; integration tests require Docker/OrbStack.")
    ensure_pytest_image(
        ALPHA_IMAGE_TAG,
        dockerfile="Dockerfile.alpha",
        prebuilt_env="AIO_ALPHA_PYTEST_USE_PREBUILT_IMAGE",
    )


def test_happy_path_boot_and_recreate_persists_data(build_image) -> None:
    with (
        docker_volume("sure-aio-storage") as storage_volume,
        docker_volume("sure-aio-pg") as pgdata_volume,
        docker_volume("sure-aio-redis") as redis_volume,
    ):
        with container(storage_volume, pgdata_volume, redis_volume) as (
            name,
            host_port,
        ):
            wait_for_http(name, host_port)
            assert container_path_exists(
                name, "/var/lib/postgresql/data/PG_VERSION"
            )  # nosec B101
            assert_no_https_redirect(host_port)
            first_logs = logs(name)
            assert "Running Sure database preparations" in first_logs  # nosec B101
            assert "Listening on http://0.0.0.0:3000" in first_logs  # nosec B101
            assert (
                "export: fatal: invalid variable name" not in first_logs
            )  # nosec B101
            assert "Completed 404 Not Found" not in first_logs  # nosec B101
            assert 'table: "settings" does not exist' not in first_logs  # nosec B101

        with container(storage_volume, pgdata_volume, redis_volume) as (
            name,
            host_port,
        ):
            wait_for_http(name, host_port)
            assert container_path_exists(
                name, "/var/lib/postgresql/data/PG_VERSION"
            )  # nosec B101
            assert_no_https_redirect(host_port)
            second_logs = logs(name)
            assert (
                "PostgreSQL database already initialized." in second_logs
            )  # nosec B101
            assert (
                "Initializing PostgreSQL database..." not in second_logs
            )  # nosec B101
            assert (
                "export: fatal: invalid variable name" not in second_logs
            )  # nosec B101


def test_image_reports_pinned_upstream_version(build_image) -> None:
    result = run_command(
        [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "cat",
            IMAGE_TAG,
            "/rails/.sure-version",
        ]
    )

    assert result.stdout.strip() == pinned_upstream_version()  # nosec B101


def test_proxy_null_origin_escape_hatch_keeps_token_csrf_validation(
    build_image,
    tmp_path,
) -> None:
    proxy_env = {
        "APP_DOMAIN": "sure.domain.com",
        "APP_URL": "https://sure.domain.com",
        "RAILS_ASSUME_SSL": "true",
        "RAILS_FORCE_SSL": "false",
        "SURE_REFERRER_POLICY": "strict-origin-when-cross-origin",
    }

    with (
        docker_volume("sure-aio-origin-default-storage") as storage_volume,
        docker_volume("sure-aio-origin-default-pg") as pgdata_volume,
        docker_volume("sure-aio-origin-default-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            extra_env=proxy_env,
        ) as (name, host_port):
            wait_for_http(name, host_port)
            cookie_path = str(tmp_path / f"{name}.cookies")
            token = login_form_token(host_port, cookie_path)
            result = post_login_with_null_origin(host_port, cookie_path, token)

            assert "HTTP/1.1 422" in result.stdout  # nosec B101
            assert "The change you wanted was rejected" in result.stdout  # nosec B101
            assert "InvalidAuthenticityToken" in logs(name)  # nosec B101

    with (
        docker_volume("sure-aio-origin-disabled-storage") as storage_volume,
        docker_volume("sure-aio-origin-disabled-pg") as pgdata_volume,
        docker_volume("sure-aio-origin-disabled-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            extra_env={**proxy_env, "SURE_CSRF_ORIGIN_CHECK": "false"},
        ) as (name, host_port):
            wait_for_http(name, host_port)
            cookie_path = str(tmp_path / f"{name}.cookies")
            token = login_form_token(host_port, cookie_path)
            result = post_login_with_null_origin(host_port, cookie_path, token)

            assert "HTTP/1.1 422" in result.stdout  # nosec B101
            assert (
                "The change you wanted was rejected" not in result.stdout
            )  # nosec B101
            assert "InvalidAuthenticityToken" not in logs(name)  # nosec B101


def test_proxy_service_worker_does_not_trigger_cross_origin_js_guard(
    build_image,
) -> None:
    proxy_env = {
        "APP_DOMAIN": "sure.domain.com",
        "APP_URL": "https://sure.domain.com",
        "RAILS_ASSUME_SSL": "true",
        "RAILS_FORCE_SSL": "false",
        "SURE_CSRF_ORIGIN_CHECK": "false",
        "SURE_REFERRER_POLICY": "strict-origin-when-cross-origin",
    }

    with (
        docker_volume("sure-aio-service-worker-storage") as storage_volume,
        docker_volume("sure-aio-service-worker-pg") as pgdata_volume,
        docker_volume("sure-aio-service-worker-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            extra_env=proxy_env,
        ) as (name, host_port):
            wait_for_http(name, host_port)
            result = get_service_worker(host_port)

            assert "HTTP/1.1 200" in result.stdout  # nosec B101
            assert (
                "content-type: application/javascript" in result.stdout.lower()
            )  # nosec B101
            assert "CACHE_VERSION" in result.stdout  # nosec B101
            assert "ActionController::InvalidCrossOriginRequest" not in logs(
                name
            )  # nosec B101


def test_alpha_image_boots_with_version_import_limits_and_webauthn_env(
    build_alpha_image,
) -> None:
    with (
        docker_volume("sure-aio-alpha-storage") as storage_volume,
        docker_volume("sure-aio-alpha-pg") as pgdata_volume,
        docker_volume("sure-aio-alpha-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            image_tag=ALPHA_IMAGE_TAG,
            name_prefix="sure-aio-alpha-pytest",
            extra_env={
                "SURE_IMPORT_MAX_NDJSON_SIZE_MB": "250",
                "SURE_IMPORT_MAX_ROWS": "1000000",
                "WEBAUTHN_RP_ID": "finance.example.com",
                "WEBAUTHN_ALLOWED_ORIGINS": (
                    "https://finance.example.com,https://sure.example.net"
                ),
            },
        ) as (
            name,
            host_port,
        ):
            wait_for_http(name, host_port)
            version = docker_exec(name, "cat /rails/.sure-version").stdout.strip()
            assert version == pinned_upstream_version("Dockerfile.alpha")  # nosec B101
            assert_alpha_import_and_webauthn_config(
                name,
                (
                    "262144000:262144000:1000000:1000000:"
                    "finance.example.com:"
                    "https://finance.example.com|https://sure.example.net"
                ),
            )
            assert_alpha_import_preflight_blocks_dirty_target(name)
            assert_alpha_admin_reset_task_available(name)


def test_alpha_import_limit_defaults_are_runtime_defaults(build_alpha_image) -> None:
    with (
        docker_volume("sure-aio-alpha-default-storage") as storage_volume,
        docker_volume("sure-aio-alpha-default-pg") as pgdata_volume,
        docker_volume("sure-aio-alpha-default-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            image_tag=ALPHA_IMAGE_TAG,
            name_prefix="sure-aio-alpha-default-pytest",
        ) as (name, host_port):
            wait_for_http(name, host_port)
            assert_alpha_import_and_webauthn_config(
                name,
                "262144000:262144000:1000000:1000000:localhost:"
                "http://localhost:3000",
            )


def test_alpha_import_limit_env_overrides_are_applied(build_alpha_image) -> None:
    with (
        docker_volume("sure-aio-alpha-custom-storage") as storage_volume,
        docker_volume("sure-aio-alpha-custom-pg") as pgdata_volume,
        docker_volume("sure-aio-alpha-custom-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            image_tag=ALPHA_IMAGE_TAG,
            name_prefix="sure-aio-alpha-custom-pytest",
            extra_env={
                "SURE_IMPORT_MAX_NDJSON_SIZE_MB": "12",
                "SURE_IMPORT_MAX_ROWS": "3456",
            },
        ) as (name, host_port):
            wait_for_http(name, host_port)
            assert_alpha_import_and_webauthn_config(
                name,
                "12582912:12582912:3456:3456:localhost:http://localhost:3000",
            )


def test_alpha_import_limit_invalid_env_falls_back_to_defaults(
    build_alpha_image,
) -> None:
    with (
        docker_volume("sure-aio-alpha-invalid-storage") as storage_volume,
        docker_volume("sure-aio-alpha-invalid-pg") as pgdata_volume,
        docker_volume("sure-aio-alpha-invalid-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            image_tag=ALPHA_IMAGE_TAG,
            name_prefix="sure-aio-alpha-invalid-pytest",
            extra_env={
                "SURE_IMPORT_MAX_NDJSON_SIZE_MB": "0",
                "SURE_IMPORT_MAX_ROWS": "not-a-number",
            },
        ) as (name, host_port):
            wait_for_http(name, host_port)
            assert_alpha_import_and_webauthn_config(
                name,
                "262144000:262144000:1000000:1000000:localhost:"
                "http://localhost:3000",
            )


def test_alpha_webauthn_env_is_parsed_by_upstream_initializer(
    build_alpha_image,
) -> None:
    with (
        docker_volume("sure-aio-alpha-webauthn-storage") as storage_volume,
        docker_volume("sure-aio-alpha-webauthn-pg") as pgdata_volume,
        docker_volume("sure-aio-alpha-webauthn-redis") as redis_volume,
    ):
        with container(
            storage_volume,
            pgdata_volume,
            redis_volume,
            image_tag=ALPHA_IMAGE_TAG,
            name_prefix="sure-aio-alpha-webauthn-pytest",
            extra_env={
                "WEBAUTHN_RP_ID": "https://finance.example.com:443/settings",
                "WEBAUTHN_ALLOWED_ORIGINS": (
                    "https://finance.example.com/, https://sure.example.net"
                ),
            },
        ) as (name, host_port):
            wait_for_http(name, host_port)
            assert_alpha_import_and_webauthn_config(
                name,
                "262144000:262144000:1000000:1000000:"
                "finance.example.com:"
                "https://finance.example.com|https://sure.example.net",
            )
