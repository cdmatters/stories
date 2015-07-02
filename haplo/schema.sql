DROP TABLE if exists entries;
CREATE TABLE entries (
    id integer PRIMARY KEY autoincrement,
    children text,
    message text,
    parent integer,
    user_id integer
    );
