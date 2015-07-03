DROP TABLE if exists entries;
DROP TABLE if exists users;
CREATE TABLE entries (
    id integer PRIMARY KEY autoincrement,
    children text,
    message text,
    parent integer,
    user_id integer
    );

CREATE TABLE users (
    user_id integer PRIMARY KEY autoincrement,
    username text ,
    password text);
