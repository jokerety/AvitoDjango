import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'item-parse-from-catalog': {
        'task': 'item.tasks.parse_from_catalog',
        'schedule': crontab(minute='*/5'),
    },
    'item-send-to-telegram': {
        'task': 'item.tasks.send_to_telegram',
        'schedule': crontab(minute='*/5'),
    },
    'clear-ancient-item': {
        'task': 'item.tasks.clear_ancient',
        'schedule': crontab(minute=0, hour=0),
    },
}
