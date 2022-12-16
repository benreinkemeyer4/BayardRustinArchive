#!/usr/bin/env python
from flask import Flask, render_template, request, make_response, redirect, flash, url_for, session
from database.query_db import query_db
from database.insert_db import insert_db
from database.query_singleitem_db import query_singleitem_db
from database.approve_sub import approve_sub
from database.unapprove_sub import unapprove_sub
from database.delete_db import delete_db
from database.edit_db import edit_db
import auth
import urllib.parse
import os
from flask_mail import Mail, Message
from flask_recaptcha import ReCaptcha # Import ReCaptcha object
from twilio.rest import Client
from dotenv import load_dotenv
from twilio.base.exceptions import TwilioRestException
import cloudinary_methods
import flask_wtf.csrf



ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}
UPLOAD_FOLDER = './uploads'

load_dotenv()
# current directory
app = Flask(__name__, template_folder='./pages')
app.secret_key = "secret key"

flask_wtf.csrf.CSRFProtect(app)


# 10 Mb limit
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


mail = Mail(app)
#mail config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# twilio config

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN= os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_VERIFY_SERVICE = os.environ.get('TWILIO_VERIFY_SERVICE')
SENDGRID_API_KEY= os.environ.get('SENDGRID_API_KEY')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['RECAPTCHA_ENABLE'] = True
app.config['RECAPTCHA_SITE_KEY'] = os.environ.get('RECAPTCHA_SITE_KEY')
app.config['RECAPTCHA_SECRET_KEY'] = os.environ.get('RECAPTCHA_SECRET_KEY')
recaptcha = ReCaptcha(app) # Create a ReCaptcha object by passing in 'app' as parameter



media_url = ""
media_type = ""

tags = ["1963 March on Washington for Jobs and Freedom", "Paper", "Pamphlet", "Leaflet", "Video", "Audio", "Essay", "Book", "Photograph", "Research", "Personal", "Interaction", "Story", "Speech", "Activism", "Gandhi", "Civil Rights", "LGBTQIA+ rights", "Intersectionality", "Labor Rights", "Voting Rights", "Union", "AFL-CIO", "Black Power", "Organizer", "Martin Luther King", "A. Philip Randolph", "Pacifism", "Quaker", "Protest", "Boycott", "Sit-in", "News", "Queer", "Africa", "Zambia", "Malcolm X", "President Obama", "Southern Christian Leadership Conference", "Freedom Riders", "Medal of Freedom", "Walter Naegle", "Bayard Rustin Center For Social Justice"]

tags.sort()

# parse youtube url and return unique key
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
    return None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes for authentication. -------------------
@app.route('/login', methods=['GET'])
def login():
    session['logged_in'] = True
    return auth.login()

@app.route('/login/callback', methods=['GET'])
def callback():
    return auth.callback()

@app.route('/logoutgoogle', methods=['GET'])
def logoutgoogle():
    session['logged_in'] = False
    return auth.logoutgoogle()

# ---------------------------------------------------
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

            extension = file.filename.rsplit('.', 1)[1].lower()
            print(extension)
            if extension == "pdf":
                type = "Document"
            else:
                type = "Image"


            #upload to cloudinary
            res = cloudinary_methods.upload(file)

            if res["error"] == False:
                url = res["result"]

                global media_url
                global media_type
                media_url = url
                media_type = type


                print('File successfully uploaded')
                return redirect(url_for('upload_media_details'))
            else:
                print(res["error"])
                return render_template('index.html', error_message="File unable to be uploaded to Cloudinary. Please try again.")

        else:
            print('Allowed file types are pdf, jpg, jpeg')
            flash('Allowed file types are pdf, jpg, jpeg')
            return redirect(request.url)


    html_code = render_template('index.html')
    response = make_response(html_code)
    return response



@app.errorhandler(413)
def error413(e):
    return render_template('index.html', error_message="Maximum file size is 10 MB (megabytes). Please upload a smaller file."), 413

@app.route('/upload_media_details', methods=['GET', 'POST'])
def upload_media_details():
    global tags
    message=""
    if request.method == 'POST':
        if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
            user_tags = []
            to_email = request.form.get('submitter-email')
            session['to_email'] = to_email

            status = send_verification(to_email)

            if not status:
                return render_template('upload_media_details.html', error_message="Unable to send verification code. Please resubmit the form again.")

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
            session['submission'] = submission
            return redirect(url_for('generate_verification_code'))
        else:
            message = 'Please fill out the ReCaptcha!' # Send error message


    html_code = render_template('upload_media_details.html', tags = tags, message=message)
    response = make_response(html_code)
    return response

def send_verification(to_email):
    try:
        verification = client.verify \
            .services(TWILIO_VERIFY_SERVICE) \
            .verifications \
            .create(to=to_email, channel='email')
        return verification.status
    except Exception:
        return False

@app.route('/video_instructions', methods=['GET', "POST"])
def video_instructions():
    if request.method == 'POST':
        return redirect(url_for('upload_video_details'))

    html_code = render_template('video_instructions.html')
    response = make_response(html_code)
    return response

# @app.route('/csrfattack', methods=['GET', "POST"])
# def csrf_attack():

#     html_code = render_template('csrfattack.html')
#     response = make_response(html_code)
#     return response

@app.route('/upload_video_details', methods=['GET', 'POST'])
def upload_video_details():
    global tags
    message=""
    if request.method == 'POST':
        if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
            user_tags = []

            to_email = request.form.get('submitter-email')
            print(to_email)
            session['to_email'] = to_email

            status = send_verification(to_email)

            if not status:
                return render_template('upload_video_details.html', error_message="Unable to send verification code. Please resubmit the form again.")

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

            session['submission'] = submission
            return redirect(url_for('generate_verification_code'))
        else:
            message = 'Please fill out the ReCaptcha!' # Send error message


    html_code = render_template('upload_video_details.html', tags = tags, message=message)
    response = make_response(html_code)
    return response

def send_verification(to_email):
    try:
        verification = client.verify \
            .services(TWILIO_VERIFY_SERVICE) \
            .verifications \
            .create(to=to_email, channel='email')
        return verification.status
    except Exception:
        return False

@app.route('/unauthorized_page', methods=['GET'])
def unauthorized_page():
    html_code = render_template('unauthorized_page.html')
    response = make_response(html_code)
    return response

@app.route('/verifyme', methods=['GET', 'POST'])
def generate_verification_code():
    to_email = session['to_email']

    error = None
    if request.method == 'POST':
        verification_code = request.form['verificationcode']

        status = check_verification_token(to_email, verification_code)

        if not status["error"]:
            if status["approved"]:
                submission = session['submission']
                print(submission)





                db_result = insert_db(submission)

                error = db_result["error"]

                if error:
                    if submission["media-type"] == "Video":
                        return render_template('upload_video_details.html', error_message="Unable to submit submission. Please resubmit the form again.")
                    else:
                        return render_template('upload_media_details.html', error_message="Unable to submit submission. Please resubmit the form again.")


                # send email to admin
                msg = Message(
                '[Bayard Rustin Archive] New Upload',
                sender ='bayardrustinarchive@gmail.com',
                recipients = ['bayardrustinarchive@gmail.com','brcsjqueerlib@gmail.com','rustincenter@gmail.com']
                )
                msg.body = 'There is a new upload to the Bayard Rustin Archive! View it here: https://bayard-rustin-archive-web.onrender.com/'
                mail.send(msg)

                return redirect('/thank_you')
            else:
                error = "Invalid verification code. Please try again."
                return render_template('verifypage.html', error = error)

        else:
            return redirect(url_for('unauthorized_page'))

    return render_template('verifypage.html', email = to_email)

def check_verification_token(phone, token):
    try:
        check = client.verify \
            .services(TWILIO_VERIFY_SERVICE) \
            .verification_checks \
            .create(to=phone, code=token)
        return {"approved":check.status == 'approved', "error":False}
    except TwilioRestException as e:
        return {"approved":False, "error":True}


@app.route('/thank_you', methods=['GET'])
def thank_you():
    html_code = render_template('thank_you.html')
    response = make_response(html_code)
    return response

@app.route('/gallery', methods=['GET'])
def gallery():
    status_results = query_db()

    if status_results["error"]:
        html_code = render_template('db_error.html')
        response = make_response(html_code)
        return response

    results = status_results["res"]
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
    status_results = query_db()

    if status_results["error"]:
        html_code = render_template('db_error.html')
        response = make_response(html_code)
        return response

    results = status_results["res"]

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
    status_results = query_singleitem_db(str(mediaid))

    if status_results["error"]:
        html_code = render_template('db_error.html')
        response = make_response(html_code)
        return response

    results = status_results["res"]


    if results is None or len(results) ==0:
            html_code = render_template('no_such_item.html')
            response = make_response(html_code)
            return response
    result = results[0]

    # prevents attcker from cycling through media ids to find unapproved media
    approved = result[8]
    if not approved:
        html_code = render_template('no_such_item.html')
        response = make_response(html_code)
        return response

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


    # non video
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
    if request.method == 'POST':
        mediaid = request.form.get('mediaid')

        # attacker tries to change mediaid when approving, deleting, etc.
        if (mediaid is None) or (mediaid.strip() == ''):
            redirect(url_for('unauthorized_page'))
        # delete media
        if request.form.get('btn_identifier') == 'delete':

            deleted = delete_db(str(mediaid))

            if deleted:
                return redirect('/admin_gallery')
            else:
                html_code = render_template('no_such_item.html')
                response = make_response(html_code)
                return response

        # approve media
        elif request.form.get('btn_identifier') == 'approve':
            approved = approve_sub(str(mediaid))
            if approved:
                return redirect('/admin_gallery')
            else:
                html_code = render_template('no_such_item.html')
                response = make_response(html_code)
                return response
        # unapprove media
        else:
            unapproved = unapprove_sub(str(mediaid))
            if unapproved:
                return redirect('/admin_gallery')
            else:
                html_code = render_template('no_such_item.html')
                response = make_response(html_code)
                return response

    # GET Request
    else:
        mediaid = request.args.get('mediaid')

        # attacker tries to change mediaid to empty
        if (mediaid is None) or (mediaid.strip() == ''):
            redirect(url_for('unauthorized_page'))

        status_results = query_singleitem_db(str(mediaid))

        if status_results["error"]:
            html_code = render_template('db_error.html')
            response = make_response(html_code)
            return response

        results = status_results["res"]

        if results is None or len(results) ==0:
            html_code = render_template('no_such_item.html')
            response = make_response(html_code)
            return response

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
            "submitter-email": result[4],
            "mediaurl": embed_url,
            "mediatype": mediatype,
            "tags": result[10],
            "mediaid":result[0],
            "submitter-pronouns":result[11],
            "approved": result[8]
        }
            html_code = render_template('admin_singleitemview.html', result_dict=result_dict, mediaid=mediaid)
            response = make_response(html_code)
            return response



        # non video media
        result_dict = {
            "title": result[5],
            "desc": result[6],
            "submitter-name": result[1],
            "submitter-email": result[4],
            "mediaurl": mediaurl,
            "mediatype": mediatype,
            "tags": result[10],
            "mediaid":result[0],
            "submitter-pronouns":result[11],
            "approved": result[8]
        }
        html_code = render_template('admin_singleitemview.html', result_dict=result_dict, mediaid=mediaid)
        response = make_response(html_code)
        return response

@app.route('/admin_edit', methods=['GET', 'POST'])
def admin_edit():
    global tags
    user_tags = []
    # displaying previously values
    mediaid = request.args.get('mediaid')

    # attacker tries to change mediaid to empty
    if (mediaid is None) or (mediaid.strip() == ''):
        redirect(url_for('unauthorized_page'))


    status_results = query_singleitem_db(str(mediaid))

    if status_results["error"]:
        html_code = render_template('db_error.html')
        response = make_response(html_code)
        return response

    results = status_results["res"]

    if results is None or len(results) ==0:
        html_code = render_template('no_such_item.html')
        response = make_response(html_code)
        return response
    if request.method == 'POST':
        # when they submit edits
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
            "mediaid": mediaid
        }
        edited = edit_db(submission)
        if edited:
            url = 'admin_details?mediaid=' + str(mediaid)
            return redirect(url) #change this to going back to original media id
        else:
            html_code = render_template('no_such_item.html')
            response = make_response(html_code)
            return response


    result = results[0]

    mediatype = result[9]
    mediaurl = result[7]
    result_dict=""
    if mediatype == "Video":
        youtube_id = video_id(mediaurl)
        embed_url = "https://www.youtube.com/embed/"+youtube_id

        ## IF WE DON'T DISPLAY THE VIDEO THEN WE DO NOT NEED A SEPARATE IF STATEMENT

        result_dict = {
        "title": result[5],
        "desc": result[6],
        "submitter-name": result[1],
        "submitter-email": result[4],
        "tags": result[10],
        "submitter-pronouns":result[11],
        "date_taken":result[2],
        "mediaurl": embed_url,
        "mediatype": mediatype,
    }
    else:
        result_dict = {
        "title": result[5],
        "desc": result[6],
        "submitter-name": result[1],
        "submitter-email": result[4],
        "tags": result[10],
        "submitter-pronouns":result[11],
        "date_taken":result[2],
        "mediaurl": mediaurl,
        "mediatype": mediatype
    }

    if result[10] == "":
        result_dict["tags"] = None


    html_code = render_template('admin_edit.html', tags = tags, result_dict = result_dict, mediaid=mediaid)
    response = make_response(html_code)
    return response


@app.route('/header', methods=['GET'])
def header():
    html_code = render_template('header.html', logged_in = session["logged_in"])
    response = make_response(html_code)
    return response

@app.route('/footer', methods=['GET'])
def footer():
    html_code = render_template('footer.html')
    response = make_response(html_code)
    return response

@app.route('/about_us', methods=['GET'])
def about_us():
    html_code = render_template('about_us.html')
    response = make_response(html_code)
    return response

# Add special icon gallery view
@app.route('/gallery_icon', methods=['GET'])
def gallery_icon():

    status_results = query_db()

    if status_results["error"]:
        html_code = render_template('db_error.html')
        response = make_response(html_code)
        return response

    results = status_results["res"]

    print(results)
    results_dict_list = []
    for result in results:
        mediatype = result[9]
        mediaurl = result[7]

        if mediatype == "Video":
            youtube_id = video_id(mediaurl)
            embed_url = "https://www.youtube.com/embed/"+youtube_id
            result_dict = {
                "title": result[5],
                "contributor": result[1],
                "uploaddate": result[3],
                "mediatype": result[9],
                "tags": result[10],
                "approved": result[8],
                "id": result[0],
                "mediaurl":embed_url
            }
        else:
            result_dict = {
                "title": result[5],
                "contributor": result[1],
                "uploaddate": result[3],
                "mediatype": result[9],
                "tags": result[10],
                "approved": result[8],
                "id": result[0],
                "mediaurl": mediaurl
            }
        results_dict_list.append(result_dict)
    html_code = render_template('gallery_icon.html', \
        results_dict_list = results_dict_list

        )
    response = make_response(html_code)
    return response

