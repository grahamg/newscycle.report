from django import forms
from .models import RSSFeed, UserSubscription, UserKeywordLists

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
class KeywordListsForm(forms.ModelForm):
    class Meta:
        model = UserKeywordLists
        fields = ['highlight_keywords', 'exclude_keywords']
        
        widgets = {
            'highlight_keywords': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded mt-2',
                'placeholder': 'technology, ai, climate, science'
            }),
            'exclude_keywords': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded mt-2',
                'placeholder': 'trump, biden, russia, ukraine'
            }),
        }
