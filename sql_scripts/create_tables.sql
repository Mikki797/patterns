SET lc_monetary TO "en_US.UTF-8";

CREATE TABLE products (
        id serial PRIMARY KEY,
        name text UNIQUE NOT NULL,
        price numeric(12,2) NOT NULL CHECK (price > 0)
    );

CREATE TABLE users (
        login varchar(32) PRIMARY KEY CHECK (char_length(login) > 4),
        password bytea NOT NULL, -- хэшировано
        secret_question varchar(128) NOT NULL,
        secret_answer bytea NOT NULL, --хэшировано
        name varchar(32) NOT NULL
    );

CREATE TYPE status as ENUM ('save', 'in_way', 'received');
CREATE TYPE delivery as ENUM ('none', 'common', 'express');

CREATE TABLE orders (
        id serial PRIMARY KEY,
        order_time timestamptz NOT NULL DEFAULT (CURRENT_TIMESTAMP),
        current_status status NOT NULL,
        delivery_type delivery NOT NULL,
        discount boolean NOT NULL,
        price numeric(12,2) NOT NULL CHECK (price > 0),
        user_login varchar(32) REFERENCES users
    );

CREATE UNIQUE INDEX orders_unique_save ON orders(user_login) WHERE current_status = 'save';

CREATE TABLE orders_products (
        id serial PRIMARY KEY,
        order_id integer REFERENCES orders ON DELETE CASCADE,
        product_name text REFERENCES products (name),
        parent_id integer REFERENCES orders_products,
        number smallint NOT NULL
    );

CREATE TABLE logs (
        id serial PRIMARY KEY,
        time timestamptz NOT NULL DEFAULT (CURRENT_TIMESTAMP),
        log text NOT NULL,
        order_id integer REFERENCES orders
    );
--
--INSERT INTO users VALUES
--    ('user1'),
--    ('user2');

INSERT INTO products VALUES
    (DEFAULT, 'Коробка', 1),
    (DEFAULT, 'Яблоко', 5),
    (DEFAULT, 'Ручка', 10),
    (DEFAULT, 'Телефон', 1000),
    (DEFAULT, 'Лампа', 500),
    (DEFAULT, 'Стол', 5000);
