from logging import Logger

import pytest
from mock import mock
from twython import TwythonError

from tweet.bills import Bills
from tweet.handler import tweet, get_new_introductions, App
from tweet.ocd_api import BillsRequestParams, BillsAPI
from tweet.tests.conftest import EXAMPLE_INTRODUCTIONS
from tweet.twitter import TwitterBot


@pytest.fixture
def bills_api():
    bills_api = mock.create_autospec(BillsAPI)
    bills_api.get_bills.return_value = EXAMPLE_INTRODUCTIONS
    yield bills_api


@pytest.fixture
def bills_request_params():
    bills_request_params = mock.create_autospec(BillsRequestParams)
    yield bills_request_params


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
def app(bills_api, bills_request_params, bills, twitter_bot):
    yield App(bills_api, bills_request_params, bills, twitter_bot)


def test_tweet(app):
    tweet(app.bills_api, app.query, app.bills, app.twitter_bot)

    tweet_introductions_expected_calls = [mock.call(i) for i in EXAMPLE_INTRODUCTIONS]
    assert app.twitter_bot.tweet_introductions.call_count == 2
    app.twitter_bot.tweet_introductions.assert_has_calls(tweet_introductions_expected_calls)

    insert_expected_calls = [mock.call(i) for i in EXAMPLE_INTRODUCTIONS]
    assert app.bills.insert.call_count == 2
    app.bills.insert.assert_has_calls(insert_expected_calls)


def test_tweet_error(app):
    app.twitter_bot.tweet_introductions.side_effect = [TwythonError('error'), None]
    app.bills_api.return_value = EXAMPLE_INTRODUCTIONS
    tweet(app.bills_api, app.query, app.bills, app.twitter_bot)

    tweet_introductions_expected_calls = [mock.call(i) for i in EXAMPLE_INTRODUCTIONS]
    assert app.twitter_bot.tweet_introductions.call_count == 2
    app.twitter_bot.tweet_introductions.assert_has_calls(tweet_introductions_expected_calls)

    assert app.bills.insert.call_count == 1
    app.bills.insert.assert_called_with(EXAMPLE_INTRODUCTIONS[1])


def test_get_new_introductions(bills_api, bills_request_params, bills):
    assert get_new_introductions(bills_api, bills_request_params, bills) == EXAMPLE_INTRODUCTIONS


def test_get_new_introductions_filtering(bills_api, bills_request_params, bills):
    bills.exists.side_effect = [False, True]
    assert get_new_introductions(bills_api, bills_request_params, bills) == [EXAMPLE_INTRODUCTIONS[0]]
