import openai

from django.conf import settings
from django.template import Template, Context

from feed.models import RSSFeedItem
from feed.exceptions import NotImplementedException

openai.api_key = settings.OPENAI_API_KEY

class APIClientFactory(object):
    @staticmethod
    def get_client(provider):
        if provider == 'chatgpt':
            return openai.Completion
        elif provider == 'gemini':
            raise NotImplementedException("Google Gemini related functionality")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

class SummaryRequestService(object):
    def __init__(self, feed_item_id):
        self.feed_item_id = feed_item_id
        self.rss_feed_item = self._get_rss_feed_item()
    
    def __call__(self):
        response = self.api_client.create(
            engine = self.engine,
            prompt = self.prompt,
            max_tokens = self.max_tokens
        )
        return response.choices[0].text.strip()
    
    def _get_rss_feed_item(self):
        try:
            return RSSFeedItem.objects.get(id = self.feed_item_id)
        except RSSFeedItem.DoesNotExist:
            raise ValueError(f"RSSFeedItem with id {self.feed_item_id} does not exist")
    
    @property
    def summary_request_context(self):
        return self.rss_feed_item.feed.summary_request_context
    
    @property
    def api_client(self):
        api_provider = self.summary_request_context.api_provider
        return APIClientFactory.get_client(api_provider)
    
    @property
    def prompt(self):
        template = Template(self.summary_request_context.prompt_template)
        context = Context({'feed_item_url': self.rss_feed_item.link})
        return template.render(context)
    
    @property
    def engine(self):
        return self.summary_request_context.engine or 'gpt-4'
    
    @property
    def max_tokens(self):
        return self.summary_request_context.max_tokens or 150