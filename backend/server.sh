#!/usr/bin/env bash

mkdir -p /var/run/celery /var/log/celery
chown -R nobody:nogroup /var/run/celery /var/log/celery

python manage.py run -h 0.0.0.0 & \
celery -A app.celery beat \
      --loglevel=DEBUG \
      --logfile=/var/log/celery/scheduler.log \
      -s /var/run/celery/celerybeat-schedule \
      --uid=nobody --gid=nogroup && fg
