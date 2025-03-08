import feedparser
import timeago
import time
import datetime
import xml.etree.ElementTree as ET
import pytz

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.db import IntegrityError
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .forms import OPMLUploadForm, SubscriptionForm, KeywordListsForm
from .models import RSSFeed, RSSFeedItem, UserSubscription, UserBookmark, RSSDateTimeUpdate, UserKeywordLists
import feedparser
import timeago
import time
import datetime
import xml.etree.ElementTree as ET
import pytz

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.db import IntegrityError
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


def index(request):
    subscriptions = []
    feeds_by_source = {}
    snapshot_id = request.GET.get('snapshot')

    if snapshot_id:
        snapshot = get_object_or_404(RSSDateTimeUpdate, id=snapshot_id)
    else:
        snapshot = RSSDateTimeUpdate.objects.latest('updated')

    # Get feed items for this snapshot
    feed_items = RSSFeedItem.objects.filter(snapshot=snapshot)

    # Organize items by feed
    feeds_by_source = {}
    for item in feed_items:
        if item.feed not in feeds_by_source:
            feeds_by_source[item.feed] = []
        feeds_by_source[item.feed].append(item)

    # Check if this is the user's first visit
    if not request.session.get('has_visited', False):
        welcome_message = render_to_string('new_visitor_message.html',
            {'request': request, 'user': request.user})
        messages.info(request, welcome_message)
        request.session['has_visited'] = True
    
    # Get relevent feeds based on authentication status
    if not request.user.is_authenticated:
        subscriptions = RSSFeed.objects.filter(default_page=True)
    else:
        try:
            user_filter = UserSubscription.objects.filter(user=request.user)
            subscriptions = [choice.feed for choice in user_filter]
        except ObjectDoesNotExist:
            subscriptions = RSSFeed.objects.filter(default_page=True)
        except Exception:
            subscriptions = RSSFeed.objects.filter(default_page=True)
    
    # Apply keyword filtering for authenticated users
    exclude_keywords = []
    highlight_keywords = []
    if request.user.is_authenticated:
        try:
            keyword_lists = UserKeywordLists.objects.get(user=request.user)
            
            # Get exclude keywords as a list, strip whitespace and convert to lowercase
            exclude_keywords = [kw.strip().lower() for kw in keyword_lists.exclude_keywords.split(',') if kw.strip()]
            
            # Get highlight keywords as a list for template highlighting
            highlight_keywords = [kw.strip().lower() for kw in keyword_lists.highlight_keywords.split(',') if kw.strip()]
        except UserKeywordLists.DoesNotExist:
            pass
    
    # Organize feed items by source
    feeds_by_source = {}
    for feed in subscriptions:
        feeds_by_source[feed.title] = []

        # Get the most recent items for this feed
        feed_items = RSSFeedItem.objects.filter(
            feed=feed
        ).order_by('-pub_date')[:10] # Limit to recent items
        
        for item in feed_items:
            # Check if this item should be excluded based on keywords
            if exclude_keywords:
                title_lower = item.title.lower()
                if any(kw in title_lower for kw in exclude_keywords):
                    continue  # Skip this item as it contains an excluded keyword
            
            # Add the item to the list
            feeds_by_source[feed.title].append({
                'title': item.title,
                'date_time': item.relative_pub_date,
                'link': item.link,
                'rss_feed_item_id': item.id,
            })

    # Get next/previous snapshots
    next_snapshot = snapshot.get_next_snapshot()
    previous_snapshot = snapshot.get_previous_snapshot()

    return render(request, 'feeds.html', {
        'feeds': feeds_by_source,
        'last_update': snapshot.updated,
        'snapshot': snapshot,
        'next_snapshot': next_snapshot,
        'previous_snapshot': previous_snapshot,
        'highlight_keywords': ','.join(highlight_keywords) if highlight_keywords else '',
    })


def about(request):
    return render(request, 'about.html')

def premium(request):
    return render(request, 'premium.html')

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

def bookmarks(request, username):
    url_user = User.objects.get(username=username)
    bookmarks = UserBookmark.objects.filter(user=url_user, visible=True).order_by('-added_on')
    context = {'url_username': username, 'bookmarks': bookmarks}
    
    # Only proceed with keyword lists for authenticated users viewing their own bookmarks
    if request.user.is_authenticated and request.user.username == username:
        # Get or create the user's keyword lists
        keyword_lists, created = UserKeywordLists.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = KeywordListsForm(request.POST, instance=keyword_lists)
            if form.is_valid():
                form.save()
                # Add a success message if desired
                messages.success(request, "Keyword lists updated successfully!")
                return redirect('bookmarks', username=username)
        else:
            form = KeywordListsForm(instance=keyword_lists)
        
        context['keyword_form'] = form
    
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
