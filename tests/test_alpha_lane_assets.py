from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree  # nosec B405

ROOT = Path(__file__).resolve().parents[1]


def _xml_root(path: str) -> ElementTree.Element:
    return ElementTree.parse(ROOT / path).getroot()  # nosec B314


def _config_targets(root: ElementTree.Element) -> dict[str, ElementTree.Element]:
    return {
        str(config.get("Target")): config
        for config in root.findall("Config")
        if config.get("Target")
    }


def _host_paths(root: ElementTree.Element) -> set[str]:
    return {
        host_dir.text or ""
        for host_dir in root.findall("./Data/Volume/HostDir")
        if host_dir.text
    }


def test_alpha_template_has_separate_identity_and_storage() -> None:
    stable = _xml_root("sure-aio.xml")
    alpha = _xml_root("sure-aio-alpha.xml")

    assert stable.findtext("Name") == "sure-aio"  # nosec B101
    assert alpha.findtext("Name") == "sure-aio-alpha"  # nosec B101
    assert (  # nosec B101
        alpha.findtext("Repository") == "jsonbored/sure-aio-alpha:latest-alpha"
    )
    assert (  # nosec B101
        alpha.findtext("Registry")
        == "https://hub.docker.com/r/jsonbored/sure-aio-alpha"
    )
    assert alpha.findtext("TemplateURL", "").endswith(  # nosec B101
        "/sure-aio-alpha.xml"
    )
    assert stable.findtext("Beta") is None  # nosec B101
    assert alpha.findtext("Beta") == "True"  # nosec B101
    assert _host_paths(stable).isdisjoint(_host_paths(alpha))  # nosec B101
    assert all(  # nosec B101
        path.startswith("/mnt/user/appdata/sure-aio-alpha/")
        for path in _host_paths(alpha)
    )
    assert "Testing / Unstable" in alpha.findtext("Overview", "")  # nosec B101
    assert "stable [code]sure-aio[/code] appdata" in alpha.findtext(  # nosec B101
        "Overview", ""
    )


def test_stable_and_alpha_ca_metadata_is_complete() -> None:
    stable = _xml_root("sure-aio.xml")
    alpha = _xml_root("sure-aio-alpha.xml")

    assert stable.findtext("Category") == "Productivity Tools:Utilities"  # nosec B101
    assert alpha.findtext("Category") == "Productivity Tools:Utilities"  # nosec B101
    assert (
        stable.findtext("ReadMe") == "https://github.com/JSONbored/sure-aio#readme"
    )  # nosec B101
    assert alpha.findtext("ReadMe") == (  # nosec B101
        "https://github.com/JSONbored/sure-aio#alpha-testing-lane"
    )

    for root in (stable, alpha):
        assert root.findtext("Requires")  # nosec B101
        assert root.findtext("DonateText") == (  # nosec B101
            "Support JSONbored on GitHub Sponsors."
        )
        assert root.findtext("DonateLink") == (  # nosec B101
            "https://github.com/sponsors/JSONbored"
        )
        assert len(root.findall("Screenshot")) == 3  # nosec B101

    assert all(  # nosec B101
        "/screenshots/sure-aio/" in screenshot.text
        for screenshot in stable.findall("Screenshot")
    )
    assert all(  # nosec B101
        "/screenshots/sure-aio-alpha/" in screenshot.text
        for screenshot in alpha.findall("Screenshot")
    )


def test_alpha_template_declares_import_limit_controls() -> None:
    stable_targets = _config_targets(_xml_root("sure-aio.xml"))
    alpha_targets = _config_targets(_xml_root("sure-aio-alpha.xml"))
    ndjson = alpha_targets["SURE_IMPORT_MAX_NDJSON_SIZE_MB"]
    rows = alpha_targets["SURE_IMPORT_MAX_ROWS"]

    assert "SURE_IMPORT_MAX_NDJSON_SIZE_MB" not in stable_targets  # nosec B101
    assert "SURE_IMPORT_MAX_ROWS" not in stable_targets  # nosec B101
    assert ndjson.text == "250"  # nosec B101
    assert ndjson.get("Default") == "250"  # nosec B101
    assert ndjson.get("Display") == "always"  # nosec B101
    assert ndjson.get("Required") == "false"  # nosec B101
    assert ndjson.get("Mask") == "false"  # nosec B101
    assert "Alpha-only" in ndjson.get("Description", "")  # nosec B101
    assert rows.text == "1000000"  # nosec B101
    assert rows.get("Default") == "1000000"  # nosec B101
    assert rows.get("Display") == "always"  # nosec B101
    assert rows.get("Required") == "false"  # nosec B101
    assert rows.get("Mask") == "false"  # nosec B101
    assert "web, API, and preflight" in rows.get("Description", "")  # nosec B101
    assert alpha_targets["3000"].text == "3001"  # nosec B101


def test_stable_and_alpha_mask_secret_bearing_network_fields() -> None:
    for template in ("sure-aio.xml", "sure-aio-alpha.xml"):
        targets = _config_targets(_xml_root(template))

        assert targets["HTTPS_PROXY"].get("Mask") == "true"  # nosec B101
        assert targets["HTTP_PROXY"].get("Mask") == "true"  # nosec B101
        assert targets["NO_PROXY"].get("Mask") == "false"  # nosec B101
        assert targets["REDIS_URL"].get("Mask") == "true"  # nosec B101
        assert targets["REDIS_SENTINEL_HOSTS"].get("Mask") == "false"  # nosec B101
        assert (
            targets["EXTERNAL_ASSISTANT_SESSION_KEY"].get("Default") == ""
        )  # nosec B101
        assert targets["EXTERNAL_ASSISTANT_SESSION_KEY"].text in (
            None,
            "",
        )  # nosec B101
        assert "isolated per-chat" in targets[  # nosec B101
            "EXTERNAL_ASSISTANT_SESSION_KEY"
        ].get("Description", "")


def test_dockerfiles_do_not_mutate_upstream_bundle_resolution() -> None:
    bundle_assertion = (ROOT / "docker/assert-sure-bundle-versions.rb").read_text()

    for dockerfile in ("Dockerfile", "Dockerfile.alpha"):
        text = (ROOT / dockerfile).read_text()

        assert "bundle update" not in text  # nosec B101
        assert "bundle config set frozen false" not in text  # nosec B101
        assert "bundle check" in text  # nosec B101
        assert "COPY docker/assert-sure-bundle-versions.rb" in text  # nosec B101
        assert "ruby /tmp/assert-sure-bundle-versions.rb" in text  # nosec B101
    assert '"rack" => "3.2.6"' in bundle_assertion  # nosec B101
    assert '"rack-session" => "2.1.2"' in bundle_assertion  # nosec B101
    assert '"addressable" => "2.8.7"' in bundle_assertion  # nosec B101
    assert '"rexml" => "3.4.2"' in bundle_assertion  # nosec B101
    assert "unexpected upstream gem versions" in bundle_assertion  # nosec B101


def test_shared_runtime_waits_for_final_postgres_and_omits_init_db() -> None:
    web_run = (ROOT / "rootfs/etc/s6-overlay/s6-rc.d/web/run").read_text()
    external_session = (
        ROOT
        / "rootfs/rails/config/initializers/sure_aio_external_assistant_session_key.rb"
    ).read_text()

    assert (  # nosec B101
        ROOT / "rootfs/etc/s6-overlay/s6-rc.d/web/dependencies.d/postgres"
    ).exists()
    init_db_dir = ROOT / "rootfs/etc/s6-overlay/s6-rc.d/init-db"
    assert not any(path.is_file() for path in init_db_dir.rglob("*"))  # nosec B101
    assert not (ROOT / "rootfs/usr/local/bin/init-db.sh").exists()  # nosec B101
    assert 'PGPASSWORD="${POSTGRES_PASSWORD}" psql' in web_run  # nosec B101
    assert '-d "${POSTGRES_DB}"' in web_run  # nosec B101
    assert "bundle exec rails db:prepare" in web_run  # nosec B101
    assert "SureAioExternalAssistantSessionKey" in external_session  # nosec B101
    assert (
        'ENV["EXTERNAL_ASSISTANT_SESSION_KEY"].to_s.strip' in external_session
    )  # nosec B101
    assert "sure-chat:" in external_session  # nosec B101
    assert "chat&.id" in external_session  # nosec B101


def test_alpha_template_exposes_upstream_alpha_webauthn_controls() -> None:
    stable_targets = _config_targets(_xml_root("sure-aio.xml"))
    alpha_targets = _config_targets(_xml_root("sure-aio-alpha.xml"))
    rp_id = alpha_targets["WEBAUTHN_RP_ID"]
    origins = alpha_targets["WEBAUTHN_ALLOWED_ORIGINS"]

    assert "WEBAUTHN_RP_ID" not in stable_targets  # nosec B101
    assert "WEBAUTHN_ALLOWED_ORIGINS" not in stable_targets  # nosec B101
    assert rp_id.get("Default") == ""  # nosec B101
    assert rp_id.text in (None, "")  # nosec B101
    assert rp_id.get("Display") == "advanced"  # nosec B101
    assert rp_id.get("Required") == "false"  # nosec B101
    assert rp_id.get("Mask") == "false"  # nosec B101
    assert "passkey/WebAuthn relying party ID" in rp_id.get(  # nosec B101
        "Description", ""
    )
    assert "browser trust" in rp_id.get("Description", "")  # nosec B101
    assert "Settings > Security" in rp_id.get("Description", "")  # nosec B101
    assert "authenticator-app 2FA" in rp_id.get("Description", "")  # nosec B101
    assert origins.get("Default") == ""  # nosec B101
    assert origins.text in (None, "")  # nosec B101
    assert origins.get("Display") == "advanced"  # nosec B101
    assert origins.get("Required") == "false"  # nosec B101
    assert origins.get("Mask") == "false"  # nosec B101
    assert "comma-separated WebAuthn origins" in origins.get(  # nosec B101
        "Description", ""
    )
    assert "browser trust" in origins.get("Description", "")  # nosec B101
    assert "Settings > Security" in origins.get("Description", "")  # nosec B101
    assert "authenticator-app 2FA" in origins.get("Description", "")  # nosec B101


def test_alpha_template_does_not_expose_dirty_merge_controls() -> None:
    stable_targets = _config_targets(_xml_root("sure-aio.xml"))
    alpha_targets = _config_targets(_xml_root("sure-aio-alpha.xml"))

    forbidden_targets = {
        "CONFIRM_RESET_FINANCIAL_DATA",
        "DRY_RUN",
        "MERGE_EXISTING_TAXONOMY",
        "SURE_IMPORT_MERGE_EXISTING_TAXONOMY",
        "SURE_IMPORT_MERGE_EXISTING_TAXONOMY_DEFAULT",
        "USER_EMAIL",
    }

    assert forbidden_targets.isdisjoint(stable_targets)  # nosec B101
    assert forbidden_targets.isdisjoint(alpha_targets)  # nosec B101


def test_alpha_overlay_is_documented_and_copied() -> None:
    dockerfile = (ROOT / "Dockerfile.alpha").read_text()
    import_limits = (
        ROOT / "rootfs-alpha/rails/config/initializers/sure_aio_alpha_import_limits.rb"
    )
    import_preflight = (
        ROOT
        / "rootfs-alpha/rails/config/initializers/sure_aio_alpha_import_preflight.rb"
    )
    route_parity = (
        ROOT
        / "rootfs-alpha/rails/config/initializers/sure_aio_alpha_route_parity_importer.rb"
    )
    admin_reset_model = (
        ROOT / "rootfs-alpha/rails/app/models/family/financial_data_reset.rb"
    )
    admin_reset_job = ROOT / "rootfs-alpha/rails/app/jobs/family_reset_job.rb"
    admin_reset_ui = (
        ROOT / "rootfs-alpha/rails/config/initializers/sure_aio_alpha_admin_reset_ui.rb"
    )
    admin_reset_danger_view = (
        ROOT
        / "rootfs-alpha/rails/app/views/settings/hostings/_danger_zone_settings.html.erb"
    )
    admin_reset_preview_view = (
        ROOT
        / "rootfs-alpha/rails/app/views/settings/hostings/financial_data_reset.html.erb"
    )
    admin_reset_complete_view = (
        ROOT
        / "rootfs-alpha/rails/app/views/settings/hostings/financial_data_reset_complete.html.erb"
    )
    webauthn_security_view = (
        ROOT / "rootfs-alpha/rails/app/views/settings/securities/show.html.erb"
    )
    admin_reset_task = ROOT / "rootfs-alpha/rails/lib/tasks/sure_admin.rake"
    failure_view = ROOT / "rootfs-alpha/rails/app/views/imports/_failure.html.erb"
    ledger = (ROOT / "docs/alpha-lane.md").read_text()

    assert "COPY rootfs-alpha/ /" in dockerfile  # nosec B101
    assert import_limits.exists()  # nosec B101
    assert import_preflight.exists()  # nosec B101
    assert route_parity.exists()  # nosec B101
    assert admin_reset_model.exists()  # nosec B101
    assert admin_reset_job.exists()  # nosec B101
    assert admin_reset_ui.exists()  # nosec B101
    assert admin_reset_danger_view.exists()  # nosec B101
    assert admin_reset_preview_view.exists()  # nosec B101
    assert admin_reset_complete_view.exists()  # nosec B101
    assert webauthn_security_view.exists()  # nosec B101
    assert admin_reset_task.exists()  # nosec B101
    assert failure_view.exists()  # nosec B101
    import_limits_text = import_limits.read_text()
    import_preflight_text = import_preflight.read_text()
    admin_reset_model_text = admin_reset_model.read_text()
    admin_reset_job_text = admin_reset_job.read_text()
    admin_reset_ui_text = admin_reset_ui.read_text()
    admin_reset_danger_view_text = admin_reset_danger_view.read_text()
    admin_reset_preview_view_text = admin_reset_preview_view.read_text()
    webauthn_security_view_text = webauthn_security_view.read_text()
    admin_reset_task_text = admin_reset_task.read_text()
    failure_view_text = failure_view.read_text()
    assert "SURE_IMPORT_MAX_NDJSON_SIZE_MB" in import_limits_text  # nosec B101
    assert "SURE_IMPORT_MAX_ROWS" in import_limits_text  # nosec B101
    assert "MAX_NDJSON_SIZE_MB = 250" in import_limits_text  # nosec B101
    assert "MAX_ROWS = 1_000_000" in import_limits_text  # nosec B101
    assert "capped_positive_integer_env" in import_limits_text  # nosec B101
    assert "SureImport.const_set(:MAX_NDJSON_SIZE" in import_limits_text  # nosec B101
    assert "SureImport::Preflight" in import_preflight_text  # nosec B101
    assert "PreflightError" in import_preflight_text  # nosec B101
    assert "preflight_failed" in import_preflight_text  # nosec B101
    assert "invalid_accountable" in import_preflight_text  # nosec B101
    assert "!accountable.is_a?(Hash)" in import_preflight_text  # nosec B101
    assert (  # nosec B101
        "invalid_rows_count: @rows_count - @valid_rows_count" in import_preflight_text
    )
    assert "Family::FinancialDataReset" in admin_reset_model_text  # nosec B101
    assert "CONFIRM_RESET_FINANCIAL_DATA=yes" in admin_reset_model_text  # nosec B101
    assert "Family::FinancialDataReset.new(" in admin_reset_job_text  # nosec B101
    assert "financial_data_reset" in admin_reset_ui_text  # nosec B101
    assert "destroy_financial_data_reset" in admin_reset_ui_text  # nosec B101
    assert "ensure_financial_data_reset_admin" in admin_reset_ui_text  # nosec B101
    assert "review_financial_data_reset" in admin_reset_danger_view_text  # nosec B101
    assert (  # nosec B101
        "financial-data-reset-confirmation-help" in admin_reset_preview_view_text
    )
    assert "webauthn_mfa_required_title" in webauthn_security_view_text  # nosec B101
    assert (  # nosec B101
        "task reset_financial_data: :environment" in admin_reset_task_text
    )
    assert "USER_EMAIL is required" in admin_reset_task_text  # nosec B101
    assert "import.error" in failure_view_text  # nosec B101
    assert "import-limits-env" in ledger  # nosec B101
    assert "import-preflight-strict" in ledger  # nosec B101
    assert "route-parity-importer" in ledger  # nosec B101
    assert "admin-financial-reset" in ledger  # nosec B101
    assert "Settings -> Self-Hosting -> Danger Zone" in ledger  # nosec B101
    assert "browser trust" in ledger  # nosec B101


def test_alpha_dockerfile_declares_revision_and_repo_metadata() -> None:
    alpha = (ROOT / "Dockerfile.alpha").read_text()

    assert "ARG AIO_REVISION=1" in alpha  # nosec B101
    assert (  # nosec B101
        'org.opencontainers.image.source="https://github.com/JSONbored/sure-aio"'
        in alpha
    )
    assert 'org.opencontainers.image.title="Sure AIO Alpha"' in alpha  # nosec B101


def test_alpha_release_history_is_separate_from_stable_changelog() -> None:
    alpha_changelog = (ROOT / "CHANGELOG.alpha.md").read_text()
    stable_changelog = (ROOT / "CHANGELOG.md").read_text()

    assert "0.7.1-alpha.10-aio.1" in alpha_changelog  # nosec B101
    assert "docs/alpha-lane.md" in alpha_changelog  # nosec B101
    assert "0.7.1-alpha.9-aio.1" not in stable_changelog  # nosec B101


def test_alpha_changelog_documents_runtime_differences() -> None:
    alpha = _xml_root("sure-aio-alpha.xml")
    overview = alpha.findtext("Overview", "")
    changes = alpha.findtext("Changes", "")

    assert "upstream" in overview  # nosec B101
    assert "alpha prereleases" in overview  # nosec B101
    assert (  # nosec B101
        alpha.findtext("Repository", "") == "jsonbored/sure-aio-alpha:latest-alpha"
    )
    assert "sha-alpha-<commit>" not in changes  # nosec B101
    assert "Testing / Unstable" in overview  # nosec B101
    assert "separate alpha tag namespace" in overview  # nosec B101
    assert "SURE_IMPORT_MAX_NDJSON_SIZE_MB" in overview  # nosec B101
    assert "SURE_IMPORT_MAX_ROWS" in overview  # nosec B101
    assert "strict SureImport preflight" in overview  # nosec B101
    assert "admin reset UI/task" in overview  # nosec B101
    assert "Harden Sure runtime" in changes  # nosec B101
    assert "malformed Account preflight errors" in changes  # nosec B101
    assert "authenticated PostgreSQL access" in changes  # nosec B101


def test_alpha_docs_use_dedicated_package_and_trimmed_tags() -> None:
    docs = "\n".join(
        [
            (ROOT / "README.md").read_text(),
            (ROOT / "docs/alpha-lane.md").read_text(),
            (ROOT / "docs/releases.md").read_text(),
        ]
    )

    assert "jsonbored/sure-aio-alpha" in docs  # nosec B101
    assert "latest-alpha" in docs  # nosec B101
    assert "0.7.1-alpha.7-aio.8" in docs  # nosec B101
    assert "self-hosted admin reset UI/task" in docs  # nosec B101
    assert "authenticator-app 2FA" in docs  # nosec B101
    assert "publishes to the shared `jsonbored/sure-aio`" not in docs  # nosec B101
    assert "shares the same `jsonbored/sure-aio` image repo" not in docs  # nosec B101
    assert "sha-alpha-<commit>" not in docs  # nosec B101
    assert "the upstream alpha version tag" not in docs  # nosec B101
