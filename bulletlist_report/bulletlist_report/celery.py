from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from feed.services.summary_service import SummaryRequestService

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bulletlist_report.settings')

app = Celery('bulletlist_report')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(broker_connection_retry_on_startup=True,)
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=False)
def debug_task(self):
    return 42