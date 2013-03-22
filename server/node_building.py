import collections

from py2neo import neo4j

class HtmlPrintableNode(object):
    def __init__(self, node, depth):
        self.node = node
        self.depth = depth

    def write_head_tag(self, html_builder):
        html_builder.write('''
           <head>
              <link rel="stylesheet" type="text/css" media="all" href="http://s3-media4.ak.yelpcdn.com/assets/2/www/css/a5c276338038/www-pkg-en_US.css">
              <link rel="stylesheet" type="text/css" media="all" href="http://s3-media2.ak.yelpcdn.com/assets/2/www/css/273ebdc66076/homepage-en_US.css">
              <link rel="stylesheet" type="text/css" media="all" href="http://s3-media4.ak.yelpcdn.com/assets/2/www/css/40429fd12d50/new_search/search-en_US.css">

              <style>
                  * {
                      border: 1px solid #000 !important;
                      margin: 5px !important;
                      padding: 5px !important;
                  }
              </style>
            </head>
        ''')

    def build_str(self, html_builder):
        properties = self.node.get_properties()
        node_name = properties['tagName'].lower()
        class_string = properties.get('classString', '')
        tab = 2 * self.depth * ' '
        children = self.node.get_related_nodes(neo4j.Direction.OUTGOING, 'PARENT')

        if node_name != 'base':
            html_builder.write('{tab}<{node_name} class={class_string}'.format(
                tab=tab, node_name=node_name, class_string=class_string
            ))

            for property in properties:
                if property not in ['classArray', 'classString', 'tagName']:
                    html_builder.write(' {0}="{1}"'.format(property, properties[property]))

            html_builder.write('>\n')

            if node_name != 'html':
                html_builder.write('{tab}classString: {class_string}\n'.format(
                    tab=tab, class_string=class_string
                ))
            else:
                self.write_head_tag(html_builder)

        if children:
            for child in children:
                HtmlPrintableNode(child, self.depth + 1).build_str(html_builder)
        else:
            # Print counts for event nodes
            events = self.node.get_related_nodes(neo4j.Direction.OUTGOING, 'EVENT')
            event_types = collections.defaultdict(int)
            for event in events:
                event_types[event.get_properties()['eventType']] += 1

            for event_type in event_types:
                html_builder.write('{tab}{event_type} = {count}'.format(
                    tab=tab, event_type=event_type, count=event_types[event_type]
                ))

        if node_name != 'base':
            html_builder.write('{tab}</{node_name}>\n'.format(
                tab=tab, node_name=node_name
            ))

class FakeNode(object):
    def __init__(self, id, properties, children=[], events=[]):
        self.id = id
        self.properties = properties
        self.children = children
        self.events = events

    def get_properties(self):
        return self.properties

    def get_related_nodes(self, direction, relation):
        if direction == neo4j.Direction.OUTGOING and relation == 'PARENT':
            return self.children
        elif direction == neo4j.Direction.OUTGOING and relation == 'EVENT':
            return self.events

    def add_child(self, child):
        # Um wtf? why didn't self.children.append(child) work?
        children_copy = self.children[:]
        children_copy.append(child)
        self.children = children_copy

    def __repr__(self):
        return 'FakeNode({id}, [{children}])'.format(
            id=self.id,
            children=','.join(repr(child) for child in self.children)
        )

def build_tree(query_results):
    if not query_results:
        return None

    nodes = {}
    root_node_id = None

    for node in query_results:
        node = node[0]

        if node.id not in nodes:
            nodes[node.id] = FakeNode(
                node.id,
                node.get_properties(),
                events=node.get_related_nodes(neo4j.Direction.OUTGOING, 'EVENT')
            )

        while True:
            node_parent = node.get_related_nodes(neo4j.Direction.INCOMING, 'PARENT')[0]
            if node_parent.id not in nodes:
                nodes[node_parent.id] = FakeNode(
                    node_parent.id,
                    node_parent.get_properties(),
                    children=[nodes[node.id],],
                )
            else:
                nodes[node_parent.id].add_child(nodes[node.id])
                break

            node = node_parent
            if node.get_properties()['tagName'] == 'BASE':
                root_node_id = node.id
                break

    return nodes[root_node_id]
