#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CHANGELOG = ROOT / "CHANGELOG.md"
DEFAULT_DOCKERFILE = ROOT / "Dockerfile"


def read_upstream_version(dockerfile: pathlib.Path) -> str:
    pattern = re.compile(r"^ARG UPSTREAM_VERSION=(.+)$")
    for line in dockerfile.read_text().splitlines():
        match = pattern.match(line.strip())
        if match:
            return match.group(1).split("@", 1)[0]
    raise SystemExit(f"Unable to find ARG UPSTREAM_VERSION in {dockerfile}")


def git_tags() -> list[str]:
    output = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return [line.strip() for line in output.splitlines() if line.strip()]


def next_release_version(dockerfile: pathlib.Path) -> str:
    upstream_version = read_upstream_version(dockerfile)
    pattern = re.compile(rf"^{re.escape(upstream_version)}-aio\.(\d+)$")
    revisions = []
    for tag in git_tags():
        match = pattern.match(tag)
        if match:
            revisions.append(int(match.group(1)))
    next_revision = max(revisions, default=0) + 1
    return f"{upstream_version}-aio.{next_revision}"


def latest_changelog_version(changelog: pathlib.Path) -> str:
    pattern = re.compile(r"^##\s+([^\s]+)")
    for line in changelog.read_text().splitlines():
        match = pattern.match(line.strip())
        if match and match.group(1) != "Unreleased":
            return match.group(1)
    raise SystemExit(f"Unable to find a released version heading in {changelog}")


def extract_release_notes(version: str, changelog: pathlib.Path) -> str:
    heading = re.compile(rf"^##\s+{re.escape(version)}(?:\s+-\s+.+)?$")
    next_heading = re.compile(r"^##\s+")

    lines = changelog.read_text().splitlines()
    start = None
    for index, line in enumerate(lines):
        if heading.match(line.strip()):
            start = index + 1
            break

    if start is None:
        raise SystemExit(f"Unable to find release section for {version} in {changelog}")

    end = len(lines)
    for index in range(start, len(lines)):
        if next_heading.match(lines[index].strip()):
            end = index
            break

    notes = "\n".join(lines[start:end]).strip()
    if not notes:
        raise SystemExit(f"Release section for {version} in {changelog} is empty")
    return notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Release helpers for sure-aio.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upstream_parser = subparsers.add_parser("upstream-version")
    upstream_parser.add_argument("--dockerfile", type=pathlib.Path, default=DEFAULT_DOCKERFILE)

    next_parser = subparsers.add_parser("next-version")
    next_parser.add_argument("--dockerfile", type=pathlib.Path, default=DEFAULT_DOCKERFILE)

    latest_parser = subparsers.add_parser("latest-changelog-version")
    latest_parser.add_argument("--changelog", type=pathlib.Path, default=DEFAULT_CHANGELOG)

    notes_parser = subparsers.add_parser("extract-release-notes")
    notes_parser.add_argument("version")
    notes_parser.add_argument("--changelog", type=pathlib.Path, default=DEFAULT_CHANGELOG)

    args = parser.parse_args()

    if args.command == "upstream-version":
        print(read_upstream_version(args.dockerfile))
        return
    if args.command == "next-version":
        print(next_release_version(args.dockerfile))
        return
    if args.command == "latest-changelog-version":
        print(latest_changelog_version(args.changelog))
        return
    if args.command == "extract-release-notes":
        print(extract_release_notes(args.version, args.changelog))
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
