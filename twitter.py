import logging
from collections import namedtuple

from twython import Twython, TwythonError

TwitterCredentials = namedtuple('TwitterCredentials',
                                ['consumer_key', 'consumer_secret', 'access_token', 'access_secret'])

TWITTER_MAX_CHARS = 280

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


class TwitterBot:
    def __init__(self, twitter_client):
        self.twitter_client = twitter_client

    @staticmethod
    def tweet_template(bill):
        classifications = ' '.join(['#' + classification for classification in bill.classifications])
        return (
            "{identifier} {url} {classifications}\n{title}".format(
                identifier=bill.identifier,
                url=bill.legistar_url,
                classifications=classifications,
                title=bill.title)
        )

    def delete_last_tweet(self):
        last_tweet = self.twitter_client.get_home_timeline(count=1)
        self.twitter_client.destroy_status(id=last_tweet[0]['id'])

    def tweet_introductions(self, bill):
        tweet = self.format_tweets(bill)
        return self.twitter_client.update_status(status=tweet)

    def format_tweets(self, bill):
        status = self.tweet_template(bill=bill)
        status = self.shorten(status)
        return status

    @staticmethod
    def shorten(text):
        if len(text) > TWITTER_MAX_CHARS:
            return text[:(TWITTER_MAX_CHARS - 3)] + "..."
        return text


class TwitterClient:
    def __init__(self, twitter_credentials):
        try:
            self.twitter_client = self.connect(twitter_credentials)
        except TwythonError as e:
            LOGGER.info(e)

    @staticmethod
    def connect(twitter_credentials):
        return Twython(twitter_credentials.consumer_key, twitter_credentials.consumer_secret,
                       twitter_credentials.access_token, twitter_credentials.access_secret)

    def update_status(self, status):
        self.twitter_client.update_status(status=status)
