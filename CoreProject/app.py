# from flask import Flask, render_template, request, jsonify, Response
# import backend.mongo as mongo
# import body
# import cv2
# import webbrowser

# username, email, password, disability, role, dob, slink, llink, glink, bio, gender = "", "", "", "", "", "", "", "", "", "", ""
# video_camera = None
# global_frame = None
# image, pred_img, original, crop_bg, label = None, None, None, None, None

# # safe: body module may implement lazy cap; only release if present
# if hasattr(body, "cap"):
#     try:
#         body.cap.release()
#     except Exception:
#         pass

# app = Flask(__name__)

# # Index Page
# @app.route('/index')
# def index():
#     if hasattr(body, "cap"):
#         try:
#             body.cap.release()
#         except Exception:
#             pass
#     return render_template('index.html')

# @app.route("/label")  # for label
# def label_text():
#     return jsonify(label)

# @app.route("/translate")  # for translation
# def translate():
#     # ensure camera started via body if available
#     try:
#         if hasattr(body, "get_cap"):
#             body.get_cap()
#         else:
#             body.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#     except Exception:
#         try:
#             body.cap = cv2.VideoCapture(0)
#         except Exception:
#             pass
#     txt = label_text()
#     return render_template('video_out.html', txt=txt.json)

# def gen_vid():     # Video Stream
#     global video_camera
#     global global_frame
#     global label
#     while True:
#         global image, pred_img, original, crop_bg, name
#         try:
#             image, pred_img, original, crop_bg, name = body.collectData()
#         except Exception:
#             image, pred_img, original, crop_bg, name = None, None, None, None, None

#         if name is not None:
#             label = name
#         else:
#             label = "--"

#         if image is None:
#             if global_frame is not None:
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')
#             else:
#                 continue

#         try:
#             frame = cv2.imencode('.jpg', image)[1].tobytes()
#         except Exception:
#             if global_frame is not None:
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')
#             continue

#         if frame is not None:
#             global_frame = frame
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         else:
#             if global_frame is not None:
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

# @app.route("/video")    # Video page
# def video():
#     return Response(gen_vid(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route("/about")    # About page
# def about():
#     if hasattr(body, "cap"):
#         try:
#             body.cap.release()
#         except Exception:
#             pass
#     return render_template('about_us.html')

# @app.route("/signup")   # Sign up page (GET)
# def sign_up():
#     if hasattr(body, "cap"):
#         try:
#             body.cap.release()
#         except Exception:
#             pass
#     return render_template('sign_up.html')

# @app.route("/")  # for login page
# def login():
#     if hasattr(body, "cap"):
#         try:
#             body.cap.release()
#         except Exception:
#             pass
#     return render_template('login.html', userinfo=None, accept=None)

# @app.route("/profile")      # Profile page
# def profile():
#     if hasattr(body, "cap"):
#         try:
#             body.cap.release()
#         except Exception:
#             pass
#     userinfo = mongo.show(email)
#     return render_template('profile.html', userinfo=userinfo)

# @app.route("/choice")       # Choice page
# def choice():
#     return render_template('choice.html')

# @app.route("/audio")        # Audio page
# def audio():
#     if hasattr(body, "cap"):
#         try:
#             body.cap.release()
#         except Exception:
#             pass
#     return render_template('audio_out.html')

# @app.route('/validate', methods=['POST'])
# def validate_sign():
#     try:
#         email = request.form.get('email', '')
#         password = request.form.get('password', '')
#         ok = mongo.validate(email, password)
#         if ok:
#             userinfo = mongo.show(email)
#             return render_template('login.html', accept="success", userinfo=userinfo, email=email, password=password)
#         else:
#             return render_template('login.html', accept="failed", userinfo=None, email=email, password=None)
#     except Exception as e:
#         # print full traceback to console for debugging
#         import traceback
#         traceback.print_exc()
#         # safe fallback UI
#         return render_template('login.html', accept="error", userinfo=None, email=None, password=None)

# @app.route('/signup', methods=['POST'])
# def getvalue():
#     global username, email, password, disability, role, gender
#     username = request.form.get('name', "").strip()
#     email = request.form.get('email', "").strip()
#     password = request.form.get('password', "").strip()
#     disability = request.form.get('inputDisability', "").strip()
#     role = request.form.get('inputRole', "").strip()
#     gender = request.form.get('gender', "").strip()

#     if username and email and password and disability and role:
#         # mongo.check returns True if email NOT present
#         if not mongo.check(email):
#             accept = "exist"
#             return render_template('sign_up.html', accept=accept, email=email, username=username)
#         else:
#             # directly create user (no OTP)
#             slink = ""
#             llink = ""
#             glink = ""
#             dob = ""
#             bio = ""
#             ok = mongo.insert(username, email, password, disability, role, dob, slink, glink, llink, bio, gender)
#             if ok:
#                 accept = "success"
#                 return render_template('sign_up.html', accept=accept, email=email, username=username)
#             else:
#                 accept = "failed"
#                 return render_template('sign_up.html', accept=accept, email=email, username=username)
#     else:
#         accept = "failed"
#         return render_template('sign_up.html', accept=accept, email=email, username=username)

# # removed OTP and forgot-password routes per request

# @app.route('/changepass', methods=['POST'])
# def changepass():
#     password = request.form['new_password']
#     email = request.form['chg_email']
#     mongo.updatepwd(email, password)
#     userinfo = mongo.show(email)
#     return render_template('profile.html', userinfo=userinfo)

# @app.route('/update', methods=['POST'])
# def update():
#     name = request.form['name']
#     email = request.form['up_email']
#     role = request.form['role']
#     disability = request.form['disability']
#     dob = request.form['dob']
#     bio = request.form['bio']
#     slink = request.form['slink']
#     llink = request.form['llink']
#     glink = request.form['glink']
#     gender = request.form['gender']
#     mongo.update(name, email, disability, role, dob, slink, llink, glink, bio, gender)
#     userinfo = mongo.show(email)
#     return render_template('profile.html', userinfo=userinfo)

# webbrowser.open('http://127.0.0.1:5000/')

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', threaded=True, port=5000, debug=False)


from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, session
import backend.mongo as mongo
import body
import cv2
import webbrowser

# ------------------ Global Variables ------------------
username, email, password, disability, role, dob, slink, llink, glink, bio, gender = "", "", "", "", "", "", "", "", "", "", ""
video_camera = None
global_frame = None
image, pred_img, original, crop_bg, label = None, None, None, None, None

# Release camera if body.cap exists
if hasattr(body, "cap"):
    try:
        body.cap.release()
    except Exception:
        pass

# ------------------ Flask App Setup ------------------
app = Flask(__name__)
app.secret_key = "your_secret_key"  # required for session

# ------------------ Routes ------------------

# Index Page
@app.route('/index')
def index():
    if hasattr(body, "cap"):
        try:
            body.cap.release()
        except Exception:
            pass
    userinfo = None
    if 'email' in session:
        userinfo = mongo.show(session['email'])
    return render_template('index.html', userinfo=userinfo)

# Label endpoint
@app.route("/label")
def label_text():
    return jsonify(label)

# Translation page
@app.route("/translate")
def translate():
    try:
        if hasattr(body, "get_cap"):
            body.get_cap()
        else:
            body.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    except Exception:
        try:
            body.cap = cv2.VideoCapture(0)
        except Exception:
            pass
    txt = label_text()
    return render_template('video_out.html', txt=txt.json)

# Video generator
def gen_vid():
    global video_camera, global_frame, label
    while True:
        global image, pred_img, original, crop_bg, name
        try:
            image, pred_img, original, crop_bg, name = body.collectData()
        except Exception:
            image, pred_img, original, crop_bg, name = None, None, None, None, None

        label = name if name is not None else "--"

        if image is None:
            if global_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')
            continue

        try:
            frame = cv2.imencode('.jpg', image)[1].tobytes()
        except Exception:
            if global_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')
            continue

        if frame is not None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Video page
@app.route("/video")
def video():
    return Response(gen_vid(), mimetype='multipart/x-mixed-replace; boundary=frame')

# About page
@app.route("/about")
def about():
    if hasattr(body, "cap"):
        try:
            body.cap.release()
        except Exception:
            pass
    return render_template('about_us.html')

# Signup page (GET)
@app.route("/signup")
def sign_up():
    if hasattr(body, "cap"):
        try:
            body.cap.release()
        except Exception:
            pass
    return render_template('sign_up.html')

# Login page (GET)
@app.route("/")
def login():
    if hasattr(body, "cap"):
        try:
            body.cap.release()
        except Exception:
            pass
    return render_template('login.html', userinfo=None, accept=None)

# Profile page
@app.route("/profile")
def profile():
    if hasattr(body, "cap"):
        try:
            body.cap.release()
        except Exception:
            pass
    userinfo = None
    if 'email' in session:
        userinfo = mongo.show(session['email'])
    return render_template('profile.html', userinfo=userinfo)

# Choice page
@app.route("/choice")
def choice():
    return render_template('choice.html')

# Audio page
@app.route("/audio")
def audio():
    if hasattr(body, "cap"):
        try:
            body.cap.release()
        except Exception:
            pass
    return render_template('audio_out.html')

# Features page
@app.route('/features')
def features():
    if hasattr(body, "cap"):
        try:
            body.cap.release()
        except Exception:
            pass
    userinfo = None
    if 'email' in session:
        userinfo = mongo.show(session['email'])
    return render_template('features.html', userinfo=userinfo)

# Home page
@app.route('/home')
def home():
    # safe release if body exposes a camera
    try:
        if hasattr(body, "cap") and body.cap is not None:
            body.cap.release()
    except Exception:
        pass
    userinfo = None
    try:
        userinfo = mongo.show(email) if email else None
    except Exception:
        userinfo = None
    return render_template('index.html', userinfo=userinfo)

# keep compatibility for links that may point to /index
@app.route('/index')
def index_redirect():
    return redirect(url_for('home'))

# ------------------ Form Actions ------------------

# Validate login (POST)
@app.route('/validate', methods=['POST'])
def validate_sign():
    try:
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        ok = mongo.validate(email, password)
        if ok:
            session['email'] = email  # store email in session
            return redirect(url_for('index'))  # redirect to home page
        else:
            return render_template('login.html', accept="failed", userinfo=None, email=email, password=None)
    except Exception:
        import traceback
        traceback.print_exc()
        return render_template('login.html', accept="error", userinfo=None, email=None, password=None)

# Signup form (POST)
@app.route('/signup', methods=['POST'])
def getvalue():
    global username, email, password, disability, role, gender
    username = request.form.get('name', "").strip()
    email = request.form.get('email', "").strip()
    password = request.form.get('password', "").strip()
    disability = request.form.get('inputDisability', "").strip()
    role = request.form.get('inputRole', "").strip()
    gender = request.form.get('gender', "").strip()

    if username and email and password and disability and role:
        if not mongo.check(email):
            accept = "exist"
            return render_template('sign_up.html', accept=accept, email=email, username=username)
        else:
            slink = ""
            llink = ""
            glink = ""
            dob = ""
            bio = ""
            ok = mongo.insert(username, email, password, disability, role, dob, slink, glink, llink, bio, gender)
            accept = "success" if ok else "failed"
            return render_template('sign_up.html', accept=accept, email=email, username=username)
    else:
        accept = "failed"
        return render_template('sign_up.html', accept=accept, email=email, username=username)

# Change password
@app.route('/changepass', methods=['POST'])
def changepass():
    password = request.form['new_password']
    email = request.form['chg_email']
    mongo.updatepwd(email, password)
    userinfo = mongo.show(email)
    return render_template('profile.html', userinfo=userinfo)

# Update profile
@app.route('/update', methods=['POST'])
def update():
    name = request.form['name']
    email = request.form['up_email']
    role = request.form['role']
    disability = request.form['disability']
    dob = request.form['dob']
    bio = request.form['bio']
    slink = request.form['slink']
    llink = request.form['llink']
    glink = request.form['glink']
    gender = request.form['gender']
    mongo.update(name, email, disability, role, dob, slink, llink, glink, bio, gender)
    userinfo = mongo.show(email)
    return render_template('profile.html', userinfo=userinfo)

# ------------------ Launch App ------------------
webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=5000, debug=False)
