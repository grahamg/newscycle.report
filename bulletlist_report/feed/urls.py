from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views as feed_views

urlpatterns = [
    path('', feed_views.index, name='index'),
    path('~<str:username>/', feed_views.bookmarks, name='bookmarks'),
    path('config/', feed_views.config, name='config'),
    path('api/v1/bookmark/', feed_views.APIBookmarkActionView.as_view(), name='api_bookmark'),
]
