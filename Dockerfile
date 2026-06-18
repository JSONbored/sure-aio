# syntax=docker/dockerfile:1@sha256:2780b5c3bab67f1f76c781860de469442999ed1a0d7992a5efdf2cffc0e3d769
# checkov:skip=CKV_DOCKER_8: s6-overlay entrypoint must start as root so init scripts can prepare filesystem state before dropping privileges

ARG UPSTREAM_VERSION=0.7.1-hotfix.1
ARG UPSTREAM_IMAGE_DIGEST=sha256:64fa5951bcd426863759f5f06cf0316522bc5ecb3552bb6894f4101ca8708f6f
ARG PGVECTOR_VERSION=0.8.2
FROM jsonbored/aio-base:s6-3.2.1.0@sha256:07db479a01a95ba28480b4605f5d1cc8bedb574b77cf167ee46e29b9558fee90 AS aio-base

FROM ghcr.io/we-promise/sure:${UPSTREAM_VERSION}@${UPSTREAM_IMAGE_DIGEST}

ARG UPSTREAM_VERSION
ARG PGVECTOR_VERSION

# hadolint ignore=DL3002
USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /rails

# Shared, pinned s6-overlay + hardening from the fleet aio-base overlay.
COPY --from=aio-base /aio-overlay/ /

COPY docker/assert-sure-bundle-versions.rb /tmp/assert-sure-bundle-versions.rb

# Upstream hotfix images can lag their release tag in this file, but Sure's UI
# reports the version from it.
RUN printf '%s\n' "${UPSTREAM_VERSION}" > /rails/.sure-version

# 1. Install prerequisites, s6-overlay, Redis, and pgvector support
# We use standard PATH binaries for Postgres (it's installed as postgresql)
# Refresh inherited Debian packages before adding our own runtime dependencies so
# published security fixes from the upstream base layer land in the wrapper image.
RUN aio-harden pre && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade && \
    apt-get install -y --no-install-recommends \
    build-essential="$(apt-cache madison build-essential | awk 'NR==1 {print $3}')" \
    ca-certificates="$(apt-cache madison ca-certificates | awk 'NR==1 {print $3}')" \
    curl="$(apt-cache madison curl | awk 'NR==1 {print $3}')" \
    git="$(apt-cache madison git | awk 'NR==1 {print $3}')" \
    postgresql="$(apt-cache madison postgresql | awk 'NR==1 {print $3}')" \
    postgresql-client="$(apt-cache madison postgresql-client | awk 'NR==1 {print $3}')" \
    postgresql-server-dev-17="$(apt-cache madison postgresql-server-dev-17 | awk 'NR==1 {print $3}')" \
    redis-server="$(apt-cache madison redis-server | awk 'NR==1 {print $3}')" \
    xz-utils="$(apt-cache madison xz-utils | awk 'NR==1 {print $3}')" && \
    bundle check && \
    ruby /tmp/assert-sure-bundle-versions.rb && \
    git clone --branch "v${PGVECTOR_VERSION}" --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    make -C /tmp/pgvector OPTFLAGS="" && \
    make -C /tmp/pgvector install && \
    apt-get purge -y --auto-remove \
      build-essential git postgresql-server-dev-17 \
      clang-19 llvm-19 llvm-19-dev llvm-19-linker-tools llvm-19-runtime llvm-19-tools && \
    rm -f /etc/ssl/private/ssl-cert-snakeoil.key /etc/ssl/certs/ssl-cert-snakeoil.pem && \
    rm -rf /tmp/* /var/lib/apt/lists/*

# 2. Setup persistent internal storage paths
RUN mkdir -p /var/lib/postgresql/data /var/lib/redis /rails/storage /run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql /run/postgresql && \
    if [ -d /etc/postgresql ]; then chown -R postgres:postgres /etc/postgresql; fi && \
    chown -R redis:redis /var/lib/redis

# 3. Apply S6 Root Filesystem logic
COPY rootfs/ /

# Remove retired service definitions that may still exist in older base layers.
RUN rm -rf /etc/s6-overlay/s6-rc.d/init-db \
    /etc/s6-overlay/s6-rc.d/user/contents.d/init-db \
    /etc/s6-overlay/s6-rc.d/web/dependencies.d/init-db \
    /etc/s6-overlay/s6-rc.d/worker/dependencies.d/init-db

# Ensure scripts are executable
RUN find /etc/s6-overlay/s6-rc.d -type f \( -name "run" -o -name "up" \) -exec chmod +x {} \; && \
    find /etc/cont-init.d -type f -exec chmod +x {} \; && \
    find /usr/local/bin -maxdepth 1 -type f -name "*.sh" -exec chmod +x {} \; || true

# 4. Expose the App Storage
VOLUME ["/rails/storage", "/var/lib/postgresql/data", "/var/lib/redis"]

EXPOSE 3000

ENV SKYLIGHT_ENABLED=false
ENV S6_CMD_WAIT_FOR_SERVICES_MAXTIME=300000
ENV S6_BEHAVIOUR_IF_STAGE2_FAILS=2

HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
  CMD curl -fsS http://localhost:3000/up >/dev/null || exit 1

ENTRYPOINT ["/init"]
