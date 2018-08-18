An AWS Lambda twitter bot that shares legislation introduced by Chicago mayor Rahm Emanuel

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

- Deploy with serverless `serverless deploy`
