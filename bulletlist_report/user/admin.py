from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

class UserProfileAdmin(UserAdmin):
    model = UserProfile
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('private', 'bio', 'has_summary_access', 'private_bookmarks')}),
    )
    add_fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('private', 'bio', 'has_summary_access', 'private_bookmarks')}),
    )

admin.site.register(UserProfile, UserProfileAdmin)