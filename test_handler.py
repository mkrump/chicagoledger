import datetime
from unittest.mock import patch

from handler import call
from ocd_api import Bill, BillsRequestParams

example_introductions = [
    Bill('O2099-1111', 'Make it illegal to put ketchup on hotdogs', ['ordinance']),
    Bill('O2098-1112', 'Dye the lake green everyday', ['ordinance'])
]


# TODO maybe try to simplify this test / setup
# TODO Also need to add error handling to handler
@patch('handler.today')
@patch('handler.TwitterBot.tweet_introductions')
@patch('handler.Bills.insert')
@patch('handler.Bills.exists')
@patch('handler.BillsEndpoint.get_bills')
def test_call(mock_get_bills, mock_handler_exists, mock_handler_insert, mock_tweet_introductions, mock_today):
    mock_today.return_value = datetime.datetime(2018, 8, 15)
    mock_get_bills.return_value = example_introductions
    mock_handler_exists.return_value = False

    call(None, None)

    query_params = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-07-15',
        description='Referred'
    )
    mock_get_bills.assert_called_with(query_params)
    mock_handler_exists.assert_any_call(example_introductions[0].identifier)
    mock_handler_exists.assert_any_call(example_introductions[1].identifier)
    mock_handler_insert.assert_called_with(example_introductions)
    mock_tweet_introductions.assert_called_with(example_introductions)
