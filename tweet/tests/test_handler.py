import pytest
from mock import mock, patch
from twython import TwythonError

from tweet.bills import Bills, Bill
from tweet.handler import tweet, App, start_new_thread, continue_thread, get_prev_tweet_id
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
@patch('tweet.handler.start_new_thread')
@patch('tweet.handler.continue_thread')
def test_tweet(mock_continue_thread, mock_start_new_thread, mock_prev_tweet_id_is_missing, app):
    app.bills.missing_tweet_id.return_value = EXAMPLE_INTRODUCTIONS
    mock_prev_tweet_id_is_missing.side_effect = [True, False]

    tweet(app.bills, app.twitter_bot)

    assert app.bills.missing_tweet_id.call_count == 1
    assert app.bills.get_prev_tweet_id.call_count == len(EXAMPLE_INTRODUCTIONS)
    assert mock_start_new_thread.call_count == 1
    assert mock_continue_thread.call_count == len(EXAMPLE_INTRODUCTIONS)


@patch('tweet.handler.prev_tweet_id_is_missing')
@patch('tweet.handler.start_new_thread')
@patch('tweet.handler.continue_thread')
@patch('tweet.handler.get_prev_tweet_id')
def test_tweet_threading(mock_get_prev_tweet_id, mock_continue_thread, mock_start_new_thread, mock_prev_tweet_id_is_missing, app):
    introductions = []
    for i in range(6):
        bill = mock.create_autospec(Bill)
        if i <= 3:
            bill.date = '10/25/18'
        else:
            bill.date = '01/01/18'
        introductions.append(bill)
    app.bills.missing_tweet_id.return_value = introductions
    app.bills.get_prev_tweet_id.side_effect = list(range(len(introductions)))
    first_appearance = [False] * len(introductions)
    i = [i for i, b in enumerate(introductions) if b.date == '10/25/18'][0]
    first_appearance[i] = True
    i = [i for i, b in enumerate(introductions) if b.date == '01/01/18'][0]
    first_appearance[i] = True
    mock_prev_tweet_id_is_missing.side_effect = first_appearance
    mock_start_new_thread.side_effect = ['100', '500']
    mock_continue_thread.return_value = {'10/25/18': '1'}

    tweet(app.bills, app.twitter_bot)

    assert app.bills.missing_tweet_id.call_count == 1
    assert mock_get_prev_tweet_id.call_count == len(introductions)
    assert mock_start_new_thread.call_count == 2
    assert mock_continue_thread.call_count == len(introductions)


@patch('tweet.handler.prev_tweet_id_is_missing')
@patch('tweet.handler.start_new_thread')
@patch('tweet.handler.continue_thread')
def test_tweet_cant_start_thread(mock_continue_thread, mock_start_new_thread, mock_prev_tweet_id_is_missing, app):
    app.bills.missing_tweet_id.return_value = EXAMPLE_INTRODUCTIONS
    mock_start_new_thread.return_value = None
    mock_prev_tweet_id_is_missing.return_value = True

    tweet(app.bills, app.twitter_bot)

    assert app.bills.missing_tweet_id.call_count == 1
    assert app.bills.get_prev_tweet_id.call_count == len(EXAMPLE_INTRODUCTIONS)
    # keep trying to create new thread until succeed
    assert mock_start_new_thread.call_count == 2
    # continue_thread get called if can't create initial thread
    assert mock_continue_thread.call_count == 0


def test_get_prev_tweet_id_no_db_call(app):
    bill_date = '1/1/2018'
    bill = Bill('1', 'title', [], '1', bill_date)
    prev_tweets = {bill_date: '1000'}

    prev_tweet_id = get_prev_tweet_id(bill, app.bills, prev_tweets)

    assert app.bills.get_prev_tweet_id.call_count == 0
    assert prev_tweet_id == '1000'


def test_get_prev_tweet_id_db_call(app):
    bill_date = '1/1/2018'
    missing_bill_date = '2/1/2018'
    bill = Bill('1', 'title', [], '1', missing_bill_date)
    prev_tweets = {bill_date: '1000'}
    app.bills.get_prev_tweet_id.return_value = '500'

    prev_tweet_id = get_prev_tweet_id(bill, app.bills, prev_tweets)

    assert app.bills.get_prev_tweet_id.call_count == 1
    assert prev_tweet_id == '500'


def test_start_new_thread(app):
    bill = mock.create_autospec(Bill)
    app.twitter_bot.start_new_thread.return_value = SUCCESS_RESPONSE

    prev_tweet_id = start_new_thread(bill, app.twitter_bot)

    app.twitter_bot.start_new_thread.assert_called_with(bill)
    assert app.twitter_bot.start_new_thread.call_count == 1
    assert prev_tweet_id == SUCCESS_RESPONSE['id_str']


def test_start_new_thread_error(app):
    bill = mock.create_autospec(Bill)
    app.twitter_bot.start_new_thread.return_value = Exception

    prev_tweet_id = start_new_thread(bill, app.twitter_bot)

    assert prev_tweet_id is None


def test_continue_thread(app):
    bill = mock.create_autospec(Bill)
    prev_tweet_id = '123'
    bill_date = '10/01/18'
    bill.date = bill_date
    app.twitter_bot.tweet_bill.return_value = SUCCESS_RESPONSE

    prev_tweets = continue_thread(bill, app.bills, prev_tweet_id, {}, app.twitter_bot)

    app.twitter_bot.tweet_bill.assert_called_with(bill, prev_tweet_id)
    assert bill.tweet_id == '123'
    assert prev_tweets == {bill.date: bill.tweet_id}
    app.bills.insert.assert_called_with(bill)


def test_continue_thread_error(app):
    bill = mock.create_autospec(Bill)
    prev_tweet_id = '123'
    app.twitter_bot.tweet_bill.side_effect = TwythonError('Error')
    no_prev_tweets = {}

    prev_tweets = continue_thread(bill, app.bills, prev_tweet_id, no_prev_tweets, app.twitter_bot)

    assert app.bills.insert.call_count == 0
    assert prev_tweets == no_prev_tweets
