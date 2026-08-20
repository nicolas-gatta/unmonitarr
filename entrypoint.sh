set -e

chown -R 1000:1000 /app/data

exec gosu 1000:1000 "$@"