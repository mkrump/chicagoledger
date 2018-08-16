import betamax
import pytest
import requests
from betamax_serializers import pretty_json
from urllib.parse import urlparse, parse_qs

from ocd_api import Bill, OCDBillsAPI


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


def test_get(betamax_session):
    api = OCDBillsAPI(betamax_session)

    response = api._get_bills('ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca', '2018-08-15', '2018-07-16', 'Referred')
    parsed_url = urlparse(response.url)
    url = parsed_url._replace(query=None).geturl()
    params = dict(parse_qs(parsed_url.query))

    assert params['actions__date__gte'] == ['2018-07-16']
    assert params['actions__date__lte'] == ['2018-08-15']
    assert params['actions__description'] == ['Referred']
    assert params['sponsorships__person_id'] == ['ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca']
    assert url == "https://ocd.datamade.us/bills/"


def test_parse_bills(betamax_session):
    api = OCDBillsAPI(betamax_session)
    expected_title = 'Fifty-fifth amending agreement with SomerCor 504, Inc. regarding Small Business Improvement Fund ' \
                     'program increases within Jefferson Park, Lawrence/Pulaski and Lincoln Avenue areas'
    expected_identifier = 'O2018-6138'
    expected_classification = ['ordinance']
    expected = Bill(expected_identifier, expected_title, expected_classification)

    response = api._get_bills('ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca', '2018-08-15', '2018-07-16', 'Referred')
    bills = api.parse_bills(response)
    actual = [bill for bill in bills if bill.identifier == expected_identifier][0]

    assert len(bills) == 31
    assert actual.identifier == expected.identifier
    assert actual.title == expected.title
    assert actual.classifications == expected.classifications
    assert actual.legistar_url == 'http://chicago.legistar.com/gateway.aspx?M=F2&ID=O2018-6138'
