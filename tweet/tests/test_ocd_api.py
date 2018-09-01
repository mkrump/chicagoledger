import datetime
import json
from urllib.parse import urlparse, parse_qs

import betamax
import mock
import pytest
import requests
from betamax_serializers import pretty_json

from tweet.ocd_api import BillsAPI, BillsRequestParams, create_query
from tweet.tests.test_config import EXPECTED_IDENTIFIER, EXPECTED_OCD_ID, EXPECTED_TITLE, EXPECTED_CLASSIFICATION


def get_url_and_params(full_url):
    parsed_url = urlparse(full_url)
    params = dict(parse_qs(parsed_url.query))
    url = parsed_url._replace(query=None).geturl()
    return params, url


@pytest.fixture
def multi_page_request():
    session = requests.Session()
    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    recorder = betamax.Betamax(
        session, cassette_library_dir='tweet/tests/cassettes'
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


@pytest.fixture
def single_page_request():
    session = requests.Session()
    betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)
    recorder = betamax.Betamax(
        session, cassette_library_dir='tweet/tests/cassettes'
    )
    matchers = ['method', 'uri', 'body']

    with recorder.use_cassette('single_page_bills', serialize_with='prettyjson', match_requests_on=matchers):
        payload = {
            'sponsorships__person_id': 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
            'actions__date__lte': '2018-08-15',
            'actions__date__gte': '2018-07-16',
            'actions__description': 'Referred'
        }
        session.get('https://ocd.datamade.us/bills/', params=payload)
        yield session


def test_get_bills_single_page(single_page_request):
    api = BillsAPI(single_page_request)
    payload = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-07-16',
        description='Referred'
    )

    bills = api.get_bills(payload)

    assert len(bills) == 31


def test_get_bills_multi_page(multi_page_request):
    api = BillsAPI(multi_page_request)
    payload = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-01-01',
        description='Referred'
    )

    bills = api.get_bills(payload)

    assert len(bills) == 285


def test_call_bills_api(multi_page_request):
    api = BillsAPI(multi_page_request)
    payload = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-01-01',
        description='Referred'
    )

    response = api._call_bills_api(payload, page=2)
    params, url = get_url_and_params(response.url)

    assert params['actions__date__gte'] == [payload.min_date]
    assert params['actions__date__lte'] == [payload.max_date]
    assert params['page'] == ['2']
    assert params['actions__description'] == [payload.description]
    assert params['sponsorships__person_id'] == [payload.person_id]
    assert url == "https://ocd.datamade.us/bills/"


def test_parse_bills(single_page_request):
    api = BillsAPI(single_page_request)
    payload = BillsRequestParams(
        person_id='ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        max_date='2018-08-15',
        min_date='2018-07-16',
        description='Referred'
    )
    response = api._call_bills_api(payload)
    bills = api.parse_bills(response.json())

    first_bill = [bill for bill in bills if bill.identifier == EXPECTED_IDENTIFIER][0]
    assert len(bills) == 31
    assert first_bill.identifier == EXPECTED_IDENTIFIER
    assert first_bill.title == EXPECTED_TITLE
    assert first_bill.classifications == EXPECTED_CLASSIFICATION
    params, url = get_url_and_params(first_bill.legistar_url)
    assert url == 'http://chicago.legistar.com/gateway.aspx'
    assert params['M'] == ['F2']
    assert params['ID'] == [EXPECTED_IDENTIFIER]
    assert first_bill.detail_url == 'https://ocd.datamade.us/{}'.format(EXPECTED_OCD_ID)


def test_create_query():
    query_date = '2018-06-01'
    min_date = '2018-04-20'
    max_date = datetime.datetime.strptime(query_date, '%Y-%m-%d')
    query = create_query(max_date=max_date, weeks_offset=6, person='person-id', description='action')
    assert query == BillsRequestParams(
        person_id='person-id',
        max_date=query_date,
        min_date=min_date,
        description='action',
    )
