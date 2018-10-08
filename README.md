**This now being managed from the City Bureau repo** The new location is https://github.com/City-Bureau/chicagoledger

An AWS Lambda twitter bot that shares legislation introduced by Chicago city council members. 
The default settings share legislation introduced by current Chicago mayor Rahm Emanuel.


## Setup

- Install and setup serverless (complete steps on 1 and 2 in the [Quick Start](
https://github.com/serverless/serverless/blob/master/README.md#quick-start))

- Get Twitter API key https://apps.twitter.com/

- In AWS Secrets Manager create a secret (if the name is not `Twitter` update the config.py) with the following keys: 
```json
{
  "twitter-consumer-key": "",
  "twitter-consumer-secret": "",
  "twitter-access-token": "",
  "twitter-access-secret": ""
}
```

- Change the ocd-person in `config.py` to the member that you want to follow. 
```python
# DEFAULT
# Rahm Emanuel -> https://ocd.datamade.us/ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca/
PERSON = 'ocd-person/f649753d-081d-4f22-8dcf-3af71de0e6ca'
```

## Deploy
- Uses the [serverless additional stacks plugin](https://github.com/SC5/serverless-plugin-additional-stacks) to separate out the DynamoDB / Lambda deployments

    - Deploy everything including DynamoDB 
    ```sls deploy```

    - Deploy only Lambda 
    ```sls deploy --skip-additionalstacks```
    
    - Remove only Lambda 
    ```sls remove --skip-additionalstacks```
    
    - Remove DynamoDB 
    ```sls remove additionalstacks```
     
## Tests

```
pip-compile --output-file requirements/requirements-dev.txt requirements/requirements-dev.in
pip install -r requirements/requirements-dev.txt 
pytest
```

