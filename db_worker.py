import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import config


conn = psycopg2.connect(user="postgres",
                            password=config.db_password,
                            host='127.0.0.1',
                            port='5432',
                            database="main_db")
cur = conn.cursor()


def create_main_db():
    conn = psycopg2.connect(user="postgres",
                            password=config.db_password,
                            host='127.0.0.1',
                            port='5432',
                            database="main_db")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    # Курсор для выполнения операций с базой данных
    cur = conn.cursor()
    sql_create_database = 'create database main_db'
    cur.execute(sql_create_database)


def create_t_user_tg():
    cur.execute("""CREATE TABLE t_user_tg(
                tg_id INTEGER PRIMARY KEY NOT NULL,
                user_mail TEXT NOT NULL);
                """)
    conn.commit()


def insert_t_user_tg(tg_id, user_mail):
    if check_user_in_t_user_tg(tg_id) is None:
        cur.execute(f"""
                    INSERT INTO t_user_tg(tg_id, user_mail)
                    VALUES ({tg_id}, '{user_mail}');
                    """)
        conn.commit()
        return True
    else:
        return False


def check_user_in_t_user_tg(tg_id):
    cur.execute(f"""
                SELECT tg_id
                FROM t_user_tg
                WHERE tg_id = {tg_id};
                """)
    return cur.fetchone()


def create_t_user_info():
    cur.execute("""CREATE TABLE t_user_info(
                user_id INTEGER PRIMARY KEY NOT NULL,
                user_mail TEXT NOT NULL,
                user_pass TEXT NOT NULL,
                user_lvl TEXT NOT NULL,
                date_lvl_end DATE);
                """)
    conn.commit()


def insert_t_user_info(user_mail, user_pass, user_lvl, date_lvl_end):
    user_id = create_id('user_id', 't_user_info')
    if date_lvl_end != 'null':
        date_lvl_end = f"'{date_lvl_end}'"
    cur.execute(f"""
                INSERT INTO t_user_info(user_id, user_mail, user_pass, user_lvl, date_lvl_end)
                VALUES ({user_id}, '{user_mail}', '{user_pass}', '{user_lvl}', {date_lvl_end});
                """)
    conn.commit()


def change_lvl(user_mail, lvl, date_lvl_end):
    cur.execute(f"""
                UPDATE t_user_info
                SET user_lvl = '{lvl}', date_lvl_end = '{date_lvl_end}'
                WHERE user_mail = '{user_mail}';
                """)
    conn.commit()


def create_t_transaction():
    cur.execute("""CREATE TABLE t_transaction(
                    user_id INTEGER NOT NULL,
                    transaction_id INT NOT NULL,
                    transaction_date DATE,
                    transaction_type TEXT NOT NULL,
                    transaction_category TEXT NOT NULL,
                    transaction_sum REAL NOT NULL,
                    transaction_description TEXT NOT NULL);
                    """)
    conn.commit()


def insert_t_transaction(user_id, transaction_id, transaction_date, transaction_type,
                         transaction_category, transaction_sum, transaction_description):
    transaction_description = 'null' if transaction_description == '' else f"'{transaction_description}'"
    transaction_category = 'Не определён' if transaction_category == '' else f"'{transaction_category}'"
    cur.execute(f"""
                INSERT INTO t_transaction(user_id, transaction_id, transaction_date, 
                transaction_type, transaction_category, transaction_sum, transaction_description)
                VALUES ({user_id}, '{transaction_id}', '{transaction_date}', 
                '{transaction_type}', {transaction_category}, '{transaction_sum}', {transaction_description});
                """)
    conn.commit()


def delete_t_transaction(user_id, transaction_id: list):
    for i in transaction_id:
        try:
            cur.execute(f"""
                        DELETE FROM t_transaction
                        WHERE user_id = {user_id}
                        and transaction_id in ({i});
                        """)
        except:
            None
    cur.execute(f"""
                SELECT transaction_id
                FROM t_transaction
                WHERE user_id = {user_id};
                """)
    items = [i[0] for i in cur.fetchall()]
    if items is not None:
        for item in range(1, len(items) + 1):
            cur.execute(f"""
                        UPDATE t_transaction
                        SET transaction_id = {item}
                        WHERE user_id = {user_id}
                        and transaction_id = {items[item - 1]};
                        """)
    conn.commit()


def select_user_transaction(user_id):
    cur.execute(f"""
                SELECT *
                FROM t_transaction
                WHERE user_id = {user_id};
                """)
    items = cur.fetchall()
    if items is None:
        return []
    else:
        return items


def create_t_user_category():
    cur.execute("""CREATE TABLE t_user_category(
                    user_id INTEGER NOT NULL,
                    category_type TEXT NOT NULL,
                    category_name TEXT NOT NULL);
                    """)
    conn.commit()


def insert_t_user_category(user_id, category_type, category_name):
    category_name = 'Не определён' if category_name == '' else f"'{category_name}'"
    cur.execute(f"""
                INSERT INTO t_user_category(user_id, category_type, category_name)
                VALUES ({user_id}, '{category_type}', {category_name});
                """)
    conn.commit()

def delete_t_user_category(user_id, category_type, category_name):
    category_name = 'Не определён' if category_name == '' else f"'{category_name}'"
    cur.execute(f"""
                DELETE
                FROM t_user_category
                WHERE user_id = {user_id} and
                category_type = '{category_type}' and
                category_name = {category_name};
                """)
    cur.execute(f"""
                UPDATE t_transaction
                SET transaction_category = 'Не определён'
                WHERE transaction_category = {category_name};
                """)
    conn.commit()


def select_user_categories(user_id, category_type):
    cur.execute(f"""
                SELECT category_name
                FROM t_user_category
                WHERE user_id = {user_id} and category_type = '{category_type}';
                """)
    items = cur.fetchall()
    if items is None:
        return []
    else:
        return [i[0] for i in items]


def select_user_mail(user_tg_id):
    cur.execute(f"""
                SELECT user_mail
                FROM t_user_tg
                WHERE tg_id = {user_tg_id};
    """)
    mail = cur.fetchall()
    if mail is not None:
        return mail[0]
    else:
        return False


def select_user_pass(user_mail):
    cur.execute(f"""
                SELECT user_pass
                FROM t_user_info
                WHERE user_mail = '{user_mail}';
    """)
    mail = cur.fetchone()
    if mail is not None:
        return mail[0]
    else:
        return False


def select_user_lvl(user_mail):
    cur.execute(f"""
                    SELECT user_lvl, date_lvl_end
                    FROM t_user_info
                    WHERE user_mail = '{user_mail}';
        """)
    user_lvl = cur.fetchone()
    if user_lvl is not None:
        return user_lvl
    else:
        return False

def select_user_id(user_mail):
    cur.execute(f"""
                    SELECT user_id
                    FROM t_user_info
                    WHERE user_mail = '{user_mail}';
        """)
    user_lvl = cur.fetchone()
    if user_lvl is not None:
        return user_lvl[0]
    else:
        return False

def create_id(select, table_name, descriptions=''):
    cur.execute(f"""
                SELECT {select}
                FROM {table_name}
                {descriptions}
                ORDER BY {select} DESC
                LIMIT 1;
                """)
    item = cur.fetchone()
    if item is not None:
        return item[0] + 1
    else:
        return 0
