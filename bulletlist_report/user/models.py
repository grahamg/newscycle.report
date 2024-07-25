from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    private = models.BooleanField(default=False)
    bio = models.TextField(null=True, blank=True)
    has_summary_access = models.BooleanField(default=False)
    private_bookmarks = models.BooleanField(default=False)