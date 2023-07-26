#!/bin/bash
alembic revision --autogenerate -m "Database creation"
alembic upgrade head

cd src

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:55713 --log-level debug --access-logfile -