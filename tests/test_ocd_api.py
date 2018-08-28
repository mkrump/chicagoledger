import json
import math
from urllib.parse import urlparse, parse_qs

import betamax
import mock
import pytest
import requests
from betamax_serializers import pretty_json

from src.ocd_api import BillsEndpoint, BillsRequestParams
from src.bills import Bill
from tests.test_config import EXPECTED_IDENTIFIER, EXPECTED_OCD_ID, EXPECTED_TITLE, EXPECTED_CLASSIFICATION


@pytest.fixture()
def multi_page_request():
    session = requests.Session()
    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    recorder = betamax.Betamax(
        session, cassette_library_dir='tests/cassettes'
    )
    matchers = ['method', 'uri', 'body']

    with recorder.use_cassette('multi_page_bills', serialize_with='prettyjson', match_requests_on=matchers):
        payload = {
            'sponsorships__person_id': 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
            'actions__date__lte': '2018-08-15',
            'actions__date__gte': '2018-01-01',
            'actions__description': 'Referred'
        }
        session.get('https://ocd.datamade.us/bills/', params=payload)
        payload.update(page=2)
        session.get('https://ocd.datamade.us/bills/', params=payload)
        payload.update(page=3)
        session.get('https://ocd.datamade.us/bills/', params=payload)
    yield session


def create_mock_response(meta):
    mock_bill = mock.Mock(Bill)
    result_one = {'results': [mock_bill],
                  'meta': meta,
                  }
    mock_response_one = mock.Mock(requests.Response)
    mock_response_one.json.return_value = result_one
    return mock_response_one


def create_multi_page_mock_response(total_count, per_page):
    to_process = min(max(total_count - per_page, per_page), total_count)
    max_page = max(math.floor(total_count / per_page), 1)
    page = 1
    while to_process > 0:
        count = min(per_page, to_process)
        yield create_mock_response(
            {"per_page": per_page,
             "total_count": total_count,
             "max_page": max_page,
             "count": count,
             "page": page}
        )
        to_process -= per_page
        page += 1


@mock.patch('src.ocd_api.BillsEndpoint._call_bills_api')
@mock.patch('src.ocd_api.BillsEndpoint.parse_bills')
def test_get_bills_single_page(mock_parse_bills, mock_call_bills_api):
    api = BillsEndpoint(mock.Mock(requests.Session))
    responses = list(create_multi_page_mock_response(10, 100))
    mock_call_bills_api.side_effect = responses
    expected_calls = [mock.call(r.json()) for r in responses]

    payload = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-07-16',
        description='Referred'
    )
    api.get_bills(payload)

    assert mock_call_bills_api.call_count == 1
    assert mock_parse_bills.call_count == 1
    mock_parse_bills.assert_has_calls(expected_calls, any_order=True)


@mock.patch('src.ocd_api.BillsEndpoint._call_bills_api')
@mock.patch('src.ocd_api.BillsEndpoint.parse_bills')
def test_get_bills_multi_page(mock_parse_bills, mock_call_bills_api):
    api = BillsEndpoint(mock.Mock(requests.Session))
    responses = list(create_multi_page_mock_response(384, 100))
    mock_call_bills_api.side_effect = responses
    expected_calls = [mock.call(r.json()) for r in responses]

    payload = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-01-01',
        description='Referred'
    )
    api.get_bills(payload)

    assert mock_call_bills_api.call_count == 3
    assert mock_parse_bills.call_count == 3
    mock_parse_bills.assert_has_calls(expected_calls, any_order=True)


def test_call_bills_api(multi_page_request):
    api = BillsEndpoint(multi_page_request)
    payload = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-07-16',
        description='Referred'
    )

    response = api._call_bills_api(payload, page=2)
    parsed_url = urlparse(response.url)
    params = dict(parse_qs(parsed_url.query))
    url = parsed_url._replace(query=None).geturl()

    assert params['actions__date__gte'] == [payload.min_date]
    assert params['actions__date__lte'] == [payload.max_date]
    assert params['page'] == ['2']
    assert params['actions__description'] == [payload.description]
    assert params['sponsorships__person_id'] == [payload.person_id]
    assert url == "https://ocd.datamade.us/bills/"


def test_parse_bills():
    with open('tests/cassettes/single_page_bills.json') as f:
        cassette_json = json.load(f)
        response_json = json.loads(cassette_json['http_interactions'][0]['response']['body']['string'])
        api = BillsEndpoint(mock.Mock(requests.Session))

        bills = api.parse_bills(response_json)

        first_bill = [bill for bill in bills if bill.identifier == EXPECTED_IDENTIFIER][0]
        assert len(bills) == 31
        assert first_bill.identifier == EXPECTED_IDENTIFIER
        assert first_bill.title == EXPECTED_TITLE
        assert first_bill.classifications == EXPECTED_CLASSIFICATION
        assert first_bill.legistar_url == 'http://chicago.legistar.com/gateway.aspx?M=F2&ID={}'.format(
            EXPECTED_IDENTIFIER)
        assert first_bill.detail_url == 'https://ocd.datamade.us/{}'.format(EXPECTED_OCD_ID)
