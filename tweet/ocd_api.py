from collections import namedtuple
from copy import copy

from dateutil import relativedelta

from tweet.bills import Bill

BillsRequestParams = namedtuple('BillsRequestParams', 'person_id, min_date, max_date, description')


class BillsAPI:
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

    def get_intro_date(self, ocd_bill_id):
        url = 'https://ocd.datamade.us/{ocd_bill_id}'.format(ocd_bill_id=ocd_bill_id)
        response = self.session.get(url)
        actions = response.json()['actions']
        referral = [action for action in actions if action['description'] == 'Referred'][0]
        return referral['date']

    def add_bills_dates(self, bills):
        updated_bills = []
        for bill in bills:
            updated_bill = copy(bill)
            updated_bill.date = self.get_intro_date(bill.ocd_id)
            updated_bills.append(updated_bill)
        return updated_bills

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
            b = Bill(bill['identifier'], bill['title'].strip(), bill['classification'], bill['id'])
            bills.append(b)
        return bills


# TODO Not sure this query does quite what we want
# TODO since only getting bills with any
# TODO action date = 'Query Date' and any action = 'Referred'
def create_query(max_date, weeks_offset, person, description):
    min_date = max_date - relativedelta.relativedelta(weeks=weeks_offset)
    return BillsRequestParams(
        person_id=person,
        max_date=max_date.strftime("%Y-%m-%d"),
        min_date=min_date.strftime("%Y-%m-%d"),
        description=description,
    )
