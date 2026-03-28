#!/command/with-contenv sh
set -eu

: "${DB_HOST:=127.0.0.1}"
: "${DB_PORT:=5432}"
: "${POSTGRES_USER:=sure_user}"
: "${POSTGRES_PASSWORD:=internal_sure_pass}"
: "${POSTGRES_DB:=sure_production}"
: "${REDIS_URL:=redis://127.0.0.1:6379/1}"

export DB_HOST DB_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB REDIS_URL

cd /rails

echo "Waiting for PostgreSQL to become fully active..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; do
  sleep 2
done

echo "Running Sure database preparations (create/migrate/seed)..."
bundle exec rails db:prepare
