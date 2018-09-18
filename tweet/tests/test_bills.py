import boto3
import pytest
from moto import mock_dynamodb2

from tweet.bills import Bills, Bill, BillMapper
from tweet.conftest import EXAMPLE_INTRODUCTIONS

AttributeDefinitions = [
    {'AttributeName': 'identifier', 'AttributeType': 'S'},
    {'AttributeName': 'date', 'AttributeType': 'S'},
    {'AttributeName': 'tweet_id', 'AttributeType': 'N'},
]
KeySchema = [{'AttributeName': 'identifier', 'KeyType': 'HASH'}]
ProvisionedThroughput = {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
GlobalSecondaryIndexes = [
    {
        "IndexName": "date-index",
        "KeySchema": [
            {"AttributeName": "date", "KeyType": "HASH"},
            {"AttributeName": "tweet_id", "KeyType": "RANGE"}
        ],
        'Projection': {'ProjectionType': 'ALL', },
        'ProvisionedThroughput': ProvisionedThroughput
    },
    {
        "IndexName": "tweet_id-index",
        "KeySchema": [
            {"AttributeName": "tweet_id", "KeyType": "HASH"}
        ],
        'Projection': {'ProjectionType': 'ALL', },
        'ProvisionedThroughput': ProvisionedThroughput
    }
]


@pytest.fixture
def bills_table():
    with mock_dynamodb2():
        client = boto3.resource('dynamodb')

        client.create_table(
            TableName='bills',
            AttributeDefinitions=AttributeDefinitions,
            KeySchema=KeySchema,
            ProvisionedThroughput=ProvisionedThroughput,
            GlobalSecondaryIndexes=GlobalSecondaryIndexes,
        )

        table = client.Table('bills')
        yield table


def test_exists(bills_table):
    item = BillMapper().to_db(EXAMPLE_INTRODUCTIONS[0])
    bills_table.put_item(Item=item)

    bills = Bills(boto3.Session())
    assert bills.exists(EXAMPLE_INTRODUCTIONS[0]) is True
    assert bills.exists(EXAMPLE_INTRODUCTIONS[1]) is False


def test_get(bills_table):
    bill = EXAMPLE_INTRODUCTIONS[0]
    item = BillMapper().to_db(bill)
    bills_table.put_item(Item=item)

    bills = Bills(boto3.Session())
    bill = bills.get(bill)
    assert bill == EXAMPLE_INTRODUCTIONS[0]


def test_no_tweet(bills_table):
    no_tweet_id_bills = [Bill(str(i), None, None, None, '10/25/18') for i in range(4)]
    have_tweet_id_bills = [Bill(str(len(no_tweet_id_bills) + i), None, None, None, '10/25/18', str(i))
                           for i in range(4)]
    bills = Bills(boto3.Session())
    combined_bills = no_tweet_id_bills + have_tweet_id_bills
    for bill in combined_bills:
        bills.insert(bill)
    assert sorted(bills.missing_tweet_id(), key=lambda x: x.identifier) == no_tweet_id_bills


# mocking framework doesn't seem to sort by sort index for GSI
# this test actually creates a table called 'bills_test' and tests
# against dynamodb so takes a long time to run, so skipping for normal
# test runs add --run-slow to run
@pytest.mark.slow
def test_get_prev_tweet_id():
    session = boto3.Session()
    client = session.client('dynamodb')
    test_table_name = 'bills_test'
    client.create_table(
        TableName=test_table_name,
        AttributeDefinitions=AttributeDefinitions,
        KeySchema=KeySchema,
        ProvisionedThroughput=ProvisionedThroughput,
        GlobalSecondaryIndexes=GlobalSecondaryIndexes,
    )
    print('Waiting for', test_table_name, '...')
    waiter = client.get_waiter('table_exists')
    waiter.wait(TableName=test_table_name)

    introductions = [
        Bill('1', 'text', ['tag'], 'ocd-id', '10/28/18', '789'),
        Bill('2', 'text', ['tag'], 'ocd-id', '10/28/18', '123'),
        Bill('3', 'text', ['tag'], 'ocd-id', '10/28/18', '10000'),
        Bill('4', 'text', ['tag'], 'ocd-id', '10/28/18', '1'),
        Bill('5', 'text', ['tag'], 'ocd-id', '10/29/18', '10000000')
    ]
    bills = Bills(boto3.Session(), test_table_name)
    for introduction in introductions:
        bills.insert(introduction)

    prev_tweet_id = bills.get_prev_tweet_id('10/29/18')
    assert prev_tweet_id == '10000000'
    prev_tweet_id = bills.get_prev_tweet_id('10/28/18')
    assert prev_tweet_id == '10000'
    client.delete_table(TableName=test_table_name)
    waiter = client.get_waiter('table_not_exists')
    waiter.wait(TableName=test_table_name)


def test_insert(bills_table):
    bills = Bills(boto3.Session())
    for introduction in EXAMPLE_INTRODUCTIONS:
        bills.insert(introduction)

    intro1 = bills.get(EXAMPLE_INTRODUCTIONS[0])
    intro2 = bills.get(EXAMPLE_INTRODUCTIONS[1])
    assert intro1 == EXAMPLE_INTRODUCTIONS[0]
    assert intro2 == EXAMPLE_INTRODUCTIONS[1]
