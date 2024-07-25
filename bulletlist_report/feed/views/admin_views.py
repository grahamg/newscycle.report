from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required

from .forms import OPMLUploadForm

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
