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


class OCDBillsAPI:
    endpoint = 'https://ocd.datamade.us/bills/'

    def __init__(self, session):
        self.session = session

    def _get_bills(self, person_id, max_date, min_date, description):
        payload = {
            'sponsorships__person_id': person_id,
            'actions__date__lte': max_date,
            'actions__date__gte': min_date,
            'actions__description': description,
        }
        return self.session.get(self.endpoint, params=payload)

    def get_bills(self, person_id, max_date, min_date, description):
        return self.parse_bills(self._get_bills(person_id, max_date, min_date, description))

    @staticmethod
    def parse_bills(bills_response):
        bills = []
        bills_response_json = bills_response.json()
        for bill in bills_response_json['results']:
            b = Bill(bill['identifier'], bill['title'].strip(), bill['classification'])
            bills.append(b)
        return bills