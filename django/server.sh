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
cd backend_django || exit 1
python manage.py makemigrations
python manage.py migrate
python manage.py init_db

>&2 echo "... populating database"
python manage.py loaddata galvanalyser/fixtures/DataUnit.json
python manage.py loaddata galvanalyser/fixtures/DataColumnType.json
python manage.py loaddata galvanalyser/fixtures/Users.json || \
  echo "admin:admin already exists; continuing"

>&2 echo "Initialisation complete - starting server"

#mkdir -p /var/run/celery /var/log/celery
#chown -R nobody:nogroup /var/run/celery /var/log/celery

python manage.py runserver 0.0.0.0:5000 # & \
#celery -A config.celery_settings beat \
#      --loglevel=DEBUG \
#      --logfile=/var/log/celery/scheduler.log \
#      -s django_celery_beat.schedulers:DatabaseScheduler \
#      --uid=nobody --gid=nogroup
