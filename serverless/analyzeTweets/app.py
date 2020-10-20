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

    result = []
    text = []
    for i, tweet in enumerate(
        api.search(
            q=term,
            lang="en",
            result_type="recent",
            count=5,
            tweet_mode="extended"
        )
    ):
        user = tweet._json["user"]["screen_name"]
        tweet_id = tweet._json["id_str"]
        tweet = tweet._json["full_text"]

        result.append(
            {
                "url": f"twitter.com/{user}/status/{tweet_id}",
                "user": user,
                "tweet": tweet,
                "sentiment": "",
                "sentiment_score": 0.0,
                "entities": []
            }
        )

        text.append(tweet)

    # Prepare comprehend analysis
    comprehend = boto3.client("comprehend")

    # Get analysis from Comprehend
    sentiments = comprehend.batch_detect_sentiment(
        TextList=text,
        LanguageCode="en"
    )
    entities = comprehend.batch_detect_entities(
        TextList=text,
        LanguageCode="en"
    )

    # Add comprehend data to result
    for data in sentiments["ResultList"]:
        index = data["Index"]
        sentiment = data["Sentiment"]

        # Get the score for the sentiment returned
        score = 0.0
        for key in data["SentimentScore"].keys():
            if sentiment.lower() == key.lower():
                score = data["SentimentScore"][key]
                break

        result[index]["sentiment"] = sentiment
        result[index]["sentiment_score"] = score

    for data in entities["ResultList"]:
        index = data["Index"]
        output = []

        for e in data["Entities"]:
            output.append({
                "score": e["Score"],
                "text": e["Text"],
                "type": e["Type"]
            })

        result[index]["entities"] = output

    return {
        'statusCode': 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(result)
    }
