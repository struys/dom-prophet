from py2neo import neo4j, cypher

DATABASE_SERVICE = 'http://localhost:7474/db/data/'

def get_event_nodes_for_yuv(yuv):
    """For a given user yuv, fetch the events that this user
    performed in order."""

    db = neo4j.GraphDatabaseService(DATABASE_SERVICE)

    query = """
            START
                a = node(*)
            MATCH
                a-[:ACTION]->b
            WHERE
                has(a.uuid)
                and a.uuid="%s"
            RETURN b""" % yuv

    results = cypher.execute(db, query)[0]

    if not results:
        return None

    events = []
    for event_outer in results:
        events.append(event_outer[0].get_properties())

    sorted_events = sorted(events, key=lambda event_dict: event_dict['timeStamp'], reverse=True)

    return sorted_events
