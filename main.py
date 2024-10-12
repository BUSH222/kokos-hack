import os
from login import app_login, User
from forum import app_forum
from flask import Flask, render_template, request, url_for, flash, redirect, abort, jsonify, session
from flask_login import login_user, LoginManager, login_required, UserMixin, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from collections import deque
import time
import psutil
import requests
from werkzeug.utils import secure_filename
from secrets import token_urlsafe
import json
from dbloader import connect_to_db
from settings_loader import get_processor_settings
from logger import log_event
from helper import GOOGLE_CLIENT_ID

conn, cur = connect_to_db()

UPLOAD_FOLDER = os.path.abspath('DATA2')
settings = get_processor_settings()
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

app = Flask(__name__)
app.register_blueprint(app_login)
app.register_blueprint(app_forum)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = token_urlsafe(16)

config = []
login_manager = LoginManager(app)
login_manager.login_view = 'login'
conn, cur = connect_to_db()
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


request_timestamps = deque()

@app.before_request
def track_requests():
    """Track the timestamp of each request."""
    global request_timestamps
    current_time = time.time()
    request_timestamps.append(current_time)
    while request_timestamps and request_timestamps[0] < current_time - 60:
        request_timestamps.popleft()


@login_manager.user_loader
def load_user(user_id):
    cur.execute("SELECT id, name, password, email FROM users WHERE id = %s", (user_id,))
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
    return render_template("index/index.html", posts=top_three_posts, products=top_three_selling_posts,
                           closest_game=closest_game)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    An endpoint with all of a user data.
    """
    profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = '', '', '', '', '', ''
    if request.method == 'GET':
        usr_id = current_user.id
        cur.execute("SELECT profile_pic, name, fav_player, about_me, vk_acc, telegram_acc FROM users WHERE id = %s", (usr_id,))
        profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = cur.fetchone()

        if vk_acc is None:
            vk_acc = "Не привязан"
        if telegram_acc is None:
            telegram_acc = "Не привязан"
    if request.method == 'POST':
        usr_input = request.json
        if usr_input["btn_type"] == "change_user_data":
            return {'re': '/account/change_account_data'}
    return render_template('account/account.html', profile_pic=profile_pic, name=name, fav_player=fav_player,
                           about_me=about_me, telegram_acc=telegram_acc, vk_acc=vk_acc)


@app.route('/account/change_account_data', methods=['POST', 'GET'])
@login_required
def change_user_data():
    """
    An endpoint parses user info from db than puts it inside text windows for editing.
    """
    allowed_keys = ['profile_pic', 'name', 'fav_player', 'about_me', 'vk_acc', 'telegram_acc']
    # profile_pic, name, fav_player, about_me, vk_acc, telegram_acc, error = '' * 6
    if request.method == 'GET':
        usr_id = current_user.id
        cur.execute("""SELECT profile_pic, name, fav_player, about_me, vk_acc, telegram_acc
                    FROM users
                    WHERE id = %s""", (usr_id,))
        profile_pic, name, fav_player, about_me, vk_acc, telegram_acc = cur.fetchone()
        if vk_acc is None:
            vk_acc = "Не привязан"
        if telegram_acc is None:
            telegram_acc = "Не привязан"
        return render_template("account/change_user_data.html", profile_pic=profile_pic, name=name, fav_player=fav_player,
                               about_me=about_me, vk_acc=vk_acc, telegram_acc=telegram_acc)

    if request.method == 'POST':
        usr_id = current_user.id
        usr_input = request.json
        usr_input["telegram_acc"] = usr_input["telegram_acc"].replace(' ', '')
        if "@" not in usr_input["telegram_acc"]:
            usr_input["telegram_acc"] = "@" + usr_input["telegram_acc"]

        try:
            if usr_input["btn_type"] == "submit":
                for key in usr_input.keys():
                    if key in allowed_keys:
                        query = "UPDATE users SET %s = %s WHERE id = %s"
                        cur.execute(query, (key,usr_input[key], usr_id))
            conn.commit()
        except Exception:
            conn.rollback()
            print("БАЗЫ ДАЛИ ЗАЗЫ " * 5)
            abort(304)


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    """
    GET:contains all shop items, but only names and photos so they can be placed in slides
    parses info from db and places it back via jinja
    POST:expects ?search=string and makes new db request that is placed back in html form via jinja
    or redirects to itself with id and returns page of a certain item, when clicked
    So, lets get to it folks
    :return shop.html:
    """
    if request.method == "GET":
        items = cur.execute("SELECT id,picture,product_name FROM shop").fetchall()
        if request.args.get('search'):
            cur.execute("""SELECT picture,product_name,
                            FROM shop
                            WHERE product_name LIKE %s""", (f"%{request.args.get('search')}%",))
            items = cur.fetchall()
            return render_template("shop/shop.html", items)
        return render_template("shop/shop.html", items)
    if request.method == "POST":
        usr_input = request.json
        if usr_input['btn_type'] == "search":
            return {'re': f'shop?search={usr_input["search"]}'}
        if "id" in usr_input.keys():
            return {'re': f'shop?id={usr_input["id"]}'}


@app.route('/news', methods=['GET', 'POST'])
def news():
    """
    GET:contains all news items, but only names and photos so they can be placed in slides
    parses info from db and places it back via jinja
    POST:this b requests json that contains "find" field with "yes", after which it redirects
    you to itself but with all search options that are inside json that comes with find field
    i.e. tags,search,news_time etc.
    :return news.html OR if it gets an id option, returns one_new.html:
    """
    if request.method == "GET":
        exec_string = """SELECT * FROM news WHERE"""
        filter_params = []
        if request.args.get('search'):
            if exec_string.split(' ')[0] != "AND":
                exec_string += " AND "
            exec_string += "WHERE title LIKE %s OR news_text LIKE %s"
            filter_params.append(f"%{request.args.get('search')}%")
            filter_params.append(f"%{request.args.get('search')}%")
        if request.args.get('news_time'):
            if exec_string.split(' ')[0] != "AND":
                exec_string += " AND "
            exec_string += "WHERE news_time = %s"
            filter_params.append({request.args.get('news_time')})
        if request.args.get('tags'):
            if exec_string.split(' ')[0] != "AND":
                exec_string += " AND "
            exec_string += "WHERE tag LIKE %s"
            filter_params.append(f"%{request.args.get('tag')}%")
        if exec_string == """SELECT * FROM news WHERE""":
            exec_string = """SELECT * FROM news"""
        if request.args.get('pag'):
            if request.args.get('pag') == "desc":
                exec_string += " ORDER BY date DESC"
            elif request.args.get('pag') == "asc":
                exec_string += " ORDER BY date ASC"

        if len(filter_params) != 0:
            cur.execute(exec_string, filter_params)
        else:
            cur.execute(exec_string)

        items = cur.fetchall()
        return render_template("news/news.html", items)
    if request.method == "POST":
        usr_input = request.json
        if usr_input["btn_type"] == "find":
            querry_str = 'news?'
            for key in usr_input.keys():
                querry_str += f"{key}={usr_input[key]}&"
            if querry_str[-1] == "&":
                querry_str = querry_str[:-1]
            return {'re': querry_str}
        if "id" in usr_input.keys():
            return {'re': f'news/view_story?id={usr_input["id"]}'}


@app.route('/news/view_story')
@login_required
def view_story():
    if request.method == "GET":
        cur.execute("""SELECT *
         FROM news
         WHERE product_name = %s""", (request.args.get('id'),))
        items = cur.fetchall()
        return render_template("news/view_story.html", items)
    if request.method == "POST":
        usr_input = request.json
        if usr_input["btn_type"] == "submit":
            try:
                cur.execute("""INSERT INTO news_comments (comment_time,post_id,user_id,comment_text)
                VALUES (NOW(),%s,%s,%s)""", (request.args.get('id'), current_user.id, usr_input["comment_value"]))
                conn.commit()
            except Exception:
                abort(500)
                conn.rollback()


@app.route('/forum', methods=['GET', 'POST'])
def forum():
    """
    GET:contains all news items, but only names and photos so they can be placed in slides
    parses info from db and places it back via jinja
    POST:this b requests json that contains "btn_type" field with "find", after which it redirects
    you to itself but with all search options that are inside json that comes with find field
    i.e. tags,search,news_time etc.
    :return news.html OR if it gets an id option, returns one_new.html:
    """
    if request.method == "GET":
        exec_string = """SELECT * FROM news WHERE"""
        filter_params = []
        if request.args.get('search'):
            if exec_string.split(' ')[0] != "AND":
                exec_string += " AND "
            exec_string += "WHERE title LIKE %s OR post_text LIKE %s"
            filter_params.append(f"%{request.args.get('search')}%")
            filter_params.append(f"%{request.args.get('search')}%")
        if request.args.get('news_time'):
            if exec_string.split(' ')[0] != "AND":
                exec_string += " AND "
            exec_string += "WHERE post_time = %s"
            filter_params.append({request.args.get('news_time')})
        if request.args.get('tags'):
            if exec_string.split(' ')[0] != "AND":
                exec_string += " AND "
            exec_string += "WHERE tags LIKE %s"
            filter_params.append(f"%{request.args.get('tags')}%")
        if exec_string == """SELECT * FROM news WHERE""":
            exec_string = """SELECT * FROM news"""
        if request.args.get('pag'):
            if request.args.get('pag') == "desc":
                exec_string += " ORDER BY date DESC"
            elif request.args.get('pag') == "asc":
                exec_string += " ORDER BY date ASC"

        if len(filter_params) != 0:
            cur.execute(exec_string, filter_params)
        else:
            cur.execute(exec_string)

        items = cur.fetchall()
        return render_template("forum/forum.html", items)
    if request.method == "POST":
        usr_input = request.json
        if usr_input["btn_type"] == "find":
            querry_str = 'forum?'
            for key in usr_input.keys():
                querry_str += f"{key}={usr_input[key]}&"
            if querry_str[-1] == "&":
                querry_str = querry_str[:-1]
            return {'re': querry_str}
        if "id" in usr_input.keys():
            return {'re': f'forum/view_post?id={usr_input["id"]}'}


@app.route('/forum/view_post')
@login_required
def view_post():
    if request.method == "GET":
        cur.execute("""SELECT *
         FROM news
         WHERE product_name = %s""", (request.args.get('id'),))
        items = cur.fetchall()
        return render_template("forum/view_post.html", items)
    if request.method == "POST":
        usr_input = request.json
        if usr_input["btn_type"] == "submit":
            try:
                cur.execute("""INSERT INTO forum_comments (comment_time,post_id,user_id,comment_text)
                VALUES (NOW(),%s,%s,%s)""", (request.args.get('id'), current_user.id, usr_input["comment_value"]))
                conn.commit()
            except Exception:
                abort(500)
                conn.rollback()


@app.route('/forum/new_post')
@login_required
def new_post():
    if request.method == "GET":
        return render_template("forum/new_post.html")
    if request.method == "POST":
        usr_input = request.json
        if usr_input["btn_type"] == "submit":
            try:
                cur.execute("""INSERT INTO forum (post_time,author,tags,title,post_text)
                VALUES (NOW(),%s,%s,%s,%s)""", (current_user.name, usr_input["tags"],
                            usr_input["title"], usr_input["post_text"]))
                conn.commit()
            except Exception:
                abort(500)
                conn.rollback()


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
    app.run(port=5000, debug=True, ssl_context=('certificate.pem', 'private_key.pem'))
    cur.close()
    conn.close()
