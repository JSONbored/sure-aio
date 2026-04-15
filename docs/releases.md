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
- an explicit packaging line tag like `v0.6.8-aio-v1`
- `sha-<commit>`

## Release flow

1. Trigger **Release / Sure-AIO** from `main` with `action=prepare`.
2. The workflow computes the next `upstream-aio.N` version and opens a release PR.
3. Review and merge that PR into `main`.
4. Trigger **Release / Sure-AIO** from `main` again with `action=publish`.
5. The workflow reads the merged `CHANGELOG.md` entry, creates the Git tag, and publishes the GitHub Release.
