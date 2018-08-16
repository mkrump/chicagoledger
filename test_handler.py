import datetime
from unittest.mock import patch

import pytest

from handler import call
from ocd_api import Bill

empty_secret = """
{
    "twitter-consumer-key": "",
    "twitter-consumer-secret": "",
    "twitter-access-token": "",
    "twitter-access-secret": ""
}
"""

example_introductions = [
    Bill('O2099-1111', 'Make it illegal to put ketchup on hotdogs', ['ordinance']),
    Bill('O2098-1112', 'Dye the lake green everyday', ['ordinance'])
]


# TODO move this to config for entire tests suite
@pytest.fixture(autouse=True)
def fake_secret(monkeypatch):
    def mocksecret():
        return empty_secret

    monkeypatch.setattr('twitter.get_secret', mocksecret)


@patch('handler.today')
@patch('handler.TwitterBot.tweet_introductions')
@patch('handler.Bills.insert')
@patch('handler.Bills.exists')
@patch('handler.OCDBillsAPI.get_bills')
def test_call(mock_get_bills, mock_handler_exists, mock_handler_insert, mock_tweet_introductions, mock_today):
    mock_today.return_value = datetime.datetime(2018, 8, 15)
    mock_get_bills.return_value = example_introductions
    mock_handler_exists.return_value = True

    call(None, None)

    mock_get_bills.assert_called_with('ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca', '2018-08-15', '2018-07-15', 'Referred')
    mock_handler_exists.assert_any_call(example_introductions[0].identifier)
    mock_handler_exists.assert_any_call(example_introductions[1].identifier)
    mock_handler_insert.assert_called_with(example_introductions)
    mock_tweet_introductions.assert_called_with(example_introductions)
