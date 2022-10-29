#!/usr/bin/env python
import flask
from flask import request, redirect, url_for
import sys

# current directory
app = flask.Flask(__name__, template_folder='./pages')


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if flask.request.method == 'POST':
        print("UPLOAD CLICKED", file=sys.stdout)

    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response

#     #request.form['customFileInput']

@app.route('/upload_media', methods=['GET'])
def upload_media():
    html_code = flask.render_template('upload_media.html')
    response = flask.make_response(html_code)
    return response




