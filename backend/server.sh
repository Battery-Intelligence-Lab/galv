#!/bin/sh
# init.sh

# adapted from https://docs.docker.com/compose/startup-order/

set -e
PGUP=1

while [ $PGUP -ne 0 ]; do
  pg_isready -d "postgresql://postgres:galvanalyser@${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5433}/postgres"
  PGUP=$?
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres ready - initialising"
cd backend_django || exit 1
python manage.py makemigrations
python manage.py migrate
python manage.py init_db
python manage.py create_superuser

>&2 echo "... populating database"
python manage.py loaddata galvanalyser/fixtures/DataUnit.json
python manage.py loaddata galvanalyser/fixtures/DataColumnType.json

>&2 echo "Initialisation complete - starting server"

if [ -z "${DJANGO_TEST}" ]; then
  python manage.py runserver 0.0.0.0:5000
else
  python manage.py test --noinput
fi
