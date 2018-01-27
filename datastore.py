import sqlite3

from book import Book
from util import tf_val, num_val

DB_NAME = 'wishlist.db'
BOOK_TABLE = 'books'
ID = 'b_id'
TITLE = 'title'
AUTHOR = 'author'
READ = 'read'

createsql = 'CREATE TABLE IF NOT EXISTS {} ( {} INTEGER PRIMARY KEY, {} TEXT, {} TEXT, {} INTEGER )'.format(BOOK_TABLE, ID, TITLE, AUTHOR, READ)  # 0 = False, 1 = True


def setup():
    """ Connect to database, creates book table if it doesn't exist. """
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(createsql)    # Creates an intermediate cursor object


def shutdown():
    """ Any DB shutdown/cleanup tasks can go here """
    pass    # May be needed in future?


def get_books(**kwargs):
    """ Return books from DB. With no arguments, returns everything. """

    books = []

    if kwargs == {}:
        sql = 'SELECT * FROM {}'.format(BOOK_TABLE)

    elif kwargs['read'] == True:
        sql = 'SELECT * FROM {} WHERE {} = 1'.format(BOOK_TABLE, READ)

    elif kwargs['read'] == False:
        sql = 'SELECT * FROM {} WHERE {} = 0'.format(BOOK_TABLE, READ)

    if sql:

        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row  # This type of row can be accessed by column name
            cur = conn.cursor()
            rows = cur.execute(sql)

            for row in rows:
                read_bool = tf_val(row[READ])
                book = Book(row[TITLE], row[AUTHOR], read_bool, row[ID])
                books.append(book)

    return books



def add_book(book):
    """ Add to db, set id value, return Book """

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        sql_template = 'INSERT INTO {} ({}, {}, {}) VALUES (?, ?, ?)'.format(BOOK_TABLE, TITLE, AUTHOR, READ) # Remember ID autoincrements
        sql_values = (book.title, book.author, num_val(book.read) )
        cur.execute(sql_template, sql_values)

        book_id = cur.lastrowid
        book.set_id(book_id)

        return book


def set_read(book_id, read):
    """ Update book with given book_id to read boolean.
    Return True if book is found in DB and update is made, False otherwise. """

    read_update = num_val(read)
    sql = 'UPDATE {} SET {} = ? WHERE {} = ?'.format(BOOK_TABLE, READ, ID)

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(sql, (read_update, book_id) )
        return cur.rowcount > 0 # return True if rows were changed.
