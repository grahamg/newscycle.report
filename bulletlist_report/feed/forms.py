from django import forms
from .models import RSSFeed, UserSubscription
from collections import defaultdict
from django.utils.safestring import mark_safe


class OPMLUploadForm(forms.Form):
    opml_file = forms.FileField()


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = UserSubscription
        fields = ['feeds']

    feeds = forms.ModelMultipleChoiceField(
        queryset=RSSFeed.objects.filter(visible=True),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group feeds by category
        grouped_feeds = defaultdict(list)
        for feed in self.fields['feeds'].queryset:
            category = feed.category.name if feed.category else 'Uncategorized'
            grouped_feeds[category].append((feed.id, feed.title))
        
        # Generate choices with headings and padding
        grouped_choices = []
        for category, feeds in grouped_feeds.items():
            category_heading = f'<strong style="padding-top: 10px; display: block;">{category}</strong>'
            grouped_choices.append((mark_safe(category_heading), feeds))
        
        # Update the feeds field choices
        self.fields['feeds'].choices = grouped_choices

