"""
    ONLY run this batch if you intend on wiping away your data.
    This deletes *everything* in the graph and rebuilds all paths from log file.
"""


import json
from py2neo import neo4j, cypher

graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
graph_db.clear()

base_node = graph_db.create({'tagName': 'BASE'})[0]

def create_path(base_node, path_list):
    base_node.get_or_create_path(*path_list)

def create_dom_path(path_name, path_elements):
    """Create event path traversal from HTML node to target element.

        Args:
            path_name: The url's pathname for this event on a target node.
            path_elements: Array of Element objects in path from HTML root to
            target element, ex:
                [..., {
                    'tagName': 'DIV',
                    'attributes': [['id': 'wrap'], ['class', 'lang-en']]
                }, ...]
        Returns:
            List describing the path from the HTML node to the target node, ex:
                [('PARENT', {tagName: 'HTML', classString: ''}), ...]
    """
    traversal_node = base_node
    # Is there a node matching our current node?
    for element in path_elements:
        # Element Attributes.
        element_tag_name = element.get('tagName')
        element_attrs = dict(element.get('attributes'))
        element_id = element_attrs.get('id', '')
        element_class = element_attrs.get('class', '')
        # Compare current element with traversal node.
        traversal_children = traversal_node.get_related_nodes(1, 'PARENT')
        traversal_child_match = False
        for traversal_child in traversal_children:
            child_properties = traversal_child.get_properties()
            child_id = child_properties.get('id', '')
            child_class = child_properties.get('classString', '')
            child_tag_name = child_properties.get('tagName')
            child_path_name = child_properties.get('pathName', '')
            expected_path_name = path_name if child_tag_name == 'HTML' else ''
            # Note: node_path_name either both '', or a path if tag_name="HTML".
            if (element_id == child_id and element_class == child_class and
                    element_tag_name == child_tag_name and expected_path_name == child_path_name):
                # The traversal_child matches our element: advance both.
                traversal_node = traversal_child
                traversal_child_match = True
                break
        # If we haven't found a child matching element for traversal_node,
        # insert element as new node under traversal node,
        # and continue inserting new nodes.
        if not traversal_child_match:
            # Create node for element.
            element_properties = {
                'tagName': element_tag_name,
                'id': element_id,
                'classString': element_class,
                'classArray': element_class.split(' ')
            }
            if element_tag_name == 'HTML':
                element_properties['pathName'] = path_name
            element_node = graph_db.create(element_properties)[0]
            # Add relationship from traversal_node to new child node.
            traversal_node.create_relationship_to(element_node, 'PARENT');
            traversal_node = element_node

    return traversal_node

def create_event_for_target_node(log_line, target_node):
    """Create event node for the target node of the interaction.
    
    Args:
        log_line: The log line from the file.
        target_node: The neo4j node representing the event target.

    Returns:
        event_node: The neo4j node representing the event.
    """
    # Create event node.
    event_properties = {
        'eventType': log_line['eventType'],
        'url': log_line['url'],
        'pathName': log_line.get('pathName', '')
    }
    event_node = graph_db.create(event_properties)[0]

    # Add relationship between target node and event node.
    target_node.create_relationship_to(event_node, 'EVENT')
    return event_node

def upsert_to_graph(lines):
    """Read each line and insert a new tree under the base node if the tree must
    be created, otherwise we update nodes as necessary with new relationships"""

    for index, log_line in enumerate(lines):
        # Process event described by log line.
        try:
            log_line['cookie']
            log_line['elements']
            log_line['eventType']
            log_line['url']
            log_line['pathName']
        except TypeError:
            continue

        ## TODO(wstyke): Do we want to keep track of counts of visits to the nodes
        ## in the traversal / or at the target node that has an action?
        ## Not unless queries are slow!

        # Create nodes leading to target node for event in graph db.
        target_node = create_dom_path(log_line['pathName'], reversed(log_line['elements']))

        # Create event node with relationship to target dom node.
        create_event_for_target_node(log_line, target_node)

for log_line in open('log', 'r'):
    json_line = json.loads(log_line)
    upsert_to_graph(json_line)
