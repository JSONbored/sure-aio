# Changelog

All notable changes to this project will be documented in this file.

## 0.7.1-aio.1 - 2026-05-31

### Fixes

- Preserve Rails origin checks behind reverse proxies

- Add null-origin support for Sure 0.7.1

## 0.7.0-hotfix.3-aio.4 - 2026-05-31

### Fixes

- Preserve Rails origin checks behind reverse proxies

## 0.7.0-hotfix.3-aio.3 - 2026-05-26

### Documentation

- Normalize CA metadata

### Maintenance

- Reconcile app manifest

- Bump sure alpha to 0.7.1-alpha.10

- Bump sure alpha to 0.7.1-alpha.11

## 0.7.0-hotfix.3-aio.2 - 2026-05-19

### Fixes

- Harden Sure runtime, template secret masking, and release paths.
- Derive external assistant session keys when operators leave the shared key blank.
- Tighten first-boot database readiness so Rails waits for authenticated PostgreSQL access.

## 0.7.0-hotfix.3-aio.1 - 2026-05-17

### Maintenance

- Bump sure to 0.7.0-hotfix.3 (#95)

## 0.7.0-hotfix.2-aio.1 - 2026-05-05

### Build

- Harden apt package installs

### Documentation

- Document central app test dependencies

### Maintenance

- Format fleet manifest and changelog
- Move shared automation to aio-fleet
- Declare aio-fleet ownership
- Bump sure to 0.7.0-hotfix.1
- Refresh aio-fleet manifest
- Bump sure to 0.7.0-hotfix.2
- Refresh sure 0.7.0-hotfix.2 digest

### Refactors

- Remove legacy shared contract tests

## 0.7.0-aio.1 - 2026-05-01

### CI

- Use shared AIO workflows (#62)
- Pin shared validation policy
- Use shared AIO workflows
- Sync workflow path filters
- Sync catalog publication state
- Pin publish helper workflow fix
- Pin Docker Hub primary workflow
- Pin control-plane workflow foundation

### Dependency Updates

- Update Sure to v0.7.0

### Features

- Expose manual publish targets

### Fixes

- Sync shared validation and trunk cleanup
- Sync release shim path fallback
- Expose sure v0.7 runtime options
- Expose Sure v0.7 runtime options (#78)

### Maintenance

- Sync shared repository boilerplate

### Refactors

- Use shared derived repo validation
- Use shared release helper shim

### Tests

- Use shared runtime contract helpers

## v0.6.9-aio.5 - 2026-04-25

### CI

- Optimize pytest gating and Trunk uploads (#56)
- Standardize fleet publish and validation flow (#57)
- Centralize trunk config and gate release tags (#58)
- Consolidate pytest workflow steps (#60)
- Pin package tags to release targets (#59)

## v0.6.9-aio.4 - 2026-04-16

### Build

- Harden bundled dependencies and refresh security patches (#50)

### CI

- Add one-dispatch full release orchestration (#43)
- Fallback to direct merge when auto-merge is disabled
- Pass explicit aio track override from release
- Harden full release flow and deterministic aio tag publishing
- Trigger registry parity publish

### Fixes

- Restore CA trust signals and automate changelog sync (#46)
- Gate Docker Hub login without direct secrets expressions
- Make workflow-dispatch publish gates deterministic (#48)
- Always publish on manual main workflow dispatch
- Let manual publish proceed when smoke test is skipped

### Maintenance

- Trigger package publish for aio tag alignment

## v0.6.9-aio.3 - 2026-04-15

### Fixes

- Stabilize upstream pinning and align AIO package tags (#41)

## v0.6.9-aio.2 - 2026-04-15

### Documentation

- Add sure-aio support thread url (#33)

### Fixes

- Accept github pr suffix on release commits
- Resolve publish commit lookup in python
- Allow tagging workflow-updating commits
- Use dedicated token for tag and release
- Prefer pat auth for publish
- Limit changelog generation to last aio tag
- Persist self-hosted mode through dockerman (#31)
- Persist self-hosted mode through dockerman (#32)
- Update README to add new preview image (#37)
- Finalize CA metadata and upstream env coverage (#38)

## v0.6.9-aio.1 - 2026-04-01

### Dependency Updates

- Update ghcr.io/we-promise/sure docker digest to 3d899b3 (#21)

### Features

- Align sure-aio with upstream v0.6.9 self-hosting surface (#23)

### Fixes

- Make releases manual and gate heavy workflows

## v0.6.8-aio.1 - 2026-03-31

### Dependency Updates

- Update docker/setup-qemu-action action to v4 (#13)
- Update docker/setup-buildx-action action to v4 (#12)
- Update docker/login-action action to v4 (#11)
- Update docker/build-push-action action to v7 (#10)
- Update non-major infrastructure updates (#9)
- Update ghcr.io/we-promise/sure docker digest to 12f32c0 (#7)
- Pin docker/dockerfile docker tag to 4a43a54 (#6)

### Documentation

- Write comprehensive binhex-style README and power user configuration reference guide
- Exhaustively map power-user markdown guide to encompass all AI, telemetry, storage, SSO, and encryption advanced features
- Improve README formatting, add deep links to Power User guide sections, and append Star History chart

### Features

- Complete XML redesign based on upstream Sure feature parity (AI, Vectors, SMTP)
- Complete XML redesign based on upstream Sure feature parity (AI, Vectors, SMTP, OIDC, Langfuse)
- Exhaustive XML mapping of all upstream env variables including Active Storage, PostHog, encryption salts, and raw external AI configs
- Finalize enterprise standards for sure-aio (healthchecks, nightly scans, and branding)
- Standardize package tags and add release automation (#19)

### Fixes

- Change default db hosts from local context to generic IP strings
- Restructure s6-overlay v3 dependencies so db migrations safely wait for postgres to be healthy before booting the web/worker process
- Remove duplicate uppercase Sure-AIO.xml file that was orphaned during early generation
- Update build workflow to point to root context and master branch, remove pre-refactor legacy service scripts
- Add missing type and contents.d files for background worker services
- Pin scout and upload actions to full-length SHAs
- Update build-push-action sha pin to valid v6 hash
- Enforce lowercase image tags and optimize scout execution
- Disable load to support multi-platform exports and target scout via registry
- Dynamically resolve postgres version path to fix fatal binary exec errors
- Fix missing token resolution and globalize node24 fallback in sync action
- Enforce strict SYNC_TOKEN and remove unsecured GitHub token fallback
- Fix default startup and add smoke coverage

### Maintenance

- Standardize README, add FUNDING.yml, and clean up legacy files
- Add security policy and unraid template sync workflow
- Implement explicit least privilege on GitHub Actions runner
- Enforce author identity in automation
- Revert to verifiable bot identity for non-repudiation
- Pin GitHub actions to strictly verified full-length SHAs
- Replace docker-scout with anchore-grype to avoid authentication issues
- Temporarily remove anchor scan to allow build pipeline completion under strict allowlist

### Other Changes

- Initial commit: Sure-AIO build files and Unraid XML template
- Generalize postgresql package name for base image compatibility
- Security & CI: Fix node24 deprecation and package write permissions
- Feat/security scout renovate (#1)
- Codex/fix default startup (#5)
- Codex/consolidate ci workflows (#14)
- Codex/fix template icons (#15)
- Fix awesome-unraid sync for protected main
- Standardize tags and add release automation

### Refactors

- Fully realize simplelogin-aio methodology by injecting and orchestrating PostgreSQL and Redis natively inside the container via s6-overlay, dropping external DB requirements

<!-- generated by git-cliff -->
