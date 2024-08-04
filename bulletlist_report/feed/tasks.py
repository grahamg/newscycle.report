from celery import Celery
from django.utils import timezone
# from .services.summary_service import SummaryRequestService

app = Celery('bulletlist_report')

@app.task(bind=True, ignore_result=False)
def summarize_rss_feed_item(self):
    #summary_request = SummaryRequestService(feed_item_id = _id)
    #response_text = summary_request()
    return 42 + 1