import json

import boto3
from twython import Twython, TwythonError
from config import get_secret


def call(event, context):
    bucket, key = unpack_lambda_event(event)
    introductions = get_contents(bucket, key)
    tweet_introductions(introductions)


def tweet_introductions(introductions):
    twitter = create_twitter()
    for introduction in introductions:
        meeting_date = introduction['Meeting Date']
        link = introduction['Link']
        status = "On {date} Rahm introduced {link}".format(date=meeting_date, link=link)
        twitter.update_status(status=status)


def get_contents(original_bucket, original_key):
    s3_client = boto3.client('s3')
    event = s3_client.get_object(
        Bucket=original_bucket,
        Key=original_key,
    )
    return json.loads(event['Body'].read())


def create_twitter():
    secret = json.loads(get_secret())
    consumer_key = secret['twitter-consumer-key']
    consumer_secret = secret['twitter-consumer-secret']
    access_token = secret['twitter-access-token']
    access_secret = secret['twitter-access-secret']

    try:
        twitter = Twython(consumer_key, consumer_secret, access_token, access_secret)
        return twitter
    except TwythonError as e:
        print(e)


def unpack_lambda_event(event):
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    return bucket, key
