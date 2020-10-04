import json
import boto3
from pprint import pprint


def lambda_handler(event, context):
    comprehend = boto3.client("comprehend")
    text_list = [
        "Hey, welcome to this tutorial. How are you doing readers and viewers",
        "Hey, welcome to this tutorial. How are you doing readers and viewers"
    ]

    # Get analysis from Comprehend
    sentiment = comprehend.batch_detect_sentiment(
        TextList=text_list,
        LanguageCode="en"
    )
    entities = comprehend.batch_detect_entities(
        TextList=text_list,
        LanguageCode="en"
    )

    return {
        'statusCode': 200,
        'body': {
            "sentiment": sentiment,
            "entities": entities
        }
    }
