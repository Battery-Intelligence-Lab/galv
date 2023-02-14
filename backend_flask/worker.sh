#!/usr/bin/env bash

mkdir -p /var/run/celery /var/log/celery
chown -R nobody:nogroup /var/run/celery /var/log/celery

exec celery -A app.celery worker \
            --loglevel=INFO  \
            --logfile=/var/log/celery/worker.log \
            -O fair \
            -Q $HARVESTER_USERNAME \
            --uid=nobody --gid=nogroup
