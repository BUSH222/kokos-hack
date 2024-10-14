-- Insert data into users table
INSERT INTO users (name, email, password, profile_pic, register_date, points, role, fav_player, about_me, telegram_acc, vk_acc)
VALUES
('John Doe', 'john@example.com', 'password123', 'https://cdn.example.com/john.jpg', '2024-01-01', 100, '0', 'Player A', 'I love football!', '@john_doe', 'john_vk'),
('Jane Smith', 'jane@example.com', 'password456', 'https://cdn.example.com/jane.jpg', '2024-02-01', 200, '1', 'Player B', 'Football is life!', '@jane_smith', 'jane_vk'),
('Alice Johnson', 'alice@example.com', 'password789', 'https://cdn.example.com/alice.jpg', '2024-03-01', 150, '', 'Player C', 'Go team!', '@alice_johnson', 'alice_vk'),
('Bob Brown', 'bob@example.com', 'password321', 'https://cdn.example.com/bob.jpg', '2024-04-01', 250, '34', 'Player D', 'Football fanatic!', '@bob_brown', 'bob_vk'),
('Charlie Davis', 'charlie@example.com', 'password654', 'https://cdn.example.com/charlie.jpg', '2024-05-01', 300, '4', 'Player E', 'Live for the game!', '@charlie_davis', 'charlie_vk'),
('admin', 'admin@admin.com', 'admin', 'https://cdn.example.com/charlie.jpg', '2024-10-5', 0, '5', NULL, NULL, NULL, NULL);

-- Insert data into news table
INSERT INTO news (news_time, title, news_text, picture, tag)
VALUES
('2024-10-01 10:00:00', 'Big Match Coming Up', 'Don''t miss the big match this weekend!', 'https://cdn.example.com/match.jpg', 'match upcoming'),
('2024-10-02 12:00:00', 'Player Transfer News', 'We have signed a new player!', 'https://cdn.example.com/transfer.jpg', 'transfer player'),
('2024-10-03 14:00:00', 'Training Session', 'Open training session this Friday.', 'https://cdn.example.com/training.jpg', 'training session'),
('2024-10-04 16:00:00', 'Match Highlights', 'Check out the highlights from our last game.', 'https://cdn.example.com/highlights.jpg', 'highlights match'),
('2024-10-05 18:00:00', 'Fan Meet and Greet', 'Meet your favorite players this Saturday.', 'https://cdn.example.com/meet.jpg', 'fan event');

-- Insert data into news_comments table
INSERT INTO news_comments (comment_time, post_id, user_id, comment_text)
VALUES
('2024-10-01 11:00:00', 1, 1, 'Can''t wait for the match!'),
('2024-10-02 13:00:00', 2, 2, 'Great signing!'),
('2024-10-03 15:00:00', 3, 3, 'Looking forward to it!'),
('2024-10-04 17:00:00', 4, 4, 'Amazing highlights!'),
('2024-10-05 19:00:00', 5, 5, 'Excited to meet the players!');

-- Insert data into forum table
INSERT INTO forum (post_time, author, title, post_text, picture, tag)
VALUES
('2024-10-01 09:00:00', 1, 'Match Predictions', 'What are your predictions for the upcoming match?', 'https://cdn.example.com/predictions.jpg', 'match predictions'),
('2024-10-02 10:00:00', 2, 'New Player Discussion', 'Let''s talk about our new player.', 'https://cdn.example.com/new_player.jpg', 'player discussion'),
('2024-10-03 11:00:00', 3, 'Training Tips', 'Share your best training tips.', 'https://cdn.example.com/tips.jpg', 'training tips'),
('2024-10-04 12:00:00', 4, 'Favorite Matches', 'What are your favorite matches?', 'https://cdn.example.com/favorites.jpg', 'matches favorites'),
('2024-10-05 13:00:00', 5, 'Fan Stories', 'Share your best fan stories.', 'https://cdn.example.com/stories.jpg', 'fan stories');

-- Insert data into forum_comments table
INSERT INTO forum_comments (comment_time, post_id, user_id, comment_text)
VALUES
('2024-10-01 10:00:00', 1, 2, 'I think we will win!'),
('2024-10-02 11:00:00', 2, 1, 'Excited to see him play!'),
('2024-10-03 12:00:00', 3, 3, 'Great tips!'),
('2024-10-04 13:00:00', 4, 4, 'My favorite match was last year''s final.'),
('2024-10-05 14:00:00', 5, 5, 'I met the team last year, it was awesome!');

-- Insert data into shop table
INSERT INTO shop (product_name, price, sales, description, picture)
VALUES
('Team Jersey', 100, 123, 'Official team jersey', 'https://cdn.example.com/jersey.jpg'),
('Football', 200, 456, 'Official match football', 'https://cdn.example.com/football.jpg'),
('Scarf', 300, 789, 'Team scarf', 'https://cdn.example.com/scarf.jpg'),
('Cap', 400, 12, 'Team cap', 'https://cdn.example.com/cap.jpg'),
('Poster', 500, 345, 'Team poster', 'https://cdn.example.com/poster.jpg');

-- Insert data into games table
INSERT INTO games (game_name, game_start_time, game_end_time, team1_name, team2_name, team1_score, team2_score, livestream_link, video_link, game_description, match_statistic_external_link)
VALUES
('Match 1', '2024-10-05 15:00:00', '2024-10-05 17:00:00', 'Team A', 'Team B', 2, 1, 'https://vk.com/livestream1', 'https://vk.com/video1', 'Exciting match between Team A and Team B.', 'https://stats.example.com/match1'),
('Match 2', '2024-10-12 18:00:00', '2024-10-12 20:00:00', 'Team C', 'Team D', 3, 3, 'https://vk.com/livestream2', 'https://vk.com/video2', 'Thrilling draw between Team C and Team D.', 'https://stats.example.com/match2'),
('Match 3', '2024-10-19 16:00:00', '2024-10-19 18:00:00', 'Team E', 'Team F', 1, 2, 'https://vk.com/livestream3', 'https://vk.com/video3', 'Close match between Team E and Team F.', 'https://stats.example.com/match3'),
('Match 4', '2024-10-26 14:00:00', '2024-10-26 16:00:00', 'Team G', 'Team H', 4, 0, 'https://vk.com/livestream4', 'https://vk.com/video4', 'Dominant performance by Team G.', 'https://stats.example.com/match4'),
('Match 5', '2024-11-02 17:00:00', '2024-11-02 19:00:00', 'Team I', 'Team J', 2, 2, 'https://vk.com/livestream5', 'https://vk.com/video5', 'Entertaining draw between Team I and Team J.', 'https://stats.example.com/match5');

-- Insert data into game_comments table
INSERT INTO game_comments (comment_time, game_id, user_id, comment_text)
VALUES
('2024-10-05 16:00:00', 1, 1, 'What a goal!'),
('2024-10-12 19:00:00', 2, 2, 'Amazing match!'),
('2024-10-19 17:00:00', 3, 3, 'So close!'),
('2024-10-26 15:00:00', 4, 4, 'Incredible performance!'),
('2024-11-02 18:00:00', 5, 5, 'Great game!');

-- Insert data into tickets table
INSERT INTO tickets (fullname, user_id, game_id)
VALUES
('John Doe', 1, 1),
('Jane Smith', 2, 2),
('Alice Johnson', 3, 3),
('Bob Brown', 4, 4),
('Charlie Davis', 5, 5);

-- Insert data into logs table
INSERT INTO logs (log_time, log_text)
VALUES
('2024-10-05 15:00:00', 'User John Doe logged in.'),
('2024-10-12 18:00:00', 'User Jane Smith purchased a ticket.');

INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Авдеев Павел Александрович.jpg', 'Авдеев Павел Александрович', '1', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Азембловский Никита Дмитриевич.jpg', 'Азембловский Никита Дмитриевич', '2', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Алисеевич Георгий Константинович.jpg', 'Алисеевич Георгий Константинович', '3', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Васёв Николай Владимирович.jpg', 'Васёв Николай Владимирович', '4', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Власов Виктор Валерьевич.jpg', 'Власов Виктор Валерьевич', '5', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Гончаров Павел Александрович.jpg', 'Гончаров Павел Александрович', '6', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Гусев Константин Алексеевич.jpg', 'Гусев Константин Алексеевич', '7', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Домрачев Иван Леонидович.jpg', 'Домрачев Иван Леонидович', '8', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Елизаров Никита Алексеевич.jpg', 'Елизаров Никита Алексеевич', '9', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Жежа Павел Викторович.jpeg', 'Жежа Павел Викторович', '10', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Зыбин Александр Сергеевич.jpg', 'Зыбин Александр Сергеевич', '11', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Иванов Андрей Александрович-III.jpg', 'Иванов Андрей Александрович-III', '12', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Иминжанов Анвар Акмалжанович.jpg', 'Иминжанов Анвар Акмалжанович', '13', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Иноземцев Кирилл Алексеевич.jpg', 'Иноземцев Кирилл Алексеевич', '14', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Карев Александр Викторович.jpg', 'Карев Александр Викторович', '15', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Кашкаров Дмитрий Валерьевич.png', 'Кашкаров Дмитрий Валерьевич', '16', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Комягин Михаил Александрович.jpg', 'Комягин Михаил Александрович', '17', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Комяжко Кирилл Евгеньевич.jpg', 'Комяжко Кирилл Евгеньевич', '18', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Кондаков Антон Вячеславович.jpg', 'Кондаков Антон Вячеславович', '19', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Кудьяров Владислав Сергеевич.jpg', 'Кудьяров Владислав Сергеевич', '20', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Кукарин Павел Сергеевич.jpg', 'Кукарин Павел Сергеевич', '21', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Леденёв Роман Владимирович.jpg', 'Леденёв Роман Владимирович', '22', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Лидинёв Олег Васильевич.jpg', 'Лидинёв Олег Васильевич', '23', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Максутов Марат Каюмович.jpg', 'Максутов Марат Каюмович', '24', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Мареев Юрий Юрьевич.jpg', 'Мареев Юрий Юрьевич', '25', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Марьяшин Павел Андреевич.jpg', 'Марьяшин Павел Андреевич', '26', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Нестеров Александр Вадимович.jpg', 'Нестеров Александр Вадимович', '27', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Папоян Вачаган Ервандович.jpg', 'Папоян Вачаган Ервандович', '28', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Пиньков Юрий Юрьевич.jpg', 'Пиньков Юрий Юрьевич', '29', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Погребняк Артём Павлович.jpg', 'Погребняк Артём Павлович', '30', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Погребняк Кирилл Викторович.jpg', 'Погребняк Кирилл Викторович', '31', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Погребняк Павел Викторович.jpg', 'Погребняк Павел Викторович', '32', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Рыков Владимир Владимирович.jpg', 'Рыков Владимир Владимирович', '33', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Сутормин Алексей Сергеевич.jpeg', 'Сутормин Алексей Сергеевич', '34', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Терехов Антон Андреевич.jpg', 'Терехов Антон Андреевич', '35', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Терещенко Павел Сергеевич.jpg', 'Терещенко Павел Сергеевич', '36', 'Goalkeeper', 'Tall and agile');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Фомин Николай Николаевич.jpg', 'Фомин Николай Николаевич', '37', 'Defender', 'Strong in defense');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Цыбиков Александр Александрович.jpg', 'Цыбиков Александр Александрович', '38', 'Midfielder', 'Skilled midfielder');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Черкашин Артём Дмитриевич.jpg', 'Черкашин Артём Дмитриевич', '39', 'Forward', 'Quick attacker');
INSERT INTO team_members (picture_url, name, player_num, position, description) VALUES ('http://localhost:5001/assets/players/Шокуров Александр Викторович.jpg', 'Шокуров Александр Викторович', '40', 'Goalkeeper', 'Tall and agile');