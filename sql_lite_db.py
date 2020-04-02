import sqlite3
from datetime import datetime
import logging
import inspect

module_logger = logging.getLogger("bot.sql_lite_db")


test_values = (
    'AgACAgIAAxkBAAICUl56giE7gQSxdkzxkDEgZjBrZzhzAAJerDEb91PZS8QIzg_i0uG0OxDBDgAEAQADAgADbQADh2UEAAEYBA', '1585087009',
    119452, 'photo', 1, 'testo')

'''******************************files*******************************************************'''
'''file_id text, date integer, file_size integer, media_type text, chat_id text, chat_title text'''


def test_query():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        '''SELECT * FROM users_mode''')
    conn.commit()
    return c.fetchall()



def get_last_time(user_id):
    module_logger.info(user_id)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
            '''SELECT date FROM sessions WHERE user_id = ? ''', (user_id,))
    conn.commit()
    try:
        return c.fetchone()[0]
    except TypeError:
        module_logger.info('0 records')
        return 0


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
                (user_id integer UNIQUE, last_time integer, current_time integer)''')
    c.execute('''INSERT OR REPLACE INTO  sessions VALUES (?, ?)''', values)
    conn.commit()
    module_logger.info(c.fetchall())


def get_values(title=None, user_id=None):
    module_logger.info('here')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    module_logger.info('title is {} uid is {}'.format(title, user_id))
    if title and user_id:
        mode_status = get_user_mode(user_id)
        if mode_status == 'full':
            last_time = 0
        else:
            last_time = get_last_time(user_id)
        start = datetime.now()
        c.execute('''SELECT file_id FROM files WHERE chat_title = ? 
                     AND date > ? AND media_type = 'photo'  GROUP BY file_size''',
                  (title, last_time))
        photos = [i[0] for i in c.fetchall()]
        c.execute('''SELECT file_id FROM files WHERE chat_title = ? 
                      AND date > ? AND media_type = 'video'  GROUP BY file_size''',
                  (title, last_time))
        videos = [i[0] for i in c.fetchall()]
        c.execute('''SELECT file_id FROM files WHERE chat_title = ? 
                      AND date > ? AND media_type = 'video/mp4'  GROUP BY file_size''',
                  (title, last_time))
        gifs = [i[0] for i in c.fetchall()]
        c.execute('''SELECT file_id FROM files WHERE chat_title = ? 
                      AND date > ? AND media_type = 'image/jpeg'  GROUP BY file_size''',
                  (title, last_time))
        doc_images = [i[0] for i in c.fetchall()]
        c.close()
        stop = datetime.now()
        delta = stop - start
        module_logger.info(delta)
        return {'photos': photos, 'videos': videos, 'gifs': gifs, 'doc_images': doc_images}


def set_user_mode(uid, mode):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users_mode (user_id integer UNIQUE, mode text)''')
    c.execute('''INSERT OR REPLACE INTO users_mode VALUES(?, ?)''', (uid, mode))
    conn.commit()
    c.close()
    module_logger.info('value added')


def get_user_mode(uid):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT mode FROM users_mode WHERE user_id = ?''', (uid, ))
    conn.commit()
    try:
        result = c.fetchone()[0]
        module_logger.info(result)
        return result
    except TypeError as e:
        module_logger.info('0 records')
        return None


def get_chats():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT DISTINCT chat_title FROM files''')
    final_result = [i[0] for i in c.fetchall() if i[0] is not None]
    module_logger.info(final_result)
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
    module_logger.info('value added')
