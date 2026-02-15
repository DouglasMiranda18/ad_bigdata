DROP TABLE IF EXISTS guests;
DROP TABLE IF EXISTS gifts;

CREATE TABLE guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE gifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL,
    reserved_by INTEGER,
    payment_method TEXT,
    FOREIGN KEY (reserved_by) REFERENCES guests (id)
);
