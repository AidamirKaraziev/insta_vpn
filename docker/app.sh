#!/bin/bash
cd src
#alembic revision --autogenerate -m "docker migration"
alembic upgrade head


gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:55755 --timeout 600 --log-level debug --access-logfile -