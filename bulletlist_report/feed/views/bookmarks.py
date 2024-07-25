import xml.etree.ElementTree as ET

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse

from ..models import UserBookmark

User = get_user_model()

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
