
# Setup
## Requirements
- [AWS Python Client - Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html?highlight=comprehend)
- Create new IAM role for Lambda functions with `ComprehendFullAccess` and `AWSLambdaExecute` permission

## Notes on Comprehend
- [Docs on Comprehend (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html?highlight=comprehend#comprehend)
- Looks like Comprehend doesn't aggregate the sentiment / entities, so we may have to do this ourselves.

```python
I want to analyze: 
[
    "Hey, welcome to this tutorial. How are you doing readers and viewers",
    "Hey, welcome to this tutorial. How are you doing readers and viewers"
]

Comprehend returns:
{
  "statusCode": 200,
  "body": {
    "sentiment": {
      "ResultList": [
        {
          "Index": 0,
          "Sentiment": "NEUTRAL",
          "SentimentScore": {
            "Positive": 0.36617422103881836,
            "Negative": 0.007702559698373079,
            "Neutral": 0.6261109709739685,
            "Mixed": 0.000012214969501656014
          }
        },
        {
          "Index": 1,
          "Sentiment": "NEUTRAL",
          "SentimentScore": {
            "Positive": 0.36617422103881836,
            "Negative": 0.007702559698373079,
            "Neutral": 0.6261109709739685,
            "Mixed": 0.000012214969501656014
          }
        }
      ],
      "ErrorList": [],
      "ResponseMetadata": {
        "RequestId": "c81e0ae1-3765-4eb6-a460-6d57e775bff8",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
          "x-amzn-requestid": "c81e0ae1-3765-4eb6-a460-6d57e775bff8",
          "content-type": "application/x-amz-json-1.1",
          "content-length": "381",
          "date": "Sun, 04 Oct 2020 20:18:10 GMT"
        },
        "RetryAttempts": 0
      }
    },
    "entities": {
      "ResultList": [
        {
          "Index": 0,
          "Entities": []
        },
        {
          "Index": 1,
          "Entities": []
        }
      ],
      "ErrorList": [],
      "ResponseMetadata": {
        "RequestId": "5b60b4ff-f2cb-4b15-a542-097764af2bb2",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
          "x-amzn-requestid": "5b60b4ff-f2cb-4b15-a542-097764af2bb2",
          "content-type": "application/x-amz-json-1.1",
          "content-length": "83",
          "date": "Sun, 04 Oct 2020 20:18:10 GMT"
        },
        "RetryAttempts": 0
      }
    }
  }
}
```
