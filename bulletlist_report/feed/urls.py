from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('test_push_message/', views.test_push_message, name='test_push_message'),
    path('~<str:username>/', views.bookmarks, name='bookmarks'),
    re_path(r'^~(?P<username>[\w.@+-]+)/(?P<format>(raw|json|xml))/$', views.bookmarks_format, name='bookmarks_format'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('api/v1/bookmark/', views.APIBookmarkActionView.as_view(), name='api_bookmark'),
    path('api/v1/summary/', views.APISummaryActionView.as_view(), name='api_summary'),
    path('api/v1/task/<int:task_id>/', views.APITaskStatusView.as_view(), name='api_task'),
]