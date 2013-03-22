"""
	ONLY run this batch if you intend on wiping away your data.
	This will delete *everything* in the the graph and rebuild the paths reading the log file.
"""


import json
from py2neo import neo4j, cypher

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
graph_db.clear()

base_node = graph_db.create({'tagName':'BASE'})[0]

def create_path(base_node, path_list):
	base_node.get_or_create_path(*path_list)

def upsert_to_graph(lines):
	"""Read each line and insert a new tree under the base node if the tree must be created, otherwise we
	update nodes as necessary with new relationships"""

	for index, line in enumerate(lines):
		traversal = []

		try:
			line['elements']
		except TypeError:
			continue

		# Create a 'traversal' by pairing relationships.
		for element in reversed(line['elements']):
			current_node = None

			# Node attributes that we have to either find
			# or create.
			node_values = {}

			# Element may not have tagName
			node_values['tagName'] = element.get('tagName', '')

			element_attributes = element.get('attributes', None)

			# if we have attributes, we are looking at an HTML element.
			if element_attributes:
				attrib_dict = dict(element_attributes)
				node_values['classString'] = attrib_dict.get('class', '')

			relationship = ('PARENT', node_values)

			traversal.append(relationship)

		create_path(base_node, traversal)

def fix_class_attributes():
	"""Get nodes that have a non empty class string. And set the classArray property on each one"""
	query = "START \
				to_modify = node(*) \
			WHERE \
				has(to_modify.classString) \
				and not(to_modify.classString='') \
			RETURN to_modify;"

	all_nodes = cypher.execute(graph_db, query)[0];

	for node in all_nodes:
		actual_node = node[0]
		# Get the properties for this node.
		node_properties = actual_node.get_properties()
		classString = node_properties['classString']

		# Set the classArray for this node.
		node_properties['classArray'] = classString.split(' ')
		
		actual_node.set_properties(node_properties)


for log_line in open('log', 'r'):
	json_line = json.loads(log_line)
	upsert_to_graph(json_line)

# Fix class attributes because we can't create classArray when upserting, because
# get_or_create_path is naive and treats nodes with arrays as unique nodes, even if the
# nodes' arrays are the same.
fix_class_attributes()
