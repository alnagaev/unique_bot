import sqlite3
from datetime import datetime

test_values = (
    'AgACAgIAAxkBAAICUl56giE7gQSxdkzxkDEgZjBrZzhzAAJerDEb91PZS8QIzg_i0uG0OxDBDgAEAQADAgADbQADh2UEAAEYBA', '1585087009',
    119452, 'photo', 1, 'testo')

'''******************************files*******************************************************'''
'''file_id text, date integer, file_size integer, media_type text, chat_id text, chat_title text'''


def test_query():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        '''DELETE FROM sessions
            WHERE user_id IS NULL OR TRIM(user_id) = '' ''')
    conn.commit()
    c.close()


test_query()


def change_time():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.executescript(
        '''CREATE TABLE IF NOT EXISTS temp (file_id text, date integer, file_size integer, media_type text, chat_id text, chat_title text);

        INSERT INTO temp SELECT * FROM files;

        DROP TABLE files;

        ALTER TABLE temp RENAME TO files;''')
    conn.commit()
    c.close()


def session_add(values):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS sessions
                (user_id integer UNIQUE, last_time integer)''')
    c.execute('''INSERT OR REPLACE INTO  sessions VALUES (?, ?)''', values)
    conn.commit()
    print(c.fetchall())


# def get_values(filter=None, filterable=None):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("SELECT  file_id FROM files GROUP BY file_size")
#     if filter and filterable:
#         start = datetime.now()
#         c.execute("SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'photo' GROUP BY file_size".format(filter),
#                   (filterable,))
#         photos = [i[0] for i in c.fetchall()]
#         c.execute("SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'video' GROUP BY file_size".format(filter),
#                   (filterable,))
#         videos = [i[0] for i in c.fetchall()]
#         c.execute(
#             "SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'video/mp4' GROUP BY file_size".format(filter),
#             (filterable,))
#         gifs = [i[0] for i in c.fetchall()]
#         c.execute(
#             "SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'image/jpeg' GROUP BY file_size".format(filter),
#             (filterable,))
#         doc_images = [i[0] for i in c.fetchall()]
#         c.close()
#         stop = datetime.now()
#         delta = stop - start
#         print(delta)
#         return {'photos': photos, 'videos': videos, 'gifs': gifs, 'doc_images': doc_images}


def get_values(filter=None, filterable=None, user_id=None):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT  file_id FROM files GROUP BY file_size")
    if filter and filterable and user_id:
        c.execute('''SELECT date FROM sessions WHERE user_id = ?''', (user_id, ))
        last_date = c.fetchone()
        print(last_date)

        start = datetime.now()
        c.execute('''SELECT file_id FROM files WHERE {} = ? 
                     AND date > ? AND media_type = 'photo'  GROUP BY file_size'''.format(filter),
                  (filterable, last_date))
        photos = [i[0] for i in c.fetchall()]
        c.execute("SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'video' GROUP BY file_size".format(filter),
                  (filterable,))
        videos = [i[0] for i in c.fetchall()]
        c.execute(
            "SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'video/mp4' GROUP BY file_size".format(filter),
            (filterable,))
        gifs = [i[0] for i in c.fetchall()]
        c.execute(
            "SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'image/jpeg' GROUP BY file_size".format(filter),
            (filterable,))
        doc_images = [i[0] for i in c.fetchall()]
        c.close()
        stop = datetime.now()
        delta = stop - start
        print(delta)
        return {'photos': photos, 'videos': videos, 'gifs': gifs, 'doc_images': doc_images}


print(get_values('chat_title', 'bots'))

def get_chats():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT DISTINCT chat_title FROM files''')
    final_result = [i[0] for i in c.fetchall() if i[0] is not None]
    return final_result


def add_values(values):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    assert len(values) == 6, 'Wrong values'

    c.execute(
        '''CREATE TABLE IF NOT EXISTS files
                (file_id text, date integer, file_size integer, media_type text, chat_id text, chat_title text)''')
    c.execute('''INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)''', values)
    conn.commit()
    c.close()
    print('value added')
