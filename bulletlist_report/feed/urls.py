from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views as feed_views

urlpatterns = [
    path('', feed_views.index, name='index'),
    path('config', feed_views.config, name='config'),
]
