#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${1:-sure-aio:test}"
CONTAINER_NAME="${CONTAINER_NAME:-sure-aio-smoke}"
HOST_PORT="${HOST_PORT:-53000}"
READY_TIMEOUT_SECONDS="${READY_TIMEOUT_SECONDS:-420}"
HTTP_TIMEOUT_SECONDS="${HTTP_TIMEOUT_SECONDS:-120}"
KEEP_SMOKE_ARTIFACTS="${KEEP_SMOKE_ARTIFACTS:-0}"
TMP_STORAGE="$(mktemp -d /tmp/sure-aio-storage.XXXXXX)"
TMP_PGDATA="$(mktemp -d /tmp/sure-aio-pg.XXXXXX)"
TMP_REDIS="$(mktemp -d /tmp/sure-aio-redis.XXXXXX)"
SECRET_KEY_BASE="${SECRET_KEY_BASE:-0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef}"

cleanup_needed=1

cleanup() {
    local exit_code=$?
    if [[ "${KEEP_SMOKE_ARTIFACTS}" == "1" && "${exit_code}" -ne 0 ]]; then
        cleanup_needed=0
        echo "Smoke test failed; preserving artifacts for debugging." >&2
        echo "SMOKE_CONTAINER_NAME=${CONTAINER_NAME}" >&2
        echo "SMOKE_STORAGE_DIR=${TMP_STORAGE}" >&2
        echo "SMOKE_PGDATA_DIR=${TMP_PGDATA}" >&2
        echo "SMOKE_REDIS_DIR=${TMP_REDIS}" >&2
    fi
    if [[ "${cleanup_needed}" -eq 1 ]]; then
        docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
        rm -rf "${TMP_STORAGE}" "${TMP_PGDATA}" "${TMP_REDIS}"
    fi
}
trap cleanup EXIT

start_container() {
    docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${HOST_PORT}:3000" \
        -e SECRET_KEY_BASE="${SECRET_KEY_BASE}" \
        -e SELF_HOSTED=true \
        -e EXCHANGE_RATE_PROVIDER=yahoo_finance \
        -e SECURITIES_PROVIDER=yahoo_finance \
        -e ONBOARDING_STATE=open \
        -e RAILS_ASSUME_SSL=false \
        -e RAILS_FORCE_SSL=false \
        -v "${TMP_STORAGE}:/rails/storage" \
        -v "${TMP_PGDATA}:/var/lib/postgresql/data" \
        -v "${TMP_REDIS}:/var/lib/redis" \
        "${IMAGE_TAG}" >/dev/null
}

wait_for_ready_log() {
    local ready_deadline=$((SECONDS + READY_TIMEOUT_SECONDS))

    while (( SECONDS < ready_deadline )); do
        current_logs="$(docker logs "${CONTAINER_NAME}" 2>&1 || true)"
        if [[ "${current_logs}" == *"Listening on http://0.0.0.0:3000"* ]]; then
            return 0
        fi
        if curl -fsS "http://127.0.0.1:${HOST_PORT}/up" >/dev/null 2>&1; then
            return 0
        fi
        if ! docker ps --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
            echo "Smoke test container exited unexpectedly." >&2
            docker logs "${CONTAINER_NAME}" >&2 || true
            exit 1
        fi
        sleep 2
    done

    current_logs="$(docker logs "${CONTAINER_NAME}" 2>&1 || true)"
    if curl -fsS "http://127.0.0.1:${HOST_PORT}/up" >/dev/null 2>&1; then
        return 0
    fi
    [[ "${current_logs}" == *"Listening on http://0.0.0.0:3000"* ]]
}

verify_http() {
    local http_deadline=$((SECONDS + HTTP_TIMEOUT_SECONDS))

    while (( SECONDS < http_deadline )); do
        if curl -fsS "http://127.0.0.1:${HOST_PORT}/up" >/dev/null 2>&1; then
            break
        fi
        sleep 2
    done

    curl -fsS "http://127.0.0.1:${HOST_PORT}/up" >/dev/null

    root_headers="$(mktemp /tmp/sure-aio-headers.XXXXXX)"
    curl -sS -D "${root_headers}" -o /dev/null "http://127.0.0.1:${HOST_PORT}/"
    if grep -qi '^location: https://' "${root_headers}"; then
        echo "Found unexpected HTTPS redirect in default HTTP mode." >&2
        exit 1
    fi
    rm -f "${root_headers}"
}

start_container
wait_for_ready_log

verify_http
docker exec "${CONTAINER_NAME}" sh -lc 'test -f /var/lib/postgresql/data/PG_VERSION'

log_file="$(mktemp /tmp/sure-aio-logs.XXXXXX)"
docker logs "${CONTAINER_NAME}" >"${log_file}" 2>&1

grep -q "Running Sure database preparations (create/migrate/seed)" "${log_file}"
grep -q "Listening on http://0.0.0.0:3000" "${log_file}"

if grep -q "export: fatal: invalid variable name" "${log_file}"; then
    echo "Found broken s6 export error in logs." >&2
    exit 1
fi

if grep -q 'Completed 404 Not Found.*"/health"' "${log_file}"; then
    echo "Found stale /health probe in logs." >&2
    exit 1
fi

if grep -q 'table: "settings" does not exist' "${log_file}"; then
    echo "Found missing settings table warning after boot." >&2
    exit 1
fi

rm -f "${log_file}"

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

start_container
wait_for_ready_log
verify_http

restart_log_file="$(mktemp /tmp/sure-aio-restart-logs.XXXXXX)"
docker logs "${CONTAINER_NAME}" >"${restart_log_file}" 2>&1

grep -q "PostgreSQL database already initialized." "${restart_log_file}"

if grep -q "Initializing PostgreSQL database..." "${restart_log_file}"; then
    echo "Restart path unexpectedly reinitialized PostgreSQL." >&2
    exit 1
fi

if grep -q "export: fatal: invalid variable name" "${restart_log_file}"; then
    echo "Found broken s6 export error on restart." >&2
    exit 1
fi

rm -f "${restart_log_file}"

if [[ "${KEEP_SMOKE_ARTIFACTS}" != "1" ]]; then
    cleanup_needed=1
else
    cleanup_needed=0
    echo "SMOKE_CONTAINER_NAME=${CONTAINER_NAME}"
    echo "SMOKE_STORAGE_DIR=${TMP_STORAGE}"
    echo "SMOKE_PGDATA_DIR=${TMP_PGDATA}"
    echo "SMOKE_REDIS_DIR=${TMP_REDIS}"
fi
