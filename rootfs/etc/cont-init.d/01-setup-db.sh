#!/command/with-contenv sh
PGDATA="/var/lib/postgresql/data"
mkdir -p "$PGDATA" /var/lib/redis /run/postgresql
chown -R postgres:postgres "$PGDATA" /run/postgresql /etc/postgresql
chown -R redis:redis /var/lib/redis

if [ -s "$PGDATA/PG_VERSION" ]; then
    echo "PostgreSQL database already initialized."
else
    echo "PostgreSQL database will be initialized by the postgres service on first start."
fi
