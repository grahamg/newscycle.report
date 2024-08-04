from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User

class HasSummaryAccess(BasePermission):
    """
    Custom permission to check if the user has access to `feed.services.summary_service.SummaryRequestService`
    based on a boolean model-based attribute `has_summary_access` within `user.models.UserProfile`.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        try:
            return request.user.has_summary_access
        except AttributeError:
            # Case where the user does not have a profile
            return False