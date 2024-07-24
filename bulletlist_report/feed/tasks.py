from celery import shared_task
from django.utils import timezone
from .services.summary_service import SummaryRequestService

@shared_task
def summarize_rss_feed_item(rss_feed_item_id, user):
    summary_request = RSSFeedItemSummaryRequest.objects.create(
        requested_by = user,
        prompt = prompt,
        max_tokens = max_tokens,
        engine = engine,
        requested_on = timezone.now(),
        rss_feed_item = rss_feed_item
    )
    summary_request.save()
    
    summary_request = SummaryRequestService(feed_item_id = rss_feed_item_id)
    response_text = summary_request()
    
    summary_request.completed_on = timezone.now()
    summary_request.save()
    
    summary_response = RSSFeedItemSummaryRequest.objects.create(
        created_on = timezone.now(),
        text = response_text,
        rss_feed_item_summary_request = summary_request
    )
    summary_response.save()
    
    summary_request.response = summary_response
    summary_request.save()
    
    return summary_response