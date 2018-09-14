from copy import copy

import pytest
from mock import mock, patch

from tweet.bills import Bills
from tweet.ocd_api import BillsRequestParams, BillsAPI
from tweet.query import get_new_introductions, filter_already_exists, filter_missing_date, save_introductions
from tweet.conftest import EXAMPLE_INTRODUCTIONS


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


@patch('tweet.query.filter_already_exists')
@patch('tweet.query.filter_missing_date')
def test_get_new_introductions(mock_filter_missing_date, mock_filter_already_exists,
                               bills_api, bills_request_params, bills):
    bills_api.get_bills.return_value = EXAMPLE_INTRODUCTIONS
    mock_filter_already_exists.return_value = EXAMPLE_INTRODUCTIONS
    bills_api.add_bills_dates.return_value = EXAMPLE_INTRODUCTIONS
    mock_filter_missing_date.return_value = EXAMPLE_INTRODUCTIONS

    new_introductions = get_new_introductions(bills_api, bills_request_params, bills)

    bills_api.get_bills.assert_called_with(bills_request_params)
    mock_filter_already_exists.assert_called_with(bills, EXAMPLE_INTRODUCTIONS)
    bills_api.add_bills_dates.assert_called_with(EXAMPLE_INTRODUCTIONS)
    mock_filter_missing_date.assert_called_with(EXAMPLE_INTRODUCTIONS)
    assert new_introductions == EXAMPLE_INTRODUCTIONS


def test_filter_already_exists(bills):
    bills.exists.side_effect = [True, False]

    new_bills = filter_already_exists(bills, EXAMPLE_INTRODUCTIONS)

    assert new_bills == [EXAMPLE_INTRODUCTIONS[1]]


def test_filter_missing_date():
    introductions = [copy(introduction) for introduction in EXAMPLE_INTRODUCTIONS]
    introductions[1].date = ''
    introductions[0].date = '10/28/2018'

    valid_bills = filter_missing_date(introductions)

    assert valid_bills == [introductions[0]]


def test_save_introductions(bills):
    save_introductions(bills, EXAMPLE_INTRODUCTIONS)

    assert bills.insert.call_count == len(EXAMPLE_INTRODUCTIONS)
