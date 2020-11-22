import json
import os

import boto3
import tweepy
from unidecode import unidecode
from utils import entity_data_cleanse


def get_tweets(term: str, result: list) -> list:
    """
    Fetch tweets from twitter using tweepy
    Returns list of all tweets pulled
    """
    tweets = []

    auth = tweepy.AppAuthHandler(os.environ["KEY"], os.environ["SECRET"])
    api = tweepy.API(auth)

    for i, tweet in enumerate(
            api.search(
                q=f"{term} -filter:retweets",  # Ignore retweets
                lang="en",
                result_type="recent",
                count=25,
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

        tweets.append(tweet)

    return tweets


def get_comprehend_analysis(term: str, tweets: list, result: list):
    """
    Gets analysis from Comprehend
    Returns all entities extracted from tweets
    """
    all_entities = []

    comprehend = boto3.client("comprehend")

    sentiments = comprehend.batch_detect_sentiment(
        TextList=tweets,
        LanguageCode="en"
    )
    entities = comprehend.batch_detect_entities(
        TextList=tweets,
        LanguageCode="en"
    )

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
            score = e["Score"]
            entity = e["Text"].strip().lower()
            type = e["Type"]

            output.append({
                "score": score,
                "entity": entity,
                "type": type
            })

            # Cleanse the entity
            entity = unidecode(entity)
            if entity_data_cleanse(entity, type, term):
                all_entities.append({
                    "score": score,
                    "entity": entity,
                    "type": type
                })

        result[index]["entities"] = output

    return all_entities


def invoke_neptune_lambda(term: str, entities: list):
    """
    Invokes the "AddTermToNeptune" lambda function
    """
    client = boto3.client("lambda")

    client.invoke(
        FunctionName=os.environ["ADD_TERM_TO_NEPTUNE_ARN"],
        InvocationType="Event",
        Payload=json.dumps({
            "term": term.upper(),  # Make it upper cased to keep it unique. Pokemon vs pokemon
            "entities": entities
        })
    )


def lambda_handler(event, context):
    term = event["body"].strip()
    result = []

    tweets = get_tweets(term, result)
    entities = get_comprehend_analysis(term, tweets, result)
    invoke_neptune_lambda(term, list(entities))

    return {
        'statusCode': 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(result)
    }
