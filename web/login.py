from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import login_user, LoginManager, UserMixin
from dbloader import connect_to_db
from oauthlib.oauth2 import WebApplicationClient
from helper import (GOOGLE_CLIENT_ID,
                    GOOGLE_CLIENT_SECRET,
                    YANDEX_CLIENT_ID,
                    YANDEX_CLIENT_SECRET,
                    YANDEX_REDIRECT_URI)
import requests
import json

app_login = Blueprint('app_login', __name__)
conn, cur = connect_to_db()
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
login_manager = LoginManager(app_login)
login_manager.login_view = 'login'
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = WebApplicationClient(GOOGLE_CLIENT_ID)


class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    cur.execute("SELECT id, name, password, email FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    if user_data:
        return User(*user_data)
    return None


@app_login.route('/login', methods=['GET', 'POST'])
def login():
    """Choosing an entry method and logging in
        Redirects to account or google sign in"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT id, name, password, email FROM users WHERE name = %s", (username, ))
        user_data = cur.fetchone()

        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(*user_data)
                login_user(user)
                return 'OK'
            else:
                return "Invalid username or password"
        else:
            cur.execute('INSERT INTO users(name, password) VALUES (%s, %s) RETURNING id, name, password, email',
                        (username, password))
            conn.commit()
            new_user_data = cur.fetchone()
            new_user = User(*new_user_data)
            login_user(new_user)
    return render_template('login_password/login.html')


@app_login.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form["confirm_password"]

        cur.execute('SELECT 1 FROM users WHERE name = %s', (username,))
        if cur.fetchone() is not None:
            return 'Логин занят'
        elif confirm_password == password:
            cur.execute("INSERT INTO users (name, password) VALUES (%s, %s) \
                        RETURNING id, name, password, email", (username, password,))
            conn.commit()
            new_user_data = cur.fetchone()
            new_user = User(*new_user_data)
            login_user(new_user)
            return 'OK'  # redirect(url_for('account'))
        else:
            return 'Пароли не совпадают'

    return render_template('login_password/register.html')


@app_login.route('/login_yandex', methods=['GET', 'POST'])
def login_yandex():
    """Get authorization code Yandex sent back to you"""
    yandex_auth_url = (
        'https://oauth.yandex.ru/authorize?response_type=code'
        f'&client_id={YANDEX_CLIENT_ID}&redirect_uri={YANDEX_REDIRECT_URI}'
    )
    return redirect(yandex_auth_url)


@app_login.route('/login_yandex/yandex_callback')
def yandex_callback():
    """Enters user information from Yandex into the db"""
    code = request.args.get('code')
    token_response = requests.post(
        'https://oauth.yandex.ru/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': YANDEX_CLIENT_ID,
            'client_secret': YANDEX_CLIENT_SECRET,
            'redirect_uri': YANDEX_REDIRECT_URI
        }
    )
    token = token_response.json().get('access_token')
    user_info_response = requests.get(
        'https://login.yandex.ru/info',
        headers={'Authorization': f'OAuth {token}'}
    )
    user_info = user_info_response.json()
    user_name = user_info.get('display_name', 'absent')
    unique_id = user_info.get('id', 'absent')
    user_email = user_info.get('default_email', 'absent')
    user_pic = user_info.get('default_avatar_id', 'absent')

    if user_pic:
        user_pic_url = f"https://avatars.yandex.net/get-yapic/{user_pic}/islands-200"
    else:
        user_pic_url = "https://avatars.yandex.net/get-yapic/"

    cur.execute("SELECT id, name, password, email FROM users WHERE name = %s", (user_name,))
    user_data = cur.fetchone()
    if user_data:
        user = User(*user_data)
        login_user(user)
        return redirect(url_for('account'))
    else:
        cur.execute('INSERT INTO users(name, password, email, profile_pic) \
                    VALUES (%s, %s, %s, %s) RETURNING id, name, password, email',
                    (user_name, unique_id, user_email, user_pic_url))
        conn.commit()
        new_user_data = cur.fetchone()
        new_user = User(*new_user_data)
        login_user(new_user)
        return redirect(url_for('account'))


@app_login.route('/login_gmail', methods=['GET', 'POST'])
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


@app_login.route("/login_gmail/callback")
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
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        user_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        username = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    cur.execute("SELECT id, name, password, email FROM users WHERE name = %s", (username,))
    user_data = cur.fetchone()
    if user_data:
        user = User(*user_data)
        login_user(user)
        return redirect(url_for('account'))
    else:
        cur.execute(
            'INSERT INTO users(name, password, email, profile_pic) VALUES (%s, %s, %s, %s) '
            'RETURNING id, name, password, email',
            (username, unique_id, user_email, picture)
        )
        conn.commit()
        new_user_data = cur.fetchone()
        new_user = User(*new_user_data)
        login_user(new_user)
        return redirect(url_for('account'))


if __name__ == '__main__':
    app_login.run(host='0.0.0.0', port=5000, ssl_context=('certificate.pem', 'private_key.pem'))
    # , ssl_context='adhoc')
