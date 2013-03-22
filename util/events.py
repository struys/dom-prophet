from py2neo import neo4j, cypher

DATABASE_SERVICE = 'http://localhost:7474/db/data/'

def get_event_nodes_for_yuv(yuv):
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

    results = cypher.execute(db, query)
    return results
