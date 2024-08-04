import random
import string

from django.conf import settings
from django.db import models
from datetime import datetime

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class RSSFeedCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class SummaryRequestContext(models.Model):
    API_PROVIDER_CHOICES = [
        ('chatgpt', 'OpenAI ChatGPT'),
        ('gemini', 'Google Gemini'),
    ]
    name = models.CharField(
        max_length=255,
        unique=True,
        default=get_random_string(6),
        help_text='Not used with API provider call, a unique name identifier used to differentiate against multiple context choices.'
    )
    prompt_template = models.TextField(
        help_text=f'Use {{ feed_item_url }} template tag as placeholder for article to summarize.'
    )
    api_provider = models.CharField(
        max_length=10,
        choices=API_PROVIDER_CHOICES,
        default='chatgpt',
        help_text='Specifies which API provider to use for summary requests.'
    )
    engine = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text='Optional. If nothing is specified here, "gpt-4" will be used.'
    )
    max_tokens = models.IntegerField(
        null=True,
        blank=True,
        help_text='Optional. If nothing is specified here, the quantity 150 will be used.'
    )
    
    class Meta:
        unique_together = ('prompt_template', 'api_provider', 'engine', 'max_tokens')
    
    def __str__(self):
        return self.name

class RSSFeed(models.Model):
    title = models.CharField(max_length=255, unique=True)
    link = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)
    default_page = models.BooleanField(default=True)
    category = models.ForeignKey(RSSFeedCategory, null=True, blank=True, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)
    summary_request_context = models.ForeignKey(
        SummaryRequestContext,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='Optional. Specifies API parameters to the chosen provider. To disable summaries for a given feed source, leave the request context field blank.'
    )

    def __str__(self):
        return self.title
    
    @property
    def summaries_enabled(self):
        """
        Returns a boolean response relating to if the given rss feed source has the authorization
        to have it's articles summarized. Not all rss feed context is mostly textual, some are
        collections of images as a main medium such as web comics, etc.
        """
        response = True
        if self.summary_request_context is None:
            response = False
        return response

class RSSFeedItemModelManager(models.Manager):
    def get_summary_context(self, feed_item_id):
        return self.get(id = feed_item_id).feed.summary_request_context

class RSSFeedItem(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True)
    pub_date = models.DateTimeField(auto_now=True)
    feed = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)
    
    objects = RSSFeedItemModelManager()
    
    def __str__(self):
        return f'{self.title} -> {self.link}'

class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feed = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)
    subscribed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'feed')

    def __str__(self):
        return f'{self.user.username} subscribed to {self.feed.title}'

class UserBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rss_feed_item = models.ForeignKey(RSSFeedItem, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255)
    visible = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'rss_feed_item')
    
    def __str__(self):
        return f'{self.user.username} bookmarked rss item "{self.rss_feed_item}" from {self.rss_feed_item.feed}'

class RSSFeedItemSummaryRequest(models.Model):
    rss_feed_item = models.ForeignKey(RSSFeedItem, related_name='summary_requests', on_delete=models.CASCADE)
    request_context = models.ForeignKey(SummaryRequestContext, related_name='summary_requests', on_delete=models.CASCADE)
    prompt = models.TextField()
    requested_on = models.DateTimeField()
    completed_on = models.DateTimeField(null=True, blank=True)
    response = models.ForeignKey('RSSFeedItemSummaryResponse', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Summary request queued for "{self.rss_feed_item}" at {self.requested_on}'

class RSSFeedItemSummaryResponse(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    rss_feed_item_summary_request = models.OneToOneField(RSSFeedItemSummaryRequest, on_delete=models.CASCADE)
    
    def __str__(self):
       return f'Summary response for request {self.rss_feed_item_summary_request.id}'