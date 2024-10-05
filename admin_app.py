from flask import Flask, render_template, redirect, request, url_for, abort
from flask_login import login_user, LoginManager, current_user, login_required, UserMixin
from dbloader import connect_to_db
import logging


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
    print(user_data)
    if user_data:
        return User(*user_data)
    return None



@app.route('/admin_panel')
@login_required
def admin_panel():
    print(current_user.is_authenticated)
    return render_template('admin_panel.html')


@app.route('/admin_panel/login', methods=['GET', 'POST'])
def login():
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
    return render_template('admin_panel_community.html')


@app.route('/admin_panel/community/delete_account')
@login_required
def admin_panel_community_delete_account():
    user = request.args.get('user')
    cur.execute('DELETE FROM users WHERE name = %s', (user, ))
    if cur.rowcount == 0:
        return False
    conn.commit()
    return True

@app.route('/admin_panel/community/add_role')
@login_required
def admin_panel_community_add_role():
    user = request.args.get('user')
    role = request.args.get('role')
    cur.execute('SELECT role FROM users WHERE name = %s', (user, ))
    roles = list(cur.fetchone()[0])
    if cur.rowcount == 0:
        return False
    conn.commit()
    return True



if __name__ == "__main__":
    app.run(port=5002, debug=True)
    cur.close()
    conn.close()
