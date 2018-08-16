import json

from twython import Twython, TwythonError

from config import get_secret


class TwitterBot:
    def __init__(self):
        secret = json.loads(get_secret())
        consumer_key = secret['twitter-consumer-key']
        consumer_secret = secret['twitter-consumer-secret']
        access_token = secret['twitter-access-token']
        access_secret = secret['twitter-access-secret']

        try:
            self.twython = Twython(consumer_key, consumer_secret, access_token, access_secret)
        except TwythonError as e:
            print(e)

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
        for i, bill in enumerate(bills):
            status = self.tweet_template(bill=bill)
            self.twython.update_status(status=status)
