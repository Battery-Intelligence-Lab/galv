#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

# init.sh

# adapted from https://docs.docker.com/compose/startup-order/

set -e
PGUP=1

cd backend_django || exit 1

>&2 echo "Collecting static files"
python manage.py collectstatic --noinput

>&2 echo "Waiting for Postgres to start"

while [ $PGUP -ne 0 ]; do
  pg_isready -d "postgresql://postgres:galvanalyser@${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}/postgres"
  PGUP=$?
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres ready - initialising"
>&2 echo "DJANGO_TEST=${DJANGO_TEST}"
>&2 echo "DJANGO_SETTINGS=${DJANGO_SETTINGS}"
python manage.py makemigrations
python manage.py migrate
python manage.py init_db
python manage.py create_superuser

>&2 echo "... populating database"
python manage.py loaddata galvanalyser/fixtures/DataUnit.json
python manage.py loaddata galvanalyser/fixtures/DataColumnType.json

>&2 echo "Initialisation complete - starting server"

if [ -z "${DJANGO_TEST}" ]; then
  if [ "${DJANGO_SETTINGS}" = "dev" ]; then
    >&2 echo "Launching dev server"
    python manage.py runserver 0.0.0.0:80
  else
    >&2 echo "Launching production server with gunicorn"
    gunicorn config.wsgi \
      --env DJANGO_SETTINGS_MODULE=config.settings \
      --bind 0.0.0.0:80 \
      --access-logfile - \
      --error-logfile -
  fi
else
  python manage.py test --noinput
fi
