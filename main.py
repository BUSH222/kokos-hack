from flask import Flask, redirect, render_template, request, url_for, abort, Response
from flask_login import login_user, LoginManager, current_user, login_required, UserMixin, logout_user
from oauthlib.oauth2 import WebApplicationClient
from helper import (GOOGLE_CLIENT_ID,
                    GOOGLE_CLIENT_SECRET,
                    GOOGLE_DISCOVERY_URL)
import requests
import json
from dbloader import connect_to_db
conn,cur = connect_to_db()
app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = WebApplicationClient(GOOGLE_CLIENT_ID)
app.config['SECRET_KEY'] = 'bruh'


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


@app.route('/')
def index():
    return render_template("login_with.html")


@app.route('/login_password', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
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
                    return redirect(url_for('dashboard'))
                else:
                    return "Invalid username or password"
            else:
                cur.execute('INSERT INTO users(name, password) VALUES (%s, %s) RETURNING (id, name, password, email)',
                            (username, password))
                conn.commit()
                new_user_data = cur.fetchone()[0]
                new_user = User(*new_user_data)
                login_user(new_user)
                return redirect(url_for('dashboard'))
        else:
            # Find out what URL to hit for Google login
            authorization_endpoint = google_provider_cfg["authorization_endpoint"]

            # Use library to construct the request for Google login and provide
            # scopes that let you retrieve user's profile from Google
            request_uri = client.prepare_request_uri(
                authorization_endpoint,
                redirect_uri=request.base_url + "/callback",
                scope=["openid", "email", "profile"],)
            return redirect(request_uri)
    return render_template('login_password.html')


@app.route('/login_gmail', methods=['GET', 'POST'])
def login_gmail():
    # Find out what URL to hit for Google login
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],)
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
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
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # if not users_email.endswith('@edu.misis.ru'):
    #     abort(403)

    user = User(id_=unique_id, name=users_name, email=users_email)
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email)
    login_user(user)
    return redirect(url_for("index"))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
def main_page():
    top_three_posts = cur.execute("SELECT TOP 3 * FROM forum").fetchone()
    top_three_selling_posts = cur.execute("SELECT * FROM forum ORDER BY sales DESC")
    closest_game = cur.execute("SELECT your_timestamp FROM your_table ORDER BY ABS(TIMESTAMPDIFF(SECOND, your_timestamp, NOW())) ASC LIMIT 1;").fetchone()
    return render_template("main_page.html",posts=top_three_posts,products= top_three_selling_posts,closest_game=closest_game)
