#!/usr/bin/env python
import flask

# current directory
app = flask.Flask(__name__, template_folder='.')


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():

    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response



