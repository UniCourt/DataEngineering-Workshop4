from __future__ import absolute_import
from celery import Celery
import os

app = Celery('test_celery',
             broker='amqp://jimmy:jimmy123@localhost/jimmy_vhost',
             backend='rpc://',
             include=['test_celery.tasks'])



# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myworld.settings')

app = Celery('myworld')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    #Scheduler Name
    'run-task-ten-seconds': {
        # Task Name (Name Specified in Decorator)
        'task': 'extract',
        # Schedule
        'schedule': 60.0,
        # Function Arguments
        'args': (0,)
    }
}
