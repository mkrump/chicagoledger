from logging import Logger

import pytest
from mock import mock
from twython import TwythonError

from tweet.bills import Bills
from tweet.handler import tweet, get_new_introductions
from tweet.ocd_api import BillsRequestParams, BillsAPI
from tweet.tests.test_config import EXAMPLE_INTRODUCTIONS
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
def logger():
    logger = mock.create_autospec(Logger)
    yield logger


def test_tweet(bills_api, bills_request_params, bills, twitter_bot, logger):
    bills_api.return_value = EXAMPLE_INTRODUCTIONS
    tweet(bills_api, bills_request_params, bills, twitter_bot, logger)

    tweet_introductions_expected_calls = [mock.call(i) for i in EXAMPLE_INTRODUCTIONS]
    assert twitter_bot.tweet_introductions.call_count == 2
    twitter_bot.tweet_introductions.assert_has_calls(tweet_introductions_expected_calls)

    insert_expected_calls = [mock.call(i) for i in EXAMPLE_INTRODUCTIONS]
    assert bills.insert.call_count == 2
    bills.insert.assert_has_calls(insert_expected_calls)


def test_tweet_error(bills_api, bills_request_params, bills, twitter_bot, logger):
    twitter_bot.tweet_introductions.side_effect = [TwythonError('error'), None]
    bills_api.return_value = EXAMPLE_INTRODUCTIONS
    tweet(bills_api, bills_request_params, bills, twitter_bot, logger)

    tweet_introductions_expected_calls = [mock.call(i) for i in EXAMPLE_INTRODUCTIONS]
    assert twitter_bot.tweet_introductions.call_count == 2
    twitter_bot.tweet_introductions.assert_has_calls(tweet_introductions_expected_calls)

    assert bills.insert.call_count == 1
    bills.insert.assert_called_with(EXAMPLE_INTRODUCTIONS[1])


def test_get_new_introductions(bills_api, bills_request_params, bills):
    assert get_new_introductions(bills_api, bills_request_params, bills) == EXAMPLE_INTRODUCTIONS


def test_get_new_introductions_filtering(bills_api, bills_request_params, bills):
    bills.exists.side_effect = [False, True]
    assert get_new_introductions(bills_api, bills_request_params, bills) == [EXAMPLE_INTRODUCTIONS[0]]
