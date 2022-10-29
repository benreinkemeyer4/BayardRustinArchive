#!/usr/bin/env python
from flask import Flask, render_template, request, make_response, redirect
import sys

# current directory
app = Flask(__name__, template_folder='./pages')


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("UPLOAD CLICKED", file=sys.stdout)

    html_code = render_template('index.html')
    response = make_response(html_code)
    return response

#     #request.form['customFileInput']


@app.route('/upload_media', methods=['GET', 'POST'])
def upload_media():
    if request.method == 'POST':
        submission = {
            "submitter-name": request.form.get('submitter-name'),
            "date": request.form.get('date'),
            "submitter-email": request.form.get('submitter-email'),
            "tags": request.form.get('tags'),
            "title": request.form.get('title'),
            "description": request.form.get('description')
        }
        print(submission)
        return redirect('/thank_you')

    html_code = render_template('upload_media.html')
    response = make_response(html_code)
    return response


@app.route('/thank_you', methods=['GET'])
def thank_you():
    html_code = render_template('thank_you.html')
    response = make_response(html_code)
    return response



