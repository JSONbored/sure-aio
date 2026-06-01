from __future__ import annotations

from pathlib import Path

from aio_fleet.app_testing import *  # noqa: F403
from aio_fleet.app_testing import configure_repo_root

REPO_ROOT = Path(__file__).resolve().parents[1]
configure_repo_root(REPO_ROOT)
