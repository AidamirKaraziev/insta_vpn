#!/bin/bash

cd src

if [[ "${1}" == "celery" ]]; then
  celery --app=tasks.tasks:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=tasks.tasks:celery flower
elif [[ "${1}" == "beat" ]]; then
  celery --app=tasks.beat_tasks:celery_beat beat -l INFO
fi
