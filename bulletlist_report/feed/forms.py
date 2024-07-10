from django import forms
from .models import RSSFeed, UserSubscription

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