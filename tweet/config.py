from collections import namedtuple

from dateutil.utils import today

from tweet.ocd_api import create_query

AppConfig = namedtuple('AppConfig', 'aws_profile, aws_secret_name, query')

# OCD Query params
# Rahm Emanuel -> https://ocd.datamade.us/ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca/
PERSON = 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca'
ACTIONS = 'Referred'

# AWS params
# .aws/config to use
# profile is expected to have region
AWS_PROFILE_NAME = 'default'
AWS_SECRETSMANAGER_SECRET_NAME = 'Twitter'
QUERY = create_query(
    max_date=today(),
    weeks_offset=6,
    person=PERSON, description=ACTIONS
)

APP_CONFIG = AppConfig(AWS_PROFILE_NAME, AWS_SECRETSMANAGER_SECRET_NAME, QUERY)
