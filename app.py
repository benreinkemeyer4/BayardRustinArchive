#!/usr/bin/env python
from flask import Flask, render_template, request, make_response, redirect, flash, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from database.query_db import query_db
from database.insert_db import insert_db
from database.query_singleitem_db import query_singleitem_db
from database.approve_sub import approve_sub
from database.delete_db import delete_db
import auth
import urllib.parse
import os
#from flask_mail import Mail, Message
#try 2 of sending mail
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib
# import ssl
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask_recaptcha import ReCaptcha # Import ReCaptcha object



import cloudinary_methods

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}
UPLOAD_FOLDER = './uploads'


# current directory
app = Flask(__name__, template_folder='./pages')
app.secret_key = "secret key"


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['RECAPTCHA_ENABLE'] = True
app.config['RECAPTCHA_SITE_KEY'] = '6LfwBSkjAAAAAEyt-PsS-GxKSfyVWT4jo882WD6R' # <-- Add your site key
app.config['RECAPTCHA_SECRET_KEY'] = '6LfwBSkjAAAAAFJf6CN8M2G-_NZm8AaN1pSjYdwm' # <-- Add your secret key
recaptcha = ReCaptcha(app) # Create a ReCaptcha object by passing in 'app' as parameter



media_url = ""
media_type = ""

tags = ["1963 March on Washington for Jobs and Freedom", "Paper", "Pamphlet", "Leaflet", "Video", "Audio", "Essay", "Book", "Photograph", "Research", "Personal", "Interaction", "Story", "Speech", "Activism", "Gandhi", "Civil Rights", "LGBTQIA+ rights", "Intersectionality", "Labor Rights", "Voting Rights", "Union", "AFL-CIO", "Black Power", "Organizer", "Martin Luther King", "A. Philip Randolph", "Pacifism", "Quaker", "Protest", "Boycott", "Sit-in", "News", "Queer", "Africa", "Zambia", "Malcolm X", "President Obama", "Southern Christian Leadership Conference", "Freedom Riders", "Medal of Freedom"]


def video_id(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urllib.parse.urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urllib.parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes for authentication. -------------------
@app.route('/login', methods=['GET'])
def login():
    return auth.login()

@app.route('/login/callback', methods=['GET'])
def callback():
    return auth.callback()

@app.route('/logoutapp', methods=['GET'])
def logoutapp():
    return auth.logoutapp()

@app.route('/logoutgoogle', methods=['GET'])
def logoutgoogle():
    return auth.logoutgoogle()

# ---------------------------------------------------
@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    #try 3: sendgrid doesnt work rn because certificate verify failed: unable to get local issuer certificate (_ssl.c:997)>
    # message = Mail(
    #     from_email='bayardrustinarchive@gmail.com',
    #     to_emails='kathyli4735@gmail.com',
    #     subject='Sending with Twilio SendGrid is easy',
    #     html_content='<strong>Even with Python</strong>')

    # #sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    # sg = SendGridAPIClient("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")
    # response = sg.send(message)
    # print(response.status_code, response.body, response.headers)
    #------try 3 end



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

            extension = file.filename.rsplit('.', 1)[1].lower()
            print(extension)
            if extension == "pdf":
                type = "Document"
            else:
                type = "Image"

            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            print(file_length)

            if file_length > 10000000:
                flash('Maximum file size is 10 MB (megabytes)')
                return redirect(request.url)
            else:
                file.seek(0)
                #upload to cloudinary
                url = cloudinary_methods.upload(file)

                global media_url
                global media_type
                media_url = url
                media_type = type


                print('File successfully uploaded')
                return redirect(url_for('upload_media_details'))
        else:
            print('Allowed file types are pdf, jpg, jpeg')
            flash('Allowed file types are pdf, jpg, jpeg')
            return redirect(request.url)


    html_code = render_template('index.html')
    response = make_response(html_code)
    return response

#     #request.form['customFileInput']


@app.route('/upload_media_details', methods=['GET', 'POST'])
def upload_media_details():
    global tags
    message=""
    if request.method == 'POST':
        if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
            user_tags = []
            for index in request.form.getlist('tags'):
                user_tags.append(tags[int(index)])
            submission = {
                "submitter-name": request.form.get('submitter-name'),
                "date_taken": request.form.get('date'),
                "submitter-email": request.form.get('submitter-email'),
                "submitter-pronouns": request.form.get('submitter-pronouns'),
                "tags": user_tags,
                "title": request.form.get('title'),
                "description": request.form.get('description'),
                "media_url": media_url,
                "media_type": media_type
            }

            print(submission)
            insert_db(submission)
            return redirect('/thank_you')
        else:
            message = 'Please fill out the ReCaptcha!' # Send error message


    html_code = render_template('upload_media_details.html', tags = tags, message=message)
    response = make_response(html_code)
    return response



@app.route('/video_instructions', methods=['GET', "POST"])
def video_instructions():
    if request.method == 'POST':
        return redirect(url_for('upload_video_details'))

    html_code = render_template('video_instructions.html')
    response = make_response(html_code)
    return response


@app.route('/upload_video_details', methods=['GET', 'POST'])
def upload_video_details():
    global tags
    message=""
    if request.method == 'POST':
        if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
            user_tags = []
            for index in request.form.getlist('tags'):
                user_tags.append(tags[int(index)])
            submission = {
                "submitter-name": request.form.get('submitter-name'),
                "date_taken": request.form.get('date'),
                "submitter-email": request.form.get('submitter-email'),
                "tags": user_tags,
                "title": request.form.get('title'),
                "description": request.form.get('description'),
                "media_url": request.form.get('media-url'),
                "media_type": "Video",
                "submitter-pronouns": request.form.get('submitter-pronouns'),

            }

            print(submission)
            insert_db(submission)
            return redirect('/thank_you')
        else:
            message = 'Please fill out the ReCaptcha!' # Send error message


    html_code = render_template('upload_video_details.html', tags = tags, message=message)
    response = make_response(html_code)
    return response







    html_code = render_template('upload_media_details.html', tags = tags)
    response = make_response(html_code)
    return response



@app.route('/unauthorized_page', methods=['GET'])
def unauthorized_page():
    html_code = render_template('unauthorized_page.html')
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
    results_dict_list = []
    for result in results:
        result_dict = {
            "title": result[5],
            "contributor": result[1],
            "uploaddate": result[3],
            "mediatype": result[9],
            "tags": result[10],
            "approved": result[8],
            "id": result[0]
        }
        results_dict_list.append(result_dict)
    html_code = render_template('gallery.html', \
        results_dict_list = results_dict_list

        )
    response = make_response(html_code)
    return response

@app.route('/admin_gallery', methods=['GET'])
def admin_gallery():
    # id, name, date created, date submitted, email, title, description, media url, approved, media_type, tags
    # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    username = auth.authenticate()
    results = query_db()
    print(results)

    results_dict_list = []
    for result in results:
        result_dict = {
            "title": result[5],
            "contributor": result[1],
            "uploaddate": result[3],
            "mediatype": result[9],
            "tags": result[10],
            "approved": result[8],
            "id": result[0]
        }
        results_dict_list.append(result_dict)


    html_code = render_template('admin_gallery.html', \
        results_dict_list = results_dict_list)
    response = make_response(html_code)
    return response


@app.route('/details', methods=['GET'])
def singleitemview():
    mediaid = request.args.get('mediaid')
    print(mediaid)
    results = query_singleitem_db(str(mediaid))

    result = results[0]

    mediatype = result[9]
    mediaurl = result[7]

    if mediatype == "Video":
        youtube_id = video_id(mediaurl)
        embed_url = "https://www.youtube.com/embed/"+youtube_id

        result_dict = {
        "title": result[5],
        "desc": result[6],
        "submitter-name": result[1],
        "mediaurl": embed_url,
        "mediatype": mediatype,
        "tags": result[10],
        "mediaid":result[0]
    }
        html_code = render_template('singleitemview.html', result_dict=result_dict)
        response = make_response(html_code)
        return response



    result_dict = {
            "title": result[5],
            "desc": result[6],
            "submitter-name": result[1],
            "mediaurl": mediaurl,
            "mediatype": mediatype,
            "tags": result[10],
            "mediaid":result[0]
        }
    html_code = render_template('singleitemview.html', result_dict=result_dict)
    response = make_response(html_code)
    return response



@app.route('/admin_details', methods=['GET', 'POST'])
def admin_singleitemview():
    username = auth.authenticate()
    if request.method == 'POST':
        if request.form.get('btn_identifier') == 'delete':
            mediaid = request.form.get('mediaid')
            delete_db(str(mediaid))
            return redirect('/admin_gallery')
        else:
            mediaid = request.form.get('mediaid')
            approve_sub(str(mediaid))
            return redirect('/admin_gallery')

    else:

        mediaid = request.args.get('mediaid')
        results = query_singleitem_db(str(mediaid))

        result = results[0]
        print(result)

        mediatype = result[9]
        mediaurl = result[7]

        if mediatype == "Video":
            youtube_id = video_id(mediaurl)
            embed_url = "https://www.youtube.com/embed/"+youtube_id

            result_dict = {
            "title": result[5],
            "desc": result[6],
            "submitter-name": result[1],
            "submitter-email": result[4],
            "mediaurl": embed_url,
            "mediatype": mediatype,
            "tags": result[10],
            "mediaid":result[0],
            "submitter-pronouns":result[11]
        }
            html_code = render_template('admin_singleitemview.html', result_dict=result_dict)
            response = make_response(html_code)
            return response




        result_dict = {
            "title": result[5],
            "desc": result[6],
            "submitter-name": result[1],
            "submitter-email": result[4],
            "mediaurl": mediaurl,
            "mediatype": mediatype,
            "tags": result[10],
            "mediaid":result[0],
            "submitter-pronouns":result[11]
        }
        html_code = render_template('admin_singleitemview.html', result_dict=result_dict)
        response = make_response(html_code)
        return response

@app.route('/header', methods=['GET'])
def header():
    html_code = render_template('header.html')
    response = make_response(html_code)
    return response

