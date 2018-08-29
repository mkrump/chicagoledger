import boto3
import pytest
from moto import mock_dynamodb2

from tweet.bills import Bills
from tweet.tests.test_config import EXAMPLE_INTRODUCTIONS


@pytest.fixture
def bills_table():
    with mock_dynamodb2():
        client = boto3.resource('dynamodb')
        client.create_table(
            TableName='bills',
            AttributeDefinitions=[{'AttributeName': 'bill_id', 'AttributeType': 'S'}],
            KeySchema=[{'AttributeName': 'bill_id', 'KeyType': 'HASH'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
        table = client.Table('bills')
        yield table


def test_exists(bills_table):
    bills_table.put_item(Item={'bill_id': '12345xyz'})

    bills = Bills(boto3.Session())
    assert bills.exists('12345xyz') is True
    assert bills.exists('not_there') is False


def test_insert(bills_table):
    bills = Bills(boto3.Session())
    for introduction in EXAMPLE_INTRODUCTIONS:
        bills.insert(introduction)

    intro1 = bills_table.get_item(Key={'bill_id': EXAMPLE_INTRODUCTIONS[0].identifier})['Item']
    intro2 = bills_table.get_item(Key={'bill_id': EXAMPLE_INTRODUCTIONS[1].identifier})['Item']
    assert intro1['bill_id'] == EXAMPLE_INTRODUCTIONS[0].identifier
    assert intro2['bill_id'] == EXAMPLE_INTRODUCTIONS[1].identifier
