#!/usr/bin/env python
from flask import Flask, render_template, request, make_response, redirect, flash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from database.query_db import query_db
import os
import cloudinary_methods


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'jpg', 'jpeg'}
UPLOAD_FOLDER = './uploads'

# current directory
app = Flask(__name__, template_folder='./pages')
app.secret_key = "secret key"

MAX_MB = 10
#It will allow below 10MB contents only, you can change it
app.config['MAX_CONTENT_LENGTH'] = MAX_MB * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')

            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            #upload to cloudinary
            url = cloudinary_methods.upload(path)
            # add this url to database (backend job)
            print(url)

            print('File successfully uploaded')
            flash('File successfully uploaded')
            return redirect('/upload_media_details')
        else:
            print('Allowed file types are txt, pdf, jpg, jpeg')
            flash('Allowed file types are txt, pdf, jpg, jpeg')
            return redirect(request.url)


    html_code = render_template('index.html')
    response = make_response(html_code)
    return response

#     #request.form['customFileInput']


@app.route('/upload_media_details', methods=['GET', 'POST'])
def upload_media_details():
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

    html_code = render_template('upload_media_details.html')
    response = make_response(html_code)
    return response


@app.route('/thank_you', methods=['GET'])
def thank_you():
    html_code = render_template('thank_you.html')
    response = make_response(html_code)
    return response

@app.route('/gallery', methods=['GET'])
def gallery():
    results = query_db()
    print(results)
    html_code = render_template('gallery.html', \
        results = results)
    response = make_response(html_code)
    return response



