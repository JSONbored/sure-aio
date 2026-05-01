from __future__ import annotations

import os
import sys
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


def test_unraid_metadata_contract_is_complete_and_unprivileged() -> None:
    assert_unraid_metadata_contract(CONTRACT)


def test_template_declares_runtime_targets() -> None:
    assert_template_declares_contract(CONTRACT)


def test_secret_like_template_variables_are_masked() -> None:
    assert_secret_like_template_variables_are_masked(CONTRACT.template_xml)


def test_required_appdata_paths_are_declared_as_container_volumes() -> None:
    assert_required_appdata_paths_declared_as_volumes(CONTRACT)


def test_template_ports_are_exposed_by_image() -> None:
    assert_template_ports_exposed_by_image(CONTRACT)


def test_dockerfile_has_runtime_safety_contract() -> None:
    assert_dockerfile_runtime_safety_contract(CONTRACT)


def test_docker_socket_mount_is_advanced_and_documented_when_present() -> None:
    assert_docker_socket_mount_is_advanced_when_present(CONTRACT.template_xml)
