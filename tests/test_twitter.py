from unittest.mock import patch

from mock import create_autospec

from tests.test_config import EXAMPLE_INTRODUCTIONS
from src.twitter import TwitterBot, TwitterCredentials, TWITTER_MAX_CHARS, TwitterClient

example_introduction = EXAMPLE_INTRODUCTIONS[0]
tweet = 'O2099-1111 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2099-1111 #ordinance\n' \
        'Make it illegal to put ketchup on hotdogs'


@patch('src.twitter.TwitterBot.format_tweets')
def test_tweet_introductions(mock_format_tweets):
    twitter_client = create_autospec(TwitterClient)
    twitter_bot = TwitterBot(twitter_client)
    mock_format_tweets.return_value = tweet

    twitter_bot.tweet_introductions(example_introduction)

    mock_format_tweets.assert_called_once()
    assert twitter_client.update_status.call_count == 1
    twitter_bot.twitter_client.update_status.assert_any_call(
        status='O2099-1111 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2099-1111 #ordinance\n'
               'Make it illegal to put ketchup on hotdogs'
    )


def test_format_tweets():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))

    formatted_tweets = bot.format_tweets(example_introduction)

    assert formatted_tweets == tweet


def test_shorten():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))
    text = 'a' * 281
    shortened_text = bot.shorten(text)
    assert len(shortened_text) == TWITTER_MAX_CHARS
    assert text[:TWITTER_MAX_CHARS - 3] + '...' == shortened_text
