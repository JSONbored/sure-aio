#!/usr/bin/env python3
from __future__ import annotations

import configparser
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request


ROOT = pathlib.Path(".")
UPSTREAM_FILE = ROOT / "upstream.toml"
DOCKERFILE = ROOT / "Dockerfile"
SEMVER_RE = re.compile(
    r"^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?$"
)


def fail(message: str) -> "NoReturn":
    print(message, file=sys.stderr)
    raise SystemExit(1)


def http_json(url: str, headers: dict[str, str] | None = None) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json, application/json",
            "User-Agent": "jsonbored-sure-aio",
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        fail(f"HTTP error while requesting {url}: {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        fail(f"Network error while requesting {url}: {exc.reason}")


def parse_version(value: str) -> tuple[int, int, int, bool, str]:
    match = SEMVER_RE.match(value)
    if not match:
        fail(f"Unsupported version format: {value}")
    prerelease = match.group("prerelease")
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        prerelease is not None,
        prerelease or "",
    )


def prerelease_sort_key(prerelease: str) -> tuple[tuple[int, object], ...]:
    parts: list[tuple[int, object]] = []
    for item in prerelease.split("."):
        if item.isdigit():
            parts.append((0, int(item)))
        else:
            parts.append((1, item))
    return tuple(parts)


def version_sort_key(value: str) -> tuple[int, int, int, int, tuple[tuple[int, object], ...]]:
    major, minor, patch, is_prerelease, prerelease = parse_version(value)
    return (
        major,
        minor,
        patch,
        0 if is_prerelease else 1,
        prerelease_sort_key(prerelease),
    )


def filter_versions(values: list[str], stable_only: bool) -> list[str]:
    semver_values = [value for value in values if SEMVER_RE.match(value)]
    if not stable_only:
        return semver_values
    stable_values: list[str] = []
    for value in semver_values:
        _, _, _, is_prerelease, _ = parse_version(value)
        if not is_prerelease:
            stable_values.append(value)
    return stable_values


def github_headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def latest_github_tag(repo: str, stable_only: bool) -> str:
    data = http_json(f"https://api.github.com/repos/{repo}/tags?per_page=100", github_headers())
    if not isinstance(data, list):
        fail(f"Unexpected GitHub tags response for {repo}")
    tags = [entry["name"] for entry in data if isinstance(entry, dict) and isinstance(entry.get("name"), str)]
    candidates = filter_versions(tags, stable_only)
    if not candidates:
        fail(f"No matching tags found for upstream repo {repo}")
    return sorted(candidates, key=version_sort_key)[-1]


def try_ghcr_digest_for_tag(image: str, tag: str) -> str | None:
    token_data = http_json(f"https://ghcr.io/token?scope=repository:{image}:pull")
    if not isinstance(token_data, dict) or not token_data.get("token"):
        fail(f"Could not get GHCR token for {image}")
    token = str(token_data["token"])
    request = urllib.request.Request(
        f"https://ghcr.io/v2/{image}/manifests/{tag}",
        headers={
            "Accept": ",".join(
                [
                    "application/vnd.oci.image.index.v1+json",
                    "application/vnd.oci.image.manifest.v1+json",
                    "application/vnd.docker.distribution.manifest.list.v2+json",
                    "application/vnd.docker.distribution.manifest.v2+json",
                ]
            ),
            "Authorization": f"Bearer {token}",
            "User-Agent": "jsonbored-sure-aio",
        },
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.headers.get("docker-content-digest", "").strip() or None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        fail(f"HTTP error while requesting GHCR manifest for {image}:{tag}: {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        fail(f"Network error while requesting GHCR manifest for {image}:{tag}: {exc.reason}")
    return None


def ghcr_digest_for_version(image: str, version: str) -> str:
    candidates = [version]
    if version.startswith("v"):
        candidates.append(version[1:])
    for tag in candidates:
        digest = try_ghcr_digest_for_tag(image, tag)
        if digest:
            return digest
    fail(f"Could not determine digest for GHCR image {image} using version tags: {', '.join(candidates)}")


def read_local_version(config: dict[str, object]) -> str:
    version_source = str(config.get("version_source", "")).strip()
    version_key = str(config.get("version_key", "")).strip()
    if version_source != "dockerfile-arg":
        fail(f"Unsupported version_source: {version_source}")
    pattern = re.compile(rf"^\s*ARG\s+{re.escape(version_key)}=(.+?)\s*$")
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1)
    fail(f"Could not find ARG {version_key} in Dockerfile")


def write_local_version(config: dict[str, object], new_version: str) -> None:
    version_key = str(config.get("version_key", "")).strip()
    pattern = re.compile(rf"^(\s*ARG\s+{re.escape(version_key)}=).+?(\s*)$")
    updated_lines: list[str] = []
    changed = False
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            updated_lines.append(f"{match.group(1)}{new_version}{match.group(2)}")
            changed = True
        else:
            updated_lines.append(line)
    if not changed:
        fail(f"Could not update ARG {version_key} in Dockerfile")
    DOCKERFILE.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def read_local_digest(config: dict[str, object]) -> str:
    digest_source = str(config.get("digest_source", "")).strip()
    digest_key = str(config.get("digest_key", "")).strip()
    if digest_source != "dockerfile-arg":
        fail(f"Unsupported digest_source: {digest_source}")
    pattern = re.compile(rf"^\s*ARG\s+{re.escape(digest_key)}=(.+?)\s*$")
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1)
    fail(f"Could not find ARG {digest_key} in Dockerfile")


def write_local_digest(config: dict[str, object], new_digest: str) -> None:
    digest_source = str(config.get("digest_source", "")).strip()
    digest_key = str(config.get("digest_key", "")).strip()
    if digest_source != "dockerfile-arg":
        fail(f"Unsupported digest_source: {digest_source}")

    pattern = re.compile(rf"^(\s*ARG\s+{re.escape(digest_key)}=).+?(\s*)$")
    updated_lines: list[str] = []
    changed = False
    for line in DOCKERFILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            updated_lines.append(f"{match.group(1)}{new_digest}{match.group(2)}")
            changed = True
        else:
            updated_lines.append(line)
    if not changed:
        fail(f"Could not update ARG {digest_key} in Dockerfile")
    DOCKERFILE.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def write_outputs(outputs: dict[str, str]) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            for key, value in outputs.items():
                handle.write(f"{key}={value}\n")
    else:
        for key, value in outputs.items():
            print(f"{key}={value}")


def parse_upstream_toml(path: pathlib.Path) -> dict[str, dict[str, object]]:
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read_string(path.read_text(encoding="utf-8"))
    result: dict[str, dict[str, object]] = {}
    for section in parser.sections():
        values: dict[str, object] = {}
        for key, raw_value in parser.items(section):
            value = raw_value.strip()
            lower = value.lower()
            if lower == "true":
                values[key] = True
            elif lower == "false":
                values[key] = False
            else:
                values[key] = value.strip('"')
        result[section] = values
    return result


def main() -> None:
    if not UPSTREAM_FILE.exists():
        fail("Missing upstream.toml")

    config = parse_upstream_toml(UPSTREAM_FILE)
    upstream = config.get("upstream")
    notifications = config.get("notifications", {})
    if not isinstance(upstream, dict):
        fail("Invalid upstream.toml: missing [upstream]")

    stable_only = bool(upstream.get("stable_only", True))
    current_version = read_local_version(upstream)
    current_digest = read_local_digest(upstream)
    latest_version = latest_github_tag(str(upstream.get("repo", "")).strip(), stable_only)
    latest_digest = ghcr_digest_for_version(str(upstream.get("image", "")).strip(), latest_version)
    version_update_available = latest_version != current_version
    digest_update_available = latest_digest != current_digest
    updates_available = version_update_available or digest_update_available

    if os.environ.get("WRITE_UPSTREAM_VERSION") == "true" and updates_available:
        if version_update_available:
            write_local_version(upstream, latest_version)
        if digest_update_available:
            write_local_digest(upstream, latest_digest)

    branch_version = latest_version.replace("/", "-")
    if version_update_available:
        branch_name = f"codex/upstream-{branch_version}"
        pr_title = f"chore(sync): bump upstream sure to {latest_version}"
    elif digest_update_available:
        branch_name = f"codex/upstream-digest-{branch_version}"
        pr_title = f"chore(sync): refresh upstream sure digest for {latest_version}"
    else:
        branch_name = f"codex/upstream-{branch_version}"
        pr_title = f"chore(sync): bump upstream sure to {latest_version}"

    release_notes = ""
    if isinstance(notifications, dict):
        release_notes = str(notifications.get("release_notes_url", "")).strip()
    if not release_notes:
        release_notes = f"https://github.com/{upstream['repo']}/releases"

    write_outputs(
        {
            "current_version": current_version,
            "latest_version": latest_version,
            "current_digest": current_digest,
            "latest_digest": latest_digest,
            "updates_available": "true" if updates_available else "false",
            "version_update_available": "true" if version_update_available else "false",
            "digest_update_available": "true" if digest_update_available else "false",
            "strategy": str(upstream.get("strategy", "pr")).strip() or "pr",
            "upstream_name": str(upstream.get("name", "")).strip(),
            "release_notes_url": release_notes,
            "branch_name": branch_name,
            "pr_title": pr_title,
        }
    )


if __name__ == "__main__":
    main()
