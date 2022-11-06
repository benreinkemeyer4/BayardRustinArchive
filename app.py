#!/usr/bin/env python
from flask import Flask, render_template, request, make_response, redirect, flash, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from database.query_db import query_db
from database.insert_db import insert_db
from database.query_singleitem_db import query_singleitem_db
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

media_url = ""

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
            #upload to cloudinary
            url = cloudinary_methods.upload(file)

            print(url)

            global media_url
            media_url = url


            print('File successfully uploaded')
            return redirect(url_for('upload_media_details'))
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
            "date_taken": request.form.get('date'),
            "submitter-email": request.form.get('submitter-email'),
            "tags": request.form.get('tags'),
            "title": request.form.get('title'),
            "description": request.form.get('description'),
            "media_url": media_url
        }
        print(submission)
        insert_db(submission)
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

@app.route('/admin_gallery', methods=['GET'])
def admin_gallery():
    results = query_db()
    print(results)
    html_code = render_template('admin_gallery.html', \
        results = results)
    response = make_response(html_code)
    return response


@app.route('/details', methods=['GET'])
def singleitemview():
    mediaid = request.args.get('mediaid')
    print(mediaid)
    results = query_singleitem_db(str(mediaid))

    result = results[0]

    print(result)

    result_dict = {
        "title": result[6],
        "desc": result[7],
        "submitter-name": result[1],
        "mediaurl": result[8],
        "tag": result[5]
    }
    html_code = render_template('singleitemview.html', result=result_dict)
    response = make_response(html_code)
    return response


@app.route('/admin_details', methods=['GET'])
def admin_singleitemview():
    mediaid = request.args.get('mediaid')
    print(mediaid)
    results = query_singleitem_db(str(mediaid))

    result = results[0]

    print(result)

    result_dict = {
        "title": result[6],
        "desc": result[7],
        "submitter-name": result[1],
        "mediaurl": result[8],
        "tag": result[5]
    }
    html_code = render_template('admin_singleitemview.html', result=result_dict)
    response = make_response(html_code)
    return response