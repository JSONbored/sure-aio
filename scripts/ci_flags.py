#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass


TRUE_VALUES = {"1", "true", "yes", "on"}


def parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in TRUE_VALUES


@dataclass(frozen=True)
class CiFlags:
    run_smoke_requested: bool
    publish_requested: bool


def resolve_flags(
    event_name: str,
    ref: str,
    run_smoke_test_input: str | None = None,
    publish_image_input: str | None = None,
) -> CiFlags:
    if event_name == "push" and ref == "refs/heads/main":
        return CiFlags(run_smoke_requested=True, publish_requested=True)

    if event_name == "workflow_dispatch":
        return CiFlags(
            run_smoke_requested=parse_bool(run_smoke_test_input),
            publish_requested=parse_bool(publish_image_input),
        )

    return CiFlags(run_smoke_requested=False, publish_requested=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve CI gate flags for build workflow.")
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--run-smoke-test-input", default="")
    parser.add_argument("--publish-image-input", default="")
    args = parser.parse_args()

    flags = resolve_flags(
        event_name=args.event_name,
        ref=args.ref,
        run_smoke_test_input=args.run_smoke_test_input,
        publish_image_input=args.publish_image_input,
    )
    print(f"run_smoke_requested={'true' if flags.run_smoke_requested else 'false'}")
    print(f"publish_requested={'true' if flags.publish_requested else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
