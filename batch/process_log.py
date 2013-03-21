import json
from py2neo import neo4j, cypher

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
graph_db.clear()

def create_nodes(lines):
    for line in lines:
        last_node = None
        for element in reversed(line['elements']):
            node_values = {}
            node_values['tagName'] = element['tagName']

            for name, values in element['attributes']:
                node_values[name] = values.split(' ')

            next = graph_db.create(node_values)[0]

            if last_node is not None:
                last_node.create_relationship_to(next, 'PARENT')

            last_node = next

for lines in open('../log', 'r'):
    create_nodes(json.loads(lines[:-1]))

# Example query "Find all divs who's parent has a class container"
print cypher.execute(graph_db, "start a=node(*) match (a)-[:PARENT]->(b) where has(a.class) and a.tagName='DIV' and has(b.class) and any(class in a.class where class='container') return b.tagName, b.class")
