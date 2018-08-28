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
