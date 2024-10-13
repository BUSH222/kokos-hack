import os
from login import app_login, User
from flask import Flask, render_template, request, url_for, redirect, abort, jsonify
from flask_login import LoginManager, login_required, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient
from collections import deque
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["5 per second"],
    storage_uri="memory://",
)

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
    GET: Renders the account page
    Behavior:
    - Redirects to change user data on button click
    Returns:
        Rendered account template.
    """
    name, fav_player, about, vk_acc, telegram_acc, points = '', '', '', '', '', 0
    if request.method == 'GET':
        usr_id = current_user.id
        cur.execute("SELECT name, fav_player, about_me, vk_acc, telegram_acc, points FROM users WHERE id = %s",
                    (usr_id,))
        name, fav_player, about, vk_acc, telegram_acc, points = cur.fetchone()
        if vk_acc is None:
            vk_acc = "Не привязан"
        if telegram_acc is None:
            telegram_acc = "Не привязан"

        user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png',
                'nickname': name, 'about': about, 'fav_player_img': fav_player,
                'telegram_url': telegram_acc, 'vk_url': vk_acc}
        if current_user.is_authenticated:
            user['logged_in'] = True
            user['profile_picture_url'] = '/static/img/eye.png'
        print(points)  # TODO
        return render_template('account/account.html', user=user)
    if request.method == 'POST':
        usr_input = request.json
        if usr_input["btn_type"] == "change_user_data":
            return jsonify({'re': '/account/change_account_data'})


@app.route('/account/change_account_data', methods=['POST', 'GET'])
@login_required
def change_user_data():
    """
    GET: Renders the account page
    Behavior:
    - Parses user info and places it in textlines that send change info on button click
    Returns:
        Rendered news template.
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
                        query = f"UPDATE users SET {key} = %s WHERE id = %s"
                        cur.execute(query, (usr_input[key], usr_id,))
            conn.commit()
            return jsonify({"change_data": "Success!"})
        except Exception:
            conn.rollback()
            print("БАЗЫ ДАЛИ ЗАЗЫ " * 5)
            abort(500)


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
               news.news_text AS text,
               news.picture
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
    cur.execute(exec_string, tuple(sql_params))
    news_fields = ['id', 'date_created', 'like_count', 'comment_count',
                   'title', 'tags', 'text', 'news_photo_url']
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
                news.news_text AS text,
                news.picture
            FROM news
            LEFT JOIN news_likes ON news.id = news_likes.post_id
            LEFT JOIN news_comments ON news.id = news_comments.post_id
            WHERE news.id = %s
            GROUP BY news.id
        """
        cur.execute(exec_string, (request.args.get('id'), ))
        news_fields = ['id', 'date_created', 'like_count', 'comment_count',
                       'title', 'tags', 'text', 'news_photo_url']
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
               forum.post_text AS text,
               forum.picture
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
    cur.execute(exec_string, tuple(sql_params))
    forum_fields = ['id', 'date_created', 'author', 'like_count', 'comment_count',
                    'title', 'tags', 'text', 'news_photo_url']
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
                forum.post_text AS text,
                forum.picture
            FROM forum
            LEFT JOIN forum_likes ON forum.id = forum_likes.post_id
            LEFT JOIN forum_comments ON forum.id = forum_comments.post_id
            WHERE forum.id = %s
            GROUP BY forum.id
        """
        cur.execute(exec_string, (request.args.get('id'), ))
        news_fields = ['id', 'date_created', 'like_count', 'comment_count',
                       'title', 'tags', 'text', 'news_photo_url']
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


@app.route('/new-post', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == "GET":
        user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
        if current_user.is_authenticated:
            user['logged_in'] = True
            user['profile_picture_url'] = '/static/img/eye.png'
        return render_template("forum/new-post.html", user=user)
    elif request.method == "POST":
        usr_input = request.form
        file = request.files['post-image']
        try:
            file_name = 'forum/' + token_urlsafe(16) + '.' + file.filename.split('.')[-1]
            target_url = 'http://localhost:5001/upload_assets'
            files = {'file': (file_name, file.stream, file.content_type)}
            data = {'img_name': file_name}
            picurl = 'http://localhost:5001/assets/'+file_name

            requests.post(target_url, files=files, data=data)

            cur.execute("""INSERT INTO forum (post_time, author, tag, title, post_text, picture)
                        VALUES (NOW(),%s,%s,%s,%s,%s)""",
                        (current_user.id, usr_input["tags"],
                         usr_input["post-title"], usr_input["post-content"], picurl))
            conn.commit()

            return 'OK'
        except Exception as e:
            conn.rollback()
            return f'Error, {e}'


@app.route('/new-story', methods=['GET', 'POST'])
@login_required
def new_story():
    try:
        cur.execute('SELECT role FROM users WHERE id = %s', (current_user.id, ))
        if '5' not in cur.fetchone()[0]:
            abort(403)
    except Exception as e:
        return f'Error verifying user: {e}'

    if request.method == "GET":
        user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
        if current_user.is_authenticated:
            user['logged_in'] = True
            user['profile_picture_url'] = '/static/img/eye.png'
        return render_template("forum/new-post.html", user=user)
    elif request.method == "POST":
        usr_input = request.form
        file = request.files['post-image']
        try:
            file_name = 'news/' + token_urlsafe(16) + '.' + file.filename.split('.')[-1]
            target_url = 'http://localhost:5001/upload_assets'
            files = {'file': (file_name, file.stream, file.content_type)}
            data = {'img_name': file_name}
            picurl = 'http://localhost:5001/assets/'+file_name

            requests.post(target_url, files=files, data=data)

            cur.execute("""INSERT INTO forum (post_time, author, tag, title, post_text, picture)
                        VALUES (NOW(),%s,%s,%s,%s,%s)""",
                        (current_user.id, usr_input["tags"],
                         usr_input["post-title"], usr_input["post-content"], picurl))
            conn.commit()

            return 'OK'
        except Exception as e:
            conn.rollback()
            return f'Error, {e}'


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


@app.route('/games', methods=['GET'])
def games():
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'

    current_time = datetime.now()

    current_game_query = """
        SELECT id, team1_name, team2_name, game_start_time
        FROM games
        WHERE game_start_time <= %s AND game_end_time >= %s
        ORDER BY game_start_time DESC
        LIMIT 1;
    """
    cur.execute(current_game_query, (current_time, current_time))
    game_fields = ['id', 'team1', 'team2', 'datetime']
    current_game_data = cur.fetchone()
    if current_game_data:
        current_game = dict(zip(game_fields, current_game_data))
    else:
        current_game = None

    upcoming_game_query = """
        SELECT id, team1_name, team2_name, game_start_time
        FROM games
        WHERE game_start_time > %s
        ORDER BY game_start_time ASC
        LIMIT 1;
    """
    cur.execute(upcoming_game_query, (current_time,))
    upcoming_game_data = cur.fetchone()

    if upcoming_game_data:
        upcoming_game = dict(zip(game_fields, upcoming_game_data))
    else:
        upcoming_game = None

    past_games_query = """
    SELECT id, team1_name, team2_name, game_start_time
    FROM games
    WHERE game_end_time < %s
    """
    query_params = [current_time]
    # If 'query' parameter is present, add search condition
    if request.args.get('query'):
        search_term = f"%{request.args.get('query')}%"
        past_games_query += """
            AND (team1_name ILIKE %s OR team2_name ILIKE %s OR game_name ILIKE %s)
        """
        query_params.extend([search_term, search_term, search_term])

    # If 'date' parameter is present, match the game_start_time date
    if request.args.get('date'):
        game_date = request.args.get('date')  # Expected format: 'YYYY-MM-DD'
        past_games_query += " AND DATE(game_start_time) = %s"
        query_params.append(game_date)

    # Execute the query with dynamic parameters
    past_games_query += " ORDER BY game_end_time DESC"
    cur.execute(past_games_query, tuple(query_params))
    games_data = cur.fetchall()
    if games_data:
        games = [dict(zip(game_fields, i)) for i in games_data]
    else:
        games = []
    # Render template with game data
    return render_template("games/games.html",
                           current_game=current_game,
                           upcoming_game=upcoming_game,
                           games=games,
                           user=user
                           )


@app.route('/like', methods=['GET', 'POST'])
@limiter.exempt
@login_required
def like():
    print('BRUH')
    print(request.args)
    if request.method == 'GET' and request.args:
        uid = current_user.id
        destination = request.args.get('dest')  # forum or news
        post_id = request.args.get('id')
        if destination == "news":
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM news_likes
                    WHERE post_id = %s AND user_id = %s
                );
            """
            query_total = "SELECT COUNT(*) FROM news_likes WHERE post_id = %s"
        elif destination == "forum":
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM forum_likes
                    WHERE post_id = %s AND user_id = %s
                );
            """
            query_total = "SELECT COUNT(*) FROM forum_likes WHERE post_id = %s"
        cur.execute(query, (post_id, uid))
        post_isliked = cur.fetchone()
        post_isliked = post_isliked[0] if post_isliked is not None else False
        cur.execute(query_total, (post_id, ))
        post_totallikes = cur.fetchone()
        post_totallikes = post_totallikes[0] if post_totallikes is not None else 0
        return jsonify({'likes': post_totallikes, 'is_liked': post_isliked})

    elif request.method == 'POST' and request.args:
        uid = current_user.id
        destination = request.args.get('dest')
        assert destination in ['news', 'forum']
        post_id = request.args.get('id')
        if destination == "news":
            check_query = "SELECT 1 FROM news_likes WHERE post_id = %s AND user_id = %s"
            insert_query = "INSERT INTO news_likes (post_id, user_id) VALUES (%s, %s)"
            delete_query = "DELETE FROM news_likes WHERE post_id = %s AND user_id = %s"
        elif destination == "forum":
            check_query = "SELECT 1 FROM forum_likes WHERE post_id = %s AND user_id = %s"
            insert_query = "INSERT INTO forum_likes (post_id, user_id) VALUES (%s, %s)"
            delete_query = "DELETE FROM forum_likes WHERE post_id = %s AND user_id = %s"

        cur.execute(check_query, (post_id, uid))
        is_liked = cur.fetchone()

        if is_liked:
            cur.execute(delete_query, (post_id, uid))
            message = "Like removed"
        else:
            cur.execute(insert_query, (post_id, uid))
            message = "Like added"
        conn.commit()
        # Return the updated total number of likes
        cur.execute("SELECT COUNT(*) FROM {}_likes WHERE post_id = %s".format(destination), (post_id,))
        total_likes = cur.fetchone()[0]

        return jsonify({'message': message, 'likes': total_likes})
    else:
        abort(403)


@app.route('/about')
def about_page():
    """
    GET: Renders the about page with a list of filtered and sorted news items.
    Returns:
        Rendered about template.
    """
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'
    return render_template('/about/about.html', user=user)


@app.route('/team-members')
def team_page():
    """
    GET: Renders the team_members page
    Returns:
        Rendered team_membres template.
    """
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'
    cur.execute("SELECT name, description, position, join_time FROM team_members")
    new_keys = ['name', 'description', 'position', 'join_time']
    items = dict(zip(new_keys, cur.fetchone()))
    return render_template('/about/team-members.html', user=user, data=items)


if __name__ == "__main__":
    app.run(port=5000, debug=True, ssl_context=('certificate.pem', 'private_key.pem'))
    cur.close()
    conn.close()
