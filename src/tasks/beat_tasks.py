from celery import Celery
from celery.schedules import crontab

from config import REDIS_HOST, REDIS_PORT

celery_beat = Celery('app_beat_tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')
celery_beat.conf.beat_schedule = {
    'describe_users': {
        'task': 'tasks.tasks.describe_users',
        'schedule': crontab(hour=2, minute=19),
    },
}