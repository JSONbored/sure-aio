# sure-aio Agent Notes

`sure-aio` packages Sure as a single Unraid-friendly container with internal PostgreSQL and Redis.

## Runtime Shape

- Web app: Sure Rails app
- Background jobs: Sidekiq worker
- Database: internal PostgreSQL
- Cache/queue: internal Redis
- Supervision: `s6-overlay`

## Important Behavior

- This repo is intentionally beginner-first: one container, one appdata path, no external database required by default.
- Redis runtime permissions matter because Unraid bind mounts can break ownership assumptions.
- Database preparation was moved away from a fragile standalone oneshot path and into the runtime flow that actually boots the app.
- Worker startup should wait for web readiness rather than racing app boot.

## CI And Publish Policy

- Validation and smoke tests should run on PRs and branch pushes.
- Publish should happen only from the default branch.
- GHCR image naming must stay lowercase.

## What To Preserve

- Keep the Unraid XML contract stable unless there is a strong reason to change user-facing setup.
- Public docs should stay product-facing and beginner-friendly.
- Smoke tests should cover first boot, restart, and persistence.

## Known Good Pattern

- Local smoke testing should verify the running service, not brittle host-side file assumptions.
- If CI flaps, prefer making readiness checks more robust instead of weakening coverage.
