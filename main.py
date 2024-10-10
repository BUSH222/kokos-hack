import os
from login import app_login, User
from news import app_news
from flask import Flask, render_template, request, url_for, flash, redirect, abort, jsonify, session
from flask_login import login_user, LoginManager, login_required, UserMixin, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
import psutil
import time
from collections import deque
import requests
from werkzeug.utils import secure_filename
import json
from dbloader import connect_to_db
from settings_loader import get_processor_settings
from logger import log_event
from helper import (GOOGLE_CLIENT_ID,
                    GOOGLE_CLIENT_SECRET,
                    YANDEX_CLIENT_ID,
                    YANDEX_CLIENT_SECRET,
                    YANDEX_REDIRECT_URI)

conn, cur = connect_to_db()

UPLOAD_FOLDER = os.path.abspath('DATA2')
settings = get_processor_settings()
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

app = Flask(__name__)
app.register_blueprint(app_login)
app.register_blueprint(app_news)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'bruh'

config = []
login_manager = LoginManager(app)
login_manager.login_view = 'login'
conn, cur = connect_to_db()
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = WebApplicationClient(GOOGLE_CLIENT_ID)
app.config['SECRET_KEY'] = 'bruh'
request_timestamps = deque()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def track_requests():  # DONT TOUCH
    """Track the timestamp of each request."""
    global request_timestamps
    current_time = time.time()
    request_timestamps.append(current_time)
    while request_timestamps and request_timestamps[0] < current_time - 60:
        request_timestamps.popleft()


@login_manager.user_loader
def load_user(user_id):
    cur.execute("SELECT id, name, password FROM users WHERE id = %s AND role", (user_id, '%5%'))
    user_data = cur.fetchone()
    print(user_data)
    if user_data:
        return User(*user_data)
    return None



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
def main_page():
    top_three_posts = cur.execute("SELECT TOP 3 * FROM forum").fetchone()
    top_three_selling_posts = cur.execute("SELECT * FROM forum ORDER BY sales DESC")
    cur.execute("""SELECT your_timestamp
                FROM your_table
                ORDER BY ABS(TIMESTAMPDIFF(SECOND, your_timestamp, NOW())) ASC
                LIMIT 1;""")
    closest_game = cur.fetchone()
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
        cur.execute("SELECT profile_pic,name,fav_player,about_me,vk_acc FROM user WHERE id = %s", (usr_id,))
        profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = cur.fetchone()

        if vk_acc is None:
            vk_acc = "Не привязан"
        if telegram_acc is None:
            telegram_acc = "Не привязан"
    if request.method == 'POST':
        usr_input = request.json
        if usr_input["btn_type"] == "change_user_data":
            return {'re':'/account/change_account_data'}
    return render_template('account.html', profile_pic=profile_pic, name=name, fav_player=fav_player,
                           about_me=about_me, telegram_acc=telegram_acc, vk_acc=vk_acc)


@app.route('/account/change_account_data', methods=['POST', 'GET'])
@login_required
def change_user_data():
    """
    An endpoint parses user info from db than puts it inside text windows for editing.
    """
    allowed_keys = ['profile_pic', 'name', 'fav_player', 'about_me', 'vk_acc', 'telegram_acc']
    #profile_pic, name, fav_player, about_me, vk_acc, telegram_acc, error = '' * 6
    if request.method == 'GET':
        usr_id = current_user.id
        cur.execute("""SELECT profile_pic, name, fav_player, about_me, vk_acc, telegram_acc
                    FROM user
                    WHERE id = %s""", (usr_id,))
        profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = cur.fetchone()
        if vk_acc is None:
            vk_acc = "Не привязан"
        if telegram_acc is None:
            telegram_acc = "Не привязан"
    if request.method == 'POST':
        usr_id = current_user.id
        usr_input = request.json
        usr_input["telegram_acc"] = usr_input["telegram_acc"].replace(' ', '')
        if "@" not in usr_input["telegram_acc"]:
            usr_input["telegram_acc"] = "@" + usr_input["telegram_acc"]
        '''input name length control'''
        if usr_input["btn_type"] == "submit":
            for key in usr_input.keys():
                if key in allowed_keys:
                    cur.execute('UPDATE user SET %s = %s where id = %s', (key, usr_input[key], usr_id,))
        try:
            cur.commit()
        except Exception:
            error = "Не удалось загрузить изменения"
            cur.rollback()
    return render_template("change_user_data", profile_pic=profile_pic, name=name, fav_player=fav_player,
                           about_me=about_me, vk_acc=vk_acc, telegram_acc=telegram_acc, error=error)



@app.route('/shop',methods=['GET','POST'])
def shop():
    """
    GET:contains all shop items, but only names and photos so they can be placed in slides
    parses info from db and places it back via jinja
    POST:expects {"search":"string"} and makes new db request that is placed back in html form via jinja
    or redirects to itself with id and returns page of a certain item, when clicked
    So, lets get to it folks
    :return shop.html:
    """
    if request.method == "GET":
        items = cur.execute("SELECT id,picture,product_name FROM shop").fetchall()
        if request.args.get('id'):
            cur.execute("SELECT picture,product_name,"
                        "description,price FROM shop WHERE "
                        "product_name = %s", (request.args.get('id'),))
            items = cur.fetchall()
            return render_template("item.html",items)
        if request.args.get('search'):
            cur.execute("SELECT picture,product_name,"
                            "FROM shop WHERE "
                            "product_name = %s", (request.args.get('search'),))
            items = cur.fetchall()
            return render_template("item.html",items)
    if request.method == "POST":
        usr_input = request.json
        if "search" in usr_input.keys():
             return {'re': f'shop?search={usr_input["search"]}'}
        if "id" in usr_input.keys():
            return {'re':f'shop?id={usr_input["id"]}'}
    return render_template("shop.html",items)




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
    return jsonify({'ram': psutil.virtual_memory().percent,
                    'cpu': psutil.cpu_percent(),
                    'rpm': len(request_timestamps)})


if __name__ == "__main__":
    app.run(port=5003, debug=True, ssl_context=('certificate.pem', 'private_key.pem'))
    cur.close()
    conn.close()
