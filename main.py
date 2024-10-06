from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/account')
def account():
    return render_template('account.html')

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