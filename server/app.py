import cStringIO
import json
import os.path

from flask import Flask
from flask import abort
from flask import request
from flask import render_template
from flask import Response
from py2neo import neo4j, cypher

from node_building import build_tree
from node_building import HtmlPrintableNode

from util.css_to_cypher import calculate_neo4j_query
from util.events import get_event_nodes_for_yuv

app = Flask(__name__)

DATABASE_SERVICE = 'http://localhost:7474/db/data/'
LOG_FILE_PATH = 'log'

@app.route('/log', methods=['POST'])
def write_to_log():
    with open(LOG_FILE_PATH, "ab") as log_file:
        log_file.write(request.form['log'] + '\n')
    return ''

@app.route('/log', methods=['GET'])
def view_log():
    index = request.args.get('index')
    if index is None:
        return open(LOG_FILE_PATH, 'r').read()

    index = int(index)

    with open(LOG_FILE_PATH) as log_file:
        for i, l in enumerate(log_file):
            if i == index:
                return l

@app.route('/log/size', methods=['GET'])
def log_length():
    with open(LOG_FILE_PATH) as log_file:
        for i, l in enumerate(log_file):
            pass

    return str(i + 1)

@app.route('/', methods=['GET'])
def index():
    search_term = request.args.get('css', '')
    env = {
        'search_term': search_term,
        'tab': 'html',
    }

    return render_template('index.htm', **env)

@app.route('/metric', methods=['GET'])
def metric():
    search_term = request.args.get('css', '')

    query = calculate_neo4j_query(search_term) if search_term else None

    results = None
    percent_breakdown = None
    hit_count = None
    histogram = None

    if query is not None:
        graph_db = neo4j.GraphDatabaseService(DATABASE_SERVICE)
        results = cypher.execute(graph_db, str(query))[0]
        percent_breakdown = get_percentage_logged_in_vs_out(graph_db, results)

    children = []

    if results:
        hit_count = get_hit_counts(graph_db, results)        
        histogram = get_histogram(graph_db, results)

        for r in [result[0] for result in results]:
            related = r.get_single_related_node(neo4j.Direction.OUTGOING, 'PARENT')

            if related is None:
                continue

            selector = related['tagName'].lower()

            def has_id(selector):
                return 'id' in related and related['id'] is not None and related['id'] != ''

            if has_id(selector):
                selector += '#' + related['id']

            if len(related['classArray']) > 0 and related['classArray'][0] != '':
                if not has_id(selector):
                    selector += '.'
                selector += '.'.join(related['classArray'])

            children.append(selector)

    env = {
        'tab': 'metric',
        'search_term': search_term,
        'query': query,
        'percent_breakdown': percent_breakdown,
        'children': set(children),
        'hit_count': hit_count,
        'histogram': histogram,
    }

    return render_template('index.htm', **env)

@app.route('/simulator', methods=['GET'])
def simulator():
    search_user = request.args.get('yuv', '')

    if search_user != '':
        nodes = get_event_nodes_for_yuv(search_user)
    else:
        nodes = []

    env = {
        'tab': 'simulator',
        'search_user': search_user,
        'results': nodes
    }

    return render_template('index.htm', **env)

@app.route('/html_nonsense', methods=['GET'])
def html_nonsense():
    graph_db = neo4j.GraphDatabaseService(DATABASE_SERVICE)

    # If we have a search term we want to build a tree that only has those
    #  nodes
    search_term = request.args.get('q', '')
    if search_term:
        query = calculate_neo4j_query(search_term)
        results = cypher.execute(graph_db, query)
        root = build_tree(results[0])
    else:
        results = cypher.execute(graph_db, "start a=node(*) where has(a.tagName) and a.tagName='BASE' return a;")
        root = results[0][0][0]

    html_builder = cStringIO.StringIO()
    html_builder.write('<!doctype html>\n')
    if root:
        HtmlPrintableNode(root, 0).build_str(html_builder)
    else:
        html_builder.write('<html><body>No results.</body></html>')
    return html_builder.getvalue()

@app.route('/path_stats', methods=['GET'])
def path_stats():
    """Get statistics about events for a given path."""
    search_term = request.args.get('cssPath', '')
    query = calculate_neo4j_query(search_term) if search_term else None

    results = None
    percent_breakdown = None
    hit_count = None

    if query is not None:
        graph_db = neo4j.GraphDatabaseService(DATABASE_SERVICE)
        results = cypher.execute(graph_db, str(query))[0]
        percent_breakdown = get_percentage_logged_in_vs_out(graph_db, results)
        hit_count = get_hit_counts(graph_db, results)
        target_data = {
            'clickCount': hit_count['click'],
            'mouseenterCount': hit_count['mouseenter']
        }
        return json.dumps(target_data)

    abort(404)

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

def get_hit_counts(graph_db, results):
    return_events = {
        'mouseenter': 0,
        'click': 0
    }
    
    x = set([])
    
    for result in [r[0] for r in results]:
        events = result.get_related_nodes(neo4j.Direction.OUTGOING, 'EVENT')
        for event in events:            
            if event.id not in x:
                x.add(event.id)
                if event['eventType'] == 'mouseenter':
                    return_events['mouseenter'] += 1
                elif event['eventType'] == 'click':
                    return_events['click'] += 1

    return return_events


def get_histogram(graph_db, results):
    timestamps = {
        'mouseenter': set([]),
        'click': set([]),
    }
    
    x = set([])
    

    for result in [r[0] for r in results]:
        events = result.get_related_nodes(neo4j.Direction.OUTGOING, 'EVENT')
        for event in events:
            x.add(event.id)
            
            if event['eventType'] == 'mouseenter':
                timestamps['mouseenter'].add(event['timeStamp'])
            elif event['eventType'] == 'click':
                timestamps['click'].add(event['timeStamp'])
    
    
    
    
    all = timestamps['mouseenter'].union(timestamps['click'])
    
    
    if len(all) == 0:
        return None
    
    
    bucket_size = (max(all) - min(all))/20
    
    result = {
        'mouseenter': [],
        'click': [],
        'labels': []
    }
    
    if bucket_size==0:
        for i in range(0, 20):
            result['labels'].append('')
            result['mouseenter'].append(len(set([t for t in timestamps['mouseenter']])))
            result['click'].append(len(set([t for t in timestamps['click']])))
    else:
        for next in range(min(all), max(all), bucket_size):
            #result['labels'].append(str(next))
            result['labels'].append('')
            result['mouseenter'].append(len(set([t for t in timestamps['mouseenter'] if t < next])))
            result['click'].append(len(set([t for t in timestamps['click'] if t < next])))
        
     
    return result

def get_percentage_logged_in_vs_out(graph_db, results):
    return_val = {
        'logged_in': 0,
        'logged_out': 0
    }

    for result in [r[0] for r in results]:
            body_node = cypher.execute(graph_db, """
                start a=node({id})
                match b-[:PARENT*]->(a)
                where has(b.tagName) and b.tagName='BODY'
                return b
            """.format(id=result.id))[0]

            if len(body_node) == 0:
                continue

            body_node = body_node[0][0]

            if body_node:
                return_val['logged_in'] += 1 if 'logged-in' in body_node['classArray'] else 0
                return_val['logged_out'] += 1 if 'logged-out' in body_node['classArray'] else 0

    return return_val

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = True)

