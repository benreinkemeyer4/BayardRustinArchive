#!/usr/bin/env python
import flask
from flask import request, redirect, url_for
import sys

# current directory
app = flask.Flask(__name__, template_folder='./templates')


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET', 'POST'])
def index(): #has upload media function
    if flask.request.method == 'POST':
        print("UPLOAD CLICKED", file=sys.stdout)
        app.logger.info('UPLOAD CLICKED')

    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response

# @app.route('/', methods=['POST'])
# def upload_file():
#     print("UPLOAD CLICKED", file=sys.stdout)
#     app.logger.info('UPLOAD CLICKED')
#     #request.form['customFileInput']

@app.route('/submit', methods=['GET'])
def submit_form(): #form to fill out additional info
    html_code = flask.render_template('submitform.html')
    response = flask.make_response(html_code)
    return response




