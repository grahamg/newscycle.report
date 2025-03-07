from django.conf import settings
from django.db import models
from datetime import datetime
from django.utils import timezone
import timeago

class RSSDateTimeUpdate(models.Model):
    updated = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated']

    def get_next_snapshot(self):
        return RSSDateTimeUpdate.objects.filter(updated__gt=self.updated).order_by('updated').first()

    def get_previous_snapshot(self):
        return RSSDateTimeUpdate.objects.filter(updated__lt=self.updated).order_by('-updated').first()

class RSSFeedCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class RSSFeed(models.Model):
    title = models.CharField(max_length=255, unique=True)
    link = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)
    default_page = models.BooleanField(default=True)
    category = models.ForeignKey(RSSFeedCategory, null=True, blank=True, on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class RSSFeedItem(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True)
    pub_date = models.DateTimeField()
    collected_date = models.DateTimeField()
    feed = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)
    snapshot = models.ForeignKey(RSSDateTimeUpdate, on_delete=models.CASCADE, null=True)

    @property
    def relative_pub_date(self):
        """Returns a human-readable relative time string."""
        return timeago.format(self.pub_date, timezone.now())

    def __str__(self):
        return self.link

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

class UserKeywordLists(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    highlight_keywords = models.TextField(blank=True, default="")
    exclude_keywords = models.TextField(blank=True, default="")
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Keyword lists for {self.user.username}'
