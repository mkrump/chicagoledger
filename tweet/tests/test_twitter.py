from unittest.mock import patch

from mock import create_autospec, call

from tweet.tests.conftest import EXAMPLE_INTRODUCTIONS
from tweet.twitter import TwitterClient, TwitterBot, TwitterCredentials, TWITTER_MAX_CHARS

EXAMPLE_INTRODUCTION = EXAMPLE_INTRODUCTIONS[0]
TWEET = 'O2099-1111: http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2099-1111 #chi_ordinance\n' \
        'Make it illegal to put ketchup on hotdogs'


@patch('tweet.twitter.TwitterBot.format_tweets')
def test_tweet_introductions(mock_format_tweets):
    twitter_client = create_autospec(TwitterClient)
    twitter_bot = TwitterBot(twitter_client)
    mock_format_tweets.return_value = TWEET

    twitter_bot.tweet_introductions(EXAMPLE_INTRODUCTION)

    assert mock_format_tweets.call_count == 1
    assert twitter_client.update_status.call_count == 1
    twitter_bot.twitter_client.update_status.assert_any_call(status=TWEET, in_reply_to_status_id=None)


def test_format_tweets():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))

    formatted_tweets = bot.format_tweets(EXAMPLE_INTRODUCTION)

    assert formatted_tweets == TWEET


def test_shorten():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))
    text = 'a' * 281
    shortened_text = bot.shorten(text)
    assert len(shortened_text) == TWITTER_MAX_CHARS
    assert text[:TWITTER_MAX_CHARS - 3] + '...' == shortened_text


