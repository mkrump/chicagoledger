import datetime
import logging
from collections import namedtuple
from copy import copy

from twython import Twython, TwythonError

TWEET_TEMPLATE = '{title} {identifier} {url}'
REPLY_TEMPLATE = '@{username} {tweet}'
NEW_THREAD_TEMPLATE = """Want to know what changes Rahm Emanuel wants to see in Chicago? Here’s each piece of legislation introduced by Chicago’s mayor at this month’s City Council session, {date}.

I’m a public service bot from @city_bureau @CHIdocumenters

Links lead to the full ordinance text!"""

log = logging.getLogger(__name__)

TwitterCredentials = namedtuple('TwitterCredentials',
                                ['consumer_key', 'consumer_secret', 'access_token', 'access_secret'])
# https://developer.twitter.com/en/docs/developer-utilities/configuration/api-reference/get-help-configuration
TWITTER_MAX_CHARS = 280
SHORT_URL_LENGTH = 23


class TwitterBot:
    def __init__(self, twitter_client):
        self.twitter_client = twitter_client

    def reply_template(self, bill, username):
        tweet = self.tweet_template(bill)
        tweet = REPLY_TEMPLATE.format(username=username, tweet=tweet)
        return tweet

    @staticmethod
    def tweet_template(bill):
        tweet = TWEET_TEMPLATE.format(
            title=bill.title,
            identifier=bill.identifier,
            url=bill.generate_legistar_url(bill.identifier),
        )
        return tweet

    def start_new_thread(self, bill):
        date = datetime.datetime.strptime(bill.date, '%Y-%m-%d').date()
        date_string = date.strftime('%b. %d, %Y')
        tweet = NEW_THREAD_TEMPLATE.format(date=date_string)
        return self.twitter_client.update_status(status=tweet)

    def tweet_bill(self, bill, in_reply_to_status_id=None):
        if in_reply_to_status_id is None:
            shortened_bill = self.shorten(bill)
            tweet = self.tweet_template(shortened_bill)
        else:
            screen_name = self.twitter_client.screen_name
            shortened_bill = self.shorten(bill, screen_name)
            tweet = self.reply_template(shortened_bill, screen_name)
        return self.twitter_client.update_status(
            status=tweet,
            in_reply_to_status_id=in_reply_to_status_id
        )

    @staticmethod
    def shorten(bill, reply_to=None):
        # render template using fake shortened url
        text_after_url_shortening = TWEET_TEMPLATE.format(
            title=bill.title,
            identifier=bill.identifier,
            url='x' * SHORT_URL_LENGTH,
        )
        if reply_to is not None:
            # TODO should be able to avoid manually adding in @username
            # TODO w/ auto_populate_reply_metadata=True param, but
            # TODO threads don't render properly for some reason when using
            # TODO this param. Investigate why at some point.
            text_after_url_shortening = REPLY_TEMPLATE.format(username=reply_to, tweet=text_after_url_shortening)
        chars_over_max = len(text_after_url_shortening) - TWITTER_MAX_CHARS
        if chars_over_max > 0:
            bill_truncated_title = copy(bill)
            shortened_text = bill.title[:-(chars_over_max + 3)] + "..."
            bill_truncated_title.title = shortened_text
            return bill_truncated_title
        return bill


class TwitterClient:
    def __init__(self, twitter_credentials):
        try:
            self.twitter_client = self.connect(twitter_credentials)
        except TwythonError as e:
            log.error(e)
        try:
            credentials = self.twitter_client.verify_credentials()
            self.screen_name = credentials['screen_name']
        except TwythonError as e:
            log.error(e)

    @staticmethod
    def connect(twitter_credentials):
        return Twython(
            twitter_credentials.consumer_key,
            twitter_credentials.consumer_secret,
            twitter_credentials.access_token,
            twitter_credentials.access_secret
        )

    def update_status(self, status, in_reply_to_status_id=None):
        if in_reply_to_status_id is None:
            return self.twitter_client.update_status(status=status, tweet_mode='extended')
        return self.twitter_client.update_status(
            status=status,
            in_reply_to_status_id=in_reply_to_status_id,
            tweet_mode='extended'
        )
