from flask import Flask, redirect, render_template, request, url_for, abort, Response, session
from flask_login import login_user, LoginManager, current_user, login_required, UserMixin, logout_user
from dbloader import connect_to_db
from authlib.integrations.flask_client import OAuth
from oauthlib.oauth2 import WebApplicationClient
from helper import (GOOGLE_CLIENT_ID,
                    GOOGLE_CLIENT_SECRET,
                    GOOGLE_DISCOVERY_URL, YANDEX_CLIENT_ID, YANDEX_CLIENT_SECRET, YANDEX_DISCOVERY_URL, YANDEX_REDIRECT_URI)
import requests
import json

conn, cur = connect_to_db()

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = WebApplicationClient(GOOGLE_CLIENT_ID)
app.config['SECRET_KEY'] = 'bruh'
oauth = OAuth(app)
clientYan = WebApplicationClient(YANDEX_CLIENT_ID)
yandex = oauth.register(
    name='yandex',
    client_id=YANDEX_CLIENT_ID,
    client_secret=YANDEX_CLIENT_SECRET,
    access_token_url='https://oauth.yandex.ru/token',
    authorize_url='https://oauth.yandex.ru/authorize',

)


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


@app.route('/')
def index():
    return render_template("login_with.html")


@app.route('/login_password', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT id, name, password, email FROM users WHERE name = %s", (username,))
        user_data = list(cur.fetchone())
        print(user_data)
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
            return redirect(url_for('account'))
    return render_template('login_password.html')

@app.route('/login_yandex', methods=['GET', 'POST'])
def login_yandex():
    yandex_auth_url = (
        'https://oauth.yandex.ru/authorize?response_type=code'
        f'&client_id={YANDEX_CLIENT_ID}&redirect_uri={YANDEX_REDIRECT_URI}'
    )
    return redirect(yandex_auth_url)

@app.route('/login_yandex/yandex_callback')
def yandex_callback():
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
    user_name = user_info.get('real_name', 'Имя пользователя не найдено')

    return f'Ваш токен: {token}<br>Ваше имя: {user_name}'


    response = requests.get("http://www.example.com/token")
    response.status_code
    print(f"DDDDDDDDDDDDDDDDDDDDD{response}")
    # token = yandex.authorize_access_token()
    # user_info = yandex.get('https://login.yandex.ru/info', token=token)
    # user = user_info.json()
    # print(user)
    return redirect(url_for('account'))
    # response = yandex.authorized_response()
    # if response is None or response.get('access_token') is None:
    #     return 'Access denied: reason={} error={}'.format(
    #         request.args['error_reason'],
    #         request.args['error_description']
    #     )
    # session['yandex_token'] = (response['access_token'], '')
    # user_info = yandex.get('https://login.yandex.ru/info')
    # return 'Logged in as: ' + user_info.data['login']
# def yandex_callback():
#     code = request.args.get('code')
#     token_url = YANDEX_DISCOVERY_URL
#     data = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'client_id': YANDEX_CLIENT_ID,
#         'client_secret': YANDEX_CLIENT_SECRET,
#         'redirect_uri': YANDEX_REDIRECT_URI
#     }
#     # response = requests.get(token_url) # ,data=data
#     # response.status_code
#     # print(f"DDDDDDDDDDDDDDDDDDDDD{response}")
#     # access_token = request.args.get('access_token')
#     # response = session.post(token_url, data=data)
#     # token_info = response.json()
#     # access_token = token_info['access_token']

#     # user_info_url = 'https://login.yandex.ru/info'
#     # headers = {'Authorization': f'OAuth {access_token}'}
#     # user_info_response = requests.post(user_info_url, headers=headers)
#     # user_info = user_info_response.json()
#     google_provider_cfg = requests.get("https://api.webmaster.yandex.net/v4/user").json()
#     print(google_provider_cfg)
#     real_name = request.args.get('real_name')
#     print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA{real_name}")
#     # session['user'] = {
#     #     'fio': user_info.get('real_name'),
#     #     'avatar': user_info.get('default_avatar_id')
#     # }

#     return redirect(url_for('account'))

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

@app.route("/login_gmail/callback")
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

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return f"Привет, {user['fio']}! <img src='https://avatars.yandex.net/get-yapic/{user['avatar']}/islands-200' alt='avatar'>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return "негры"


if __name__ == '__main__':
    # preload_db() # его нет
    app.run(host='0.0.0.0', port=5000, ssl_context=('certificate.pem', 'private_key.pem'))  # , ssl_context='adhoc')
