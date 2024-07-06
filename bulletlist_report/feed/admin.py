from django.contrib import admin
from django.urls import path
from .models import RSSFeed, UserSubscription
from .views import upload_opml

@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    change_list_template = "admin/rssfeed_changelist.html"
    list_display = ('title', 'link', 'pub_date', 'updated')
    search_fields = ('title', 'description')
    
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