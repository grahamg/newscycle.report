import feedparser
import timeago
import datetime

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.db import IntegrityError

from ..models import RSSFeed, RSSFeedItem, UserSubscription, UserBookmark

def index(request):
    subscriptions = []
    feeds_by_source = {}
    
    # Check if this is the user's first visit
    if not request.session.get('has_visited', False):
        welcome_message = render_to_string('new_visitor_message.html',
            {'request': request, 'user': request.user})
        messages.info(request, welcome_message)
        request.session['has_visited'] = True
    
    if not request.user.is_authenticated:
        subscriptions = RSSFeed.objects.filter(default_page=True)
    else:
        try:
            user_filter = UserSubscription.objects.filter(user=request.user)
            for choice in user_filter:
                subscriptions.append(choice.feed)
        except ObjectDoesNotExist as e:
            subscriptions = RSSFeed.objects.filter(default_page=True)
        except Exception as e:
            subscriptions = RSSFeed.objects.filter(default_page=True)
    
    for feed in subscriptions:
        pub_date = feed.pub_date
        if isinstance(pub_date, datetime.datetime):
            now = datetime.datetime.now(datetime.timezone.utc)
            relative_pub_date = timeago.format(pub_date, now)
            feed.relative_pub_date = relative_pub_date
        
        parsed_feed_link = feedparser.parse(feed.link)
        feeds_by_source[feed.title] = []
        for entry in parsed_feed_link.entries:
            try:
                rss_feed_item, rss_feed_item_created = RSSFeedItem.objects.get_or_create(
                    title=entry.title,
                    link=entry.link,
                    feed=feed
                )
            except IntegrityError as e:
                continue
            
            published = feed.relative_pub_date
            if hasattr(entry, 'published_parsed'):
                published_parsed = entry.published_parsed
                now_datetime = datetime.datetime.now(datetime.timezone.utc)
                datetime_published_parsed = datetime.datetime(*published_parsed[:6], tzinfo=datetime.timezone.utc)
                relative_published_parsed = timeago.format(datetime_published_parsed, now_datetime)
                published = relative_published_parsed
            
            feeds_by_source[feed.title].append({
                'title': entry.title,
                'date_time': published,
                'link': entry.link,
                'rss_feed_item_id': rss_feed_item.id,
            })
    
    return render(request, 'feeds.html', {'feeds': feeds_by_source})

def about(request):
    return render(request, 'about.html')

def test_push_message(request):
    """
    Temporary-- Adding this as a temporary test to confirm push messages are working.
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications_notifications',  # Group name must match
        {
            'type': 'chat_message',
            'message': 'Hello from Django!',
        }
    )
    return JsonResponse({'status': 'Message sent'})
