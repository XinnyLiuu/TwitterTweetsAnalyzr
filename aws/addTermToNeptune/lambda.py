import os

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph


def create_vertices(term: str, entities: list):
    """
    Creates vertices to graph term to entities
    """
    graph = Graph()
    connection = DriverRemoteConnection(
        f'wss://{os.environ["NEPTUNE_ENDPOINT"]}:8182/gremlin', 'g')

    g = graph.traversal().withRemote(connection)

    # Check if a vertex has been created for the term
    term_vertex = g.V().has("term", "value", term)
    term_vertex = term_vertex.next() if term_vertex.hasNext() else g.addV("term").property("value", term).next()

    # Create an entity vertex for each and link to term
    for e in entities:
        entity_vertex = g.V().has("entity", "value", e)
        entity_vertex = entity_vertex.next() if entity_vertex.hasNext() else \
            g.addV("entity") \
                .property("value", e["entity"]) \
                .property("score", e["score"]) \
                .property("type", e["type"]).next()

        g.V(term_vertex).addE("has_entity").to(entity_vertex).iterate()

    connection.close()


def lambda_handler(event, context):
    term = event["term"]
    entities = event["entities"]

    create_vertices(term, entities)

    return {
        "statusCode": 200
    }