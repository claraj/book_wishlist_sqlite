import sqlite3

from book import Book

DB_NAME = 'wishlist.db'
BOOK_TABLE = 'books'
ID = 'b_id'
TITLE = 'title'
AUTHOR = 'author'
READ = 'read'


def setup():
    '''Connect to database, creates book table if it doesn't exist.'''
    conn = sqlite3.connect(DB_NAME)
    createsql = 'CREATE TABLE IF NOT EXISTS {} ( {} INTEGER PRIMARY KEY, {} TEXT, {} TEXT, {} INTEGER )'.format(BOOK_TABLE, ID, AUTHOR, TITLE, READ)  # 0 = False, 1 = True
    conn.execute(createsql)    # Creates an intermediate cursor object
    conn.commit()
    conn.close()


def shutdown():
    '''Any DB shutdown/cleanup tasks can go here'''
    pass    # May be needed in future?


def get_books(**kwargs):
    ''' Return books from DB. With no arguments, returns everything. '''

    sql = None

    books = []

    if kwargs == None:
        sql = 'SELECT * FROM {}'.format(BOOK_TABLE)

    if kwargs['read'] == True:
        sql = 'SELECT * FROM {} WHERE {} = 1'.format(BOOK_TABLE, READ)

    if kwargs['read'] == False:
        sql = 'SELECT * FROM {} WHERE {} = 0'.format(BOOK_TABLE, READ)

    if sql:

        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # This type of row can be accessed by column name
        cur = conn.cursor()
        rows = cur.execute(sql)

        for row in rows:
            read_bool = tf_val(row[3])
            book = Book(row[TITLE], row[AUTHOR], read_bool, row[ID])
            books.append(book)

        conn.close()

    return books




def add_book(book):
    ''' Add to db, set id value, return Book'''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    sql_template = 'INSERT INTO {}({}, {}, {}) VALUES (?, ?, ?)'.format(BOOK_TABLE, AUTHOR, TITLE, READ) # Autoincrement

    print(book.title)
    print(book.author)
    print(book.read)

    sql_values = (book.title, book.author, num_val(book.read) )
    cur.execute(sql_template, sql_values)

    book_id = cur.lastrowid
    book.set_id(book_id)

    conn.commit()
    conn.close()

    return book


def set_read(book_id, read):
    '''Update book with given book_id to read. Return True if book is found in DB and update is made, False otherwise.'''

    read_update = num_val(read)
    sql = 'UPDATE {} SET {} = ? WHERE {} = ?'.format(BOOK_TABLE, READ, ID)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(sql, (read_update, book_id) )
    conn.commit()
    conn.close()

    return cur.rowcount > 0 # return True if rows were changed.


# Utility methods
def tf_val(number):
    '''Convert 0 to False and 1 (or any other value) to True'''
    return number != 0


def num_val(bool_val):
    '''Convert True to 1 and False to 0'''
    if bool_val:
        return 1
    else:
        return 0
