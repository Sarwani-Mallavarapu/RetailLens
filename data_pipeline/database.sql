DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS category_master;
DROP TABLE IF EXISTS availability_master;


CREATE TABLE category_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT UNIQUE NOT NULL
);


CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    category_id INTEGER,
    availability boolean,

    FOREIGN KEY (category_id)
        REFERENCES category_master(id)
);