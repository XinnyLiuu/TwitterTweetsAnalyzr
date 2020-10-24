from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph


def query_neptune(term: str, entities: list):
    """
    Creates vertices to graph term to entities
    """

    graph = Graph()
    connection = DriverRemoteConnection(
        'wss://test-instance-1.c6w4fir6wswm.us-east-1.neptune.amazonaws.com:8182/gremlin', 'g')

    g = graph.traversal().withRemote(connection)

    # Check if a vertex has been created for the term
    term_vertex = g.V().has("term", "value", term)
    term_vertex = term_vertex.next() if term_vertex.hasNext() else g.addV("term").property("value", term).next()

    # Create a vertex for each and link term to entity
    for e in entities:
        entity_vertex = g.addV("entity").property("value", e).next()
        g.V(term_vertex).addE("has_entity").to(entity_vertex).iterate()

    print(g.V().toList())


def lambda_handler(event, context):
    term = event["term"]
    entities = event["entities"]

    query_neptune(term, entities)

    return {
        "statusCode": 200
    }
