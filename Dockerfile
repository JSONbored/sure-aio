# syntax=docker/dockerfile:1@sha256:2780b5c3bab67f1f76c781860de469442999ed1a0d7992a5efdf2cffc0e3d769

ARG UPSTREAM_VERSION=v0.6.9
ARG UPSTREAM_IMAGE_DIGEST=sha256:3d899b3eced520d8d3166a3d53184cbb1356670fb52d050f94f8e62e59754d70
ARG PGVECTOR_VERSION=0.8.2
FROM ghcr.io/we-promise/sure@${UPSTREAM_IMAGE_DIGEST}

ARG PGVECTOR_VERSION
ARG S6_OVERLAY_VERSION=3.1.6.2
ARG S6_OVERLAY_NOARCH_SHA256=05af2536ec4fb23f087a43ce305f8962512890d7c71572ed88852ab91d1434e3
ARG S6_OVERLAY_AARCH64_SHA256=3fc0bae418a0e3811b3deeadfca9cc2f0869fb2f4787ab8a53f6944067d140ee
ARG S6_OVERLAY_X86_64_SHA256=95081f11c56e5a351e9ccab4e70c2b1c3d7d056d82b72502b942762112c03d1c
ARG TARGETARCH

USER root

# 1. Install prerequisites, s6-overlay, Redis, and pgvector support
# We use standard PATH binaries for Postgres (it's installed as postgresql)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl git xz-utils \
    postgresql postgresql-client postgresql-server-dev-17 redis-server && \
    git clone --branch "v${PGVECTOR_VERSION}" --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    make -C /tmp/pgvector OPTFLAGS="" && \
    make -C /tmp/pgvector install && \
    apt-get purge -y --auto-remove \
      build-essential git postgresql-server-dev-17 \
      clang-19 llvm-19 llvm-19-dev llvm-19-linker-tools llvm-19-runtime llvm-19-tools && \
    curl -L -o /tmp/s6-overlay-noarch.tar.xz https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz && \
    echo "${S6_OVERLAY_NOARCH_SHA256}  /tmp/s6-overlay-noarch.tar.xz" | sha256sum -c - && \
    tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz && \
    case "${TARGETARCH}" in \
      amd64) s6_arch="x86_64"; s6_sha="${S6_OVERLAY_X86_64_SHA256}" ;; \
      arm64) s6_arch="aarch64"; s6_sha="${S6_OVERLAY_AARCH64_SHA256}" ;; \
      *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac && \
    curl -L -o /tmp/s6-overlay-arch.tar.xz https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${s6_arch}.tar.xz && \
    echo "${s6_sha}  /tmp/s6-overlay-arch.tar.xz" | sha256sum -c - && \
    tar -C / -Jxpf /tmp/s6-overlay-arch.tar.xz && \
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

ENV SKYLIGHT_ENABLED=false

HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
  CMD curl -f http://localhost:3000/up || exit 1

ENTRYPOINT ["/init"]
