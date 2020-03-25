import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()
test_values = ('AgACAgIAAxkBAAICUl56giE7gQSxdkzxkDEgZjBrZzhzAAJerDEb91PZS8QIzg_i0uG0OxDBDgAEAQADAgADbQADh2UEAAEYBA', '1585087009', 119451, 'photo')


def get_values():
    c.execute("SELECT  * FROM files GROUP BY file_size")
    print(c.fetchall())


def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS files
                (file_id text, date text, file_size integer, media_type text)''')


def add_values(values):
    assert len(values) == 4, 'Wrong values'

    c.execute(
        "INSERT INTO files VALUES (?, ?, ?, ?)", values)
    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.

create_table()
add_values(test_values)
get_values()
c.close()