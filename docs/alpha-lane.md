# Sure AIO Alpha Lane

`sure-aio-alpha` is the testing lane for Sure prereleases and small wrapper-only experiments. It is separately installable from stable `sure-aio`, publishes to the dedicated `jsonbored/sure-aio-alpha` Docker Hub and GHCR packages, and uses separate Unraid appdata paths.

Alpha updates track upstream `we-promise/sure` alpha prereleases through `aio-fleet`. Routine alpha bumps publish images, update the alpha template, and create/update GitHub prereleases under the `sure-alpha/` tag namespace without creating stable Sure AIO release debt.

Release history for this lane lives in `CHANGELOG.alpha.md`. Image tags are intentionally limited to `latest-alpha` and the explicit alpha AIO revision tag, such as `0.7.1-alpha.7-aio.7`.

## Upstream Alpha Template Surface

The alpha Unraid template exposes upstream alpha-only self-hosting controls when they are useful for testing and documented upstream:

- `WEBAUTHN_RP_ID`
- `WEBAUTHN_ALLOWED_ORIGINS`

These are not wrapper patches. They belong to upstream Sure's passkey/WebAuthn MFA alpha work and are shown in the alpha template only until the feature stabilizes.

The alpha XML changelog must call out exposed upstream alpha controls separately from wrapper patches so users can tell what came from Sure and what came from AIO.

## Patch Ledger

### import-limits-env

- Status: active alpha-only overlay.
- Overlay: `rootfs-alpha/rails/config/initializers/sure_aio_alpha_import_limits.rb`.
- Defaults: `SURE_IMPORT_MAX_NDJSON_SIZE_MB=250`, `SURE_IMPORT_MAX_ROWS=1000000`.
- Why: local alpha testing needs larger Sure NDJSON imports than upstream's current `10MB` upload limit and `100000` row/import limit.
- Upstream issue/PR: none yet.
- Promotion/removal path: keep alpha-only until the behavior is accepted upstream or we deliberately decide the raised/configurable limits are safe for stable Unraid users.

### import-preflight-strict

- Status: active alpha-only overlay.
- Overlay: `rootfs-alpha/rails/config/initializers/sure_aio_alpha_import_preflight.rb` and `rootfs-alpha/rails/app/views/imports/_failure.html.erb`.
- Defaults: strict clean-target validation before `SureImport#publish_later` and `SureImport#publish`.
- Why: alpha certification needs specific operator-visible failures for dirty taxonomy, missing required fields, unsupported record types, bad accountables, duplicate valuation rows, and missing references instead of the generic failure screen.
- Template/env surface: none. Dirty-target merge is not an Unraid variable and should remain explicit upstream/API behavior when separately proven.
- Upstream issue/PR: PR 1785 may need reconciliation because it also touches `SureImport` and import sessions.
- Promotion/removal path: remove this overlay once the pinned upstream alpha image includes equivalent model/API/UI preflight behavior.

### route-parity-importer

- Status: active alpha-only overlay.
- Overlay: `rootfs-alpha/rails/config/initializers/sure_aio_alpha_route_parity_importer.rb`.
- Why: Enhanced route proof packages can include split lines and linked transfers before the pinned upstream alpha importer has that exact proof behavior.
- Template/env surface: none.
- Promotion/removal path: remove once the pinned upstream alpha image includes equivalent split-line and transfer ID mapping behavior.

### admin-financial-reset

- Status: active alpha-only overlay.
- Overlay: `rootfs-alpha/rails/app/models/family/financial_data_reset.rb` and `rootfs-alpha/rails/lib/tasks/sure_admin.rake`.
- Command: `bin/rails sure:admin:reset_financial_data USER_EMAIL="user@example.com"` for dry-run, or add `CONFIRM_RESET_FINANCIAL_DATA=yes` for destructive reset.
- Defaults: dry-run unless the confirmation environment variable is set exactly to `yes`.
- Why: self-hosted alpha operators need a safe way to clear one selected family workspace before re-importing a complete Sure NDJSON package.
- Template/env surface: none. This is an explicit admin task, not an Unraid form control.
- Promotion/removal path: remove once the pinned upstream alpha image includes equivalent self-hosted admin reset behavior.

## Governance

- Every alpha customization must be named here and covered by validation.
- Prefer environment-driven Rails initializers over direct source patches because they survive daily alpha image bumps better.
- Use `patches/sure-alpha/` only when an initializer cannot hook the behavior cleanly.
- If an upstream alpha bump breaks an overlay, validation should fail before the alpha image is published.

## Validation Expectations

- XML tests must keep stable `sure-aio` free of alpha-only variables.
- XML tests must verify the beta marker, separate tag/template identity, separate appdata paths, import controls, WebAuthn controls, and alpha changelog text.
- Runtime tests must boot the alpha image and verify `/up`, `/rails/.sure-version`, import limit defaults/overrides/fallback behavior, WebAuthn environment parsing, strict SureImport preflight behavior, and the admin reset task surface inside Rails.
