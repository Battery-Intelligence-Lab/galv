#!/usr/bin/env bash

mkdir -p /var/run/celery /var/log/celery
chown -R nobody:nogroup /var/run/celery /var/log/celery

cd backend_django || exit 1
exec celery -A config.celery_settings worker \
            --loglevel=INFO  \
            --logfile=/var/log/celery/worker.log \
            -O fair \
            -Q $HARVESTER_USERNAME \
            --uid=nobody --gid=nogroup
