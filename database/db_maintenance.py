import sqlite3 as sq
import loguru
from datetime import datetime

result = ((38972696, 'ArgentovSG'), '/lowprice', [(461799, 'Clink 261 Hostel'), (514990528, 'Astor Victoria Hostel - Adults Only'), (614864, 'Dover Castle Hostel')])



def create_table():
    with sq.connect('database/db_hotel.db', ) as con:
        cur = con.cursor()

    #cur.execute("""drop table if exists hotels""")
    cur.execute("""create table if not exists hotels (
                                    id_hotel INTEGER PRIMARY KEY NOT NULL,
                                    name TEXT
        )""")

    #cur.execute("""drop table if exists users""")
    cur.execute("""create table if not exists users (
                                        id_user INTEGER PRIMARY KEY NOT NULL,
                                        name TEXT
            )""")

    #cur.execute("""drop table if exists requests""")
    cur.execute("""create table if not exists requests (
                                        id_request INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                        time TEXT,
                                        command TEXT,
                                        id_user INTEGER NOT NULL,
                                        FOREIGN KEY (id_user) REFERENCES users(id_user)
        )""")

    #cur.execute("""drop table if exists requests_hotels""")
    cur.execute("""create table if not exists requests_hotels (
                                        id_hotel INTEGER  NOT NULL,
                                        id_request INTEGER  NOT NULL,
                                        FOREIGN KEY (id_hotel) REFERENCES hotels(id_hotel),
                                        FOREIGN KEY (id_request) REFERENCES requests(id_request)
        )""")


def record_request(record_db):
    create_table()
    with sq.connect('database/db_hotel.db') as con:
        cur = con.cursor()

        # регистрируем в базе данных пользователей
        cur.execute(f"SELECT id_user FROM users WHERE id_user = {record_db[0][0]}")
        table_users = cur.fetchall()
        if not table_users:
            cur.execute(f"INSERT INTO users (id_user, name) VALUES (?, ?)",
                            [record_db[0][0], record_db[0][1]])
            loguru.logger.info(f'К боту обратился новый пользователь, его зарегистрировали')
        else:
            loguru.logger.info(f'С ботом общается ранее зарегистрированный пользователь')

        # регистрируем в базе данных новые отели
        hotels_id = tuple([id_hotel[0] for id_hotel in record_db[2]])
        cur.execute(f"SELECT id_hotel, name FROM hotels WHERE id_hotel in {hotels_id}")
        table_hotels = cur.fetchall()
        registr_hotels = set(record_db[2]) - set(table_hotels)
        for hotel in list(registr_hotels):
            cur.execute(f"INSERT INTO hotels (id_hotel, name) VALUES (?, ?)",
                        [hotel[0], hotel[1]])

        # регистрируем в базе данных запросы
        cur.execute(f"INSERT INTO requests (time, command, id_user) VALUES (?, ?, ?)",
                    [datetime.today(), record_db[1], record_db[0][0]])

        # регистрация отелей в запросе
        id_request = cur.lastrowid
        for id in hotels_id:
            cur.execute(f"INSERT INTO requests_hotels (id_request, id_hotel) VALUES (?, ?)",
                        [id_request, id])


def user_history(id):
    with sq.connect('database/db_hotel.db') as con:
        cur = con.cursor()
        try:
            cur.execute(f"SELECT id_user, name FROM users WHERE id_user = {id}")
            user = cur.fetchall()
            if user[0][0]:
                cur.execute(f"SELECT r.id_request, r.time, r.command, h.name "
                            f"FROM (SELECT * FROM requests WHERE id_user = {user[0][0]}) r "
                            f"LEFT OUTER JOIN requests_hotels rh "
                            f"ON r.id_request = rh.id_request "
                            f"LEFT OUTER JOIN hotels h "
                            f"ON rh.id_hotel = h.id_hotel ")
                table = list(cur.fetchall())
                history = []
                for i, elem in enumerate(table):
                    if len(history) == 0:
                        history.append([elem[1], elem[2], str('\n') + str(elem[3])])
                    elif elem[0] == table[i - 1][0]:
                        history[len(history) - 1][2] = str(history[len(history) - 1][2]) + '\n' + str(elem[3])
                    else:
                        history.append([elem[1], elem[2], str('\n') + str(elem[3])])
                return history
            else:
                return False
        except Exception:
            return False

