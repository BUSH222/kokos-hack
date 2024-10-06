from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_login import login_user, LoginManager, login_required, UserMixin
from dbloader import connect_to_db
import requests
import requests.exceptions
import psutil


app = Flask(__name__)
app.config['SECRET_KEY'] = 'CHANGE_ME_AS_SOON_AS_POSSIBLE'  # CHANGE THIS
login_manager = LoginManager(app)
login_manager.login_view = 'login'

conn, cur = connect_to_db()


class User(UserMixin):
    def __init__(self, id, username, password) -> None:
        self.id = id
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
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
        username = request.form['username']
        password = request.form['password']
        cur.execute('SELECT id, name, password FROM users WHERE name = %s AND role LIKE %s', (username, '%5%'))
        user_data = cur.fetchone()
        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(*user_data)
                login_user(user)
                return redirect(url_for('admin_panel'))
            else:
                return "Invalid username or password"
        else:
            return "Registration not allowed or user is not admin"
    else:
        return render_template('admin_panel_login.html')


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
    Delete a user account based on the user name.

    Args:
        user (str): The username of the account to delete.

    Returns:
        bool: True if the account was successfully deleted, False otherwise.
    """
    user = request.args.get('user')
    cur.execute('DELETE FROM users WHERE name = %s', (user, ))
    if cur.rowcount == 0:
        return False
    conn.commit()
    return True


@app.route('/admin_panel/community/view_roles')
@login_required
def admin_panel_community_view_roles():
    """
    View the roles of a user based on the name.

    Args:
        user (str): The username of the account to view roles for.

    Returns:
        str: The roles of the user.
        bool: False if the user does not exist.
    """
    user = request.args.get('user')
    cur.execute('SELECT role FROM users WHERE name = %s', (user, ))
    roles_raw = cur.fetchone()
    if not roles_raw:
        return False
    return roles_raw[0]


@app.route('/admin_panel/community/set_roles')
@login_required
def admin_panel_community_set_roles():
    """
    Set the roles for a user based on the name.

    Args:
        user (str): The username of the account to set roles for.
        roles (str): The roles to assign to the user.

    Returns:
        bool: True if the roles were successfully set, False otherwise.
    """
    user = request.args.get('user')
    roles = request.args.get('roles')
    cur.execute('UPDATE users SET role = %s WHERE name = %s', (roles, user))
    conn.commit()
    return True


@app.route('/admin_panel/community/view_activity_points')
@login_required
def admin_panel_community_view_activity_points():
    """
    View the activity points of a user.

    Args:
        user (str): The username of the account to view activity points for.

    Returns:
        int: The activity points of the user.
        bool: False if the user does not exist.
    """
    user = request.args.get('user')
    cur.execute('SELECT points FROM users WHERE name = %s', (user, ))
    points = cur.fetchone()
    if not points:
        return False
    return str(points[0])


@app.route('/admin_panel/community/set_activity_points')
@login_required
def admin_panel_community_set_activity_points():
    """
    Set the activity points for a user in the community.

    Args:
        user (str): The username of the account to set activity points for.
        points (int): The activity points to assign to the user.

    Returns:
        bool: True if the activity points were successfully set, False otherwise.
    """
    user = request.args.get('user')
    points = request.args.get('user')
    cur.execute('UPDATE users SET points = %s WHERE name = %s', (int(points), user))
    if cur.rowcount == 0:
        return False
    conn.commit()
    return True


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
    image_name = request.form.get('image_name')
    file = request.files.get('img')
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


@app.route('/admin_panel/full_server_status')
@login_required
def full_server_status():
    """Returns the server statuses for all microservices running except postgres database.

    Returns:
        json: json of ram and cpu usage of every server in the format {"server_status": {"ram": number, "cpu": number}}
    """
    try:
        main_status = requests.get('http://172.0.0.1:5000/main_server_status', timeout=0.1).json()
    except requests.exceptions.Timeout:
        main_status = {'ram': 0, 'cpu': 0}
    try:
        asset_delivery_status = requests.get('http://172.0.0.1:5001/asset_delivery_server_status', timeout=0.1).json()
    except requests.exceptions.Timeout:
        asset_delivery_status = {'ram': 0, 'cpu': 0}
    admin_panel_status = {'ram': psutil.virtual_memory().percent, 'cpu': psutil.cpu_percent()}

    return jsonify({"main_status": main_status,
                    "asset_delivery_status": asset_delivery_status,
                    "admin_panel_status": admin_panel_status})


if __name__ == "__main__":
    app.run(port=5002, debug=True)
    cur.close()
    conn.close()
