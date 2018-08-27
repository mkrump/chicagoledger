from collections import namedtuple

from requests import Request


class Bill:
    def __init__(self, identifier, title, classifications):
        self.identifier = identifier
        self.title = title
        self.classifications = classifications
        self.legistar_url = self._build_legistar_url(identifier)

    @staticmethod
    def _build_legistar_url(identifier):
        url = 'http://chicago.legistar.com/gateway.aspx'
        params = {
            'M': 'F2',
            'ID': identifier
        }
        r = Request('GET', url=url, params=params).prepare()
        return r.url


BillsRequestParams = namedtuple('BillsRequestParams', 'person_id, min_date, max_date, description')


class BillsEndpoint:
    endpoint = 'https://ocd.datamade.us/bills/'

    def __init__(self, session):
        self.session = session

    def _call_bills_api(self, bills_request_params, page=1):
        payload = {
            'sponsorships__person_id': bills_request_params.person_id,
            'actions__date__lte': bills_request_params.max_date,
            'actions__date__gte': bills_request_params.min_date,
            'actions__description': bills_request_params.description,
            'page': page,
        }
        return self.session.get(self.endpoint, params=payload)

    def _page_bills_results(self, bills_request_params):
        first_page = self._call_bills_api(bills_request_params)
        yield first_page.json()
        max_page = first_page.json()['meta']['max_page']
        for page in range(2, max_page + 1):
            next_page = self._call_bills_api(bills_request_params, page=page)
            yield next_page.json()

    def get_bills(self, bills_request_params):
        bills = []
        for page in self._page_bills_results(bills_request_params):
            bill = self.parse_bills(page)
            bills.extend(bill)
        return bills

    @staticmethod
    def parse_bills(bills_json):
        bills = []
        for bill in bills_json['results']:
            b = Bill(bill['identifier'], bill['title'].strip(), bill['classification'])
            bills.append(b)
        return bills
