from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Life_Prescriber.settings')

app = Celery('Life_Prescriber')
app.conf.enable_utc = False
app.conf.update(timezone="Africa/Kigali")
app.config_from_object(settings, namespace='CELERY')

# celery beat settings
app.conf.beat_schedule = {
    'task-name': {
        'task': 'prescription_ongo.tasks.send_async_email',
        'schedule': crontab(minute='*/10'),
    },
}

app.autodiscover_tasks()

# this default_queue is very needed don't change!!!
# and also --pool=solo is compulsory when running celery worker
app.conf.task_default_queue = 'default'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
