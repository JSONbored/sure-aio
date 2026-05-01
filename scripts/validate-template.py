#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import subprocess  # nosec B404
import sys
import xml.etree.ElementTree as ET  # nosec B405 - this validator reads a trusted local repository XML file only
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "sure-aio.xml"

# This is the audited upstream self-hosting/runtime surface we intentionally expose
# in the Unraid template. Exclusions like PORT and DISABLE_SSL are deliberate.
REQUIRED_TARGETS = {
    "ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY",
    "ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT",
    "ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY",
    "ACTIVE_STORAGE_SERVICE",
    "AI_DEBUG_MODE",
    "APP_DOMAIN",
    "APP_URL",
    "ALPHA_VANTAGE_API_KEY",
    "ALPHA_VANTAGE_MAX_REQUESTS_PER_DAY",
    "ALPHA_VANTAGE_URL",
    "ASSISTANT_TYPE",
    "AUTH_JIT_MODE",
    "AUTH_LOCAL_ADMIN_OVERRIDE_ENABLED",
    "AUTH_LOCAL_LOGIN_ENABLED",
    "AUTH_PROVIDERS_SOURCE",
    "AUTO_SYNC_ENABLED",
    "AUTO_SYNC_TIME",
    "AUTO_SYNC_TIMEZONE",
    "ALLOWED_OIDC_DOMAINS",
    "BRAND_FETCH_CLIENT_ID",
    "BRAND_FETCH_HIGH_RES_LOGOS",
    "BRAND_NAME",
    "BINANCE_EGRESS_IP",
    "BINANCE_PUBLIC_URL",
    "CATEGORIZATION_MODEL",
    "CATEGORIZATION_PROVIDER",
    "CHAT_MODEL",
    "CHAT_PROVIDER",
    "CLOUDFLARE_ACCESS_KEY_ID",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_BUCKET",
    "CLOUDFLARE_SECRET_ACCESS_KEY",
    "DB_HOST",
    "DB_PORT",
    "DEFAULT_UI_LAYOUT",
    "EMAIL_SENDER",
    "EMBEDDING_ACCESS_TOKEN",
    "EMBEDDING_DIMENSIONS",
    "EMBEDDING_MODEL",
    "EMBEDDING_URI_BASE",
    "EXCHANGE_RATE_PROVIDER",
    "EXTERNAL_ASSISTANT_AGENT_ID",
    "EXTERNAL_ASSISTANT_ALLOWED_EMAILS",
    "EXTERNAL_ASSISTANT_SESSION_KEY",
    "EXTERNAL_ASSISTANT_TOKEN",
    "EXTERNAL_ASSISTANT_URL",
    "EODHD_API_KEY",
    "EODHD_MAX_REQUESTS_PER_DAY",
    "EODHD_URL",
    "GENERIC_S3_ACCESS_KEY_ID",
    "GENERIC_S3_BUCKET",
    "GENERIC_S3_ENDPOINT",
    "GENERIC_S3_FORCE_PATH_STYLE",
    "GENERIC_S3_REGION",
    "GENERIC_S3_SECRET_ACCESS_KEY",
    "GCS_BUCKET",
    "GCS_KEYFILE",
    "GCS_KEYFILE_JSON",
    "GCS_PROJECT",
    "GITHUB_BUTTON_ICON",
    "GITHUB_BUTTON_LABEL",
    "GITHUB_CLIENT_ID",
    "GITHUB_CLIENT_SECRET",
    "GOOGLE_BUTTON_ICON",
    "GOOGLE_BUTTON_LABEL",
    "GOOGLE_OAUTH_CLIENT_ID",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "LANGFUSE_HOST",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_REGION",
    "LANGFUSE_SECRET_KEY",
    "INDEXA_API_TOKEN",
    "LEGAL_PRIVACY_URL",
    "LEGAL_TERMS_URL",
    "LLM_CONTEXT_WINDOW",
    "LLM_JSON_MODE",
    "LLM_MAX_HISTORY_TOKENS",
    "LLM_MAX_ITEMS_PER_CALL",
    "LLM_MAX_RESPONSE_TOKENS",
    "LLM_SYSTEM_PROMPT_RESERVE",
    "LOGTAIL_API_KEY",
    "LOGTAIL_INGESTING_HOST",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "MCP_API_TOKEN",
    "MCP_USER_EMAIL",
    "MFAPI_URL",
    "NO_PROXY",
    "OIDC_BUTTON_ICON",
    "OIDC_BUTTON_LABEL",
    "OIDC_AUTHENTIK_CLIENT_ID",
    "OIDC_AUTHENTIK_CLIENT_SECRET",
    "OIDC_AUTHENTIK_ISSUER",
    "OIDC_AUTHENTIK_REDIRECT_URI",
    "OIDC_CLIENT_ID",
    "OIDC_CLIENT_SECRET",
    "OIDC_ISSUER",
    "OIDC_KEYCLOAK_CLIENT_ID",
    "OIDC_KEYCLOAK_CLIENT_SECRET",
    "OIDC_KEYCLOAK_ISSUER",
    "OIDC_KEYCLOAK_REDIRECT_URI",
    "OIDC_REDIRECT_URI",
    "ONBOARDING_STATE",
    "OPENAI_ACCESS_TOKEN",
    "OPENAI_MODEL",
    "OPENAI_REQUEST_TIMEOUT",
    "OPENAI_SUPPORTS_PDF_PROCESSING",
    "OPENAI_SUPPORTS_RESPONSES_ENDPOINT",
    "OPENAI_URI_BASE",
    "PLAID_CLIENT_ID",
    "PLAID_ENV",
    "PLAID_EU_CLIENT_ID",
    "PLAID_EU_ENV",
    "PLAID_EU_SECRET",
    "PLAID_INCLUDE_PENDING",
    "PLAID_SECRET",
    "POSTGRES_DB",
    "POSTGRES_PASSWORD",
    "POSTGRES_USER",
    "POSTHOG_HOST",
    "POSTHOG_KEY",
    "PRODUCT_NAME",
    "QDRANT_API_KEY",
    "QDRANT_URL",
    "RAILS_ASSUME_SSL",
    "RAILS_FORCE_SSL",
    "RAILS_LOG_LEVEL",
    "RAILS_MAX_THREADS",
    "REDIS_PASSWORD",
    "REDIS_SENTINEL_HOSTS",
    "REDIS_SENTINEL_MASTER",
    "REDIS_SENTINEL_USERNAME",
    "REDIS_URL",
    "REQUIRE_EMAIL_CONFIRMATION",
    "REQUIRE_INVITE_CODE",
    "S3_ACCESS_KEY_ID",
    "S3_BUCKET",
    "S3_REGION",
    "S3_SECRET_ACCESS_KEY",
    "SECRET_KEY_BASE",
    "SECURITIES_PROVIDER",
    "SECURITIES_PROVIDERS",
    "SELF_HOSTING_ENABLED",
    "SENTRY_DSN",
    "SIDEKIQ_WEB_PASSWORD",
    "SIDEKIQ_WEB_USERNAME",
    "SKYLIGHT_AUTHENTICATION",
    "SKYLIGHT_ENABLED",
    "SMTP_ADDRESS",
    "SMTP_PASSWORD",
    "SMTP_PORT",
    "SMTP_TLS_ENABLED",
    "SMTP_TLS_SKIP_VERIFY",
    "SMTP_USERNAME",
    "SIMPLEFIN_CC_OVERPAYMENT_HEURISTIC",
    "SIMPLEFIN_DEBUG_RAW",
    "SIMPLEFIN_INCLUDE_PENDING",
    "SSL_CA_FILE",
    "SSL_CERT_FILE",
    "SSL_DEBUG",
    "SSL_VERIFY",
    "LUNCHFLOW_DEBUG_RAW",
    "LUNCHFLOW_INCLUDE_PENDING",
    "TIINGO_API_KEY",
    "TIINGO_MAX_REQUESTS_PER_HOUR",
    "TIINGO_URL",
    "TWELVE_DATA_API_KEY",
    "TWELVE_DATA_MAX_REQUESTS_PER_MINUTE",
    "TWELVE_DATA_MIN_REQUEST_INTERVAL",
    "TWELVE_DATA_URL",
    "VECTOR_STORE_PROVIDER",
    "WEB_CONCURRENCY",
    "YAHOO_FINANCE_MAX_RETRIES",
    "YAHOO_FINANCE_MIN_REQUEST_INTERVAL",
    "YAHOO_FINANCE_RETRY_INTERVAL",
    "YAHOO_FINANCE_URL",
}

GENERATED_CHANGELOG_NOTE = (
    "Generated from CHANGELOG.md during release preparation. Do not edit manually."
)
GENERATED_CHANGELOG_BULLET = f"- {GENERATED_CHANGELOG_NOTE}"
CHANGELOG_HEADER_PATTERN = re.compile(r"^### \d{4}-\d{2}-\d{2}$")
LEGACY_CHANGELOG_MARKERS = (
    "[b]Latest release[/b]",
    "GitHub Releases",
    "Full changelog and release notes:",
)
ALLOWED_CATEGORY_TOKENS = {
    "Productivity:",
    "Tools:Utilities",
}


def run_common_template_validation() -> int:
    candidates = []
    explicit = os.environ.get("AIO_FLEET_MANIFEST", "").strip()
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            ROOT / ".aio-fleet" / "fleet.yml",
            ROOT.parent / "aio-fleet" / "fleet.yml",
        ]
    )
    manifest = next((candidate for candidate in candidates if candidate.exists()), None)
    if manifest is None:
        print(
            "warning: aio-fleet manifest not found; skipping common template validation",
            file=sys.stderr,
        )
        return 0

    env = os.environ.copy()
    fleet_src = manifest.parent / "src"
    if fleet_src.exists():
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{fleet_src}{os.pathsep}{existing}" if existing else str(fleet_src)
        )
    python = sys.executable
    fleet_python = manifest.parent / ".venv" / "bin" / "python"
    if fleet_python.exists():
        python = str(fleet_python)

    result = subprocess.run(  # nosec B603
        [
            python,
            "-m",
            "aio_fleet.cli",
            "--manifest",
            str(manifest),
            "validate-template-common",
            "--repo",
            ROOT.name,
            "--repo-path",
            str(ROOT),
        ],
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


def validate_changes(changes: str) -> str | None:
    for marker in LEGACY_CHANGELOG_MARKERS:
        if marker in changes:
            return f"sure-aio.xml <Changes> still uses the legacy release-link format: {marker}"

    lines = [line.strip() for line in changes.splitlines() if line.strip()]
    if len(lines) < 3:
        return "sure-aio.xml <Changes> must include a date heading, the generated note, and at least one bullet"
    if not CHANGELOG_HEADER_PATTERN.fullmatch(lines[0]):
        return "sure-aio.xml <Changes> must start with '### YYYY-MM-DD'"
    if lines[1] != GENERATED_CHANGELOG_BULLET:
        return f"sure-aio.xml <Changes> second line should be '{GENERATED_CHANGELOG_BULLET}'"
    invalid_lines = [line for line in lines[1:] if not line.startswith("- ")]
    if invalid_lines:
        return f"sure-aio.xml <Changes> must use bullet lines after the heading; found {invalid_lines[0]!r}"
    return None


def main() -> int:
    common_status = run_common_template_validation()
    if common_status:
        return common_status

    tree = ET.parse(TEMPLATE_PATH)  # nosec B314 - trusted local template file only
    root = tree.getroot()

    targets = {
        elem.attrib["Target"]
        for elem in root.findall(".//Config")
        if "Target" in elem.attrib and elem.attrib["Target"]
    }

    missing = sorted(REQUIRED_TARGETS - targets)
    if missing:
        print(
            "sure-aio.xml is missing required upstream/runtime targets:",
            file=sys.stderr,
        )
        for target in missing:
            print(f"  - {target}", file=sys.stderr)
        return 1

    category = (root.findtext("Category") or "").strip()
    if not category:
        print("sure-aio.xml is missing a <Category> value", file=sys.stderr)
        return 1

    category_tokens = [token for token in category.split(" ") if token]
    unknown_categories = sorted(set(category_tokens) - ALLOWED_CATEGORY_TOKENS)
    if unknown_categories:
        print(
            "sure-aio.xml contains unknown/unapproved category tokens:", file=sys.stderr
        )
        for token in unknown_categories:
            print(f"  - {token}", file=sys.stderr)
        print(
            f"Allowed tokens: {', '.join(sorted(ALLOWED_CATEGORY_TOKENS))}",
            file=sys.stderr,
        )
        return 1

    changes = (root.findtext("Changes") or "").strip()
    if not changes:
        print("sure-aio.xml is missing a non-empty <Changes> section", file=sys.stderr)
        return 1
    error = validate_changes(changes)
    if error:
        print(error, file=sys.stderr)
        return 1

    print(
        f"sure-aio.xml parsed successfully and includes {len(REQUIRED_TARGETS)} required targets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
