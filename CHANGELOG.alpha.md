# Alpha Changelog

Alpha releases are testing builds for `sure-aio-alpha`. They track upstream Sure
alpha prereleases and may include wrapper-only experiments before those changes
are upstreamed or promoted to stable. Alpha uses the dedicated
`jsonbored/sure-aio-alpha` image repo so testing tags stay out of the stable
`jsonbored/sure-aio` package.

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
