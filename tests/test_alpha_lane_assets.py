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
    assert origins.get("Default") == ""  # nosec B101
    assert origins.text in (None, "")  # nosec B101
    assert origins.get("Display") == "advanced"  # nosec B101
    assert origins.get("Required") == "false"  # nosec B101
    assert origins.get("Mask") == "false"  # nosec B101
    assert "comma-separated WebAuthn origins" in origins.get(  # nosec B101
        "Description", ""
    )


def test_alpha_template_does_not_expose_dirty_merge_controls() -> None:
    stable_targets = _config_targets(_xml_root("sure-aio.xml"))
    alpha_targets = _config_targets(_xml_root("sure-aio-alpha.xml"))

    forbidden_targets = {
        "MERGE_EXISTING_TAXONOMY",
        "SURE_IMPORT_MERGE_EXISTING_TAXONOMY",
        "SURE_IMPORT_MERGE_EXISTING_TAXONOMY_DEFAULT",
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
    failure_view = ROOT / "rootfs-alpha/rails/app/views/imports/_failure.html.erb"
    ledger = (ROOT / "docs/alpha-lane.md").read_text()

    assert "COPY rootfs-alpha/ /" in dockerfile  # nosec B101
    assert import_limits.exists()  # nosec B101
    assert import_preflight.exists()  # nosec B101
    assert route_parity.exists()  # nosec B101
    assert failure_view.exists()  # nosec B101
    import_limits_text = import_limits.read_text()
    import_preflight_text = import_preflight.read_text()
    failure_view_text = failure_view.read_text()
    assert "SURE_IMPORT_MAX_NDJSON_SIZE_MB" in import_limits_text  # nosec B101
    assert "SURE_IMPORT_MAX_ROWS" in import_limits_text  # nosec B101
    assert "SureImport.const_set(:MAX_NDJSON_SIZE" in import_limits_text  # nosec B101
    assert "SureImport::Preflight" in import_preflight_text  # nosec B101
    assert "PreflightError" in import_preflight_text  # nosec B101
    assert "preflight_failed" in import_preflight_text  # nosec B101
    assert (  # nosec B101
        "invalid_rows_count: @rows_count - @valid_rows_count" in import_preflight_text
    )
    assert "import.error" in failure_view_text  # nosec B101
    assert "import-limits-env" in ledger  # nosec B101
    assert "import-preflight-strict" in ledger  # nosec B101
    assert "route-parity-importer" in ledger  # nosec B101


def test_alpha_dockerfile_declares_revision_and_repo_metadata() -> None:
    alpha = (ROOT / "Dockerfile.alpha").read_text()

    assert "ARG AIO_REVISION=6" in alpha  # nosec B101
    assert (  # nosec B101
        'org.opencontainers.image.source="https://github.com/JSONbored/sure-aio"'
        in alpha
    )
    assert 'org.opencontainers.image.title="Sure AIO Alpha"' in alpha  # nosec B101


def test_alpha_release_history_is_separate_from_stable_changelog() -> None:
    alpha_changelog = (ROOT / "CHANGELOG.alpha.md").read_text()
    stable_changelog = (ROOT / "CHANGELOG.md").read_text()

    assert "0.7.1-alpha.7-aio.6" in alpha_changelog  # nosec B101
    assert "docs/alpha-lane.md" in alpha_changelog  # nosec B101
    assert "0.7.1-alpha.7-aio.6" not in stable_changelog  # nosec B101


def test_alpha_changelog_documents_runtime_differences() -> None:
    alpha = _xml_root("sure-aio-alpha.xml")
    changes = alpha.findtext("Changes", "")

    assert "upstream Sure alpha prereleases" in changes  # nosec B101
    assert "jsonbored/sure-aio-alpha" in changes  # nosec B101
    assert "latest-alpha" in changes  # nosec B101
    assert "0.7.1-alpha.7-aio.6" in changes  # nosec B101
    assert "sha-alpha-<commit>" not in changes  # nosec B101
    assert "beta/testing" in changes  # nosec B101
    assert "separate app name" in changes  # nosec B101
    assert "SURE_IMPORT_MAX_NDJSON_SIZE_MB" in changes  # nosec B101
    assert "SURE_IMPORT_MAX_ROWS" in changes  # nosec B101
    assert "SureImport preflight/failure diagnostics" in changes  # nosec B101
    assert "dirty-target merge out of the Unraid template/env" in changes  # nosec B101
    assert "WEBAUTHN_RP_ID" in changes  # nosec B101
    assert "WEBAUTHN_ALLOWED_ORIGINS" in changes  # nosec B101


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
    assert "0.7.1-alpha.7-aio.6" in docs  # nosec B101
    assert "publishes to the shared `jsonbored/sure-aio`" not in docs  # nosec B101
    assert "shares the same `jsonbored/sure-aio` image repo" not in docs  # nosec B101
    assert "sha-alpha-<commit>" not in docs  # nosec B101
    assert "the upstream alpha version tag" not in docs  # nosec B101
