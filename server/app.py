import os.path

from flask import Flask
from flask import abort
from flask import request
from flask import render_template
from flask import Response
from py2neo import neo4j, cypher

from util.css_to_cypher import calculate_neo4j_query

app = Flask(__name__)

DATABASE_SERVICE = 'http://localhost:7474/db/data/'


log_file_path = 'log'

@app.route('/log', methods=['POST'])
def write_to_log():
    with open(log_file_path, "ab") as log_file:
        log_file.write(request.form['log'] + '\n')

    return ''

@app.route('/log', methods=['GET'])
def view_log():
    index = request.args.get('index')
    if index is None:
        return open(log_file_path, 'r').read()

    index = int(index)

    with open(log_file_path) as log_file:
        for i, l in enumerate(log_file):
            if i == index:
                return l

@app.route('/log/size', methods=['GET'])
def log_length():
    with open(log_file_path) as log_file:
        for i, l in enumerate(log_file):
            pass

    return str(i + 1)

@app.route('/', methods=['GET'])
def index():
    '''Expects parameter "q"'''
    search_term = request.args.get('q', '')

    query = calculate_neo4j_query(search_term) if search_term else None

    results = None

    if query is not None:
        graph_db = neo4j.GraphDatabaseService(DATABASE_SERVICE)
        results = cypher.execute(graph_db, str(query))[0]

    env = {
        'search_term': search_term,
        'query': query,
        'results': [result[0]['classArray'] for result in results] if results else None
    }

    return render_template('index.htm', **env)

def node_helper(node, depth, string_wrapper):
    properties = node.get_properties()
    node_name = properties['tagName'].lower()
    class_string = properties.get('classString', '')

    if node_name != 'base':
        string_wrapper['s'] += 2 * depth * ' '
        string_wrapper['s'] += '<'
        string_wrapper['s'] += node_name
        string_wrapper['s'] += ' class="{0}"'.format(class_string)
        for property in properties:
            if property not in ['classArray', 'classString', 'tagName']:
                string_wrapper['s'] += ' {0}="{1}"'.format(property, properties[property])

        string_wrapper['s'] += '>'
        string_wrapper['s'] += '\n'

        if node_name != 'html':
            string_wrapper['s'] += 2 * depth * ' '
            string_wrapper['s'] += 'classString: {0}<br>'.format(class_string)
            string_wrapper['s'] += '\n'
        else:
            string_wrapper['s'] += '''
                <head>
                  <link rel="stylesheet" type="text/css" media="all" href="http://s3-media4.ak.yelpcdn.com/assets/2/www/css/a5c276338038/www-pkg-en_US.css">
                  <link rel="stylesheet" type="text/css" media="all" href="http://s3-media2.ak.yelpcdn.com/assets/2/www/css/273ebdc66076/homepage-en_US.css">
                  <style>
                      * {
                          border: 1px solid #000 !important;
                          margin: 5px !important;
                          padding: 5px !important;
                      }
                  </style>
                </head>
            '''

    for child in node.get_related_nodes(neo4j.Direction.OUTGOING, 'PARENT'):
        node_helper(child, depth + 1, string_wrapper)

    if node_name != 'base':
        string_wrapper['s'] += 2 * depth * ' '
        string_wrapper['s'] += '</{0}>'.format(node_name)
        string_wrapper['s'] += '\n'

@app.route('/html_nonsense', methods=['GET'])
def html_nonsense():
    graph_db = neo4j.GraphDatabaseService(DATABASE_SERVICE)
    results = cypher.execute(graph_db, "start a=node(*) where a.tagName='BASE' return a;")
    root = results[0][0][0]
    string_wrapper = { 's': '' }
    node_helper(root, 0, string_wrapper)

    return '<!doctype html>\n{0}'.format(string_wrapper['s'])

EXTENSIONS_TO_MIMETYPES = {
    '.js': 'application/javascript',
    '.css': 'text/css',
}

@app.route('/<path:path>')
def catch_all(path):
    if not app.debug:
        abort(404)
    try:
        # Make the paths relative to where this file is
        path = os.path.join(
            os.path.split(os.path.abspath(__file__))[0],
            path
        )

        with open(path, 'r') as f:
            extension = os.path.splitext(path)[1]
            return Response(
                f.read(),
                mimetype=EXTENSIONS_TO_MIMETYPES.get(extension, 'text/html')
            )
    except IOError:
        abort(404)
        return

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = True)

