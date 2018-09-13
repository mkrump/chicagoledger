from decimal import Decimal

from boto3.dynamodb.conditions import Key, Attr
from requests import Request


class Bills:
    def __init__(self, boto3_session, table_name=None):
        if table_name is None:
            _table_name = 'bills'
        else:
            _table_name = table_name
        self.bills = boto3_session.resource('dynamodb', boto3_session.region_name).Table(_table_name)

    def insert(self, introduction):
        item = BillMapper().to_db(introduction)
        self.bills.put_item(Item=item)

    def exists(self, bill):
        response = self.get(bill)
        if response:
            return True
        return False

    def get_prev_tweet_id(self, date):
        response = self.bills.query(
            IndexName='date-index',
            Limit=1,
            ScanIndexForward=False,
            KeyConditionExpression=Key('date').eq(date)
        )
        if 'Items' in response and len(response['Items']) > 0:
            item = response['Items'][0]
            return BillMapper().from_db(item).tweet_id
        return None

    def missing_tweet_id(self):
        response = self.bills.query(
            IndexName='tweet_id-index',
            KeyConditionExpression=Key('tweet_id').eq(Decimal('-1'))
        )
        bills = []
        if 'Items' in response:
            for item in response["Items"]:
                bill = BillMapper().from_db(item)
                bills.append(bill)
        return bills

    def get(self, bill):
        response = self.bills.get_item(
            Key={'identifier': bill.identifier}
        )
        if 'Item' in response:
            item = response['Item']
            return BillMapper().from_db(item)
        return None


class Bill:
    def __init__(self, identifier, title, classifications, ocd_id, date=None, tweet_id='-1'):
        self.identifier = identifier
        self.title = title
        self.classifications = classifications
        self.ocd_id = ocd_id
        self.date = date
        self.tweet_id = tweet_id

    def __repr__(self):
        return "{0}({1}, {2}, {3}, {4}, {5}, {6})".format(
            self.__class__.__name__,
            self.identifier,
            self.title,
            self.classifications,
            self.ocd_id,
            self.date,
            self.tweet_id
        )

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.identifier == other.identifier and
                    self.title == other.title and
                    self.classifications == other.classifications and
                    self.date == other.date and
                    self.ocd_id == other.ocd_id and
                    self.tweet_id == other.tweet_id
                    )

    @staticmethod
    def generate_ocd_detail_url(ocd_id):
        return 'https://ocd.datamade.us/{}'.format(ocd_id)

    @staticmethod
    def generate_legistar_url(identifier):
        url = 'http://chicago.legistar.com/gateway.aspx'
        params = (('M', 'F2'), ('ID', identifier))
        r = Request('GET', url=url, params=params).prepare()
        return r.url


class BillMapper:
    @staticmethod
    def from_db(item):
        return Bill(
            item['identifier'],
            item['title'],
            item['classifications'],
            item['ocd_id'],
            item['date'],
            str(item['tweet_id'])
        )

    @staticmethod
    def to_db(bill):
        return {
            'identifier': bill.identifier,
            'title': bill.title,
            'classifications': bill.classifications,
            'date': bill.date,
            'ocd_id': bill.ocd_id,
            'tweet_id': Decimal(bill.tweet_id),
        }
