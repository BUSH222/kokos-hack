# Кокос хакатон, кейс 1; решение команды MISIS LEAF LOVERS

ХАКАТОН ШЁЛ 10-12 ДНЕЙ, ЗАБЫЛ УКАЗАТЬ В ГУГЛФОРМЕ

Этот проект представляет собой веб-платформу для футбольного клуба, которая позволяет фанатам взаимодействовать, следить за новостями клуба, смотреть игры в прямом эфире и многое другое. 

> см презентацию в репозитории

## Члены команды
- Второв Фёдор(team lead, fullstack, разработка: бд, эндпоинты адимн панели, помогал с фронтом)
- Емельянцев Михаил(backend, разработка эндпоинтов пользовательской части)
- Великанов Вадим(frontend, планировка проекта, js, html, css))
- Панов Никита(devops, разработка: бд, docker-compose и эндпоинты регистрации и логина)

## Демонстрация продукта
- Юзер часть
![image](https://github.com/user-attachments/assets/471f1b11-be70-407b-8ae6-4717e7c6a661)
![image](https://github.com/user-attachments/assets/2e006560-cc5e-4dc1-ad08-b74d5c8082b0)
- Адимн часть
![image](https://github.com/user-attachments/assets/1f1bc6ec-23c1-4339-a5f6-cfa66023202c)


# КАК ЗАПУСТИТЬ

> Склонировать репозиторий

> (НЕ РАБОТАЕТ) Запустите докер контейнеры используя docker-compose up

! ЕСЛИ НЕ РАБОТАЕТ, ЗАПУСТИТЕ ТЕСТОВЫЙ СЕРВЕР 

1. Чтобы настроить дб поставьте пароль администратора postgres 12345678
2. установите все библиотеки в requirements.txt
3. cd в web и запустите dbloader.py
4. Запустите файл run.sh или main.py и admin_app.py по отдельности
5. Зайдите на https://localhost:5000 для юзер части и https://localhost:5002/admin_panel для админ части
6. Зайти на юзера: 'admin':'admin' либо 'Bob Brown':'password321'

# КАК РАБОТАЕТ
### Технологии и инструменты
- Flask
- Postgres
- HTML/CSS
- JS
- Docker

### Библиотеки(основные)
- Flask==2.2.5
- Flask_Limiter==3.8.0
- Flask_Login==0.6.2
- oauthlib==3.2.2
- psutil==5.9.8
- psycopg2_binary==2.9.9
- python-dotenv==1.0.1
- Requests==2.32.3

Мы использовали микросервисную архитекруру - у нас 4 микросервиса

1. web (main.py) - главный микросервис, содержит большую часть логики и отвечает за весь пользовательский интерфейс
2. admin_panel (admin_panel.py) - панель администратора, с этой панели администратор может контролировать все остальные сервера, а также просматривать их нагруженность
3. asset_contain (asset_delivery.py) - микросервис на котором размещаются все картинки пользователей
4. postgresql - база данных

## web (main.py)
### Главная страница:

На главной странице представлены предстоящие матчи, где вы можете заказать билет или посмотреть прямую трансляцию на платформе VK.
Также отображаются три самых популярных новости клуба и три самых продаваемых товара из магазина.
Навигационная панель:

### Навигационная панель:

На сайте есть навигационная панель, которая перенаправляет на следующие страницы: новости, игры, магазин, информация о клубе и форум.

### Новости:

На этой странице представлены все опубликованные новости клуба.
Вы можете лайкать новости и оставлять комментарии.
Также есть панель поиска с функциями фильтрации по тегам и дате.

### Игры:

Внизу страницы отображаются предстоящие матчи, где можно заказать билет или посмотреть прямую трансляцию игры на платформе VK.
Также представлены все прошедшие игры футбольного клуба.

### Магазин:

На странице магазина представлены все товары, которые вы можете приобрести.

### О клубе:

На этой странице вы можете ознакомиться с историей и достижениями футбольного клуба.

### Форум:

На форуме пользователи могут взаимодействовать друг с другом, создавать собственные посты, добавлять изображения, писать тексты и добавлять теги, чтобы помочь другим пользователям найти ваш пост.
Также присутствует панель поиска, аналогичная той, что на странице новостей.

### Аккаунт:

На странице аккаунта вы можете настроить свой профиль: добавить свои социальные сети, фотографию профиля и даже выбрать своего любимого игрока клуба.
Также предусмотрена система очков сообщества, которые можно зарабатывать и использовать, а также указание вашей роли: пользователь (0), суперфан (1), модератор (2), персонал кокоса (3), игрок (4), администратор (5).

### Панель администратора:

На панели администратора можно отслеживать статистику сервера, например нагрузку ЦП. Также можно изменять данные пользователей, отслеживать логи и др. Есть кнопка help и адаптивная верстка.

## Архитектура и структура проекта
![image](https://github.com/user-attachments/assets/10ff9179-7746-484d-88a1-9aaa9202e807)


## Заключение
Успели реализовать большую часть задачи, в отличии от большинства команд успели сделать необходимые странциы и связть фронт с беком. В качестве улучшения можно доделать онлайн магазин и сделать из приложения чуть ли не полноценную социальную сеть.
