from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from tests.helpers import docker_available, reserve_host_port, run_command

IMAGE_TAG = "sure-aio:pytest"
pytestmark = pytest.mark.integration


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


@contextmanager
def container(storage_dir: Path, pgdata_dir: Path, redis_dir: Path):
    name = f"sure-aio-pytest-{uuid.uuid4().hex[:10]}"
    host_port = reserve_host_port()
    secret = (
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"  # nosec B105
    )
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
        f"SECRET_KEY_BASE={secret}",
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
        f"{storage_dir}:/rails/storage",
        "-v",
        f"{pgdata_dir}:/var/lib/postgresql/data",
        "-v",
        f"{redis_dir}:/var/lib/redis",
        IMAGE_TAG,
    ]
    run_command(command)
    try:
        yield name, host_port
    finally:
        run_command(["docker", "rm", "-f", name], check=False)


@pytest.fixture(scope="session", autouse=True)
def build_image() -> None:
    if not docker_available():
        pytest.skip("Docker is unavailable; integration tests require Docker/OrbStack.")
    run_command(["docker", "build", "--platform", "linux/amd64", "-t", IMAGE_TAG, "."])


def test_happy_path_boot_and_recreate_persists_data() -> None:
    with (
        TemporaryDirectory(prefix="sure-aio-storage-") as storage_dir,
        TemporaryDirectory(prefix="sure-aio-pg-") as pgdata_dir,
        TemporaryDirectory(prefix="sure-aio-redis-") as redis_dir,
    ):
        with container(Path(storage_dir), Path(pgdata_dir), Path(redis_dir)) as (
            name,
            host_port,
        ):
            wait_for_http(name, host_port)
            assert Path(pgdata_dir, "PG_VERSION").is_file()  # nosec B101
            assert_no_https_redirect(host_port)
            first_logs = logs(name)
            assert "Running Sure database preparations" in first_logs  # nosec B101
            assert "Listening on http://0.0.0.0:3000" in first_logs  # nosec B101
            assert (
                "export: fatal: invalid variable name" not in first_logs
            )  # nosec B101
            assert "Completed 404 Not Found" not in first_logs  # nosec B101
            assert 'table: "settings" does not exist' not in first_logs  # nosec B101

        with container(Path(storage_dir), Path(pgdata_dir), Path(redis_dir)) as (
            name,
            host_port,
        ):
            wait_for_http(name, host_port)
            assert Path(pgdata_dir, "PG_VERSION").is_file()  # nosec B101
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
