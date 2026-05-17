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


def test_alpha_template_declares_import_limit_controls() -> None:
    stable_targets = _config_targets(_xml_root("sure-aio.xml"))
    alpha_targets = _config_targets(_xml_root("sure-aio-alpha.xml"))

    assert "SURE_IMPORT_MAX_NDJSON_SIZE_MB" not in stable_targets  # nosec B101
    assert "SURE_IMPORT_MAX_ROWS" not in stable_targets  # nosec B101
    assert alpha_targets["SURE_IMPORT_MAX_NDJSON_SIZE_MB"].text == "250"  # nosec B101
    assert alpha_targets["SURE_IMPORT_MAX_ROWS"].text == "1000000"  # nosec B101
    assert alpha_targets["3000"].text == "3001"  # nosec B101


def test_alpha_template_exposes_upstream_alpha_webauthn_controls() -> None:
    stable_targets = _config_targets(_xml_root("sure-aio.xml"))
    alpha_targets = _config_targets(_xml_root("sure-aio-alpha.xml"))

    assert "WEBAUTHN_RP_ID" not in stable_targets  # nosec B101
    assert "WEBAUTHN_ALLOWED_ORIGINS" not in stable_targets  # nosec B101
    assert alpha_targets["WEBAUTHN_RP_ID"].get("Display") == "advanced"  # nosec B101
    assert (  # nosec B101
        alpha_targets["WEBAUTHN_ALLOWED_ORIGINS"].get("Display") == "advanced"
    )


def test_alpha_overlay_is_documented_and_copied() -> None:
    dockerfile = (ROOT / "Dockerfile.alpha").read_text()
    initializer = (
        ROOT / "rootfs-alpha/rails/config/initializers/sure_aio_alpha_import_limits.rb"
    )
    ledger = (ROOT / "docs/alpha-lane.md").read_text()

    assert "COPY rootfs-alpha/ /" in dockerfile  # nosec B101
    assert initializer.exists()  # nosec B101
    text = initializer.read_text()
    assert "SURE_IMPORT_MAX_NDJSON_SIZE_MB" in text  # nosec B101
    assert "SURE_IMPORT_MAX_ROWS" in text  # nosec B101
    assert "SureImport.const_set(:MAX_NDJSON_SIZE" in text  # nosec B101
    assert "import-limits-env" in ledger  # nosec B101
