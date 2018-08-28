from requests import Request


class Bills:
    def __init__(self, boto3_session):
        self.bills = boto3_session.resource('dynamodb', boto3_session.region_name).Table('bills')

    def insert(self, introduction):
        self.bills.put_item(
            Item={'bill_id': introduction.identifier,
                  'title': introduction.title,
                  'classification': introduction.classifications,
                  'legistar_url': introduction.legistar_url,
                  }
        )

    def exists(self, hash_key):
        response = self.bills.get_item(
            Key={'bill_id': hash_key}
        )
        if 'Item' in response:
            return True
        return False


class Bill:
    def __init__(self, identifier, title, classifications, ocd_id):
        self.identifier = identifier
        self.title = title
        self.classifications = classifications
        self.legistar_url = self._build_legistar_url(identifier)
        self.detail_url = 'https://ocd.datamade.us/{}'.format(ocd_id)

    @staticmethod
    def _build_legistar_url(identifier):
        url = 'http://chicago.legistar.com/gateway.aspx'
        params = {
            'M': 'F2',
            'ID': identifier
        }
        r = Request('GET', url=url, params=params).prepare()
        return r.url