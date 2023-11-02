#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

# init.sh

# adapted from https://docs.docker.com/compose/startup-order/

set -e
PGUP=1

cd backend_django || exit 1

>&2 echo "Collecting static files"
python manage.py collectstatic --noinput

>&2 echo "Waiting for Postgres to start"

while [ $PGUP -ne 0 ]; do
  pg_isready -d "postgresql://postgres:galv@${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}/postgres"
  PGUP=$?
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres ready - initialising"
>&2 echo "DJANGO_TEST=${DJANGO_TEST}"
>&2 echo "DJANGO_SETTINGS=${DJANGO_SETTINGS}"
python manage.py makemigrations
python manage.py migrate
#python manage.py init_db
python manage.py create_superuser

>&2 echo "... populating database"
python manage.py loaddata galv/fixtures/*
#python manage.py loaddata galv/fixtures/LabFixtures.json
#python manage.py loaddata galv/fixtures/DataUnit.json
#python manage.py loaddata galv/fixtures/DataColumnType.json
#python manage.py loaddata galv/fixtures/EquipmentFixtures.json
#python manage.py loaddata galv/fixtures/CellFixtures.json
#python manage.py loaddata galv/fixtures/ScheduleFixtures.json
#python manage.py loaddata galv/fixtures/CyclerTestFixtures.json
#python manage.py loaddata galv/fixtures/ValidationSchemaFixtures.json

>&2 echo "Initialisation complete - starting server"

if [ -z "${DJANGO_TEST}" ]; then
  if [ "${DJANGO_SETTINGS}" = "dev" ]; then
    >&2 echo "Launching dev server"
    python manage.py runserver 0.0.0.0:80
  else
    WORKERS_PER_CPU=${GUNICORN_WORKERS_PER_CPU:-2}
    WORKERS=$(expr $WORKERS_PER_CPU \* $(grep -c ^processor /proc/cpuinfo))
    >&2 echo "Launching production server with gunicorn ($WORKERS workers [${WORKERS_PER_CPU} per CPU])"
    gunicorn config.wsgi \
      --env DJANGO_SETTINGS_MODULE=config.settings \
      --bind 0.0.0.0:80 \
      --access-logfile - \
      --error-logfile - \
      --workers=$WORKERS
  fi
else
  python manage.py test --noinput
fi
