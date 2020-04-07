import psycopg2
from datetime import datetime
import logging

module_logger = logging.getLogger("bot.pg_db")



test_values = (
    'AgACAgIAAxkBAAICUl56giE7gQSxdkzxkDEgZjBrZzhzAAJerDEb91PZS8QIzg_i0uG0OxDBDgAEAQADAgADbQADh2UEAAEYBA', '1585087009',
    119452, 'photo', 1, 'testo')


def add_values(values):
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    assert len(values) == 6, 'Wrong values'

    c.execute(
        '''CREATE TABLE IF NOT EXISTS files
                (file_id text, date integer, file_size integer, media_type text, chat_id text, chat_title text)''')
    c.execute('''INSERT INTO files VALUES (%s, %s, %s, %s, %s, %s)''', values)
    conn.commit()
    c.close()


def get_last_time(user_id):
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    try:
        c.execute(
            '''SELECT date FROM sessions WHERE user_id = %s ''', (user_id,))
        conn.commit()
        return c.fetchone()[0]
    except psycopg2.Error:
        return 0


def change_time():
    """
    Taken from sqlite3 could be replaced by some pg methods
    """
    
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    c.executescript(
        '''CREATE TABLE IF NOT EXISTS temp (file_id text, date integer, file_size integer, media_type text, chat_id text, chat_title text);

        INSERT INTO temp SELECT * FROM files;

        DROP TABLE files;

        ALTER TABLE temp RENAME TO files;''')
    conn.commit()
    c.close()


def session_add(values):
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS sessions
                (user_id integer UNIQUE, last_time integer, current_time integer)''')
    c.execute('''INSERT OR REPLACE INTO  sessions VALUES (%s, %s)''', values)
    conn.commit()


def get_values(title=None, user_id=None):
    module_logger.info('here')
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    module_logger.info('title is {} uid is {}'.format(title, user_id))
    c.execute(
        '''CREATE TABLE IF NOT EXISTS files
                (file_id text, date integer, file_size integer, media_type text, chat_id text, chat_title text)'''
    )
    conn.commit()
    c.execute('SELECT COUNT(*) from files')
    if c.fetchone()[0] == 0:
        raise FileNotFoundError
    if title and user_id:
        mode_status = get_user_mode(user_id)
        if mode_status == 'full':
            last_time = 0
        else:
            last_time = get_last_time(user_id)
        start = datetime.now()
        c.execute('''SELECT file_id FROM files WHERE chat_title = %s 
                     AND date > %s AND media_type = 'photo'  GROUP BY file_size''',
                  (title, last_time))
        photos = [i[0] for i in c.fetchall()]
        c.execute('''SELECT file_id FROM files WHERE chat_title = %s 
                      AND date > %s AND media_type = 'video'  GROUP BY file_size''',
                  (title, last_time))
        videos = [i[0] for i in c.fetchall()]
        c.execute('''SELECT file_id FROM files WHERE chat_title = %s 
                      AND date > %s AND media_type = 'video/mp4'  GROUP BY file_size''',
                  (title, last_time))
        gifs = [i[0] for i in c.fetchall()]
        c.execute('''SELECT file_id FROM files WHERE chat_title = %s 
                      AND date > %s AND media_type = 'image/jpeg'  GROUP BY file_size''',
                  (title, last_time))
        doc_images = [i[0] for i in c.fetchall()]
        c.close()
        stop = datetime.now()
        delta = stop - start
        module_logger.info(delta)
        return {'photos': photos, 'videos': videos, 'gifs': gifs, 'doc_images': doc_images}


def set_user_mode(uid, mode):
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users_mode (user_id integer UNIQUE, mode text)''')
    c.execute('''INSERT INTO users_mode as um (user_id, mode) VALUES(%s, %s) ON CONFLICT (user_id)
                DO UPDATE SET mode = um.mode WHERE um.user_id = %s''', (uid, mode, uid))
    conn.commit()
    c.close()
    module_logger.info('value added')


def get_user_mode(uid):
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    try:
        c.execute('''SELECT mode FROM users_mode WHERE user_id = %s''', (uid, ))
        conn.commit()
        result = c.fetchone()[0]
        module_logger.info(result)
        return result

    except psycopg2.Error as e:
        module_logger.info('0 records')
        return None


def get_chats():
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    try:
        c.execute('''SELECT DISTINCT chat_title FROM files''')
        final_result = [i[0] for i in c.fetchall() if i[0] is not None]
        module_logger.info(final_result)
        return final_result
    except psycopg2.Error as e:
        raise FileNotFoundError



def test_query():
    conn = psycopg2.connect(dbname='ded22jl3v2q4tm', user='omkkrbovhjnvrx', port='5432',
                            password='4d391132de0bbff018b79d63cd51758c0395216e1d90dc32594da3b4762d70bf',
                            host='ec2-54-217-204-34.eu-west-1.compute.amazonaws.com')
    c = conn.cursor()
    c.execute('''SELECT * FROM files''')
    conn.commit()
    return c.fetchall()

