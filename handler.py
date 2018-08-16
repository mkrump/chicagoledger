import logging

import dateutil
import requests
from dateutil.utils import today

from bills import Bills
from ocd_api import OCDBillsAPI
from twitter import TwitterBot

logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = requests.Session()
ocd_bills = OCDBillsAPI(session)

bills = Bills()
bot = TwitterBot()


# TODO change date to range
# Also not sure this query does quite what we want
# since only getting bills with any
# action date = 'Query Date' and any action = 'Referred'
def create_query(max_date):
    min_date = max_date - dateutil.relativedelta.relativedelta(months=1)

    max_date.strftime("%Y-%m-%d")
    return {
        # Rahm Emanuel -> https://ocd.datamade.us/ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca/
        'ocd-person': 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca',
        'max_date': max_date.strftime("%Y-%m-%d"),
        'min_date': min_date.strftime("%Y-%m-%d"),
        'actions': 'Referred',
    }


def call(event, context):
    query_params = create_query(today())
    introductions = ocd_bills.get_bills(
        query_params['ocd-person'],
        query_params['max_date'],
        query_params['min_date'],
        query_params['actions'],
    )
    new_introductions = [introduction for introduction in introductions
                         if not bills.exists(introduction.identifier)]
    logger.info("call: {} new introductions".format(len(new_introductions)))
    bills.insert(new_introductions)
    if len(introductions) > 0:
        bot.tweet_introductions(introductions)
