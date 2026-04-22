# sure-aio

![sure-aio](https://socialify.git.ci/jsonbored/sure-aio/image?custom_description=The+easiest+way+to+deploy+Sure+Finance+%28Maybe+Finance+fork%29+via+Unraid+CA.&custom_language=Dockerfile&description=1&font=KoHo&forks=1&language=1&logo=https%3A%2F%2Favatars.githubusercontent.com%2Fu%2F49853598%3Fv%3D4&name=1&owner=1&pattern=Signal&pulls=1&stargazers=1&theme=Dark)

An Unraid-first, single-container deployment of [Sure](https://github.com/we-promise/sure) for people who want the easiest reliable self-hosted install without manually wiring PostgreSQL and Redis on day one.

`sure-aio` packages the Rails web app, Sidekiq worker, PostgreSQL, and Redis into one Unraid template with persistent appdata paths. The wrapper is opinionated for a predictable beginner install, but it does not hide the real tradeoffs: backups still matter, reverse-proxy and SMTP settings still need operator judgment, and bundled services are convenience infrastructure rather than the ideal long-term topology for every deployment.

## What This Image Includes

- Sure web UI on port `3000`
- bundled Sidekiq worker supervised in the same container
- embedded PostgreSQL and Redis for the default beginner path
- persistent Rails storage plus separate PostgreSQL and Redis appdata mounts
- `SKYLIGHT_ENABLED=false` by default so AIO users are not forced into external APM setup
- Unraid CA template at [sure-aio.xml](sure-aio.xml)

## Beginner Install

1. Install the Unraid template.
2. Generate `SECRET_KEY_BASE` with `openssl rand -hex 64`.
3. Leave the default appdata paths in place for first boot.
4. Click Apply and wait for initialization to finish.
5. Open `http://SERVER_IP:3000`.
6. Move to Advanced View only when you actually need external services or upstream feature overrides.

## Power User Surface

This repo is not a stripped-down wrapper. Advanced View exposes the broader practical Sure self-hosting surface plus AIO defaults for the bundled PostgreSQL + Redis path. Useful references:

- [Power User Guide](docs/power-user.md) for external DB/Redis, AI routing, object storage, SSO, SMTP, and custom CA setup
- [pgvector behavior notes](docs/pgvector.md) for the internal-vs-external vector-store path
- `SKYLIGHT_ENABLED=false` is exposed intentionally so AIO users are not forced into upstream Skylight APM defaults

Some settings are deliberately template-owned rather than UI-owned. When upstream sees those environment variables, it may disable the matching app control and treat the container value as source of truth. That is expected in this wrapper.

## Data Persistence

Persistent data lives under the normal Unraid appdata paths:

- Rails uploads: `/mnt/user/appdata/sure-aio/system`
- PostgreSQL data: `/mnt/user/appdata/sure-aio/postgres`
- Redis data: `/mnt/user/appdata/sure-aio/redis`

If you care about the instance, back up all three paths.

## Runtime Notes

- the bundled PostgreSQL and Redis services keep first boot simple, but more advanced deployments may still prefer external infrastructure
- `SECRET_KEY_BASE` is required; do not rotate it casually on a live deployment
- `RAILS_ASSUME_SSL` and `RAILS_FORCE_SSL` should stay `false` unless you are intentionally fronting the app with a correct HTTPS-terminating reverse proxy
- pgvector and qdrant-backed document search are advanced paths, not beginner defaults

## Publishing and Releases

- wrapper releases follow the upstream version plus an AIO revision, such as `v0.6.9-aio.1`
- the repo monitors stable upstream Sure tags and digest drift through [upstream.toml](upstream.toml) and [scripts/check-upstream.py](scripts/check-upstream.py)
- `main` publishes `latest`, the exact upstream version tag, an explicit AIO packaging line tag, and `sha-<commit>`
- release notes are generated with `git-cliff`, and the XML `<Changes>` block is synced from `CHANGELOG.md`

See [docs/releases.md](docs/releases.md) for the release workflow details.

## Validation

Required local validation is pytest-first:

```bash
python3 -m venv .venv-local
.venv-local/bin/pip install -r requirements-dev.txt
.venv-local/bin/pytest tests/unit tests/template --junit-xml=reports/pytest-unit.xml -o junit_family=xunit1
.venv-local/bin/pytest tests/integration -m integration --junit-xml=reports/pytest-integration.xml -o junit_family=xunit1
trunk flakytests validate --junit-paths "reports/pytest-unit.xml,reports/pytest-integration.xml"
trunk check --show-existing --all
```

## Support

- Repo issues: [JSONbored/sure-aio issues](https://github.com/JSONbored/sure-aio/issues)
- Unraid support thread: [Sure-AIO support thread](https://forums.unraid.net/topic/198074-support-sure-aio-all-in-one-sure-for-unraid/)
- Upstream app: [we-promise/sure](https://github.com/we-promise/sure)

## Funding

If this work saves you time, support it here:

- [GitHub Sponsors](https://github.com/sponsors/JSONbored)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JSONbored/sure-aio&type=date&legend=top-left)](https://www.star-history.com/#JSONbored/sure-aio&type=date&legend=top-left)
