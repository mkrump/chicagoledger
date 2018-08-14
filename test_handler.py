import json
from unittest.mock import patch

import boto3
import pytest
from moto import mock_s3

from handler import call, tweet_introductions, get_contents

example_introductions = [
    {
        "Meeting Date": "2018-07-25",
        "Type": "Mayoral Introductions",
        "Link": "http://www.chicityclerk.com/file/7799/download?token=Sk93gadp"
    },
    {
        "Meeting Date": "2018-06-27",
        "Type": "Mayoral Introductions",
        "Link": "http://www.chicityclerk.com/file/7776/download?token=c3vW_dga"
    }
]


def s3_object_created_event(bucket_name, key):
    return {
        "Records": [
            {
                "s3": {
                    "object": {
                        "key": key,
                    },
                    "bucket": {
                        "name": bucket_name,
                    },
                },
            }
        ]
    }


empty_secret = """
{
    "twitter-consumer-key": "",
    "twitter-consumer-secret": "",
    "twitter-access-token": "",
    "twitter-access-secret": ""
}
"""


@pytest.fixture(autouse=True)
def fake_secret(monkeypatch):
    def mocksecret():
        return empty_secret

    monkeypatch.setattr('handler.get_secret', mocksecret)


@patch('handler.get_contents')
@patch('handler.tweet_introductions')
def test_call(mock_tweet_introductions, mock_get_event):
    mock_get_event.return_value = example_introductions

    call(s3_object_created_event("some-bucket", "events/20180725.json"), None)

    mock_get_event.assert_called_with('some-bucket', 'events/20180725.json')
    mock_tweet_introductions.assert_called_with(example_introductions)


@patch('handler.Twython.update_status')
def test_bot(mock_twitter):
    tweet_introductions(example_introductions)

    mock_twitter.assert_any_call(
        status='On 2018-06-27 Rahm introduced http://www.chicityclerk.com/file/7776/download?token=c3vW_dga')
    mock_twitter.assert_any_call(
        status='On 2018-07-25 Rahm introduced http://www.chicityclerk.com/file/7799/download?token=Sk93gadp')
    assert mock_twitter.call_count == 2


@mock_s3
def test_get_event():
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket="some-bucket")
    payload = json.dumps(example_introductions)
    (boto3.client('s3', region_name='us-east-1')
     .put_object(Bucket="some-bucket", Key="events/20180725.json", Body=payload))

    event = get_contents('some-bucket', 'events/20180725.json')

    assert event == example_introductions
