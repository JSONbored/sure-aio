# Build Status

Before treating a release as ready:

- local smoke test should pass
- the upstream Sure version should be pinned explicitly
- the upstream monitor should point at stable Sure tags
- GitHub Actions should pass for validation, smoke-test, and security
- the GHCR package should remain public and pullable
