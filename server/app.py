import json
from flask import Flask, request
app = Flask(__name__)

log_file_path = '../log'

@app.route('/log', methods=['POST'])
def write_to_log():
	with open(log_file_path, "ab") as log_file:
		log_file.write(request.form['log'] + '\n')

	return ''

@app.route('/log', methods=['GET'])	
def view_log():
	return open(log_file_path, 'r').read()

@app.route('/log/size', methods=['GET'])		
def log_length():
	with open(log_file_path) as log_file:
		for i, l in enumerate(log_file):
			pass

	return str(i + 1)

if __name__ == "__main__":
	app.run(debug = True)

