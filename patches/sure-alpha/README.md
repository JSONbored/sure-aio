# Sure Alpha Source Patches

This directory is reserved for alpha-only patches that must change upstream Sure source files directly.

Prefer `rootfs-alpha/rails/config/initializers/` for runtime behavior that can be hooked cleanly. Direct source patches should be small, named, documented in `docs/alpha-lane.md`, and covered by a smoke check.
