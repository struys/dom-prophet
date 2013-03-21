import os.path

from flask import Flask
from flask import abort
from flask import request
from flask import render_template
from flask import Response

app = Flask(__name__)

log_file_path = '../log'

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
    return render_template('index.htm', search_term=request.args.get('q', ''))

EXTENSIONS_TO_MIMETYPES = {
    '.js': 'application/javascript',
    '.css': 'text/css',
}

@app.route('/<path:path>')
def catch_all(path):
    if not app.debug:
        abort(404)
    try:
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

