import os
from login import app_login, User
from flask import Flask, render_template, request, url_for, redirect, abort, jsonify
from flask_login import LoginManager, login_required, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from collections import deque
from datetime import datetime
import time
import psutil
import requests
from secrets import token_urlsafe
from dbloader import connect_to_db
from settings_loader import get_processor_settings
from helper import GOOGLE_CLIENT_ID

conn, cur = connect_to_db()

UPLOAD_FOLDER = os.path.abspath('DATA2')
settings = get_processor_settings()
ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg'}

app = Flask(__name__)
app.register_blueprint(app_login)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = token_urlsafe(16)

login_manager = LoginManager(app)
login_manager.login_view = 'app_login.login'

config = []

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
    return redirect(url_for('app_login.login'))


@app.route("/")
def main_page():
    """Renders the template for the main page and fills it with data.

    Args:
        None

    Returns:
        index.html (str) - index.html template
        posts: (list(dict)) - top 3 posts to be rendered on index
            The dicts have the following keys:
                'id', 'post_time', 'like_count', 'comment_count', 'title', 'tags', 'text'
        products: (list(dict)) - top 3 most sold products to be rendered on index
            The dicts have the following keys:
                'team1', 'team2', 'datetime', 'id'
        upcoming_game: (dict) - next game of the football club
            The dict has the following keys:
                'team1', 'team2', 'datetime', 'id'
        user: (dict) - user data for the navbar
            The dict has the following keys:
                'logged_in', 'profile_picture_url'
    """

    cur.execute("""SELECT news.id,
                news.news_time,
                COUNT(news_likes.post_id) AS like_count,
                COUNT(news_comments.post_id) AS comment_count,
                news.title,
                news.tag,
                news.news_text
                FROM news
                LEFT JOIN news_likes ON news.id = news_likes.post_id
                LEFT JOIN news_comments ON news.id = news_comments.post_id
                GROUP BY news.id
                ORDER BY news.news_time
                LIMIT 3;""")
    top_three_posts_fields = ['id', 'post_time', 'like_count', 'comment_count', 'title', 'tags', 'text']
    rows = cur.fetchall()
    top_three_posts = [dict(zip(top_three_posts_fields, i)) for i in rows]
    cur.execute("SELECT product_name, price, description, picture FROM shop ORDER BY sales DESC LIMIT 3")
    fields_shop = ['title', 'price', 'text', 'shop_photo_url']
    top_three_selling_posts = [dict(zip(fields_shop, i)) for i in cur.fetchall()]

    cur.execute("""SELECT team1_name, team2_name, game_start_time, id
                FROM games
                ORDER BY ABS(EXTRACT(EPOCH FROM (game_start_time - NOW()))) ASC
                LIMIT 1;
                """)
    closest_game_fields = ['team1', 'team2', 'datetime', 'id']
    closest_game = dict(zip(closest_game_fields, cur.fetchone()))
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'
    return render_template("index/index.html", posts=top_three_posts, products=top_three_selling_posts,
                           upcoming_game=closest_game, user=user)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    An endpoint with all of a user data.
    """
    name, fav_player, about, vk_acc, telegram_acc = '', '', '', '', ''
    if request.method == 'GET':
        usr_id = current_user.id
        cur.execute("SELECT name, fav_player, about_me, vk_acc, telegram_acc FROM users WHERE id = %s",
                    (usr_id,))
        name, fav_player, about, vk_acc, telegram_acc = cur.fetchone()

        if vk_acc is None:
            vk_acc = "Не привязан"
        if telegram_acc is None:
            telegram_acc = "Не привязан"
    if request.method == 'POST':
        usr_input = request.json
        if usr_input["btn_type"] == "change_user_data":
            return {'re': '/account/change_account_data'}

    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png',
            'nickname': name, 'about': about, 'fav_player_img': fav_player,
            'telegram_url': telegram_acc, 'vk_url': vk_acc}

    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'

    return render_template('account/account.html', user=user)


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
        return render_template("account/change_user_data.html", profile_pic=profile_pic, name=name,
                               fav_player=fav_player, about_me=about_me, vk_acc=vk_acc, telegram_acc=telegram_acc)

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
                        cur.execute(query, (key, usr_input[key], usr_id))
            conn.commit()
        except Exception:
            conn.rollback()
            print("БАЗЫ ДАЛИ ЗАЗЫ " * 5)
            abort(304)


@app.route('/shop', methods=['GET'])
def shop():
    """
    GET:contains all shop items, but only names and photos so they can be placed in slides
    parses info from db and places it back via jinja
        expects ?search=string and makes new db request that is placed back in html form via jinja
    or redirects to itself with id and returns page of a certain item, when clicked
    So, lets get to it folks
    :return shop.html:
    """
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'
    cur.execute("SELECT product_name, price, picture, description FROM shop")
    items_fields = ['title', 'price', 'news_photo_url', 'text']
    items = [dict(zip(items_fields, a)) for a in cur.fetchall()]
    if request.args.get('query'):
        cur.execute("""SELECT product_name, price, picture, description
                        FROM shop
                        WHERE LOWER(product_name) LIKE %s""", (f"%{request.args.get('query').lower()}%",))
        items = [dict(zip(items_fields, a)) for a in cur.fetchall()]
        return render_template("shop/shop.html", data=items, user=user)
    return render_template("shop/shop.html", data=items, user=user)


@app.route('/news', methods=['GET'])
def news():
    """
    GET: Renders the news page with a list of filtered and sorted news items.

    Behavior:
    - Retrieves news items from the database, applying filters and sorting based on the given query parameters.
    - Filters news based on a search term in the title or content, specific tags, and a date if provided.
    - Defaults to showing the most recent news if no filters are applied.
    - Allows sorting by either the number of likes (for "top" posts) or by date (for "recent" posts).

    Query Parameters:
        query (str, optional): A search string to filter news by title or content.
        tags (str, optional): A comma-separated list of tags to filter news by. Each tag can be up to 10 chars long.
        date (str, optional): A specific date (in 'YYYY-MM-DD' format) to filter news items.
            Only news posted on or after the given date will be shown.
        sort (str, optional): Determines the sorting order. Options are:
            'recent': Sort news by the most recent posts (default).
            'top': Sort news by the number of likes (most liked posts appear first).

    Returns:
        Rendered news template.
    """

    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'

    # Get search parameters
    search_query = request.args.get('query', '').strip()
    tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
    date = request.args.get('date', None)
    sort_order = request.args.get('sort', 'recent')  # Default to recent if not specified

    # Base SQL query
    exec_string = """
        SELECT news.id,
               news.news_time AS date_created,
               COUNT(news_likes.post_id) AS like_count,
               COUNT(news_comments.post_id) AS comment_count,
               news.title,
               news.tag AS tags,
               news.news_text AS text
        FROM news
        LEFT JOIN news_likes ON news.id = news_likes.post_id
        LEFT JOIN news_comments ON news.id = news_comments.post_id
        WHERE 1=1
    """
    filters = []
    if search_query:
        filters.append("(news.title ILIKE %s OR news.news_text ILIKE %s)")

    if tags:
        tag_filters = ' OR '.join(['news.tag ILIKE %s'] * len(tags))
        filters.append(f"({tag_filters})")
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
            print(date)
            filters.append("DATE(news.news_time) = %s")
        except ValueError:
            pass  # Invalid date, skip the filter
    if filters:
        exec_string += " AND " + " AND ".join(filters)

    # Sorting
    if sort_order == 'top':
        exec_string += " GROUP BY news.id ORDER BY like_count DESC"
    else:
        exec_string += " GROUP BY news.id ORDER BY news.news_time DESC"
    sql_params = []
    if search_query:
        sql_params.extend([f"%{search_query}%", f"%{search_query}%"])
    if tags:
        sql_params.extend([f"%{tag}%" for tag in tags])
    if date:
        sql_params.append(date)

    # Execute the query
    cur.execute(exec_string, (sql_params, ))
    news_fields = ['id', 'date_created', 'like_count', 'comment_count', 'title', 'tags', 'text']
    items = [dict(zip(news_fields, i)) for i in cur.fetchall()]

    return render_template("news/news.html", data=items, user=user)


@app.route('/view-story', methods=['GET', 'POST'])
@login_required
def view_story():
    if request.method == "GET":
        user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
        if current_user.is_authenticated:
            user['logged_in'] = True
            user['profile_picture_url'] = '/static/img/eye.png'
        exec_string = """
            SELECT news.id,
                news.news_time AS date_created,
                COUNT(news_likes.post_id) AS like_count,
                COUNT(news_comments.post_id) AS comment_count,
                news.title,
                news.tag AS tags,
                news.news_text AS text
            FROM news
            LEFT JOIN news_likes ON news.id = news_likes.post_id
            LEFT JOIN news_comments ON news.id = news_comments.post_id
            WHERE news.id = %s
            GROUP BY news.id
        """
        cur.execute(exec_string, (request.args.get('id'), ))
        news_fields = ['id', 'date_created', 'like_count', 'comment_count', 'title', 'tags', 'text']
        items = dict(zip(news_fields, cur.fetchone()))
        exec_string_2 = """
            SELECT users.name,
                users.profile_pic,
                news_comments.comment_time,
                news_comments.comment_text
            FROM news_comments
            JOIN users ON news_comments.user_id = users.id
            WHERE news_comments.post_id = %s
            ORDER BY news_comments.comment_time DESC"""
        news_fields2 = ['username', 'profile_picture_url', 'date_posted', 'text']
        cur.execute(exec_string_2, (request.args.get('id'), ))
        comments = [dict(zip(news_fields2, i)) for i in cur.fetchall()]
        return render_template("news/view-story.html", data=items, user=user, comments=comments)
    if request.method == "POST":
        try:
            cur.execute("""INSERT INTO news_comments (comment_time, post_id, user_id, comment_text)
                            VALUES (NOW(),%s,%s,%s)""",
                        (request.args.get('id'), current_user.id, request.form.get('comment')))
            conn.commit()
            return 'OK'
        except Exception:
            conn.rollback()
            return "Error making comment"


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
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'

    # Get search parameters
    search_query = request.args.get('query', '').strip()
    tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
    date = request.args.get('date', None)
    sort_order = request.args.get('sort', 'recent')  # Default to recent if not specified

    # Base SQL query
    exec_string = """
        SELECT forum.id,
               forum.post_time AS date_created,
               forum.author,
               COUNT(forum_likes.post_id) AS like_count,
               COUNT(forum_comments.post_id) AS comment_count,
               forum.title,
               forum.tag AS tags,
               forum.post_text AS text
        FROM forum
        LEFT JOIN forum_likes ON forum.id = forum_likes.post_id
        LEFT JOIN forum_comments ON forum.id = forum_comments.post_id
        WHERE 1=1
    """
    filters = []
    if search_query:
        filters.append("(forum.title ILIKE %s OR forum.post_text ILIKE %s)")

    if tags:
        tag_filters = ' OR '.join(['forum.tag ILIKE %s'] * len(tags))
        filters.append(f"({tag_filters})")
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
            print(date)
            filters.append("DATE(forum.post_time) = %s")
        except ValueError:
            pass  # Invalid date, skip the filter
    if filters:
        exec_string += " AND " + " AND ".join(filters)

    # Sorting
    if sort_order == 'top':
        exec_string += " GROUP BY forum.id ORDER BY like_count DESC"
    else:
        exec_string += " GROUP BY forum.id ORDER BY forum.post_time DESC"
    sql_params = []
    if search_query:
        sql_params.extend([f"%{search_query}%", f"%{search_query}%"])
    if tags:
        sql_params.extend([f"%{tag}%" for tag in tags])
    if date:
        sql_params.append(date)

    # Execute the query
    cur.execute(exec_string, (sql_params, ))
    forum_fields = ['id', 'date_created', 'author', 'like_count', 'comment_count', 'title', 'tags', 'text']
    items = [dict(zip(forum_fields, i)) for i in cur.fetchall()]

    return render_template("forum/forum.html", data=items, user=user)


@app.route('/view-post', methods=['GET', 'POST'])
@login_required
def view_post():
    if request.method == "GET":
        user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
        if current_user.is_authenticated:
            user['logged_in'] = True
            user['profile_picture_url'] = '/static/img/eye.png'
        exec_string = """
            SELECT forum.id,
                forum.post_time AS date_created,
                COUNT(forum_likes.post_id) AS like_count,
                COUNT(forum_comments.post_id) AS comment_count,
                forum.title,
                forum.tag AS tags,
                forum.post_text AS text
            FROM forum
            LEFT JOIN forum_likes ON forum.id = forum_likes.post_id
            LEFT JOIN forum_comments ON forum.id = forum_comments.post_id
            WHERE forum.id = %s
            GROUP BY forum.id
        """
        cur.execute(exec_string, (request.args.get('id'), ))
        news_fields = ['id', 'date_created', 'like_count', 'comment_count', 'title', 'tags', 'text']
        items = dict(zip(news_fields, cur.fetchone()))
        exec_string_2 = """
            SELECT users.name,
                users.profile_pic,
                forum_comments.comment_time,
                forum_comments.comment_text
            FROM forum_comments
            JOIN users ON forum_comments.user_id = users.id
            WHERE forum_comments.post_id = %s
            ORDER BY forum_comments.comment_time DESC"""
        news_fields2 = ['username', 'profile_picture_url', 'date_posted', 'text']
        cur.execute(exec_string_2, (request.args.get('id'), ))
        comments = [dict(zip(news_fields2, i)) for i in cur.fetchall()]
        return render_template("forum/view-post.html", data=items, user=user, comments=comments)
    if request.method == "POST":
        try:
            cur.execute("""INSERT INTO forum_comments (comment_time, post_id, user_id, comment_text)
                            VALUES (NOW(),%s,%s,%s)""",
                        (request.args.get('id'), current_user.id, request.form.get('comment')))
            conn.commit()
            return 'OK'
        except Exception:
            conn.rollback()
            return "Error making comment"


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
