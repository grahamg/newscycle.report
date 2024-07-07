from django.contrib import admin
from django.urls import path
from .models import RSSFeed, RSSFeedCategory, RSSFeedItem, UserSubscription, UserBookmark
from .views import upload_opml

@admin.register(RSSFeedCategory)
class RSSFeedCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)

@admin.register(RSSFeedItem)
class RSSFeedItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'link', 'feed', 'pub_date')
    list_filter = ('feed',)

@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    change_list_template = "admin/rssfeed_changelist.html"
    list_display = ('title', 'link', 'pub_date', 'updated')
    search_fields = ('title', 'description', 'category')
    
    def get_urls(self):
            urls = super().get_urls()
            custom_urls = [
                path('upload-opml/', self.admin_site.admin_view(upload_opml), name='upload_opml'),
            ]
            return custom_urls + urls

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'feed', 'subscribed_on')
    list_filter = ('user', 'feed')

@admin.register(UserBookmark)
class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user','rss_feed_item','added_on','visible')
    list_filter = ('user','visible')