from botocore.exceptions import ClientError

# OCD Query params
# Rahm Emanuel -> https://ocd.datamade.us/ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca/
PERSON = 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca'
ACTIONS = 'Referred'

# AWS params
# .aws/config to use
# profile is expected to have region
AWS_PROFILE_NAME = 'default'
AWS_SECRETSMANAGER_SECRET_NAME = 'Twitter'


def get_secret(boto3_session):
    client = boto3_session.client(
        service_name='secretsmanager',
        region_name=boto3_session.region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=AWS_SECRETSMANAGER_SECRET_NAME
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + AWS_SECRETSMANAGER_SECRET_NAME + " was not found")
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
