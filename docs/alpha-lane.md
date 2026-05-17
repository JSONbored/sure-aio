# Sure AIO Alpha Lane

`sure-aio-alpha` is the testing lane for Sure prereleases and small wrapper-only experiments. It is separately installable from stable `sure-aio`, publishes as `jsonbored/sure-aio-alpha`, and uses separate Unraid appdata paths.

Alpha updates track upstream `we-promise/sure` alpha prereleases through `aio-fleet`. The lane is registry-only: routine alpha bumps should publish images and update the alpha template without creating stable Sure AIO release debt.

## Upstream Alpha Template Surface

The alpha Unraid template exposes upstream alpha-only self-hosting controls when they are useful for testing and documented upstream:

- `WEBAUTHN_RP_ID`
- `WEBAUTHN_ALLOWED_ORIGINS`

These are not wrapper patches. They belong to upstream Sure's passkey/WebAuthn MFA alpha work and are shown in the alpha template only until the feature stabilizes.

## Patch Ledger

### import-limits-env

- Status: active alpha-only overlay.
- Overlay: `rootfs-alpha/rails/config/initializers/sure_aio_alpha_import_limits.rb`.
- Defaults: `SURE_IMPORT_MAX_NDJSON_SIZE_MB=250`, `SURE_IMPORT_MAX_ROWS=1000000`.
- Why: TransmogriFi local testing needs larger Sure NDJSON imports than upstream's current `10MB` upload limit and `100000` row/import limit.
- Upstream issue/PR: none yet.
- Promotion/removal path: keep alpha-only until the behavior is accepted upstream or we deliberately decide the raised/configurable limits are safe for stable Unraid users.

## Governance

- Every alpha customization must be named here and covered by validation.
- Prefer environment-driven Rails initializers over direct source patches because they survive daily alpha image bumps better.
- Use `patches/sure-alpha/` only when an initializer cannot hook the behavior cleanly.
- If an upstream alpha bump breaks an overlay, validation should fail before the alpha image is published.
