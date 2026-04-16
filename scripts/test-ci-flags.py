#!/usr/bin/env python3
from __future__ import annotations

from ci_flags import resolve_flags


def main() -> int:
    cases = [
        # push on main always enables smoke + publish for build-related changes
        ("push", "refs/heads/main", "", True, True),
        # push on non-main should not force smoke/publish
        ("push", "refs/heads/feature", "", False, False),
        # workflow_dispatch on main always publishes; smoke stays optional
        ("workflow_dispatch", "refs/heads/main", "true", True, True),
        ("workflow_dispatch", "refs/heads/main", "1", True, True),
        ("workflow_dispatch", "refs/heads/main", "false", False, True),
        ("workflow_dispatch", "refs/heads/main", "", False, True),
        # workflow_dispatch on non-main should not publish
        ("workflow_dispatch", "refs/heads/feature", "true", False, False),
        # PR events should never force smoke/publish from this resolver
        ("pull_request", "refs/pull/1/merge", "", False, False),
    ]

    for idx, case in enumerate(cases, start=1):
        event_name, ref, smoke_input, expected_smoke, expected_publish = case
        result = resolve_flags(
            event_name=event_name,
            ref=ref,
            run_smoke_test_input=smoke_input,
        )
        assert result.run_smoke_requested == expected_smoke, (
            f"case #{idx} expected run_smoke_requested={expected_smoke}, "
            f"got {result.run_smoke_requested}"
        )
        assert result.publish_requested == expected_publish, (
            f"case #{idx} expected publish_requested={expected_publish}, "
            f"got {result.publish_requested}"
        )

    print(f"ci_flags tests passed ({len(cases)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
