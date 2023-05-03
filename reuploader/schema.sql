--DROP TABLE IF EXISTS user;
--DROP TABLE IF EXISTS ads;
--DROP TABLE IF EXISTS result;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    tel_num TEXT UNIQUE NOT NULL
);

--CREATE TABLE ads ();

CREATE TABLE result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    success INTEGER NOT NULL,
    message TEXT NOT NULL,
    uploaded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);