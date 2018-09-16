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
    untweeted_bills = bills.missing_tweet_id()
    log.setLevel(logging.INFO)
    log.info('handler.tweet: {} new introductions'.format(len(untweeted_bills)))
    prev_tweets = dict()
    for bill in untweeted_bills:
        prev_tweet_id = get_prev_tweet_id(bill, bills, prev_tweets)
        log.info('handler.tweet: previous tweet_id: {}'.format(prev_tweet_id))
        if prev_tweet_id_is_missing(prev_tweet_id):
            prev_tweet_id = start_new_thread(bill, twitter_bot)
            # Don't tweet if don't succeed in starting new thread
            if prev_tweet_id is None:
                continue
            # TODO think about logic here can probably return dict above
            # TODO and remove this step
            prev_tweets[bill.date] = prev_tweet_id
        prev_tweets = continue_thread(bill, bills, prev_tweet_id, prev_tweets, twitter_bot)
    log.setLevel(logging.WARNING)


def get_prev_tweet_id(bill, bills, prev_tweets):
    # inserts into dynamodb aren't instant so keep local dict w/ prev tweets
    # for a given date and only go to db if haven't seen that date yet.
    if bill.date not in prev_tweets:
        prev_tweet_id = bills.get_prev_tweet_id(bill.date)
    else:
        prev_tweet_id = prev_tweets[bill.date]
    return prev_tweet_id


def start_new_thread(bill, twitter_bot):
    try:
        response = twitter_bot.start_new_thread(bill)
        log.info('handler.start_new_thread: first tweet: {}'.format(response))
        log.info('handler.start_new_thread: tweet_id: {}'.format(response['id_str']))
        prev_tweet_id = response['id_str']
        return prev_tweet_id
    except Exception:
        log.error("handler.start_new_thread: {}".format(traceback.format_exc()))
        return None


def continue_thread(bill, bills, prev_tweet_id, prev_tweets, twitter_bot):
    try:
        response = twitter_bot.tweet_bill(bill, in_reply_to_status_id=prev_tweet_id)
        log.info('handler.continue_thread: tweet_id: {}'.format(response['id_str']))
        log.info('handler.continue_thread: response: {}'.format(response))
    except TwythonError as e:
        log.error('handler.continue_thread: {} error: {}'.format(e.error_code, e.msg))
        log.error(bill)
    else:
        bill.tweet_id = response['id_str']
        bills.insert(bill)
        prev_tweets[bill.date] = bill.tweet_id
    return prev_tweets


def prev_tweet_id_is_missing(tweet_id):
    return tweet_id == '-1'
