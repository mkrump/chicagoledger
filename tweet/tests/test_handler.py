import datetime
from unittest.mock import patch

from tweet.handler import call
from tweet.ocd_api import BillsRequestParams
from tweet.tests.test_config import EXAMPLE_INTRODUCTIONS


# TODO maybe try to simplify this test / setup
@patch('tweet.handler.today')
@patch('tweet.handler.TwitterBot.tweet_introductions')
@patch('tweet.handler.Bills.insert')
@patch('tweet.handler.Bills.exists')
@patch('tweet.handler.BillsEndpoint.get_bills')
def test_call(mock_get_bills, mock_handler_exists, mock_handler_insert, mock_tweet_introductions, mock_today):
    mock_today.return_value = datetime.datetime(2018, 8, 15)
    mock_get_bills.return_value = EXAMPLE_INTRODUCTIONS
    mock_handler_exists.return_value = False

    call(None, None)

    query_params = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-07-04',
        description='Referred'
    )
    mock_get_bills.assert_called_with(query_params)
    mock_handler_exists.assert_any_call(EXAMPLE_INTRODUCTIONS[0].identifier)
    mock_handler_exists.assert_any_call(EXAMPLE_INTRODUCTIONS[1].identifier)
    mock_handler_insert.assert_any_call(EXAMPLE_INTRODUCTIONS[0])
    mock_handler_insert.assert_any_call(EXAMPLE_INTRODUCTIONS[1])
    mock_tweet_introductions.assert_any_call(EXAMPLE_INTRODUCTIONS[0])
    mock_tweet_introductions.assert_any_call(EXAMPLE_INTRODUCTIONS[1])
