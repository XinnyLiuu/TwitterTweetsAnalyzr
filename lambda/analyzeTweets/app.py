import json
import boto3
from pprint import pprint
import tweepy
import os


def lambda_handler(event, context):
    """
    Analyze tweets (with search term) with Comprehend
    """
    # Get search term from input (ignoring all retweets)
    term = "{} -filter:retweets".format(event["body"])

    # Fetch tweets with term
    auth = tweepy.AppAuthHandler(
        os.environ["KEY"],
        os.environ["SECRET"]
    )

    api = tweepy.API(auth)

    recent_tweets = []
    for tweet in api.search(
            q=term,
            lang="en",
            result_type="recent",
            count=10,
            tweet_mode="extended"):
        recent_tweets.append(tweet.full_text)

    # Prepare comprehend analysis
    comprehend = boto3.client("comprehend")

    # Get analysis from Comprehend
    sentiment = comprehend.batch_detect_sentiment(
        TextList=recent_tweets,
        LanguageCode="en"
    )
    entities = comprehend.batch_detect_entities(
        TextList=recent_tweets,
        LanguageCode="en"
    )

    return {
        'statusCode': 200,
        "headers": {
            "Content-Type": "application/json"
        },
        'body': json.dumps({
            "tweets": recent_tweets,
            "sentiment": sentiment,
            "entities": entities
        })
    }
