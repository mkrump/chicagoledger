import json
from urllib.parse import urlparse, parse_qs

import betamax
import mock
import pytest
import requests
from betamax_serializers import pretty_json
from mock import call

from ocd_api import Bill, BillsEndpoint

EXPECTED_ORDINANCE = ['ordinance']

EXPECTED_IDENTIFIER = 'O2018-6138'

EXPECTED_TITLE = 'Fifty-fifth amending agreement with SomerCor 504, Inc. regarding Small Business Improvement Fund ' \
                 'program increases within Jefferson Park, Lawrence/Pulaski and Lincoln Avenue areas'
EXPECTED_BILL = Bill(EXPECTED_IDENTIFIER, EXPECTED_TITLE, EXPECTED_ORDINANCE)

@pytest.fixture()
def betamax_session():
    session = requests.Session()
    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    recorder = betamax.Betamax(
        session, cassette_library_dir='cassettes'
    )
    matchers = ['method', 'uri', 'body']

    with recorder.use_cassette('bills', serialize_with='prettyjson', match_requests_on=matchers):
        payload = {
            'sponsorships__person_id': 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
            'actions__date__lte': '2018-08-15',
            'actions__date__gte': '2018-07-16',
            'actions__description': 'Referred'
        }
        session.get('https://ocd.datamade.us/bills/', params=payload)
    yield session


@mock.patch('ocd_api.BillsEndpoint._call_bills_api')
@mock.patch('ocd_api.BillsEndpoint.parse_bills')
def test_get_bills(mock_parse_bills, mock_call_bills_api):
    mock_bill = mock.Mock(Bill)
    results = {'results': [mock_bill]}
    mock_response = mock.Mock(requests.Response)
    mock_response.json.return_value = results

    api = BillsEndpoint(mock.Mock(requests.Session))
    mock_call_bills_api.return_value = mock_response

    api.get_bills('ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca', '2018-08-15', '2018-07-16', 'Referred')

    assert mock_parse_bills.call_count == 1
    assert mock_call_bills_api.call_count == 1
    mock_parse_bills.assert_called_with(results)


def test_call_bills_api(betamax_session):
    api = BillsEndpoint(betamax_session)

    response = api._call_bills_api(
        'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        '2018-08-15', '2018-07-16', 'Referred'
    )
    parsed_url = urlparse(response.url)
    params = dict(parse_qs(parsed_url.query))
    url = parsed_url._replace(query=None).geturl()

    assert params['actions__date__gte'] == ['2018-07-16']
    assert params['actions__date__lte'] == ['2018-08-15']
    assert params['actions__description'] == ['Referred']
    assert params['sponsorships__person_id'] == ['ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca']
    assert url == "https://ocd.datamade.us/bills/"


def test_parse_bills():
    with open('cassettes/bills.json') as f:
        cassette_json = json.load(f)
        response_json = json.loads(cassette_json['http_interactions'][0]['response']['body']['string'])
        api = BillsEndpoint(mock.Mock(requests.Session))

        bills = api.parse_bills(response_json)

        first_bill = [bill for bill in bills if bill.identifier == EXPECTED_IDENTIFIER][0]
        assert len(bills) == 31
        assert first_bill.identifier == EXPECTED_BILL.identifier
        assert first_bill.title == EXPECTED_BILL.title
        assert first_bill.classifications == EXPECTED_BILL.classifications
        assert first_bill.legistar_url == 'http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2018-6138'
