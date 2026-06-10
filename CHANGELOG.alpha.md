# Alpha Changelog

Alpha releases are testing builds for `sure-aio-alpha`. They track upstream Sure
alpha prereleases and may include wrapper-only experiments before those changes
are upstreamed or promoted to stable. Alpha uses the dedicated
`jsonbored/sure-aio-alpha` image repo so testing tags stay out of the stable
`jsonbored/sure-aio` package.

## 0.7.2-alpha.4-aio.1 - 2026-06-10

### Build

- Track upstream Sure Alpha 0.7.2-alpha.4.
- Publish Docker Hub and GHCR tags with the configured component revision tag.

### Component Customizations

- Preserve the Sure AIO alpha import-limit overlay documented in `docs/alpha-lane.md`.
- Preserve the strict SureImport preflight/failure overlay until the pinned upstream alpha includes equivalent behavior.
- Preserve the route-parity importer overlay for Enhanced NDJSON split/transfer proof packages until upstream carries it.
- Keep `SURE_IMPORT_MAX_NDJSON_SIZE_MB` and `SURE_IMPORT_MAX_ROWS` alpha-only.
- Do not add dirty-target taxonomy merge as a Unraid template or environment control.
- Keep alpha passkey/WebAuthn template controls separate from stable.

## 0.7.2-alpha.2-aio.1 - 2026-06-02

### Build

- Track upstream Sure Alpha 0.7.2-alpha.2.
- Publish Docker Hub and GHCR tags with the configured component revision tag.

### Component Customizations

- Preserve the Sure AIO alpha import-limit overlay documented in `docs/alpha-lane.md`.
- Preserve the strict SureImport preflight/failure overlay until the pinned upstream alpha includes equivalent behavior.
- Preserve the route-parity importer overlay for Enhanced NDJSON split/transfer proof packages until upstream carries it.
- Keep `SURE_IMPORT_MAX_NDJSON_SIZE_MB` and `SURE_IMPORT_MAX_ROWS` alpha-only.
- Do not add dirty-target taxonomy merge as a Unraid template or environment control.
- Keep alpha passkey/WebAuthn template controls separate from stable.

## 0.7.2-alpha.1-aio.1 - 2026-06-02

### Build

- Track upstream Sure Alpha 0.7.2-alpha.1.
- Publish Docker Hub and GHCR tags with the configured component revision tag.

### Component Customizations

- Preserve the Sure AIO alpha import-limit overlay documented in `docs/alpha-lane.md`.
- Preserve the strict SureImport preflight/failure overlay until the pinned upstream alpha includes equivalent behavior.
- Preserve the route-parity importer overlay for Enhanced NDJSON split/transfer proof packages until upstream carries it.
- Keep `SURE_IMPORT_MAX_NDJSON_SIZE_MB` and `SURE_IMPORT_MAX_ROWS` alpha-only.
- Do not add dirty-target taxonomy merge as a Unraid template or environment control.
- Keep alpha passkey/WebAuthn template controls separate from stable.

## 0.7.1-alpha.11-aio.2 - 2026-06-01

### Fixes

- Preserve Rails origin checks behind reverse proxies.
- Add null-origin compatibility for Sure 0.7.1 alpha proxy login paths.
- Allow the browser service worker behind reverse proxies without triggering Rails cross-origin JavaScript protection.

### Component Customizations

- Preserve the Sure AIO alpha import-limit overlay documented in `docs/alpha-lane.md`.
- Preserve the strict SureImport preflight/failure overlay until the pinned upstream alpha includes equivalent behavior.
- Preserve the route-parity importer overlay for Enhanced NDJSON split/transfer proof packages until upstream carries it.
- Keep `SURE_IMPORT_MAX_NDJSON_SIZE_MB` and `SURE_IMPORT_MAX_ROWS` alpha-only.
- Do not add dirty-target taxonomy merge as a Unraid template or environment control.
- Keep alpha passkey/WebAuthn template controls separate from stable.

## 0.7.1-alpha.11-aio.1 - 2026-05-25

### Build

- Track upstream Sure Alpha 0.7.1-alpha.11.
- Publish Docker Hub and GHCR tags with the configured component revision tag.

### Component Customizations

- Preserve the Sure AIO alpha import-limit overlay documented in `docs/alpha-lane.md`.
- Preserve the strict SureImport preflight/failure overlay until the pinned upstream alpha includes equivalent behavior.
- Preserve the route-parity importer overlay for Enhanced NDJSON split/transfer proof packages until upstream carries it.
- Keep `SURE_IMPORT_MAX_NDJSON_SIZE_MB` and `SURE_IMPORT_MAX_ROWS` alpha-only.
- Do not add dirty-target taxonomy merge as a Unraid template or environment control.
- Keep alpha passkey/WebAuthn template controls separate from stable.

## 0.7.1-alpha.10-aio.1 - 2026-05-22

### Build

- Track upstream Sure Alpha 0.7.1-alpha.10.
- Publish Docker Hub and GHCR tags with the configured component revision tag.

### Component Customizations

- Preserve the Sure AIO alpha import-limit overlay documented in `docs/alpha-lane.md`.
- Preserve the strict SureImport preflight/failure overlay until the pinned upstream alpha includes equivalent behavior.
- Preserve the route-parity importer overlay for Enhanced NDJSON split/transfer proof packages until upstream carries it.
- Keep `SURE_IMPORT_MAX_NDJSON_SIZE_MB` and `SURE_IMPORT_MAX_ROWS` alpha-only.
- Do not add dirty-target taxonomy merge as a Unraid template or environment control.
- Keep alpha passkey/WebAuthn template controls separate from stable.

## 0.7.1-alpha.9-aio.2 - 2026-05-19

### Fixes

- Harden Sure runtime, alpha import preflight, template secret masking, and release paths.
- Enforce capped alpha import limits and structured malformed Account preflight errors.
- Derive external assistant session keys when operators leave the shared key blank.
- Tighten first-boot database readiness so Rails waits for authenticated PostgreSQL access.

## 0.7.1-alpha.9-aio.1 - 2026-05-19

### Build

- Track upstream Sure Alpha 0.7.1-alpha.9.
- Publish Docker Hub and GHCR tags with the configured component revision tag.

### Component Customizations

- Preserve the Sure AIO alpha import-limit overlay documented in `docs/alpha-lane.md`.
- Preserve the strict SureImport preflight/failure overlay until the pinned upstream alpha includes equivalent behavior.
- Preserve the route-parity importer overlay for Enhanced NDJSON split/transfer proof packages until upstream carries it.
- Keep `SURE_IMPORT_MAX_NDJSON_SIZE_MB` and `SURE_IMPORT_MAX_ROWS` alpha-only.
- Do not add dirty-target taxonomy merge as a Unraid template or environment control.
- Keep alpha passkey/WebAuthn template controls separate from stable.

## 0.7.1-alpha.7-aio.8 - 2026-05-19

### Alpha Customizations

- Add the self-hosted admin financial reset UI under Settings -> Self-Hosting -> Danger Zone, backed by the same dry-run/destructive reset service as the Rails task.
- Keep admin reset out of the Unraid template/env surface; operators review scope and counts in the app UI or run the explicit Rails task.
- Clarify that WebAuthn env vars only configure browser trust, and passkeys are added inside Sure from Settings -> Security after authenticator-app 2FA is enabled.
- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.

## 0.7.1-alpha.7-aio.7 - 2026-05-19

### Alpha Customizations

- Add a self-hosted admin reset task for clearing one selected user's family financial/import data before a fresh import while preserving user/auth records.
- Keep the reset task dry-run by default and require `CONFIRM_RESET_FINANCIAL_DATA=yes` for destructive use.
- Keep reset controls out of the Unraid template/env surface; run the task explicitly inside the Rails container.
- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.

## 0.7.1-alpha.7-aio.6 - 2026-05-18

### Alpha Customizations

- Add a strict alpha-only SureImport preflight overlay so bad Sure NDJSON fails before publish/enqueue with specific blocking errors instead of the generic failure path.
- Show the persisted `import.error` details on the SureImport failure page so operators can see the actual preflight/import error list.
- Keep the dirty-target merge option out of Unraid template/env controls; alpha certification remains strict unless upstream/API support explicitly proves merge mode.
- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.

## 0.7.1-alpha.7-aio.5 - 2026-05-18

### Build

- Reissue the current Sure alpha package to the dedicated `jsonbored/sure-aio-alpha` Docker Hub and GHCR packages after `0.7.1-alpha.7-aio.4` was published under the shared stable package path.
- Keep the alpha registry tag set intentionally small: `latest-alpha` plus the explicit `0.7.1-alpha.7-aio.5` package tag.
- Keep runtime behavior aligned with the prior alpha lane builds: upstream Sure alpha 0.7.1-alpha.7, the alpha-only import-limit overlay, and alpha WebAuthn template controls.
- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.

## 0.7.1-alpha.7-aio.4 - 2026-05-18

### Build

- Reissue the current Sure alpha package with registry tags and GitHub prerelease history aligned after `0.7.1-alpha.7-aio.3` was created while the alpha Dockerfile still declared AIO revision 2.
- Keep runtime behavior aligned with the prior alpha lane builds: upstream Sure alpha 0.7.1-alpha.7, the alpha-only import-limit overlay, the alpha registry tags configured for that revision, and alpha WebAuthn template controls.
- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.

## 0.7.1-alpha.7-aio.3 - 2026-05-18

### Build

- Reissue the current Sure alpha package from the latest main commit after the immutable `0.7.1-alpha.7-aio.2` prerelease was already published from an older commit.
- Keep runtime behavior aligned with `0.7.1-alpha.7-aio.2`: upstream Sure alpha 0.7.1-alpha.7, the alpha-only import-limit overlay, the alpha registry tags configured for that revision, and alpha WebAuthn template controls.
- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.

## 0.7.1-alpha.7-aio.2 - 2026-05-18

### Build

- Reissue the current Sure alpha package with a new AIO revision after fleet release-history isolation fixes.
- Publish the alpha lane with alpha-only registry tags for this revision.
- Keep runtime behavior aligned with `0.7.1-alpha.7-aio.1`: upstream Sure alpha 0.7.1-alpha.7, the alpha-only import-limit overlay, and the alpha WebAuthn template controls.
- Keep stable `sure-aio` unchanged; this release history applies only to `sure-aio-alpha`.

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
