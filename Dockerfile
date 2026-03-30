# syntax=docker/dockerfile:1

ARG UPSTREAM_VERSION=v0.6.8
ARG UPSTREAM_IMAGE_DIGEST=sha256:12f32c07c1b56efd80c92f1883bf7f88a976b403dd1e3a840ed1ee0342eb2823
FROM ghcr.io/we-promise/sure@${UPSTREAM_IMAGE_DIGEST}

ARG S6_OVERLAY_VERSION=3.1.6.2
ARG TARGETARCH

USER root

# 1. Install prerequisites, s6-overlay, and Redis
# We use standard PATH binaries for Postgres (it's installed as postgresql)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl xz-utils sudo \
    postgresql postgresql-client redis-server && \
    curl -L -o /tmp/s6-overlay-noarch.tar.xz https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz && \
    tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz && \
    case "${TARGETARCH}" in \
      amd64) s6_arch="x86_64" ;; \
      arm64) s6_arch="aarch64" ;; \
      *) echo "Unsupported TARGETARCH: ${TARGETARCH}" >&2; exit 1 ;; \
    esac && \
    curl -L -o /tmp/s6-overlay-arch.tar.xz https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${s6_arch}.tar.xz && \
    tar -C / -Jxpf /tmp/s6-overlay-arch.tar.xz && \
    rm -rf /tmp/* /var/lib/apt/lists/*

# 2. Setup persistent internal storage paths
RUN mkdir -p /var/lib/postgresql/data /var/lib/redis /rails/storage /run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql /run/postgresql /etc/postgresql && \
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

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3000/up || exit 1

ENTRYPOINT ["/init"]
