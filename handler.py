import json
import logging
import os

import boto3
import dateutil
import requests
from botocore.exceptions import ProfileNotFound
from dateutil.utils import today

import config
from bills import Bills
from ocd_api import BillsEndpoint
from twitter import TwitterBot, TwitterCredentials, TwitterClient

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

REQUESTS_SESSION = requests.Session()
ocd_bills = BillsEndpoint(REQUESTS_SESSION)

try:
    BOTO3_SESSION = boto3.Session(profile_name='default')
except ProfileNotFound:
    region = os.environ['AWS_DEFAULT_REGION']
    BOTO3_SESSION = boto3.Session(region_name=region)

BILLS = Bills(BOTO3_SESSION)
SECRET = json.loads(config.get_secret(BOTO3_SESSION))
TWITTER_CREDENTIALS = TwitterCredentials(SECRET['twitter-consumer-key'],
                                         SECRET['twitter-consumer-secret'],
                                         SECRET['twitter-access-token'],
                                         SECRET['twitter-access-secret'])

TWITTER_CLIENT = TwitterClient(TWITTER_CREDENTIALS)
TWITTER_BOT = TwitterBot(TWITTER_CLIENT)


# TODO Not sure this query does quite what we want
# TODO since only getting bills with any
# TODO action date = 'Query Date' and any action = 'Referred'
def create_query(max_date):
    min_date = max_date - dateutil.relativedelta.relativedelta(months=1)
    return {
        'ocd-person': config.PERSON,
        'max_date': max_date.strftime("%Y-%m-%d"),
        'min_date': min_date.strftime("%Y-%m-%d"),
        'actions': config.ACTIONS,
    }


def call(event, context):
    query_params = create_query(today())
    introductions = ocd_bills.get_bills(
        query_params['ocd-person'],
        query_params['max_date'],
        query_params['min_date'],
        query_params['actions'],
    )
    new_introductions = [introduction for introduction in introductions
                         if not BILLS.exists(introduction.identifier)]
    LOGGER.info("call: {} new introductions".format(len(new_introductions)))
    BILLS.insert(new_introductions)
    if len(new_introductions) > 0:
        TWITTER_BOT.tweet_introductions(new_introductions)
