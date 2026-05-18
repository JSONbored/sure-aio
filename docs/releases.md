# Releases

`sure-aio` uses upstream-version-plus-AIO-revision releases such as `v0.6.8-aio.1`.

Stable upstream version monitoring and upstream image digest monitoring are separate concerns. Version bumps should open explicit upstream-update PRs, while digest-only refreshes should flow through normal dependency update automation.

## Version format

- first wrapper release for upstream `v0.6.8`: `v0.6.8-aio.1`
- second wrapper-only release on the same upstream: `v0.6.8-aio.2`
- first wrapper release after upgrading upstream: `v0.6.9-aio.1`

## Published image tags

Every central `aio-fleet` publish for `main` publishes:

- `latest`
- the exact pinned upstream version
- `sha-<commit>`

Release commits also publish the immutable packaging line tag, for example `v0.6.9-aio-v3` derived from `v0.6.9-aio.3`. Ordinary `main` pushes do not overwrite that release tag.

The alpha lane publishes to dedicated Docker Hub and GHCR packages named
`jsonbored/sure-aio-alpha`. It intentionally publishes only `latest-alpha` and
the explicit alpha AIO revision tag, such as `0.7.1-alpha.7-aio.5`. Alpha
prereleases use the `sure-alpha/` Git tag namespace and do not move stable
`latest`.

## Release flow

1. From `aio-fleet`, run `python -m aio_fleet release status --repo sure-aio` to inspect the next release.
2. Run `python -m aio_fleet release prepare --repo sure-aio` on a release branch, then open a `chore(release): <version>` PR.
3. Review and merge that PR into `main`.
4. Run the central `aio-fleet` control check for the release target commit with publish enabled, and require `aio-fleet / required` to pass.
5. Run `python -m aio_fleet release publish --repo sure-aio` from `aio-fleet` to create the GitHub Release.
