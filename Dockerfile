# syntax=docker/dockerfile:1

FROM ghcr.io/we-promise/sure:stable

ARG S6_OVERLAY_VERSION=3.1.6.2

USER root

# 1. Install prerequisites, s6-overlay, PostgreSQL, and Redis
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl xz-utils sudo \
    postgresql-15 postgresql-client-15 redis-server && \
    curl -L -o /tmp/s6-overlay-noarch.tar.xz https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz && \
    tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz && \
    curl -L -o /tmp/s6-overlay-x86_64.tar.xz https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz && \
    tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz && \
    rm -rf /tmp/* /var/lib/apt/lists/*

# 2. Setup persistent internal storage paths
RUN mkdir -p /var/lib/postgresql/data /var/lib/redis /rails/storage /run/postgresql && \
    chown -R postgres:postgres /var/lib/postgresql /run/postgresql && \
    chown -R redis:redis /var/lib/redis

# 3. Apply S6 Root Filesystem logic (Services and Init scripts)
COPY rootfs/ /

# Ensure scripts mapped in from rootfs are executable
RUN find /etc/s6-overlay/s6-rc.d -type f -name "run" -exec chmod +x {} \; && \
    find /etc/cont-init.d -type f -exec chmod +x {} \; || true

# 4. Expose the App Storage
VOLUME ["/rails/storage", "/var/lib/postgresql/data", "/var/lib/redis"]

ENTRYPOINT ["/init"]
