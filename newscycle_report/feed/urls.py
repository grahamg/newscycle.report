from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from . import views as feed_views

urlpatterns = [
    path('', feed_views.index, name='index'),
    path('about/', feed_views.about, name='about'),
    path('~<str:username>/', feed_views.bookmarks, name='bookmarks'),
    re_path(r'^~(?P<username>[\w.@+-]+)/(?P<format>(raw|json|xml))/$', feed_views.bookmarks_format, name='bookmarks_format'),
    path('subscriptions/', feed_views.subscriptions, name='subscriptions'),
    path('api/v1/bookmark/', feed_views.APIBookmarkActionView.as_view(), name='api_bookmark'),
]
