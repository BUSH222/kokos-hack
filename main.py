from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/admin_panel_login')
def admin_panel_login():
    return render_template("admin_panel_login.html")

@app.route('/admin_panel/logs')
def admin_panel_logs():
    return render_template("admin_panel_logs.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)