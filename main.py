import os

from flask import Flask, render_template, request, url_for, flash, redirect, abort, jsonify
from flask_login import login_user, LoginManager, login_required, UserMixin, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
import psutil
from helper import (GOOGLE_CLIENT_ID,
                    GOOGLE_CLIENT_SECRET,
                    GOOGLE_DISCOVERY_URL)
import requests
from werkzeug.utils import secure_filename
import json
from dbloader import connect_to_db
from settings_loader import get_processor_settings
from logger import log_event

conn, cur = connect_to_db()

UPLOAD_FOLDER = os.path.abspath('DATA2')
settings = get_processor_settings()
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

config = []
login_manager = LoginManager(app)
login_manager.login_view = 'login'
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = WebApplicationClient(GOOGLE_CLIENT_ID)
app.config['SECRET_KEY'] = 'bruh'


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    cur.execute("SELECT id, name, password FROM users WHERE id = %s AND role", (user_id, '%5%'))
    user_data = cur.fetchone()
    print(user_data)
    if user_data:
        return User(*user_data)
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        change = ''
        usr_input = request.json
        if usr_input["btn_type"] == "use_password":
            username = request.form['username']
            password = request.form['password']
            cur.execute("SELECT id, name, password FROM users WHERE id = %s AND role", (username))
            user_data = cur.fetchone()

            if user_data:
                if user_data[2] == password and len(password) < 32:
                    user = User(*user_data)
                    login_user(user)
                    return redirect(url_for('account'))
                else:
                    change = "Invalid username or password"
            else:
                cur.execute('INSERT INTO users(name, password) VALUES (%s, %s) RETURNING (id, name, password, email)',
                            (username, password))
                conn.commit()
                new_user_data = cur.fetchone()[0]
                new_user = User(*new_user_data)
                login_user(new_user)
                return redirect(url_for('account'))
        elif usr_input["btn_type"] == "use_google":
            # Find out what URL to hit for Google login
            authorization_endpoint = google_provider_cfg["authorization_endpoint"]
            # Use library to construct the request for Google login and provide
            # scopes that let you retrieve user's profile from Google
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=request.base_url + "/callback",
                scope=["openid", "email", "profile"], )
            return redirect(request_uri)

    return render_template('login.html', change=change)


@app.route("/login_gmail/callback")
def g_callback():
    """Get authorization code Google sent back to you"""
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        username = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # user = User(username=username, password=unique_id, email=users_email)
    cur.execute("SELECT id, name, password, email FROM users WHERE name = %s", (username,))
    user_data = cur.fetchone()
    if user_data:
        # if not User.get(unique_id):
        # User.create(unique_id, users_name, users_email)
        user = User(*user_data)
        login_user(user)
    else:
        cur.execute('INSERT INTO users(name, password, email) VALUES (%s, %s, %s) RETURNING id, name, password, email',
                    (username, unique_id, users_email))
        conn.commit()
        new_user_data = cur.fetchone()
        new_user = User(*new_user_data)
        login_user(new_user)
    return redirect(url_for('account'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
def main_page():
    top_three_posts = cur.execute("SELECT TOP 3 * FROM forum").fetchone()
    top_three_selling_posts = cur.execute("SELECT * FROM forum ORDER BY sales DESC")
    closest_game = cur.execute(
        "SELECT your_timestamp FROM your_table ORDER BY ABS(TIMESTAMPDIFF(SECOND, your_timestamp, NOW())) ASC LIMIT 1;").fetchone()
    return render_template("main_page.html", posts=top_three_posts, products=top_three_selling_posts,
                           closest_game=closest_game)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    An endpoint with all of a user data.
    """
    profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = '' * 5
    if request.method == 'GET':
        usr_id = current_user.id
        profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = cur.execute(
            f"SELECT profile_pic,name,fav_player,about_me,vk_acc FROM user WHERE id = %s", (usr_id,)).fetchall()

        if vk_acc == None: vk_acc = "Не привязан"
        if telegram_acc == None: telegram_acc = "Не привязан"
    if request.method == 'POST':
        usr_input = request.json
        if usr_input["btn_type"] == "change_user_data":
            return redirect(url_for('change_user_data'))
    return render_template('account.html', profile_pic=profile_pic, name=name, fav_player=fav_player, about_me=about_me,
                           telegram_acc=telegram_acc, vk_acc=vk_acc)


@app.route('/account/change_account_data', methods=['POST', 'GET'])
@login_required
def change_user_data():
    """
    An endpoint parses user info from db than puts it inside text windows for editing.
    """
    allowed_keys = ['profile_pic', 'name', 'fav_player', 'about_me', 'vk_acc', 'telegram_acc']
    profile_pic, name, fav_player, about_me, vk_acc, telegram_acc, error = '' * 6
    if request.method == 'GET':
        usr_id = current_user.id
        profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = cur.execute(
            f"SELECT profile_pic,name,fav_player,about_me,vk_acc,telegram_acc FROM user WHERE id = %s",
            (usr_id,)).fetchall()
        if vk_acc == None: vk_acc = "Не привязан"
        if telegram_acc == None: telegram_acc = "Не привязан"
    if request.method == 'POST':
        usr_id = current_user.id
        usr_input = request.json
        usr_input["telegram_acc"] = usr_input["telegram_acc"].replace(' ', '')
        if "@" not in usr_input["telegram_acc"]: usr_input["telegram_acc"] = "@" + usr_input["telegram_acc"]
        '''input name length control'''
        if usr_input["btn_type"] == "submit":
            for key in usr_input.keys():
                if key in allowed_keys: cur.execute(f'UPDATE user SET %s = %s where id = %s',
                                                    (key, usr_input[key], usr_id,))
        try:
            cur.commit()
        except Exception:
            error = "Не удалось загрузить изменения"
    return render_template("change_user_data", profile_pic=profile_pic, name=name, fav_player=fav_player,
                           about_me=about_me, vk_acc=vk_acc, telegram_acc=telegram_acc, error=error)


@app.route("/forum/new-post")
def forum_new_post():
    if 'file' not in request.files:
        log_event('No file part', 20)
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        log_event('No selected file', 20)
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        upload_url = settings["asset_delivery_ip"]
        # Prepare the files dictionary for the POST request
        files = {'file': (file.name, file.stream, file.mimetype)}
        # Send the POST request to the other microservice
        data = {'img_name': filename}
        response = requests.post(upload_url, files=files, data=data)
        print(response.status_code)
        if response.status_code == 200:
            log_event("image upload success", 10)
            return 'Success', 200
        else:
            log_event("image upload error", 30, data=data, files=files)
            return 'Failed to upload image', 500


@app.route("/news/new-story")
@login_required
def story_new_post():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_url = settings["asset_delivery_ip"]
        # Prepare the files dictionary for the POST request
        files = {'file': (file.name, file.stream, file.mimetype)}
        # Send the POST request to the other microservice
        data = {'img_name': filename}
        response = requests.post(upload_url, files=files, data=data)
        print(response.status_code)
        if response.status_code == 200:
            log_event("image upload success", 10)
            return 'Success', 200
        else:
            log_event("image upload error", 30, data=data, files=files)
            return 'Failed to upload image', 500


@app.route('/main_server_status', methods=['GET'])
def main_server_status():
    """
    Shows the current RAM and CPU usage of the server, can only be accessed by localhost ips
    Returns:
        abort(403): accessed from the wrong ip
        json: {'ram': , 'cpu': ) ram and cpu usage percent with a comment
    """
    allowed_ips = settings['allowed_ips']
    if request.remote_addr not in allowed_ips:
        return abort(403)
    return jsonify({'ram': psutil.virtual_memory().percent, 'cpu': psutil.cpu_percent()})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
    cur.close()
    conn.close()
