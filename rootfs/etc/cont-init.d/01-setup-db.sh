#!/command/with-contenv sh
# S6 Type declarations for all services
mkdir -p /etc/s6-overlay/s6-rc.d/user/contents.d
echo "longrun" > /etc/s6-overlay/s6-rc.d/postgres/type
echo "longrun" > /etc/s6-overlay/s6-rc.d/redis/type
echo "longrun" > /etc/s6-overlay/s6-rc.d/web/type
echo "longrun" > /etc/s6-overlay/s6-rc.d/worker/type

touch /etc/s6-overlay/s6-rc.d/user/contents.d/postgres
touch /etc/s6-overlay/s6-rc.d/user/contents.d/redis
touch /etc/s6-overlay/s6-rc.d/user/contents.d/web
touch /etc/s6-overlay/s6-rc.d/user/contents.d/worker

# Database setup logic
PGDATA="/var/lib/postgresql/data"

if [ -z "$(ls -A "$PGDATA")" ]; then
    echo "Initializing PostgreSQL database..."
    chown -R postgres:postgres "$PGDATA"
    sudo -u postgres /usr/lib/postgresql/15/bin/initdb -D "$PGDATA"
    
    # Temporarily start PG to create the sure_user
    sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" -w start
    sudo -u postgres psql -c "CREATE USER sure_user WITH SUPERUSER PASSWORD 'internal_sure_pass';"
    sudo -u postgres psql -c "CREATE DATABASE sure_production OWNER sure_user;"
    sudo -u postgres /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" -m fast -w stop
else
    echo "PostgreSQL database already initialized."
fi
