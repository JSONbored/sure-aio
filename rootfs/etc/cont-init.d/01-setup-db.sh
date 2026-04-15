#!/command/with-contenv sh
set -eu

PGDATA="/var/lib/postgresql/data"
mkdir -p "$PGDATA" /var/lib/redis /run/postgresql
# Avoid recursive ownership fixes on every boot for better restart performance.
# Full recursive chown is only needed before first database initialization.
if [ -s "$PGDATA/PG_VERSION" ]; then
    chown postgres:postgres "$PGDATA" /run/postgresql
else
    chown -R postgres:postgres "$PGDATA" /run/postgresql
    if [ -d /etc/postgresql ]; then
        chown -R postgres:postgres /etc/postgresql
    fi
fi
chown redis:redis /var/lib/redis
chmod 700 "$PGDATA"
chmod 770 /var/lib/redis

if [ -s "$PGDATA/PG_VERSION" ]; then
    echo "PostgreSQL database already initialized."
else
    echo "PostgreSQL database will be initialized by the postgres service on first start."
fi
