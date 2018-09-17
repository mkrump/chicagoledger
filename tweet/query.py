import logging
from collections import namedtuple

import requests

from tweet.aws_util import generate_boto3_session
from tweet.bills import Bills
from tweet.config import APP_CONFIG
from tweet.ocd_api import BillsAPI

log = logging.getLogger(__name__)

App = namedtuple('App', 'bills_api, query, bills')


def call(event, context):
    app = setup(app_config=APP_CONFIG)
    new_introductions = get_new_introductions(app.bills_api, app.query, app.bills)
    log.setLevel(logging.INFO)
    log.info("call: {} new introductions".format(len(new_introductions)))
    log.setLevel(logging.WARNING)
    save_introductions(app.bills, new_introductions)


def setup(app_config):
    requests_session = requests.Session()
    ocd_bills_api = BillsAPI(requests_session)

    boto3_session = generate_boto3_session(app_config.aws_profile)
    bills = Bills(boto3_session)

    return App(ocd_bills_api, app_config.query, bills)


def get_new_introductions(ocd_api, query_params, bills):
    introductions = ocd_api.get_bills(query_params)
    new_introductions = filter_already_exists(bills, introductions)
    new_introductions = ocd_api.add_bills_dates(new_introductions)
    new_introductions = filter_missing_date(new_introductions)
    return new_introductions


def save_introductions(bills, introductions):
    for new_introduction in introductions:
        bills.insert(new_introduction)


def filter_already_exists(bills, introductions):
    introductions = [introduction for introduction in introductions if not bills.exists(introduction)]
    return introductions


def filter_missing_date(introductions):
    introductions = [introduction for introduction in introductions if introduction.date != '']
    return introductions
