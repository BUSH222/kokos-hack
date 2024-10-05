-- USERS AND RELATED
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) UNIQUE,
    email VARCHAR(32) UNIQUE,
    password VARCHAR(32), 
    profile_pic TEXT,  -- cdn url
    register_date DATE,
    points INTEGER,
    role VARCHAR(6), -- role numbers a user has, ascending. user-0; super_fan-1; moderator-2; kokos_staff-3; player-4; admin-5;
    fav_player VARCHAR(32),
    about_me TEXT,
    telegram_acc VARCHAR(32),
    vk_acc VARCHAR(32)
);

-- NEWS
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    news_time TIMESTAMP,
    title VARCHAR(32),
    news_text TEXT,
    picture TEXT, -- cdn url
    tag TEXT -- list of tags in a string, separated by a space
);

CREATE TABLE IF NOT EXISTS news_comments (
    id SERIAL PRIMARY KEY,
    comment_time TIMESTAMP,
    post_id INTEGER,
    user_id INTEGER,
    comment_text TEXT
);

CREATE TABLE IF NOT EXISTS news_likes (
    post_id INTEGER,
    user_id INTEGER
);

-- FORUM
CREATE TABLE IF NOT EXISTS forum (
    id SERIAL PRIMARY KEY,
    post_time TIMESTAMP,
    author INTEGER,
    title VARCHAR(32),
    post_text TEXT,
    picture TEXT, -- cdn url
    tag TEXT -- list of tags in a string, separated by a space
);

CREATE TABLE IF NOT EXISTS forum_comments (
    id SERIAL PRIMARY KEY,
    comment_time TIMESTAMP,
    post_id INTEGER,
    user_id INTEGER,
    comment_text TEXT
);

CREATE TABLE IF NOT EXISTS forum_likes (
    post_id INTEGER,
    user_id INTEGER
);

-- SHOP
CREATE TABLE IF NOT EXISTS shop (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(32),
    description TEXT,
    picture TEXT -- cdn url
);

-- GAMES
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    game_name VARCHAR(32),
    game_start_time TIMESTAMP,
    game_end_time TIMESTAMP,
    team1_name VARCHAR(32),
    team2_name VARCHAR(32),
    team1_score INTEGER,
    team2_score INTEGER,
    livestream_link TEXT, -- vk video stream url
    video_link TEXT, -- vk video link, shows post match
    game_description TEXT, -- game description written by admins
    match_statistic_external_link TEXT -- external url to match stat
);

CREATE TABLE IF NOT EXISTS game_comments (
    id SERIAL PRIMARY KEY,
    comment_time TIMESTAMP,
    game_id INTEGER,
    user_id INTEGER,
    comment_text TEXT
);

CREATE TABLE IF NOT EXISTS tickets (
    fullname VARCHAR(64), -- name surname patronymic separated by spaces
    user_id INTEGER,
    game_id INTEGER
);

--LOGS
CREATE TABLE IF NOT EXISTS logs(
    id SERIAL PRIMARY KEY,
    log_time TIMESTAMP,
    log_text TEXT
);