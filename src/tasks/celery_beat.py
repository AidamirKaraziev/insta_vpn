from celery import Celery
from celery.schedules import crontab

from config import REDIS_HOST, REDIS_PORT

celery_beat = Celery('app_beat_tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')
celery_beat.conf.timezone = 'Europe/Moscow'

celery_beat.conf.beat_schedule = {
    'describe_profiles': {
        'task': 'tasks.tasks.describe_profiles',
        'schedule': crontab(hour=0, minute=0),
    },
}
