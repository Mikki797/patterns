import psycopg2
from psycopg2 import errors

DB_NAME = 'patterns_db'
DB_USER = 'postgres'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_PORT = '5432'


def _create_cursor(dbname: str, user: str, password: str, host: str, port: str):
    con = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    con.autocommit = True
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