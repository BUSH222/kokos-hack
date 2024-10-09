from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_login import login_user, logout_user, LoginManager, login_required, UserMixin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dbloader import connect_to_db
from logger import log_event
from secrets import token_urlsafe
import requests
import requests.exceptions
import psutil
import random
import string
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = token_urlsafe(16)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1 per second"],
    storage_uri="memory://",
)

conn, cur = connect_to_db()


def generate_random_string():
    """Generates a random filler string when deleting accounts"""
    length = 32
    characters = string.ascii_letters + string.digits + '_' + ',' + '.'
    return ''.join(random.choices(characters, k=length))


class User(UserMixin):
    """Basic flask_login user class."""
    def __init__(self, id, username, password) -> None:
        self.id = id
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    """Basic flask_login user loader function."""
    cur.execute("SELECT id, name, password FROM users WHERE id = %s AND role LIKE %s", (user_id, '%5%'))
    user_data = cur.fetchone()
    if user_data:
        return User(*user_data)
    return None


@app.route('/admin_panel')
@login_required
def admin_panel():
    """
    Render the admin panel page.

    Returns:
        str: The rendered HTML template for the admin panel.
    """
    return render_template('admin_panel.html')


@app.route('/admin_panel/login', methods=['GET', 'POST'])
def login():
    """
    Handle the login process for the admin panel.

    GET:
        Render the login page.

    POST:
        Authenticate the user and redirect to the admin panel if successful.

    Returns:
        str: The rendered HTML template for the login page or a redirect to the admin panel.
        str: An error message if authentication fails.
    """
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        cur.execute('SELECT id, name, password FROM users WHERE name = %s AND role LIKE %s', (username, '%5%'))
        user_data = cur.fetchone()
        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(*user_data)
                login_user(user)
                user_ip = request.remote_addr
                user_ua = request.user_agent.string
                log_event("Successful admin login detected, ", log_level=20, kwargs=(user_ip, user_ua))
                return "OK"
            else:
                return "Invalid username or password"
        else:
            return "Registration not allowed or user is not admin"
    else:
        return render_template('admin_panel_login.html')


@app.route('/admin_panel/logout', methods=['GET'])
@login_required
def logout():
    """
    Handle the logout process for the admin panel.
    """
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin_panel/logs')
@login_required
def admin_panel_logs():
    """
    Render the admin panel server logs page.

    Returns:
        str: The rendered HTML template for the admin panel.
    """
    return render_template('admin_panel_logs.html')


@app.route('/admin_panel/logs/get_logs')
@login_required
def admin_panel_get_top100_logs():
    """
    Return top 100 latest server logs

    Returns:
        str: organised list of logs.
    """
    cur.execute("""SELECT CONCAT(id, '. [', TO_CHAR(log_time, 'YYYY-MM-DD HH24:MI:SS'), ']:  ', log_text)
                FROM logs
                ORDER BY id DESC
                LIMIT 100""")
    return jsonify(cur.fetchall())


@app.route('/admin_panel/community')
@login_required
def admin_panel_community():
    """
    Render the community management page within the admin panel.

    Returns:
        str: The rendered HTML template for the community management page.
    """
    return render_template('admin_panel_community.html')


@app.route('/admin_panel/community/delete_account')
@login_required
def admin_panel_community_delete_account():
    """
    Delete a user account based on the user id.
    Deleting the account changes its username to deleted_account[id], makes its password and email random

    Args:
        id (int): The id of the account to delete.

    Returns:
        bool: True if the account was successfully deleted, False otherwise.
    """
    user_id = request.args.get('id')
    try:
        cur.execute("UPDATE users SET name = %s, password = %s, email = %s, role = '' WHERE id = %s",
                    (f'deleted_user_{user_id}', generate_random_string(), generate_random_string(), user_id))
        conn.commit()
        if cur.rowcount == 0:
            return 'Something went wrong.'
        log_event("Deleted user account, id:", log_level=20, kwargs=user_id)
        return 'Success!'
    except Exception as e:
        conn.rollback()
        log_event("Error deleting account:", log_level=30, kwargs=e)
        return f'Error: {e}'


@app.route('/admin_panel/community/prune_account')
@login_required
def admin_panel_community_prune_account():
    """
    Prunes a user account based on the user id.

    Args:
        id (int): The id of the account to delete.

    Returns:
        bool: True if the account was successfully deleted, False otherwise.
    """
    user_id = request.args.get('id')
    try:
        cur.execute("SELECT id FROM forum WHERE author = %s;", (user_id,))
        forum_posts = cur.fetchall()
        for post in forum_posts:
            post_id = post[0]
            cur.execute("DELETE FROM forum_comments WHERE post_id = %s;", (post_id,))
            cur.execute("DELETE FROM forum_likes WHERE post_id = %s;", (post_id,))
        cur.execute("DELETE FROM news_comments WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM news_likes WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM forum WHERE author = %s;", (user_id,))
        cur.execute("DELETE FROM forum_comments WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM forum_likes WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM game_comments WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM tickets WHERE user_id = %s;", (user_id,))
        conn.commit()
        if cur.rowcount == 0:
            return 'Something went wrong.'
        log_event("Pruned user account, id:", log_level=20, kwargs=user_id)
        return 'Success!'
    except Exception as e:
        conn.rollback()
        log_event("Error pruning account:", log_level=30, kwargs=e)
        return f'Error: {e}'


@app.route('/admin_panel/community/view_account_info')
@login_required
def admin_panel_community_view_account_info():
    """
    View the account info based on the user name.

    Args:
        user (str): The username of the account to view roles for.

    Returns:
        json array:
            id (int): User's id.
            name (str): User's name.
            email (str): User's email.
            password (str): User's password
            points (int): User's activity points.
            role (str): User's roles.
                Organised as a sorted string of values 0-5, each of them being a unique role identifier.

        str: 'No results' if the search for the user returned nothing
             'Error: {error desciption}' if something went wrong.
    """
    user = request.args.get('user')
    try:
        cur.execute('SELECT id, name, email, password, points, role FROM users WHERE name = %s', (user, ))
        roles_raw = cur.fetchone()
        if not roles_raw:
            return jsonify('No results')
        log_event("User account info viewed, name:", log_level=10, kwargs=user)
        return jsonify(roles_raw)
    except Exception as e:
        conn.rollback()
        log_event("Error viewing account info:", log_level=30, kwargs=e)
        return f'Error: {e}'


@app.route('/admin_panel/community/set_account_info')
@login_required
def admin_panel_community_set_account_info():
    """
    Set account info for a user based on the user id.

    Args:
        id (int): User's id.
        name (str): User's name.
        email (str): User's email.
        password (str): User's password
        points (int): User's activity points.
        role (str): User's roles.
            Organised as a sorted string of values 0-5, each of them being a unique role identifier.

    Returns:
        str: 'Success!' if everything went ok.
             'Error: {error desciption}' if something went wrong.
    """
    uid = request.args.get('user')
    name = request.args.get('name')
    email = request.args.get('email')
    password = request.args.get('password')
    points = request.args.get('points')
    role = request.args.get('role')
    try:
        cur.execute('UPDATE users SET name = %s, email = %s, password = %s, points = %s, role = %s WHERE id = %s',
                    (name, email, password, points, role, uid))
        conn.commit()
        log_event("Updated user account, id:", log_level=20, kwargs=uid)
    except Exception as e:
        conn.rollback()
        log_event("Error setting account info:", log_level=30, kwargs=e)
        return f'Error: {e}'
    return 'Success'


@app.route('/admin_panel/update_pages')
@login_required
def admin_panel_update_pages():
    """
    Render the update pages page of the admin panel.

    Returns:
        str: The rendered HTML template for the update pages page.
    """
    return render_template('admin_panel_update_pages.html')


@app.route('/admin_panel/update_pages/update_image', methods=['POST'])
@login_required
def admin_panel_update_pages_update_image():
    """Update image API endpoint for the update pages page, passes the given image onto the asset delivery server.

    Args:
        request.form['image_name'] (str): file save destination on the asset delivery server
        request.files['img'] (werkzeug.datastructures.file_storage.FileStorage): The contents of the image
    """
    image_name = request.form.get('image_name')
    file = request.files.get('img')
    print(type(file))
    if file:
        # Define the URL of the other microservice
        upload_url = 'http://127.0.0.1:5001/upload_assets'

        # Prepare the files dictionary for the POST request
        files = {'file': (file.name, file.stream, file.mimetype)}

        # Send the POST request to the other microservice
        data = {'img_name': image_name}
        response = requests.post(upload_url, files=files, data=data)
        print(response.status_code)
        if response.status_code == 200:
            return 'Success', 200
        else:
            return 'Failed to upload image', 500
    return 'No file uploaded', 400


@app.route('/admin_panel/full_server_status', methods=['GET'])
@login_required
def full_server_status():
    """Returns the server statuses for all microservices running except postgres database.

    Returns:
        json: json of ram and cpu usage of every server in the format {"server_status": {"ram": number, "cpu": number}}
    """
    try:
        main_status_response = requests.get('http://127.0.0.1:5000/main_server_status', timeout=1)
        main_status = main_status_response.json()
    except (requests.exceptions.Timeout, requests.exceptions.JSONDecodeError, requests.exceptions.ConnectionError):
        main_status = {'ram': 0, 'cpu': 0}

    try:
        asset_delivery_status_response = requests.get('http://127.0.0.1:5001/asset_delivery_server_status', timeout=1)
        asset_delivery_status = asset_delivery_status_response.json()
    except (requests.exceptions.Timeout, requests.exceptions.JSONDecodeError, requests.exceptions.ConnectionError):
        asset_delivery_status = {'ram': 0, 'cpu': 0}
    admin_panel_status = {'ram': psutil.virtual_memory().percent, 'cpu': psutil.cpu_percent()}

    return jsonify({"Main server": main_status,
                    "Asset delivery": asset_delivery_status,
                    "Admin panel": admin_panel_status})


@app.route('/admin_panel/event_manager')
@login_required
def event_manager():
    return render_template('admin_panel_event_manager.html')


@app.route('/admin_panel/event_manager/new_event', methods=['POST'])
@login_required
def event_manager_new_event():
    try:
        # Get parameters from request
        game_name = request.form.get('game_name')
        game_start_time = request.form.get('game_start_time')
        game_end_time = request.form.get('game_end_time')
        team1_name = request.form.get('team1_name')
        team2_name = request.form.get('team2_name')
        team1_score = request.form.get('team1_score')
        team2_score = request.form.get('team2_score')
        livestream_link = request.form.get('livestream_link')
        video_link = request.form.get('video_link')
        game_description = request.form.get('game_description')
        match_statistic_external_link = request.form.get('match_statistic_external_link')

        game_start_time = datetime.strptime(game_start_time, '%Y-%m-%dT%H:%M')
        game_end_time = datetime.strptime(game_end_time, '%Y-%m-%dT%H:%M')

        insert_query = """
            INSERT INTO games (game_name, game_start_time, game_end_time, team1_name, team2_name,
            team1_score, team2_score, livestream_link, video_link, game_description, match_statistic_external_link)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (game_name, game_start_time, game_end_time, team1_name, team2_name,
                                   team1_score, team2_score, livestream_link, video_link,
                                   game_description, match_statistic_external_link))
        conn.commit()
        return 'Success', 200
    except Exception as e:
        conn.rollback()
        return f"Error: {e}", 400


@app.route('/admin_panel/event_manager/edit_event', methods=['POST'])
@login_required
def event_manager_edit_event():
    try:
        # Get parameters from request
        event_id = request.form.get('event_id')
        game_name = request.form.get('game_name')
        game_start_time = request.form.get('game_start_time')
        game_end_time = request.form.get('game_end_time')
        team1_name = request.form.get('team1_name')
        team2_name = request.form.get('team2_name')
        team1_score = request.form.get('team1_score')
        team2_score = request.form.get('team2_score')
        livestream_link = request.form.get('livestream_link')
        video_link = request.form.get('video_link')
        game_description = request.form.get('game_description')
        match_statistic_external_link = request.form.get('match_statistic_external_link')
        if game_start_time is not None:
            game_start_time = datetime.strptime(game_start_time, '%Y-%m-%dT%H:%M')
        else:
            game_start_time = None
        if game_end_time is not None:
            game_end_time = datetime.strptime(game_start_time, '%Y-%m-%dT%H:%M')
        else:
            game_end_time = None

        # Update in the database
        update_query = """
            UPDATE games SET game_name=%s, game_start_time=%s, game_end_time=%s,
            team1_name=%s, team2_name=%s, team1_score=%s, team2_score=%s,
            livestream_link=%s, video_link=%s, game_description=%s, match_statistic_external_link=%s
            WHERE id=%s
        """
        try:
            cur.execute(update_query, (game_name, game_start_time, game_end_time, team1_name, team2_name,
                        team1_score, team2_score, livestream_link, video_link,
                        game_description, match_statistic_external_link, event_id))
            conn.commit()
            return 'Success', 200
        except Exception as e:
            conn.rollback()
            return f'Error: {e}'

    except Exception as e:
        conn.rollback()
        return f"Error: {e}", 400


@app.route('/admin_panel/event_manager/get_event', methods=['GET'])
@login_required
def event_manager_get_event():
    """
    Fetches the details of a specific event based on the provided event_id.

    Args:
        event_id (int): The ID of the event to retrieve.

    Returns:
        json:
            200 OK: Returns the event details in JSON format if the event is found.
            404 Not Found: Returns an error message if the event with the specified ID is not found.
            400 Bad Request: Returns an error message if there is any issue during the process.
    """
    try:
        # Get the event id from request
        event_id = int(request.args.get('event_id'))

        select_query = """
            SELECT game_name, game_start_time, game_end_time, team1_name, team2_name,
                   team1_score, team2_score, livestream_link, video_link,
                   game_description, match_statistic_external_link
            FROM games
            WHERE id = %s
        """
        cur.execute(select_query, (event_id,))
        event = cur.fetchone()
        # If event not found, return error
        if event is None:
            return jsonify({"error": f"Event with id {event_id} not found"}), 404

        game_start_time = event[1]
        game_end_time = event[2]
        if game_start_time is not None:
            game_start_time = game_start_time.strftime('%Y-%m-%dT%H:%M')
        if game_end_time is not None:
            game_end_time = game_end_time.strftime('%Y-%m-%dT%H:%M')
        event_data = {
            "game_name": event[0],
            "game_start_time": game_start_time,
            "game_end_time": game_end_time,
            "team1_name": event[3],
            "team2_name": event[4],
            "team1_score": event[5],
            "team2_score": event[6],
            "livestream_link": event[7],
            "video_link": event[8],
            "game_description": event[9],
            "match_statistic_external_link": event[10]
        }
        return jsonify(event_data), 200

    except Exception as e:
        return jsonify({"error": f"Error: {e}"}), 400


@app.route('/admin_panel/product_manager')
@login_required
def product_manager():
    return render_template('admin_panel_event_manager.html')


if __name__ == "__main__":
    app.run(port=5002, debug=True)
    cur.close()
    conn.close()
