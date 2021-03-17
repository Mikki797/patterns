CREATE TABLE products (
        id serial PRIMARY KEY,
        name text UNIQUE NOT NULL,
        price money NOT NULL CHECK (price::numeric > 0)
    );

CREATE TABLE users (
        login varchar(32) PRIMARY KEY,
        password varchar(60) DEFAULT NULL, -- хэшировано, TODO добавить NOT NULL
        secret_question varchar(128) DEFAULT NULL, -- TODO добавить NOT NULL
        secret_question_answer varchar(60) DEFAULT NULL, --хэшировано, TODO добавить NOT NULL
        name varchar(32) DEFAULT NULL
    );

CREATE TYPE status as ENUM ('save', 'in_way', 'received');
CREATE TYPE delivery as ENUM ('none', 'common', 'express');

CREATE TABLE orders (
        id serial PRIMARY KEY,
        order_time timestamptz NOT NULL DEFAULT (CURRENT_TIMESTAMP),
        current_status status NOT NULL,
        delivery_type delivery NOT NULL,
        price money NOT NULL CHECK (price::numeric > 0),
        login varchar(32) REFERENCES users
    );

CREATE TABLE orders_products (
        order_id integer REFERENCES orders,
        product_id integer REFERENCES products,
        depth smallint NOT NULL,
        number smallint NOT NULL
    );

CREATE TABLE logs (
        id serial PRIMARY KEY,
        time timestamptz NOT NULL DEFAULT (CURRENT_TIMESTAMP),
        log text NOT NULL,
        order_id integer REFERENCES orders
    );

INSERT INTO users VALUES
    ('user1'),
    ('user2');

INSERT INTO products VALUES
    (DEFAULT, 'Коробка', 1),
    (DEFAULT, 'Яблоко', 5),
    (DEFAULT, 'Ручка', 10),
    (DEFAULT, 'Телефон', 1000),
    (DEFAULT, 'Лампа', 500),
    (DEFAULT, 'Стол', 5000);
