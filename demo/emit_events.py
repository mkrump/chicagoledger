import json
from time import sleep

import boto3


def main():
    with open('sample.json') as f:
        events = json.loads(f.read())
        s3_client = boto3.client('s3')
        for event in events:
            event_json = json.dumps([event])
            key = "events/{}".format(event['Meeting Date'].replace('-', ''))
            print(key)
            print(event_json)
            s3_client.put_object(Bucket='what-rahm-wants', Key=key, Body=event_json)
            sleep(10)


if __name__ == '__main__':
    main()
