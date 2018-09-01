import json
import logging
from collections import namedtuple

import requests
from twython import TwythonError

from tweet.aws_util import generate_boto3_session, get_secret
from tweet.bills import Bills
from tweet.config import APP_CONFIG
from tweet.ocd_api import BillsAPI
from tweet.twitter import TwitterCredentials, TwitterClient, TwitterBot

App = namedtuple('App', 'bills_api, query, bills, twitter_bot, logger')


def get_new_introductions(ocd_api, query_params, bills):
    introductions = ocd_api.get_bills(query_params)
    new_introductions = [introduction for introduction in introductions
                         if not bills.exists(introduction.identifier)]
    return new_introductions


def tweet(ocd_api, query_params, bills, twitter_bot, logger):
    new_introductions = get_new_introductions(ocd_api, query_params, bills)
    logger.info("call: {} new introductions".format(len(new_introductions)))
    if len(new_introductions) > 0:
        for new_introduction in new_introductions:
            try:
                twitter_bot.tweet_introductions(new_introduction)
            except TwythonError as e:
                logger.info("handler: {} error:  {}".format(e.error_code, e.msg))
            else:
                bills.insert(new_introduction)


def setup(app_config):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    requests_session = requests.Session()
    ocd_bills_api = BillsAPI(requests_session)

    boto3_session = generate_boto3_session(app_config.aws_profile_name)
    bills = Bills(boto3_session)

    twitter_client = TwitterClient.from_aws(boto3_session, app_config.aws_secretsmanager_secret_name)
    twitter_bot = TwitterBot(twitter_client)
    return App(ocd_bills_api, app_config.query, bills, twitter_bot, logger)


def call(event, context):
    app = setup(app_config=APP_CONFIG)
    tweet(app.bills_api, app.query, app.bills, app.twitter_bot, app.logger)
