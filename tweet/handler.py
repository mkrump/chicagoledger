import logging
import traceback
from collections import namedtuple

from twython import TwythonError

from tweet.aws_util import generate_boto3_session, twitter_client_from_aws
from tweet.bills import Bills
from tweet.config import APP_CONFIG
from tweet.twitter import TwitterBot

log = logging.getLogger(__name__)

App = namedtuple('App', 'bills, twitter_bot')


def call(event, context):
    app = setup(app_config=APP_CONFIG)
    tweet(app.bills, app.twitter_bot)


def setup(app_config):
    boto3_session = generate_boto3_session(app_config.aws_profile)
    bills = Bills(boto3_session)

    twitter_client = twitter_client_from_aws(boto3_session, app_config.aws_secret_name)
    twitter_bot = TwitterBot(twitter_client)
    return App(bills, twitter_bot)


def tweet(bills, twitter_bot):
    not_tweeted_about = bills.missing_tweet_id()
    log.setLevel(logging.INFO)
    log.info('handler.tweet: {} new introductions'.format(len(not_tweeted_about)))
    for bill in not_tweeted_about:
        prev_tweet_id = bills.get_prev_tweet_id(bill.date)
        log.info('previous tweet_id: {}'.format(prev_tweet_id))
        if prev_tweet_id_is_missing(prev_tweet_id):
            prev_tweet_id = new_thread(bill, twitter_bot)
            # Don't tweet if can't start initial thread
            if prev_tweet_id is None:
                continue
        continue_thread(bill, bills, prev_tweet_id, twitter_bot)
    log.setLevel(logging.WARNING)


def new_thread(bill, twitter_bot):
    try:
        response = twitter_bot.start_thread(bill)
        log.info('handler.tweet: first tweet: {}'.format(response))
        prev_tweet_id = response['id_str']
        return prev_tweet_id
    except Exception:
        log.error("handler.tweet: {}".format(traceback.format_exc()))
        return None


def continue_thread(bill, bills, prev_tweet_id, twitter_bot):
    try:
        # TODO rename tweet_introductions to something more meaingful
        response = twitter_bot.tweet_introductions(bill, in_reply_to_status_id=prev_tweet_id)
        log.info('handler.continue_thread: response: {}'.format(response))
    except TwythonError as e:
        log.error("handler.continue_thread: {} error: {}".format(e.error_code, e.msg))
    else:
        bill.tweet_id = response['id_str']
        bills.insert(bill)


def prev_tweet_id_is_missing(tweet_id):
    return tweet_id == '-1'
