# Alpha Changelog

Alpha releases are testing builds for `sure-aio-alpha`. They track upstream Sure
alpha prereleases and may include wrapper-only experiments before those changes
are upstreamed or promoted to stable.

## 0.7.1-alpha.7-aio.1 - 2026-05-18

### Build

- Track upstream Sure alpha 0.7.1-alpha.7.
- Publish alpha Docker Hub and GHCR tags with a distinct AIO revision tag.

### Alpha Customizations

- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.
- Add the alpha-only import-limit overlay documented in `docs/alpha-lane.md`.
- Expose `SURE_IMPORT_MAX_NDJSON_SIZE_MB` with a raised default of `250`.
- Expose `SURE_IMPORT_MAX_ROWS` with a raised default of `1000000`.
- Expose upstream alpha passkey/WebAuthn controls in the alpha Unraid template:
  `WEBAUTHN_RP_ID` and `WEBAUTHN_ALLOWED_ORIGINS`.
