from collections import namedtuple

from twython import Twython, TwythonError

TwitterCredentials = namedtuple('TwitterCredentials',
                                ['consumer_key', 'consumer_secret', 'access_token', 'access_secret'])

TWITTER_MAX_CHARS = 280


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

    def tweet_introductions(self, bills):
        tweets = self.format_tweets(bills)
        for tweet in tweets:
            self.twitter_client.update_status(status=tweet)

    def format_tweets(self, bills):
        tweets = []
        for bill in bills:
            status = self.tweet_template(bill=bill)
            status = self.shorten(status)
            tweets.append(status)
        return tweets

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
            print(e)

    @staticmethod
    def connect(twitter_credentials):
        return Twython(twitter_credentials.consumer_key, twitter_credentials.consumer_secret,
                       twitter_credentials.access_token, twitter_credentials.access_secret)

    def update_status(self, status):
        self.twitter_client.update_status(status=status)
