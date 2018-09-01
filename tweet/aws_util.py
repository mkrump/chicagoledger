import os

import boto3
from botocore.exceptions import ClientError, ProfileNotFound


def get_secret(boto3_session, secret_name):
    client = boto3_session.client(
        service_name='secretsmanager',
        region_name=boto3_session.region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']
            return binary_secret_data


def generate_boto3_session(aws_profile_name):
    try:
        boto3_session = boto3.Session(profile_name=aws_profile_name)
    except ProfileNotFound:
        region = os.environ['AWS_DEFAULT_REGION']
        boto3_session = boto3.Session(region_name=region)
    return boto3_session
