#!/bin/sh
# init.sh

# adapted from https://docs.docker.com/compose/startup-order/

set -e
PGUP=1

while [ $PGUP -ne 0 ]; do
  pg_isready -d "postgresql://postgres:galvanalyser@postgres:5433/postgres"
  PGUP=$?
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres ready - initialising"
cd backend_django
python manage.py makemigrations
python manage.py migrate

>&2 echo "... populating database"
python manage.py loaddata galvanalyser/fixtures/DataUnit.json
python manage.py loaddata galvanalyser/fixtures/DataColumnType.json
python manage.py loaddata galvanalyser/fixtures/Users.json || \
  echo "admin:admin already exists; continuing"

>&2 echo "Initialisation complete - starting server"
#exec "$@"

mkdir -p /var/run/celery /var/log/celery
chown -R nobody:nogroup /var/run/celery /var/log/celery

python manage.py runserver 0.0.0.0:5000 & \
cd .. && \
celery -A backend_django.celery beat \
      --loglevel=DEBUG \
      --logfile=/var/log/celery/scheduler.log \
      -s /var/run/celery/celerybeat-schedule \
      --uid=nobody --gid=nogroup
