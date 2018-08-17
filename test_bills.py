import boto3
import pytest
from moto import mock_dynamodb2

from bills import Bills
from ocd_api import Bill

example_introductions = [
    Bill('O2099-1111', 'Make it illegal to put ketchup on hotdogs', ['ordinance']),
    Bill('O2098-1112', 'Dye the lake green everyday', ['ordinance'])
]


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
    bills.insert(example_introductions)

    intro1 = bills_table.get_item(Key={'bill_id': example_introductions[0].identifier})['Item']
    intro2 = bills_table.get_item(Key={'bill_id': example_introductions[1].identifier})['Item']
    assert intro1['bill_id'] == example_introductions[0].identifier
    assert intro2['bill_id'] == example_introductions[1].identifier
