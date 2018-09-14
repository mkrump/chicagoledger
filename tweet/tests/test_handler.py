import pytest
from mock import mock, patch
from twython import TwythonError

from tweet.bills import Bills, Bill
from tweet.handler import tweet, App, new_thread, continue_thread
from tweet.conftest import EXAMPLE_INTRODUCTIONS
from tweet.twitter import TwitterBot

SUCCESS_RESPONSE = {'code': '200', 'id_str': '123'}


@pytest.fixture
def bills():
    bills = mock.create_autospec(Bills)
    bills.exists.return_value = False
    yield bills


@pytest.fixture
def twitter_bot():
    twitter_bot = mock.create_autospec(TwitterBot)
    yield twitter_bot


@pytest.fixture
def app(bills, twitter_bot):
    yield App(bills, twitter_bot)


@patch('tweet.handler.prev_tweet_id_is_missing')
@patch('tweet.handler.new_thread')
@patch('tweet.handler.continue_thread')
def test_tweet(mock_continue_thread, mock_new_thread, mock_prev_tweet_id_is_missing, app):
    app.bills.missing_tweet_id.return_value = EXAMPLE_INTRODUCTIONS
    mock_prev_tweet_id_is_missing.side_effect = [True, False]

    tweet(app.bills, app.twitter_bot)

    assert app.bills.missing_tweet_id.call_count == 1
    assert app.bills.get_prev_tweet_id.call_count == len(EXAMPLE_INTRODUCTIONS)
    assert mock_new_thread.call_count == 1
    assert mock_continue_thread.call_count == len(EXAMPLE_INTRODUCTIONS)


@patch('tweet.handler.prev_tweet_id_is_missing')
@patch('tweet.handler.new_thread')
@patch('tweet.handler.continue_thread')
def test_tweet_cant_start_thread(mock_continue_thread, mock_new_thread, mock_prev_tweet_id_is_missing, app):
    app.bills.missing_tweet_id.return_value = EXAMPLE_INTRODUCTIONS
    mock_new_thread.return_value = None
    mock_prev_tweet_id_is_missing.return_value = True

    tweet(app.bills, app.twitter_bot)

    assert app.bills.missing_tweet_id.call_count == 1
    assert app.bills.get_prev_tweet_id.call_count == len(EXAMPLE_INTRODUCTIONS)
    # keep trying to create new thread until succeed
    assert mock_new_thread.call_count == 2
    # continue_thread get called if can't create initial thread
    assert mock_continue_thread.call_count == 0


def test_new_thread(app):
    bill = mock.create_autospec(Bill)
    app.twitter_bot.start_thread.return_value = SUCCESS_RESPONSE

    prev_tweet_id = new_thread(bill, app.twitter_bot)

    app.twitter_bot.start_thread.assert_called_with(bill)
    assert app.twitter_bot.start_thread.call_count == 1
    assert prev_tweet_id == SUCCESS_RESPONSE['id_str']


def test_new_thread_error(app):
    bill = mock.create_autospec(Bill)
    app.twitter_bot.start_thread.return_value = Exception

    prev_tweet_id = new_thread(bill, app.twitter_bot)

    assert prev_tweet_id is None


def test_continue_thread(app):
    bill = mock.create_autospec(Bill)
    prev_tweet_id = '123'
    app.twitter_bot.tweet_introductions.return_value = SUCCESS_RESPONSE

    continue_thread(bill, app.bills, prev_tweet_id, app.twitter_bot)

    app.twitter_bot.tweet_introductions.assert_called_with(bill, prev_tweet_id)
    assert bill.tweet_id == '123'
    app.bills.insert.assert_called_with(bill)


def test_continue_thread_error(app):
    bill = mock.create_autospec(Bill)
    prev_tweet_id = '123'
    app.twitter_bot.tweet_introductions.side_effect = TwythonError('Error')

    continue_thread(bill, app.bills, prev_tweet_id, app.twitter_bot)

    assert app.bills.insert.call_count == 0
