from flask import Flask, render_template
from datetime import datetime, timedelta

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
        'news_photo_url': '/static/eye.png',  # Path to your news photo
        'text': 'Сегодня в нашем клубе произошло замечательное событие. Мы рады сообщить, что клуб очень крутой короче и ваще топ 1 скоро станет я верю в это правда. Вообще я пишу много текста чтобы проверить работает ли скролл)) судя по всему не очень он работает, точнее нет, он по идее работает вот только окно с текстом выходит за рамки и это надо фиксить срочно! а нет с ним все хорошо ну ладно тогда я просто попишу еще чего нибудь смешного и неинтересного чтобы просто всего лишь проверить работу того что я накалякал. Честно говоря я уже устал делать только одну эту страницу целый день я уже хочу просто лечь в постель, посмотреть ют, выспаться и уже завтра продолжить и да Федя я помню что мне нужно сделать еще всего лишь +-20 страниц за 1 завтрашний день bruhhh я не знаю как мне вообще выжить с такой нагрузкой! hkjdgamfjsgddghfgdhjfahjgdfhjkgafkghjafdkghdfghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghuuauau',
        'profile_picture_url': '/static/google_icon.png',  # Path to the current user's profile picture
        'username': 'Текущий Пользователь',  # Username of the current user
        'date_created': '2024-10-09'  # Example creation date for the post
    }

    max_news_data = [news_data for _ in range(3)]
    
    return render_template('news.html', data=max_news_data, post={'id': 1})

@app.route('/forum')
def forum():
    # Sample data for the news post
    news_data = {
        'title': 'Boeing jets just hit the twin towers',
        'tags': 'USA, tragedy, crash',
        'news_photo_url': '/static/eye.png',  # Path to your news photo
        'text': 'Сегодня в нашем twin towers произошло horrible событие. Мы рады сообщить, что 2979 people died that day. Вообще я пишу много текста чтобы проверить работает ли скролл)) судя по всему не очень он работает, точнее нет, он по идее работает вот только окно с текстом выходит за рамки и это надо фиксить срочно! а нет с ним все хорошо ну ладно тогда я просто попишу еще чего нибудь смешного и неинтересного чтобы просто всего лишь проверить работу того что я накалякал. Честно говоря я уже устал делать только одну эту страницу целый день я уже хочу просто лечь в постель, посмотреть ют, выспаться и уже завтра продолжить и да Федя я помню что мне нужно сделать еще всего лишь +-20 страниц за 1 завтрашний день bruhhh я не знаю как мне вообще выжить с такой нагрузкой! hkjdgamfjsgddghfgdhjfahjgdfhjkgafkghjafdkghdfghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghuuauau',
        'profile_picture_url': '/static/google_icon.png',  # Path to the current user's profile picture
        'username': 'Текущий Пользователь',  # Username of the current user
        'date_created': '2001-09-1'  # Example creation date for the post
    }

    max_news_data = [news_data for _ in range(3)]
    
    return render_template('forum.html', data=max_news_data, post={'id': 1})

@app.route('/shop')
def shop():
    # Sample data for the news post
    news_data = {
        'title': 'goobab',
        'price': '825',
        'news_photo_url': '/static/goobab.jpg',  # Path to your news photo
        'text': 'epic goobab merch or something buy now or die 神说：要有光， 就有了光。',
        'date_created': '2024-10-09'  # Example creation date for the post
    }

    max_news_data = [news_data for _ in range(3)]
    
    return render_template('shop.html', data=max_news_data)


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

# Sample games data
games = [
    {'id': 1, 'team1': 'Team A', 'team2': 'Team B', 'datetime': '2024-10-15 18:00'},
    {'id': 2, 'team1': 'Team C', 'team2': 'Team D', 'datetime': '2024-10-16 19:00'},
    {'id': 3, 'team1': 'Team E', 'team2': 'Team F', 'datetime': '2024-10-17 20:00'}
]

# Sample data for current and upcoming games
current_game = {
    'id': 1,
    'team1': 'Команда Г',
    'team1_logo_url': '/static/team1_logo.png',
    'team2': 'Команда Д',
    'team2_logo_url': '/static/team2_logo.png',
    'datetime': '2024-10-14 20:00'  # Example current game time
}

upcoming_game = {
    'id': 2,
    'team1': 'Команда А',
    'team1_logo_url': '/static/team1_logo.png',
    'team2': 'Команда Б',
    'team2_logo_url': '/static/team2_logo.png',
    'datetime': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")  # Set to tomorrow
}

@app.route('/games')
def games_view():
    return render_template('games.html', current_game=current_game, upcoming_game=upcoming_game, games=games)


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


# Sample games data
games = [
    {'id': 1, 'team1': 'Team A', 'team2': 'Team B', 'datetime': '2024-10-15 18:00'},
    {'id': 2, 'team1': 'Team C', 'team2': 'Team D', 'datetime': '2024-10-16 19:00'},
    {'id': 3, 'team1': 'Team E', 'team2': 'Team F', 'datetime': '2024-10-17 20:00'}
]

@app.route('/games')
def games_page():
    return render_template('games.html', games=games)


@app.route('/view-story')
def view_story():
    comments = [
    {'user': {'username': 'CoolGamer', 'profile_picture_url': '/static/profile2.png'}, 
     'text': 'This is an amazing post!', 
     'date_posted': '2024-09-15 14:23:41'},

    {'user': {'username': 'TechGeek', 'profile_picture_url': '/static/profile3.png'}, 
     'text': 'Wow, such a great read!', 
     'date_posted': '2024-10-05 11:09:58'},

    {'user': {'username': 'User2', 'profile_picture_url': '/static/profile1.png'}, 
     'text': 'Can you explain more about this?', 
     'date_posted': '2024-09-28 18:34:07'}]

    data = {
        'title': 'Новое событие в клубе!',
        'tags': 'Спорт, Клуб, Новости',
        'news_photo_url': '/static/eye.png',  # Path to your news photo
        'text': 'Сегодня в нашем клубе произошло замечательное событие. Мы рады сообщить, что клуб очень крутой короче и ваще топ 1 скоро станет я верю в это правда. Вообще я пишу много текста чтобы проверить работает ли скролл)) судя по всему не очень он работает, точнее нет, он по идее работает вот только окно с текстом выходит за рамки и это надо фиксить срочно! а нет с ним все хорошо ну ладно тогда я просто попишу еще чего нибудь смешного и неинтересного чтобы просто всего лишь проверить работу того что я накалякал. Честно говоря я уже устал делать только одну эту страницу целый день я уже хочу просто лечь в постель, посмотреть ют, выспаться и уже завтра продолжить и да Федя я помню что мне нужно сделать еще всего лишь +-20 страниц за 1 завтрашний день bruhhh я не знаю как мне вообще выжить с такой нагрузкой! hkjdgamfjsgddghfgdhjfahjgdfhjkgafkghjafdkghdfghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghuuauau',
        'profile_picture_url': '/static/google_icon.png',  # Path to the current user's profile picture
        'username': 'Текущий Пользователь',  # Username of the current user
        'date_created': '2024-10-09'  # Example creation date for the post
    }
    return render_template('view-story.html', data=data, comments=comments)


@app.route('/view-post')
def view_post():
    comments = [
    {'user': {'username': 'CoolGamer', 'profile_picture_url': '/static/profile2.png'}, 
     'text': 'This is an amazing post!', 
     'date_posted': '2024-09-15 14:23:41'},

    {'user': {'username': 'TechGeek', 'profile_picture_url': '/static/profile3.png'}, 
     'text': 'Wow, such a great read!', 
     'date_posted': '2024-10-05 11:09:58'},

    {'user': {'username': 'User2', 'profile_picture_url': '/static/profile1.png'}, 
     'text': 'Can you explain more about this?', 
     'date_posted': '2024-09-28 18:34:07'}]

    data = {
        'title': 'Новое событие в клубе!',
        'tags': 'Спорт, Клуб, Новости',
        'news_photo_url': '/static/eye.png',  # Path to your news photo
        'text': 'Сегодня в нашем клубе произошло замечательное событие. Мы рады сообщить, что клуб очень крутой короче и ваще топ 1 скоро станет я верю в это правда. Вообще я пишу много текста чтобы проверить работает ли скролл)) судя по всему не очень он работает, точнее нет, он по идее работает вот только окно с текстом выходит за рамки и это надо фиксить срочно! а нет с ним все хорошо ну ладно тогда я просто попишу еще чего нибудь смешного и неинтересного чтобы просто всего лишь проверить работу того что я накалякал. Честно говоря я уже устал делать только одну эту страницу целый день я уже хочу просто лечь в постель, посмотреть ют, выспаться и уже завтра продолжить и да Федя я помню что мне нужно сделать еще всего лишь +-20 страниц за 1 завтрашний день bruhhh я не знаю как мне вообще выжить с такой нагрузкой! hkjdgamfjsgddghfgdhjfahjgdfhjkgafkghjafdkghdfghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgkhfdgkafdghkfdsghdfsghkfhkgakghadfskghadsfkhgafdskghghkakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghakgdfhsgdfghkfgk hfdgkafdghkfdsghdfs ghkfhkgakghadfskghadsfkh gafdskghghkakgdfhsgdfg hkfgkhfdgkafdgh kfdsghdfsghkfhkgakghadf skghadsfkhgafdskgh ghkakgdfhsgdfghk fgkhfdgkafdghkfdsghdfsghkfhkgakgha dfskghadsfkhgafdsk ghuuauau',
        'profile_picture_url': '/static/google_icon.png',  # Path to the current user's profile picture
        'username': 'Текущий Пользователь',  # Username of the current user
        'date_created': '2024-10-09'  # Example creation date for the post
    }
    return render_template('view-post.html', data=data, comments=comments)


@app.route('/new-post')
def new_post():
    return render_template('new-post.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)