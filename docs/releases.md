# Releases

`sure-aio` uses upstream-version-plus-AIO-revision releases such as `v0.6.8-aio.1`.

Stable upstream version monitoring and upstream image digest monitoring are separate concerns. Version bumps should open explicit upstream-update PRs, while digest-only refreshes should flow through normal dependency update automation.

## Version format

- first wrapper release for upstream `v0.6.8`: `v0.6.8-aio.1`
- second wrapper-only release on the same upstream: `v0.6.8-aio.2`
- first wrapper release after upgrading upstream: `v0.6.9-aio.1`

## Published image tags

Every `main` build publishes:

- `latest`
- the exact pinned upstream version
- an explicit packaging line tag like `v0.6.9-aio-v3` (derived from the latest released `v0.6.9-aio.3`)
- `sha-<commit>`

## Release flow

1. Trigger **Release / Sure-AIO** from `main` with `action=prepare`.
2. The workflow computes the next `upstream-aio.N` version and opens a release PR.
3. Review and merge that PR into `main`.
4. Trigger **Release / Sure-AIO** from `main` again with `action=publish`.
5. The workflow reads the merged `CHANGELOG.md` entry, creates the Git tag, and publishes the GitHub Release.
6. The same publish job automatically dispatches **CI / Sure-AIO** (`workflow_dispatch`) with `publish_image=true` so GHCR package tags (including `upstream-aio-vN`) stay aligned with the new release revision.

## One-dispatch mode

You can run the same workflow with `action=full` for one-dispatch orchestration:

1. Creates/updates the release PR from `CHANGELOG.md` generation.
2. Enables auto-merge on that PR.
3. Waits for merge to complete.
4. Creates the Git tag and publishes the GitHub Release.
5. Dispatches **CI / Sure-AIO** with `publish_image=true` to publish GHCR tags.

Notes:

- `action=full` requires `auto_merge_release_pr=true` (default).
- If branch protection/policy blocks auto-merge, the workflow fails with a clear message and no partial hidden state.
