from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]


def _load_check_upstream() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "check_upstream", ROOT / "scripts" / "check-upstream.py"
    )
    assert spec is not None and spec.loader is not None  # nosec B101
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_version_tag_candidates_include_v_prefixed_and_bare_tags() -> None:
    module = _load_check_upstream()

    assert module.version_tag_candidates("v0.7.0") == [  # nosec B101
        "v0.7.0",
        "0.7.0",
    ]
    assert module.version_tag_candidates("0.7.0") == [  # nosec B101
        "0.7.0",
        "v0.7.0",
    ]


def test_ghcr_image_tag_for_version_uses_existing_container_tag(monkeypatch) -> None:
    module = _load_check_upstream()

    def fake_digest(_image: str, tag: str) -> str | None:
        return "sha256:abc" if tag == "0.7.0" else None

    monkeypatch.setattr(module, "try_ghcr_digest_for_tag", fake_digest)

    assert (  # nosec B101
        module.ghcr_image_tag_for_version("we-promise/sure", "v0.7.0") == "0.7.0"
    )
