import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv

import datetime

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

load_dotenv()

dbname = os.getenv('DBNAME')
detect_types = sqlite3.PARSE_DECLTYPES


def create_table():
    # TA FUNKCJA POWINNA SIĘ ODPALAĆ ZA KAŻDYM RAZEM GDY ZOSTANIE URUCHOMIONA APLIKACJA
    # W CELU STWORZENIA STWORZENIA STRUKTURY DANYCH JEŚLI NIE ISTNIEJE
    # ALBO PO PROSTU NAPISAĆ TEST, KTÓRY SPRAWDZA CZY JEST JAKAŚ BAZA DanYCH, NIE WIEM xD

    sql_create_table_games = """
        CREATE TABLE IF NOT EXISTS games
        (
            id              INTEGER     NOT NULL,
            link            TEXT        NOT NULL,
            title           TEXT        NOT NULL,
            release         TEXT        NOT NULL    DEFAULT '-',
            added           TEXT        NOT NULL    DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (id, link, title),
            PRIMARY KEY(id)
        );
    """

    sql_create_table_prices = """
        CREATE TABLE IF NOT EXISTS prices
        (
            id              INTEGER     NOT NULL,
            game_id         INTEGER     NOT NULL,
            base_price      NUMERIC     NOT NULL,
            finale_price    NUMERIC     NOT NULL,
            currency        TEXT        NOT NULL,
            checked_date    TEXT        NOT NULL    DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (id),
            PRIMARY KEY(id),
            FOREIGN KEY(game_id) REFERENCES games(id)
        );
    """

    conn = None
    cur = None

    try:
        conn = sqlite3.connect(database=dbname, detect_types=detect_types)
        cur = conn.cursor()

        cur.execute('BEGIN')

        cur.execute(sql_create_table_games)
        cur.execute(sql_create_table_prices)
        conn.commit()

        # games_dataframe = pd.read_sql("""SELECT * FROM games""", conn)
        # print(f"Games:\n{games_dataframe}")
        # prices_dataframe = pd.read_sql("""SELECT * FROM prices""", conn)
        #
        # # select = """
        # #     SELECT g.game_title, p.base_price, p.finale_price, p.date_update
        # #     FROM games_prices AS p
        # #     JOIN games AS g
        # #     WHERE p.game_id = g.id;
        # # """
        # # prices_dataframe = pd.read_sql(select, conn)
        # print(f"Ceny:\n{prices_dataframe}")
    except Exception as e:
        conn.rollback()
        print(f"ERROR:\n{e}")
    finally:
        cur.close()
        conn.close()


def select_data(sql: str):
    conn = None
    cur = None

    try:
        conn = sqlite3.connect(database=dbname)
        cur = conn.cursor()

        cur.execute('BEGIN')

        cur.execute(sql)

        columns = [name[0] for name in cur.description]
        data = cur.fetchall()

        conn.commit()

        return columns, data

    except Exception as e:
        conn.rollback()
        print(f"ERROR:\n{e}")
    finally:
        cur.close()
        conn.close()


def try_execute_sql(sql: str, values: tuple):
    conn = None
    cur = None

    try:
        conn = sqlite3.connect(database=dbname)
        cur = conn.cursor()

        cur.execute('BEGIN')

        cur.execute(sql, values)

        data = cur.fetchall()

        conn.commit()

        return data

    except Exception as e:
        conn.rollback()
        print(f"ERROR:\n{e}")
    finally:
        cur.close()
        conn.close()


def insert_into_games(data: dict):
    sql = """
           INSERT INTO games (link, title, release) 
           VALUES (?, ?, ?);
       """

    values = (str(data['link']), str(data['title']), str(data['release']))

    try_execute_sql(sql, values)


def insert_into_prices(data: dict):
    select_game_id = """SELECT id FROM games WHERE title LIKE ? OR title = ?;"""

    # Pojedyncza wartość str nie przechodzi przez fun. execute(sql, values), więc prześle kilka;
    # Odnoszę wrażenie, że to bug w bibliotece
    values = (data['title'], data['title'])

    game_id = try_execute_sql(select_game_id, values)[0][0]

    sql = """
            INSERT INTO prices (game_id, base_price, finale_price, currency) 
            VALUES (?, ?, ?, ?);
        """

    values = (str(game_id), str(data['base_price']), str(data['finale_price']), str(data['currency']))

    try_execute_sql(sql, values)

    # select_from('games')
    # select_from('prices')


def select_from(table_name: str):
    sql = f"SELECT * FROM {table_name}"

    conn = sqlite3.connect(database=dbname)

    print(f"{table_name}:\n{pd.read_sql(sql, conn)}")

    conn.close()


def if_record_exist(data: dict):
    sql = """
        SELECT id FROM games WHERE link = ? AND title = ?;
    """

    values = (data['link'], data['title'])

    if len(try_execute_sql(sql, values)) > 0:
        return True
    else:
        return False


select_from('games')
select_from('prices')
