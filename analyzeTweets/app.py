import json
import os

import boto3
import tweepy
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph


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

        tweets.append(tweet)

    return tweets


def get_comprehend_analysis(term: str, tweets: list, result: list):
    """
    Gets analysis from Comprehend using boto3
    Returns all entities extracted from tweets
    """
    all_entities = set()

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
            entity = e["Text"]
            type = e["Type"]

            output.append({
                "score": score,
                "entity": entity,
                "type": type
            })

            # Ignore twitter handles and quantity, date
            if "@" not in entity and type != "QUANTITY" and type != "DATE":
                all_entities.add(entity)

        result[index]["entities"] = output

    return all_entities


def add_to_neptune(entities: list):
    """
    Creates a new node in Neptune if one does not exist and adds all entities to it
    """
    print(entities)

    graph = Graph()
    conn = DriverRemoteConnection("wss://test-instance-1.c6w4fir6wswm.us-east-1.neptune.amazonaws.com:8182/gremlin",
                                  "g")
    g = graph.traversal().withRemote(conn)

    print(g.V().toList())
    conn.close()


def lambda_handler(event, context):
    """
    Analyze tweets (with search term) with Comprehend
    """
    result = []

    tweets = get_tweets(event["body"], result)
    entities = get_comprehend_analysis(event["body"], tweets, result)
    add_to_neptune(entities)

    return {
        'statusCode': 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(result)
    }
