import json
import os

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph


def get_graph(term: str):
    """
    Retrieves all the related entities a term has in Neptune
    """

    graph = Graph()
    connection = DriverRemoteConnection(
        f'wss://{os.environ["NEPTUNE_ENDPOINT"]}:8182/gremlin', 'g')

    g = graph.traversal().withRemote(connection)

    entities = g.V().has("term", "value", term.upper()).out("has_entity").valueMap(True).toList()
    connection.close()

    entity_names = set()  # Use this to filter out repeating entity names, `dedup()` does not working 100% of the time
    result = []
    for e in entities:
        data = {}

        if e["value"][0] in entity_names:
            continue
        else:
            entity_names.add(e["value"][0])

        for k, v in e.items():
            k_str = str(k)

            if "T." in k_str:
                name = k_str.split(".")[1]
                data[name] = v
                continue

            data[k] = v[0]

        result.append(data)

    return result


def lambda_handler(event, context):
    entities = get_graph(event["body"])

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps(entities)
    }
