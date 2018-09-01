import json
import logging
import os

import boto3
import requests
from botocore.exceptions import ProfileNotFound
# OCD Query params
# Rahm Emanuel -> https://ocd.datamade.us/ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca/
from dateutil.utils import today

from tweet.aws_util import get_secret
from tweet.bills import Bills
from tweet.ocd_api import BillsAPI, create_query
from tweet.twitter import TwitterCredentials, TwitterClient, TwitterBot

PERSON = 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca'
ACTIONS = 'Referred'

# AWS params
# .aws/config to use
# profile is expected to have region
AWS_PROFILE_NAME = 'default'
AWS_SECRETSMANAGER_SECRET_NAME = 'Twitter'

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

requests_session = requests.Session()
OCD_BILLS_API = BillsAPI(requests_session)

try:
    boto3_session = boto3.Session(profile_name=AWS_PROFILE_NAME)
except ProfileNotFound:
    region = os.environ['AWS_DEFAULT_REGION']
    boto3_session = boto3.Session(region_name=region)

BILLS = Bills(boto3_session)
secret = json.loads(get_secret(boto3_session, AWS_SECRETSMANAGER_SECRET_NAME))
twitter_credentials = TwitterCredentials(secret['twitter-consumer-key'],
                                         secret['twitter-consumer-secret'],
                                         secret['twitter-access-token'],
                                         secret['twitter-access-secret'])

twitter_client = TwitterClient(twitter_credentials)

TWITTER_BOT = TwitterBot(twitter_client)
QUERY = create_query(
    max_date=today(),
    weeks_offset=6,
    person=PERSON, description=ACTIONS
)
