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

request_timestamps = deque()


@app.before_request
def track_requests():
    """Track the timestamp of each request. Update"""
    global request_timestamps
    current_time = time.time()
    request_timestamps.append(current_time)
    while request_timestamps and request_timestamps[0] < current_time - 60:
        request_timestamps.popleft()


@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database based on the user ID.

    This function is called by Flask-Login to retrieve a user's
    information from the database when the user is authenticated.
    Args:
        user_id (int): The ID of the user to load.

    Returns:
        User or None:
            - Returns an instance of the User class with the user's details
              if the user is found.
            - Returns None if the user does not exist.

    Raises:
        Exception: May raise an exception if the database query fails.
    """
    cur.execute("SELECT id, name, password, email FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    print(user_data)
    if user_data:
        return User(*user_data)
    return None


@app.route('/logout')
@login_required
def logout():
    """Logs the user out and redirects them to the login page."""
    logout_user()
    return redirect(url_for('app_login.login'))


@app.route("/")
def main_page():
    """
    Displays the main page of the application.

    This endpoint retrieves and renders the top three news posts,
    the top three selling products, and the closest upcoming game.

    GET:
        Retrieves data for the main page, including:
            - The top three news posts with their like and comment counts.
            - The top three selling products from the shop.
            - The closest upcoming game.

        Returns:
            str: Renders the "index/index.html" template with the following context:
                - posts (list[dict]): A list of the top three news posts.
                - products (list[dict]): A list of the top three selling products.
                - upcoming_game (dict): Details of the closest upcoming game.
                - user (dict): Information about the logged-in user status.

    Raises:
        HTTPException: May raise an error if the database queries fail.
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
    Handles user account information display and updates.

    This endpoint allows users to view their account details and initiate changes to their data.

    GET:
        Retrieves the account information of the logged-in user.

        Returns:
            str: Renders the "account/account.html" template with the user's details.

    POST:
        Processes requests for changing user data.

        Args:
            request.json (dict):
                - btn_type (str): The type of button pressed; expected to be "change_user_data"
                  to initiate a redirect for updating user information.

        Returns:
            jsonify: A JSON response indicating where to redirect for user data changes.

    Raises:
        HTTPException: May raise an error if the request fails or the user is unauthorized.
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
    Allows users to view and update their account data.

    This endpoint handles both GET and POST requests for managing user account information.
    Users can retrieve their current profile data or update specific fields based on user input.

    GET:
        Retrieves the current account data for the logged-in user.

        Returns:
            str: Renders the "account/change_user_data.html" template with the user's
            profile information.

    POST:
        Updates the user's account data based on the provided JSON input.

        Args:
            request.json (dict):
                - profile_pic (str): The URL of the user's profile picture.
                - name (str): The user's name.
                - fav_player (str): The user's favorite player.
                - about_me (str): A brief description about the user.
                - vk_acc (str): The user's VK account link.
                - telegram_acc (str): The user's Telegram account link.
                - btn_type (str): Indicates the type of button pressed; should be "submit" for updates.

        Returns:
            jsonify: A JSON response indicating the success or failure of the update.

        Raises:
            HTTPException: If there is an error during the database update, a 500 error will be raised.
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
    Retrieves and displays a list of products available in the shop.

    This endpoint handles GET requests to fetch products from the shop database.
    Users can search for products by name using a query parameter. The results
    include product details such as name, price, picture, and description.

    GET:
        Retrieves a list of products with optional filtering by name.

        Args:
            request.args (ImmutableMultiDict):
                - query (str): The search term to filter products by their names.

        Returns:
            str: Renders the "shop/shop.html" template with the list of products
            available in the shop along with user information.

    Notes:
        If a search query is provided, only products matching the query will be returned.
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
    Retrieves and displays a list of news articles based on search parameters.

    This endpoint handles GET requests to fetch news articles, which can be filtered by search query, tags,
    and date. The results can be sorted based on either the most recent articles or the articles with the
    highest like count.

    GET:
        Retrieves a list of news articles with optional filtering and sorting.

        Args:
            request.args (ImmutableMultiDict):
                - query (str): The search term to filter news articles by title or text.
                - tags (str): A comma-separated string of tags to filter news articles.
                - date (str): The date to filter news articles (format: YYYY-MM-DD).
                - sort (str): The sorting order, either 'recent' or 'top' (default is 'recent').

        Returns:
            str: Renders the "news/news.html" template with the filtered and sorted list of news articles
            along with user information.

    Raises:
        ValueError: If the provided date is not in the correct format when filtering news articles.
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
    """
    Displays a specific news story and its comments, and allows users to add comments.

    This endpoint handles both GET and POST requests. On a GET request, it retrieves the details of a specific
    news story, including the number of likes and comments, as well as the comments associated with that story.
    On a POST request, it allows users to add a comment to the story.

    GET:
        Retrieves and displays the specified news story along with its comments.

        Args:
            request.args (ImmutableMultiDict):
                - id (int): The ID of the news story to be viewed.

        Returns:
            str: Renders the "news/view-story.html" template with the story data, user information, and comments.

    POST:
        Submits a comment for the specified news story.

        Args:
            request.args (ImmutableMultiDict):
                - id (int): The ID of the news story to comment on.
            request.form (ImmutableMultiDict):
                - comment (str): The text of the comment being submitted.

        Returns:
            str: A confirmation message ('OK') if the comment is added successfully, or an error message if
            there is an issue with the submission or database operation.

    Raises:
        Exception: If any error occurs during the database transaction when inserting a comment.
    """
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
    Displays a list of forum posts with options to filter and sort.

    This endpoint handles GET requests to display forum posts. Users can filter posts based on search queries,
    tags, and dates, as well as sort the results by recent posts or the number of likes.

    GET:
        Retrieves and displays forum posts based on search parameters.

        Args:
            request.args (ImmutableMultiDict):
                - query (str): The search term to filter posts by title or content.
                - tags (str): A comma-separated list of tags to filter posts by.
                - date (str): The date (YYYY-MM-DD) to filter posts by creation date.
                - sort (str): The sorting order for the results ('recent' or 'top'). Defaults to 'recent'.

        Returns:
            str: Renders the "forum/forum.html" template with the filtered and sorted list of forum posts
            and user information.

    Raises:
        Exception: If any error occurs during the database transaction or if invalid date format is provided.
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
    """
    Displays a specific forum post and its comments, and allows users to add comments.

    This endpoint handles both GET and POST requests. On a GET request, it retrieves the details of a specific
    forum post, including the number of likes and comments, as well as the comments associated with that post.
    On a POST request, it allows users to add a comment to the post.

    GET:
        Retrieves and displays the specified forum post along with its comments.

        Args:
            request.args (ImmutableMultiDict):
                - id (int): The ID of the post to be viewed.

        Returns:
            str: Renders the "forum/view-post.html" template with the post data, user information, and comments.

    POST:
        Submits a comment for the specified forum post.

        Args:
            request.args (ImmutableMultiDict):
                - id (int): The ID of the post to comment on.
            request.form (ImmutableMultiDict):
                - comment (str): The text of the comment being submitted.

        Returns:
            str: A confirmation message ('OK') if the comment is added successfully, or an error message if
            there is an issue with the submission or database operation.

    Raises:
        Exception: If any error occurs during the database transaction when inserting a comment.
    """
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
    """
    Allows authenticated users to create and submit new forum posts.

    This endpoint handles both GET and POST requests for creating a new forum post. Users must be logged in to
    access this route. On a successful POST request, the new post is inserted into the database, and an image file
    associated with the post is uploaded.

    GET:
        Displays the new post creation form.

        Returns:
            str: Renders the "forum/new-post.html" template with user information.

    POST:
        Submits the new forum post and associated image.

        Args:
            request.form (ImmutableMultiDict):
                - tags (str): Tags associated with the post.
                - post-title (str): The title of the new post.
                - post-content (str): The content of the new post.
            request.files (FileStorage):
                - post-image (FileStorage): The image file to be uploaded with the post.

        Returns:
            str: A confirmation message ('OK') if the post is created successfully, or an error message if
            there is an issue with the submission or database operation.

    Raises:
        Exception: If any error occurs during the database transaction or file upload.
    """
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
    """
    Allows admins to create and submit new stories.

    This endpoint handles both GET and POST requests for creating a new story. Only users with admin privileges
    can access this route. Admin verification is done by checking the user's role in the database. On a successful
    POST request, the new story is inserted into the database, and an image file associated with the story is uploaded.

    GET:
        Displays the new story creation form.

        Returns:
            str: Renders the "news/new-story.html" template.

    POST Request:
        Submits the new story and associated image.

        Args:
            request.form (ImmutableMultiDict):
                - tags (str): Tags associated with the story.
                - post-title (str): The title of the new story.
                - post-content (str): The content of the new story.
            request.files (FileStorage):
                - post-image (FileStorage): The image file to be uploaded with the story.

        Returns:
            str: A confirmation message ('OK') if the story is created successfully, or an error message if
            there is an issue with the submission or database operation.

    Raises:
        403: If the user is not an admin.
        Exception: If any error occurs during the database transaction or file upload.
    """
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
        return render_template("news/new-story.html", user=user)
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
    """
    Retrieves and displays game information including current, upcoming, and past games.

    This endpoint processes GET requests to provide information about the current game, the next upcoming game,
    and a list of past games. The results can be filtered based on a search query and a specific date.

    Args:
        - query (str, optional): A search term to filter past games by team names or game names.
        - date (str, optional): A specific date (YYYY-MM-DD) to filter past games by their start time.

    Returns:
        str: Renders the 'games/games.html' template with the following context:
            - current_game (dict or None): Information about the current game, if any.
            - upcoming_game (dict or None): Information about the next upcoming game, if any.
            - games (list of dict): A list of past games matching the search criteria and date.
            - user (dict): A dictionary containing user login status and profile picture URL.

    Raises:
        Exception: If any database query fails or if there is an issue rendering the template.
    """
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
    """
    Handles 'like' functionality for news and forum posts.

    This endpoint allows users to either fetch the like status and total number of likes for a specific post (GET)
    or to add/remove a like on a post (POST). The user must be logged in to access this route.

    GET:
        Retrieves whether the current user has liked the post and the total number of likes on the post.

        Args (request.args):
            dest (str): The type of post to interact with. Can be either 'forum' or 'news'.
            id (int): The ID of the post.

        Returns:
            dict: A JSON object containing:
                - likes (int): Total number of likes for the post.
                - is_liked (bool): Whether the current user has liked the post.

    POST:
        Adds or removes a like for a specific post based on the current like status.

        Args (request.args):
            dest (str): The type of post to interact with. Can be either 'forum' or 'news'.
            id (int): The ID of the post.

        Returns:
            dict: A JSON object containing:
                - message (str): A success message, either "Like added" or "Like removed".
                - likes (int): The updated total number of likes for the post.

    Raises:
        AssertionError: If the 'dest' parameter is not 'news' or 'forum'.
        403: If the request method is neither GET nor POST or if required arguments are missing.
    """
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
    """Renders the about page template."""
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'
    return render_template('/about/about.html', user=user)


@app.route('/team-members')
def team_page():
    """Renders the team members page template."""
    user = {'logged_in': False, 'profile_picture_url': '/static/img/default_pfp.png'}
    if current_user.is_authenticated:
        user['logged_in'] = True
        user['profile_picture_url'] = '/static/img/eye.png'
    cur.execute("SELECT picture_url, name, player_num, position, description FROM team_members")
    new_keys = ['picture_url', 'name', 'num', 'position', 'description']
    data = [dict(zip(new_keys, i)) for i in cur.fetchall()]
    return render_template('/about/team_members.html', user=user, data=data)


if __name__ == "__main__":
    app.run(port=5000, debug=True, ssl_context=('certificate.pem', 'private_key.pem'))
    cur.close()
    conn.close()
