import psycopg2
from psycopg2 import errors

from typing import Union, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

DB_NAME = 'patterns_db'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'


class OrderStatus(Enum):
    SAVE = 'save'
    IN_WAY = 'in_way'
    RECEIVED = 'received'


class DeliveryType(Enum):
    NO_DELIVERY = 'none'
    COMMON = 'common'
    EXPRESS = 'express'


@dataclass
class User:
    login: str
    password: bytes
    secret_question: str
    secret_answer: str
    name: str


def _create_cursor(dbname: str, user: str, password: str, host: str, port: str, autocommit=True):
    con = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    con.autocommit = autocommit
    cursor = con.cursor()
    return cursor


def _query_from_file(path: str) -> str:
    with open(path, 'r', encoding='UTF8')as f:
        return '\n'.join(f.readlines())


class Database:
    @staticmethod
    def create_db():
        cursor = _create_cursor(dbname='postgres', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor.execute('DROP DATABASE IF EXISTS patterns_db;')

        try:
            cursor.execute(_query_from_file('./sql_scripts/create_db.sql'))
        except psycopg2.errors.lookup('42P04'):
            print('База данных уже создана')
            return

        cursor = _create_cursor(dbname='patterns_db', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor.execute(_query_from_file('./sql_scripts/create_tables.sql'))
        cursor.close()

    @staticmethod
    def get_products():
        cursor = _create_cursor(dbname='patterns_db', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor.execute('SELECT name, price::text FROM products')
        res = cursor.fetchall()
        cursor.close()
        return res

    @staticmethod
    def get_pw_by_login(login: str) -> Union[None, bytes]:
        cursor = _create_cursor(dbname='patterns_db', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cursor.execute('SELECT password FROM users WHERE login=%s;', (login,))
        res = cursor.fetchall()
        cursor.close()
        return None if res == [] else bytes(res[0][0])

    @staticmethod
    def register_user(user: User):
        cursor = _create_cursor(dbname='patterns_db', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        try:
            cursor.execute('INSERT INTO users VALUES (%s, %s, %s, %s, %s);',
                           (user.login, user.password, user.secret_question, user.secret_answer, user.name))
        except errors.lookup("23505"):
            raise ValueError("Данный пользователь уже зарегистрирован")
        except errors.lookup("23514"):
            raise ValueError("Има пользователя слишком короткое (<5 символов)")
        finally:
            cursor.close()

    @staticmethod
    def add_product_from_dict(cursor, order_id: int, parent_id: Union[str, int], product_dict: Tuple):
        # cursor = _create_cursor(dbname='patterns_db', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        if isinstance(product_dict[1], int):
            is_box = False
            number = product_dict[1]
        else:
            is_box = True
            number = 1
        cursor.execute('INSERT INTO orders_products (id, order_id, product_name, parent_id, number)'
                       'VALUES (DEFAULT, %s, %s, %s, %s) RETURNING id;',
                       (order_id, product_dict[0], parent_id, number))
        parent_id = int(cursor.fetchall()[0][0])

        if is_box:
            for child_product in product_dict[1]:
                Database.add_product_from_dict(cursor, order_id, parent_id, child_product)
        # cursor.close()

    @staticmethod
    def add_order(login: str, status: OrderStatus, delivery_type: DeliveryType, discount: bool, price: Decimal,
                  products: Tuple):
        cursor = _create_cursor(dbname='patterns_db', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT,
                                autocommit=False)
        cursor.execute('INSERT INTO orders (id, order_time, current_status, delivery_type, discount, price, user_login)'
                       'VALUES (DEFAULT, DEFAULT, %s, %s, %s, %s, %s) RETURNING id;',
                       (status.value, delivery_type.value, discount, price, login))
        order_id = int(cursor.fetchall()[0][0])
        Database.add_product_from_dict(cursor, order_id, "NULL", products)
        cursor.commit()
        cursor.close()
