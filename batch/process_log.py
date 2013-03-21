import json
from py2neo import neo4j, cypher

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
graph_db.clear()

def create_nodes(lines):
	for index, line in enumerate(lines):
		last_node = None

		try:
			line['elements']
		except TypeError:
			# There's some weird [object Object] things in the log.
			continue

		for element in reversed(line['elements']):
			node_values = {}
			node_values['tagName'] = element['tagName']

			for name, values in element['attributes']:
				node_values[name] = values.split(' ')

			next = graph_db.create(node_values)[0]

			if last_node is not None:
				last_node.create_relationship_to(next, 'PARENT')

			last_node = next

for log_line in open('../log', 'r'):
	json_line = json.loads(log_line)
	create_nodes(json_line)

# Example query "Find all divs who's parent has a class container"
print cypher.execute(graph_db, "start a=node(*) match (a)-[:PARENT]->(b) where has(a.class) and a.tagName='DIV' and has(b.class) and any(class in a.class where class='container') return b.tagName, b.class")
