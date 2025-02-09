import feedparser
import timeago
import time
import datetime
import xml.etree.ElementTree as ET

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .forms import OPMLUploadForm, SubscriptionForm
from .models import RSSFeed, RSSFeedItem, UserSubscription, UserBookmark

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

@login_required
def subscriptions(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            selected_feeds = form.cleaned_data['feeds']
            user = request.user
            # Remove existing subscriptions
            UserSubscription.objects.filter(user=user).delete()
            # Create new subscriptions
            for feed in selected_feeds:
                UserSubscription.objects.create(user=user, feed=feed)
            messages.success(request, 'Your feed subscriptions have been updated.')
            return redirect('index')
    else:
        # Pre-select feeds the user is already subscribed to
        user_feeds = UserSubscription.objects.filter(user=request.user).values_list('feed', flat=True)
        form = SubscriptionForm(initial={'feeds': user_feeds})

    return render(request, 'subscriptions.html', {'form': form})

def bookmarks(request, username):
    url_user = User.objects.get(username=username)
    bookmarks = UserBookmark.objects.filter(user=url_user, visible=True).order_by('-added_on')
    context = {'url_username': username, 'bookmarks': bookmarks}
    return render(request, 'bookmarks.html', context)

def bookmarks_format(request, username, format):
    try:
        url_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseNotFound("<h1>User not found.</h1>")

    bookmarks = UserBookmark.objects.filter(user=url_user, visible=True).order_by('-added_on')

    if format == 'json':
        bookmarks_data = []
        for bookmark in bookmarks:
            bookmarks_data.append({
                "title": bookmark.rss_feed_item.title,
                "link": bookmark.rss_feed_item.link,
                "added_on": bookmark.added_on.strftime("%Y-%m-%d %H:%M:%S"),
            })
        return JsonResponse({"bookmarks": bookmarks_data})

    elif format == 'xml':
        root = ET.Element("bookmarks")
        for bookmark in bookmarks:
            bookmark_element = ET.SubElement(root, "bookmark")
            title_element = ET.SubElement(bookmark_element, "title")
            title_element.text = bookmark.rss_feed_item.title
            link_element = ET.SubElement(bookmark_element, "link")
            link_element.text = bookmark.rss_feed_item.link
            added_on_element = ET.SubElement(bookmark_element, "added_on")
            added_on_element.text = bookmark.added_on.strftime("%Y-%m-%d %H:%M:%S")
        xml_string = ET.tostring(root, encoding="utf-8", method="xml")
        return HttpResponse(xml_string, content_type="application/xml")

    elif format == 'raw':
        text_buffer = ""
        for bookmark in bookmarks:
            added_on = bookmark.added_on.strftime("%Y-%m-%d %H:%M:%S")
            text_buffer += f"Title: {bookmark.rss_feed_item.title}\n"
            text_buffer += f"Link: {bookmark.rss_feed_item.link}\n"
            text_buffer += f"Added on: {added_on}\n"
            text_buffer += "\n"
        return HttpResponse(text_buffer, content_type="text/plain")

    else:
        return HttpResponseNotFound("<h1>Invalid response format requested.</h1>")


class APIBookmarkActionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        bookmark_feed_item_mapping = {}
        user_bookmarks = UserBookmark.objects.filter(user=request.user, visible=True)
        for bookmark in user_bookmarks:
            bookmark_feed_item_mapping[bookmark.id] = bookmark.rss_feed_item.id
        response_data = {
            'status': 'success',
            'bookmark_feed_item_mapping': bookmark_feed_item_mapping,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        rss_feed_item_id = data.get('id')
        action = data.get('action')

        if not rss_feed_item_id or not action:
            return Response({'error': 'id and action json keys are required.'}, status=status.HTTP_400_BAD_REQUEST)

        rss_feed_item = RSSFeedItem.objects.get(id=rss_feed_item_id)
        if action == 'add':
            try:
                user_bookmark, user_bookmark_created = UserBookmark.objects.get_or_create(
                    user=request.user,
                    rss_feed_item=rss_feed_item
                )
                user_bookmark.visible = True
                user_bookmark.save()
            except IntegrityError as e:
                pass
        elif action == 'remove':
            user_bookmark = UserBookmark.objects.get(user=request.user, rss_feed_item=rss_feed_item)
            user_bookmark_created = False
            user_bookmark.visible = False
            user_bookmark.save()
        else:
            return Response({'error': 'action json value should either be add or remove.'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'id': user_bookmark.id,
            'action': action,
            'status': 'success',
            'created': user_bookmark_created,
        }
        return Response(response_data, status=status.HTTP_200_OK)

@staff_member_required
def upload_opml(request):
    if request.method == 'POST':
        form = OPMLUploadForm(request.POST, request.FILES)
        if form.is_valid():
            opml_file = form.cleaned_data['opml_file']
            opml_content = opml_file.read()
            
            # Parsing OPML content
            import xml.etree.ElementTree as ET
            root = ET.fromstring(opml_content)
            for outline in root.findall('.//outline[@type="rss"]'):
                title = outline.attrib.get('title')
                link = outline.attrib.get('xmlUrl')
                if link:
                    # Fetch RSS feed data
                    feed_data = feedparser.parse(link)
                    if feed_data.entries:
                        entry = feed_data.entries[0]
                        RSSFeed.objects.update_or_create(
                            link=link,
                            defaults={
                                'title': title or feed_data.feed.title,
                                'description': feed_data.feed.get('description', ''),
                                'pub_date': entry.published if hasattr(entry, 'published') else None,
                            }
                        )
            return redirect('admin:app_list', app_label='your_app_name')
    else:
        form = OPMLUploadForm()
    return render(request, 'admin/upload_opml.html', {'form': form})