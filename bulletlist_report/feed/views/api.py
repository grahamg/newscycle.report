from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .permissions import HasSummaryAccess
from .tasks import summarize_rss_feed_item
from .models import RSSFeedItem, UserBookmark

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
        return Response(response_data, status=status.HTTP_202_ACCEPTED)


class APISummaryActionView(APIView):
    permission_classes = [HasSummaryAccess]
    
    def get(self, request, *args, **kwargs):
        return Response({"error": "The method is not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        queued_by = request.user
        rss_feed_item_id = data.get('id') or None
        
        if rss_feed_item_id is None:
            return Response({"error": "Invalid parameter 'id'"}, status=status.HTTP_400_BAD_REQUEST)
        
        rss_feed_item = RSSFeedItem.objects.get(id=rss_feed_item_id)
        rss_feed = rss_feed_item.feed
        if rss_feed.summaries_enabled() is False:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        
        # Enqueue the celery task
        summarize_rss_feed_item.delay(rss_feed_item_id=rss_feed_item_id, user=queued_by)
        
        response_data = {
            'id': rss_feed_item_id,
            'action': 'enqueue',
            'status': 'success',
        }
        return Response(response_data, status=status.HTTP_202_ACCEPTED)
