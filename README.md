
# Setup
## Sys Diagram
![diagram](aws.png)

## Requirements
- [AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/index.html) (Basically, `CloudFormation`, but more abstracted / easier)
    - There's really no "good" way to work on this together, so the best I can think of is using SAM to spin up the resources we got
    - Set up `SAM CLI` and run `deploy.sh` under the serverless directory
    - Once all the inital resources are set up, go to `Amplify`, find the app and build it (just this once, future builds are auto deployed)

## Docs
- [Docs on Comprehend (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/comprehend.html?highlight=comprehend#comprehend)
- [Docs on Comprehend - DetectSentiment](https://docs.aws.amazon.com/comprehend/latest/dg/API_DetectSentiment.html)
- [Docs on Comprehend - DetectEntities](https://docs.aws.amazon.com/comprehend/latest/dg/API_DetectEntities.html)

# Notes 
- Looks like Comprehend doesn't aggregate the sentiment / entities, so we may have to do this ourselves.

```python
Example:
I want to analyze tweets with `Trump` 

Comprehend returns:
{
  "statusCode": 200,
  "body": {
    "tweets": [
      "@AmandiOnAir Trump is a psychopath getting away with murder. He killing people right in front of our eyes."
    ],
    "sentiment": {
      "ResultList": [
        {
          "Index": 0,
          "Sentiment": "NEGATIVE",
          "SentimentScore": {
            "Positive": 0.00022572008310817182,
            "Negative": 0.9855265617370605,
            "Neutral": 0.014246664009988308,
            "Mixed": 0.0000010548167210799875
          }
        }
      ],
      "ErrorList": [],
      "ResponseMetadata": {
        "RequestId": "66dba76a-f0f2-477c-b91f-309528abd9b0",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
          "x-amzn-requestid": "66dba76a-f0f2-477c-b91f-309528abd9b0",
          "content-type": "application/x-amz-json-1.1",
          "content-length": "209",
          "date": "Sun, 04 Oct 2020 22:38:39 GMT"
        },
        "RetryAttempts": 0
      }
    },
    "entities": {
      "ResultList": [
        {
          "Index": 0,
          "Entities": [
            {
              "Score": 0.5656334757804871,
              "Type": "ORGANIZATION",
              "Text": "@AmandiOnAir",
              "BeginOffset": 0,
              "EndOffset": 12
            },
            {
              "Score": 0.9450738430023193,
              "Type": "PERSON",
              "Text": "Trump",
              "BeginOffset": 13,
              "EndOffset": 18
            }
          ]
        }
      ],
      "ErrorList": [],
      "ResponseMetadata": {
        "RequestId": "9d69f7e4-04bc-41ec-ba6c-e35ecc795434",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
          "x-amzn-requestid": "9d69f7e4-04bc-41ec-ba6c-e35ecc795434",
          "content-type": "application/x-amz-json-1.1",
          "content-length": "252",
          "date": "Sun, 04 Oct 2020 22:38:39 GMT"
        },
        "RetryAttempts": 0
      }
    }
  }
}
```