from django.core.management.base import BaseCommand
from django.db import IntegrityError
import django
from django.utils import timezone
import datetime
import requests
import feedparser
import timeago
import logging
import requests.exceptions
from feed.models import RSSFeed, RSSFeedItem, RSSDateTimeUpdate

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Collects and updates RSS feeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--feed-id',
            type=int,
            help='ID of a specific feed to update',
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Suppress output messages',
        )

    def handle(self, *args, **options):
        feeds_by_source = {}
        quiet = options['quiet']

        # Create a snapshot for this collection run
        current_time = django.utils.timezone.now()
        self.snapshot = RSSDateTimeUpdate.objects.create(
            updated=current_time
        )

        # Get either all feeds or a specific feed
        if options['feed_id']:
            try:
                subscriptions = RSSFeed.objects.filter(id=options['feed_id'])
                if not subscriptions.exists():
                    self.stderr.write(self.style.ERROR(f'Feed with ID {options["feed_id"]} not found'))
                    return
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error fetching feed: {str(e)}'))
                return
        else:
            subscriptions = RSSFeed.objects.all()

        if not quiet:
            self.stdout.write(f'Processing {subscriptions.count()} feeds...')
        
        for feed in subscriptions:
            try:
                self._process_feed(feed, quiet)
            except Exception as e:
                error_msg = f'Error processing feed {feed.title}: {str(e)}'
                logger.error(error_msg)
                self.stderr.write(self.style.ERROR(error_msg))

    def _process_feed(self, feed, quiet):
        if not quiet:
            self.stdout.write(f'Processing feed: {feed.title}')
        
        # Parse feed with timeout and handle encoding issues
        try:
            # First try normal parsing
            parsed_feed_link = feedparser.parse(feed.link)
            
            # If there's a bozo exception and it's related to encoding
            if (hasattr(parsed_feed_link, 'bozo_exception') and 
                isinstance(parsed_feed_link.bozo_exception, UnicodeEncodeError)):
                
                # Try to fetch the content manually and force UTF-8
                response = requests.get(feed.link)
                response.encoding = 'utf-8'
                parsed_feed_link = feedparser.parse(response.text)
            
            # If we still have a bozo exception, raise it
            if hasattr(parsed_feed_link, 'bozo_exception'):
                if not parsed_feed_link.entries:  # Only raise if we got no entries
                    raise parsed_feed_link.bozo_exception
        except Exception as e:
            error_msg = f'Failed to parse feed {feed.title}: {str(e)}'
            logger.error(error_msg)
            raise

        new_items = 0
        skipped_items = 0
        latest_pub_date = None
        
        for entry in parsed_feed_link.entries:
            try:
                # Get publication date from entry if available
                entry_pub_date = None
                if hasattr(entry, 'published_parsed'):
                    entry_pub_date = datetime.datetime.fromtimestamp(
                        datetime.datetime(*entry.published_parsed[:6]).timestamp(),
                        tz=datetime.timezone.utc
                    )
                elif hasattr(entry, 'updated_parsed'):
                    entry_pub_date = datetime.datetime.fromtimestamp(
                        datetime.datetime(*entry.updated_parsed[:6]).timestamp(),
                        tz=datetime.timezone.utc
                    )
                else:
                    entry_pub_date = datetime.datetime.now()

                # Keep track of the latest publication date
                if latest_pub_date is None or (entry_pub_date and entry_pub_date > latest_pub_date):
                    latest_pub_date = entry_pub_date

                # Using current time for collected_date
                current_time = timezone.now()

                rss_feed_item, created = RSSFeedItem.objects.get_or_create(
                    title=entry.title,
                    link=entry.link,
                    feed=feed,
                    defaults={
                        'pub_date': entry_pub_date,
                        'collected_date': current_time,
                        'snapshot': self.snapshot
                    }
                )
                
                if created:
                    new_items += 1
                else:
                    skipped_items += 1
                    
            except IntegrityError:
                skipped_items += 1
                continue
            except Exception as e:
                logger.error(f'Error processing entry in feed {feed.title}: {str(e)}')
                continue

        # Update the feed's pub_date to the latest entry's publication date
        if latest_pub_date:
            feed.pub_date = latest_pub_date
            feed.save()

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Feed {feed.title}: {new_items} new items, {skipped_items} skipped'
                )
            )
