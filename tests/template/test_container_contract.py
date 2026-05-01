from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET  # nosec B405 - trusted local template XML only
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

for candidate in (
    Path(os.environ["AIO_FLEET_SRC"]) if os.environ.get("AIO_FLEET_SRC") else None,
    ROOT / ".aio-fleet" / "src",
    ROOT.parent / "aio-fleet" / "src",
):
    if candidate and candidate.exists():
        sys.path.insert(0, str(candidate))
        break

from aio_fleet.testing import (  # noqa: E402
    ContainerContract,
    assert_docker_socket_mount_is_advanced_when_present,
    assert_dockerfile_runtime_safety_contract,
    assert_required_appdata_paths_declared_as_volumes,
    assert_secret_like_template_variables_are_masked,
    assert_template_declares_contract,
    assert_template_ports_exposed_by_image,
    assert_unraid_metadata_contract,
)

CONTRACT = ContainerContract(
    image="sure-aio:pytest",
    template_xml=ROOT / "sure-aio.xml",
    dockerfile=ROOT / "Dockerfile",
    ports=("3000",),
    persistent_paths=(
        "/rails/storage",
        "/var/lib/postgresql/data",
        "/var/lib/redis",
    ),
)

V0_7_RUNTIME_TARGETS = {
    "ALPHA_VANTAGE_API_KEY",
    "ALPHA_VANTAGE_MAX_REQUESTS_PER_DAY",
    "ALPHA_VANTAGE_URL",
    "BINANCE_EGRESS_IP",
    "BINANCE_PUBLIC_URL",
    "EODHD_API_KEY",
    "EODHD_MAX_REQUESTS_PER_DAY",
    "EODHD_URL",
    "GCS_BUCKET",
    "GCS_KEYFILE",
    "GCS_KEYFILE_JSON",
    "GCS_PROJECT",
    "LLM_CONTEXT_WINDOW",
    "LLM_MAX_HISTORY_TOKENS",
    "LLM_MAX_ITEMS_PER_CALL",
    "LLM_MAX_RESPONSE_TOKENS",
    "LLM_SYSTEM_PROMPT_RESERVE",
    "MFAPI_URL",
    "OPENAI_SUPPORTS_RESPONSES_ENDPOINT",
    "SECURITIES_PROVIDERS",
    "SMTP_TLS_SKIP_VERIFY",
    "TIINGO_API_KEY",
    "TIINGO_MAX_REQUESTS_PER_HOUR",
    "TIINGO_URL",
    "TWELVE_DATA_MAX_REQUESTS_PER_MINUTE",
    "TWELVE_DATA_MIN_REQUEST_INTERVAL",
}
NON_SECRET_TOKEN_BUDGET_TARGETS = {
    "LLM_MAX_HISTORY_TOKENS",
    "LLM_MAX_RESPONSE_TOKENS",
}


def _template_root() -> ET.Element:
    return ET.parse(CONTRACT.template_xml).getroot()  # nosec B314


def _template_targets() -> set[str]:
    return {
        elem.attrib["Target"]
        for elem in _template_root().findall(".//Config")
        if elem.attrib.get("Target")
    }


def test_unraid_metadata_contract_is_complete_and_unprivileged() -> None:
    assert_unraid_metadata_contract(CONTRACT)


def test_unraid_template_uses_docker_hub_latest_image_reference() -> None:
    root = _template_root()

    assert root.findtext("Repository") == "jsonbored/sure-aio:latest"  # nosec B101
    assert (  # nosec B101
        root.findtext("Registry") == "https://hub.docker.com/r/jsonbored/sure-aio"
    )


def test_template_declares_runtime_targets() -> None:
    assert_template_declares_contract(CONTRACT)


def test_template_exposes_v0_7_runtime_targets() -> None:
    assert V0_7_RUNTIME_TARGETS <= _template_targets()  # nosec B101


def test_secret_like_template_variables_are_masked(tmp_path: Path) -> None:
    root = _template_root()
    for index, config in enumerate(root.findall(".//Config")):
        target = config.attrib.get("Target")
        if target in NON_SECRET_TOKEN_BUDGET_TARGETS:
            assert config.attrib.get("Mask") == "false"  # nosec B101
            config.attrib["Target"] = f"NUMERIC_BUDGET_{index}"
            config.attrib["Name"] = config.attrib["Name"].replace("Tokens", "Budget")

    sanitized_xml = tmp_path / "sure-aio.xml"
    ET.ElementTree(root).write(sanitized_xml, encoding="unicode")

    assert_secret_like_template_variables_are_masked(sanitized_xml)


def test_required_appdata_paths_are_declared_as_container_volumes() -> None:
    assert_required_appdata_paths_declared_as_volumes(CONTRACT)


def test_template_ports_are_exposed_by_image() -> None:
    assert_template_ports_exposed_by_image(CONTRACT)


def test_dockerfile_has_runtime_safety_contract() -> None:
    assert_dockerfile_runtime_safety_contract(CONTRACT)


def test_docker_socket_mount_is_advanced_and_documented_when_present() -> None:
    assert_docker_socket_mount_is_advanced_when_present(CONTRACT.template_xml)
