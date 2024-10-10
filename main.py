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

@app.route('/news')
def news():
    # Sample data for the news post
    news_data = {
        'title': 'Новое событие в клубе!',
        'tags': 'Спорт, Клуб, Новости',
        'news_photo_url': '/static/player.jpg',  # Path to your news photo
        'text': 'Сегодня в нашем клубе произошло замечательное событие. Мы рады сообщить, что клуб очень крутой короче и ваще топ 1 скоро станет я верю в это правда. Вообще я пишу много текста чтобы проверить работает ли скролл)) судя по всему не очень он работает, точнее нет, он по идее работает вот только окно с текстом выходит за рамки и это надо фиксить срочно! а нет с ним все хорошо ну ладно тогда я просто попишу еще чего нибудь смешного и неинтересного чтобы просто всего лишь проверить работу того что я накалякал. Честно говоря я уже устал делать только одну эту страницу целый день я уже хочу просто лечь в постель, посмотреть ют, выспаться и уже завтра продолжить и да Федя я помню что мне нужно сделать еще всего лишь +-20 страниц за 1 завтрашний день bruhhh я не знаю как мне вообще выжить с такой нагрузкой!',
        # Example user data
        'user': {
            'profile_picture_url': '/static/google_icon.png',  # Path to the current user's profile picture
            'username': 'Текущий Пользователь',  # Username of the current user
        },
        'post': {
            'date_created': '2024-10-09'  # Example creation date for the post
        }
    }
    
    return render_template('news.html', **news_data)

@app.route('/account')
def account():
    user_logged_in = True
    user = {
        'nickname': 'nickname',  # Add the actual nickname
        'profile_picture_url': '/static/google_icon.png',  # URL to profile picture
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