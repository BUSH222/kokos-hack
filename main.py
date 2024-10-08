from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/yandex')
def login_yandex():
    # Handle Yandex login
    return "Redirecting to Yandex login..."

@app.route('/login/google')
def login_google():
    # Handle Google login
    return "Redirecting to Google login..."

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handle registration logic here
    return render_template('register.html')

@app.route('/account')
def account():
    user_logged_in = True
    user = {
        'nickname': 'nickname',  # Add the actual nickname
        'profile_picture_url': '/static/profile-picture.png',  # URL to profile picture
        'about': 'About user',  # Add the actual about info
        'telegram_url': 'https://t.me/kokocfan',  # Telegram link
        'telegram_handle': 'kokocfan',  # Telegram handle
        'vk_url': 'https://vk.com/kokocfan',  # VK link
        'vk_handle': 'kokocfan'  # VK handle
    }
    return render_template('account.html', user_logged_in=user_logged_in, user=user)
@app.route('/view-account')
def view_account():
    user_logged_in = True
    user = {
        'nickname': 'nickname',  # Add the actual nickname
        'profile_picture_url': '/static/profile-picture.png',  # URL to profile picture
        'about': 'About user',  # Add the actual about info
        'telegram_url': 'https://t.me/kokocfan',  # Telegram link
        'telegram_handle': 'kokocfan',  # Telegram handle
        'vk_url': 'https://vk.com/kokocfan',  # VK link
        'vk_handle': 'kokocfan'  # VK handle
    }
    return render_template('view-account.html', user_logged_in=user_logged_in, user=user)

@app.route('/admin_panel_login')
def admin_panel_login():
    return render_template("admin_panel_login.html")

@app.route('/admin_panel/logs')
def admin_panel_logs():
    return render_template("admin_panel_logs.html")

@app.route('/admin_panel/update_pages', methods=['GET'])
def update_pages():
    return render_template('update_pages.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)