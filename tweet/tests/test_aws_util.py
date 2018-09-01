import json

import boto3
import pytest
from moto import mock_secretsmanager

from tweet.aws_util import twitter_client_from_aws, get_secret
from tweet.twitter import TwitterClient


@pytest.fixture
def secrets_manager():
    test_secret = {"twitter-consumer-key": "consumer-key",
                   "twitter-consumer-secret": "consumer-secret",
                   "twitter-access-token": "access-token",
                   "twitter-access-secret": "access-secret"}
    with mock_secretsmanager():
        client = boto3.client('secretsmanager')
        client.create_secret(
            Name='test-secret',
            SecretString=json.dumps(test_secret),
        )
        yield client


def test_get_secret(secrets_manager):
    secret = json.loads(get_secret(boto3.Session(), 'test-secret'))
    assert secret['twitter-consumer-key'] == 'consumer-key'
    assert secret['twitter-consumer-secret'] == 'consumer-secret'
    assert secret['twitter-access-token'] == 'access-token'
    assert secret['twitter-access-secret'] == 'access-secret'


def test_twitter_client_from_aws(secrets_manager):
    twitter_client = twitter_client_from_aws(boto3.Session(), 'test-secret')
    assert isinstance(twitter_client, TwitterClient)
