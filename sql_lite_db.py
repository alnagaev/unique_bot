import sqlite3
from datetime import datetime

test_values = (
    'AgACAgIAAxkBAAICUl56giE7gQSxdkzxkDEgZjBrZzhzAAJerDEb91PZS8QIzg_i0uG0OxDBDgAEAQADAgADbQADh2UEAAEYBA', '1585087009',
    119452, 'photo', 1, 'testo')

'''******************************files*******************************************************'''
'''file_id text, date text, file_size integer, media_type text, chat_id text, chat_title text'''


def test_query():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(
        '''DELETE FROM files
            WHERE file_id IS NULL OR TRIM(file_id) = '' ''')
    conn.commit()
    c.close()


test_query()

def get_values(filter=None, filterable=None):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT  file_id FROM files GROUP BY file_size")
    if filter and filterable:
        start = datetime.now()
        c.execute("SELECT  file_id FROM files  WHERE {} = ? AND media_type = 'photo' GROUP BY file_size".format(filter),
                  (filterable,))
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
                (file_id text, date text, file_size integer, media_type text, chat_id text, chat_title text)''')
    c.execute('''INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)''', values)
    conn.commit()
    c.close()
    print('value added')

# get_values('file_size', 119452)
