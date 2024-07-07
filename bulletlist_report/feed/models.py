from django.conf import settings
from django.db import models
from datetime import datetime

class RSSFeedCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class RSSFeed(models.Model):
    title = models.CharField(max_length=255, unique=True)
    link = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)
    default_page = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class RSSFeedItem(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True)
    pub_date = models.DateTimeField(auto_now=True)
    feed = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)
    
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