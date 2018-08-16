import boto3
from moto import mock_dynamodb2

from bills import Bills
from test_handler import example_introductions


@mock_dynamodb2
def test_exists():
    client = boto3.resource('dynamodb', region_name='us-east-1')
    client.create_table(
        TableName='bills',
        AttributeDefinitions=[{'AttributeName': 'bill_id', 'AttributeType': 'S'}],
        KeySchema=[{'AttributeName': 'bill_id', 'KeyType': 'HASH'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
    table = client.Table('bills')
    table.put_item(Item={'bill_id': '12345xyz'})

    bills = Bills()
    assert bills.exists('12345xyz') is True
    assert bills.exists('not_there') is False


@mock_dynamodb2
def test_insert():
    client = boto3.resource('dynamodb', region_name='us-east-1')
    client.create_table(
        TableName='bills',
        AttributeDefinitions=[{'AttributeName': 'bill_id', 'AttributeType': 'S'}],
        KeySchema=[{'AttributeName': 'bill_id', 'KeyType': 'HASH'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    bills = Bills()
    bills.insert(example_introductions)

    table = client.Table('bills')
    intro1 = table.get_item(Key={'bill_id': example_introductions[0].identifier})['Item']
    intro2 = table.get_item(Key={'bill_id': example_introductions[1].identifier})['Item']
    assert intro1['bill_id'] == example_introductions[0].identifier
    assert intro2['bill_id'] == example_introductions[1].identifier

