import feedparser
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import ObjectDoesNotExist
from .forms import OPMLUploadForm, SubscriptionForm
from .models import RSSFeed, UserSubscription

def index(request):
    subscriptions = []
    feeds_by_source = {}
    
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
        parsed_feed_link = feedparser.parse(feed.link)
        feeds_by_source[feed.title] = []
        for entry in parsed_feed_link.entries:
            feeds_by_source[feed.title].append({
                'title': entry.title,
                'date_time': entry.get('published', ''),
                'link': entry.link
            })
    
    return render(request, 'feeds.html', {'feeds': feeds_by_source})

@login_required
def config(request):
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

            return redirect('index')  # Redirect to a success page or wherever appropriate
    else:
        # Pre-select feeds the user is already subscribed to
        user_feeds = UserSubscription.objects.filter(user=request.user).values_list('feed', flat=True)
        form = SubscriptionForm(initial={'feeds': user_feeds})

    return render(request, 'config.html', {'form': form})

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