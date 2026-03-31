# Releases

`sure-aio` uses GitHub container packages and GitHub releases together, but they mean different things:

- container packages are the images published to GHCR on `main`
- GitHub releases are intentional, versioned milestones for the AIO wrapper itself

## Version format

`sure-aio` follows the pinned upstream Sure version and adds an AIO wrapper revision:

- first wrapper release for upstream `v0.6.8`: `v0.6.8-aio.1`
- second wrapper-only release on the same upstream: `v0.6.8-aio.2`
- first wrapper release after upgrading upstream to `v0.6.9`: `v0.6.9-aio.1`

This keeps the repo honest about what changed:

- the upstream application version
- the JSONbored AIO packaging revision

## Published image tags

Every `main` build publishes:

- `latest`
- the exact pinned upstream version such as `v0.6.8`
- the current packaging line tag such as `v0.6.8-aio-v1`
- `sha-<commit>`

## Release flow

1. Trigger the **Release / Sure-AIO** workflow from `main`.
2. The workflow computes the next version and opens a PR titled `chore(release): <version>`.
3. Merge that PR into `main`.
4. After merge, the release workflow creates the Git tag and GitHub Release automatically from the merged changelog.

This design avoids direct pushes from Actions into a protected `main` branch while still keeping release bookkeeping automated.
