from unittest.mock import patch

from mock import create_autospec

from test_handler import example_introductions
from twitter import TwitterBot, TwitterCredentials, TWITTER_MAX_CHARS, TwitterClient

tweets = [
    'O2099-1111 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2099-1111 #ordinance\nMake it illegal to put ketchup on hotdogs',
    'O2098-1112 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2098-1112 #ordinance\nDye the lake green everyday',
]


@patch('twitter.TwitterBot.format_tweets')
def test_bot(mock_format_tweets):
    twitter_client = create_autospec(TwitterClient)
    twitter_bot = TwitterBot(twitter_client)
    mock_format_tweets.return_value = tweets

    twitter_bot.tweet_introductions(example_introductions)

    mock_format_tweets.assert_called_once()
    assert twitter_client.update_status.call_count == 2
    twitter_bot.twitter_client.update_status.assert_any_call(
        status='O2099-1111 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2099-1111 #ordinance\n'
               'Make it illegal to put ketchup on hotdogs'
    )
    twitter_bot.twitter_client.update_status.assert_any_call(
        status='O2098-1112 http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2098-1112 #ordinance\n'
               'Dye the lake green everyday'
    )


def test_format_tweets():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))

    formatted_tweets = bot.format_tweets(example_introductions)

    assert formatted_tweets == tweets


def test_shorten():
    bot = TwitterBot(TwitterCredentials('', '', '', ''))
    text = 'a' * 281
    shortened_text = bot.shorten(text)
    assert len(shortened_text) == TWITTER_MAX_CHARS
    assert text[:TWITTER_MAX_CHARS - 3] + '...' == shortened_text
