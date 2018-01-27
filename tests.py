# Run with python -m unittest test.py

import unittest
import sqlite3

import datastore as ds
import util
from book import Book


test_db = "wishlist_test.db"
ds.DB_NAME = test_db

# Some utility methods
def rows_to_books(rows):
    return [ row_to_book(row) for row in rows]

def row_to_book(row):
    return Book(row[ds.TITLE],row[ds.AUTHOR], util.tf_val(row[ds.READ]), row[ds.ID])


class TestBookClass(unittest.TestCase):

    def test_book_creation_with_defaults(self):
        b = Book('title mc. title', 'author a. author')
        self.assertEqual('title mc. title', b.title)
        self.assertEqual('author a. author', b.author)
        self.assertFalse(b.read)
        self.assertEqual(Book.NO_ID, b.id)

    def test_book_creation_with_all_values(self):
        b = Book('title mc. title', 'author a. author', True, 42)
        self.assertEqual('title mc. title', b.title)
        self.assertEqual('author a. author', b.author)
        self.assertTrue(b.read)
        self.assertEqual(42, b.id)

    def test_str_book_not_read_has_no_id(self):
        b = Book('title', 'author')  # read = false, no id
        self.assertEqual('id: (no id) Title: title Author: author Read: no', str(b))

    def test_str_book_not_read_has_id(self):
        b = Book('title', 'author', False, 4)  # read = false, no id
        self.assertEqual('id: 4 Title: title Author: author Read: no', str(b))

    def test_str_book_read_has_no_id(self):
        b = Book('title', 'author', True)  # read = false, no id
        self.assertEqual('id: (no id) Title: title Author: author Read: yes', str(b))

    def test_str_book_read_has_id(self):
        b = Book('title', 'author', True, 5)  # read = false, no id
        self.assertEqual('id: 5 Title: title Author: author Read: yes', str(b))


class TestdsWithEmptyDatabase(unittest.TestCase):

    def setUp(self):
        with sqlite3.connect(test_db) as con:
            destroysql = 'DROP TABLE {}'.format(ds.BOOK_TABLE)
            con.cursor().execute(destroysql)
            con.cursor().execute(ds.createsql)


    def test_add_book(self):
        b = Book('A. author', 'the title')
        ds.add_book(b)
        # Book id should be updated
        self.assertEqual(1, b.id)
        # Book should exist in database with id = 1
        with sqlite3.connect(test_db) as con:
            con.row_factory = sqlite3.Row
            rows = con.cursor().execute('SELECT * FROM books').fetchall()
            self.assertEqual(1, len(rows))
            row = rows[0]
            self.assertEqual(b, row_to_book(row))


    def test_get_all_books(self):
        books = ds.get_books()
        self.assertEqual([], books)

        books = ds.get_books(read=True)
        self.assertEqual([], books)

        books = ds.get_books(read=False)
        self.assertEqual([], books)


class TestdsWithTestData(unittest.TestCase):

    def setUp(self):

        self.book_data = [(1, 'Amazing Arizona', 'Ardvark', 0),
                  (2, 'Baffling Buttons',  'Buffalo', 1),
                  (3, 'Clever Curtains', 'Cat', 0),
                  (4, 'Double Donut', 'Dog', 0)]

        self.books = [ Book(b[1], b[2], util.tf_val(b[3]), b[0]) for b in self.book_data ]

        # Delete old data, create new table and insert test data.
        with sqlite3.connect(test_db) as con:
            cur = con.cursor()
            destroysql = 'DROP TABLE {}'.format(ds.BOOK_TABLE)
            cur.execute(destroysql)
            cur.execute(ds.createsql) # Create same table
            cur.executemany('INSERT INTO books VALUES (?,?,?,?)', self.book_data)


    def test_get_all_books(self):
        read_books = ds.get_books()
        self.assertCountEqual(self.books, read_books)


    def test_show_read_books(self):
        read_books = ds.get_books(read=True)
        expected_read_books = [b for b in self.books if b.read]
        self.assertCountEqual(expected_read_books, read_books)


    def test_show_unread_books(self):
        unread_books = ds.get_books(read=False)
        expected_unread_books = [b for b in self.books if not b.read]
        self.assertCountEqual(expected_unread_books, unread_books)


    def test_add_book(self):
        new_book = Book('Elephant Eggs', 'Elephant')
        expected_new_book_after_add = Book('Elephant Eggs', 'Elephant', False, 5)
        self.books.append(expected_new_book_after_add)
        book_added = ds.add_book(new_book)
        self.assertEqual(5, book_added.id)  # new ID is correct
        self.check_db_matches_expected(self.books)  # data in DB is correct


    def test_mark_book_as_read_book_exists(self):
        mark_as_read = self.books[0]
        self.assertTrue(ds.set_read(mark_as_read.id, True))
        self.check_read_book(mark_as_read.id, 1)


    def test_mark_book_as_read_book_exists_but_is_already_read(self):
        mark_as_read = self.books[1]
        self.assertTrue(ds.set_read(mark_as_read.id, True))
        self.check_read_book(mark_as_read.id, 1)


    def test_mark_book_as_read_book_doesnt_exist(self):
        self.assertFalse(ds.set_read(100, True))
        self.check_db_matches_expected(self.books) # No modifications to DB


    def test_mark_book_as_unread_book_exists(self):
        mark_as_read = self.books[1]
        self.assertTrue(ds.set_read(mark_as_read.id, False))
        self.check_read_book(mark_as_read.id, 0)


    def test_mark_book_as_unread_book_exists_but_is_already_unread(self):
        mark_as_read = self.books[0]
        self.assertTrue(ds.set_read(mark_as_read.id, False))
        self.check_read_book(mark_as_read.id, 0)


    def test_mark_book_as_unread_book_doesnt_exist(self):
        self.assertFalse(ds.set_read(101, False))
        self.check_db_matches_expected(self.books) # No mods to DB


    # Not a test method - used by tests to compare contents of DB to expected list of Books
    def check_db_matches_expected(self, expected):
        with sqlite3.connect(test_db) as con:
            con.row_factory = sqlite3.Row
            rows = con.cursor().execute('SELECT * FROM books').fetchall()
            books_fetched = rows_to_books(rows)
            self.assertCountEqual(expected, books_fetched)


    def check_read_book(self, book_id, expected):
        with sqlite3.connect(test_db) as con:
            con.row_factory = sqlite3.Row
            row = con.cursor().execute('SELECT * FROM books WHERE b_id = ?', (book_id,)).fetchone()
            self.assertEqual(expected, row[ds.READ])



class TestUtil(unittest.TestCase):

    def test_tf_val_false(self):
        # 0 is False
        self.assertFalse(util.tf_val(0))

    def test_tf_val_true(self):
        # Any non-0 value is true
        self.assertTrue(util.tf_val(1))
        self.assertTrue(util.tf_val(0.9999))
        self.assertTrue(util.tf_val(-1))
        self.assertTrue(util.tf_val(1000))
        self.assertTrue(util.tf_val(1.1))

    def test_num_val_true_values(self):
        # Convert True or truthy values to 1
        self.assertEqual(1, util.num_val(True))
        self.assertEqual(1, util.num_val(1))
        self.assertEqual(1, util.num_val("True"))
        self.assertEqual(1, util.num_val("Read"))

    def test_num_val_true_values(self):
        # Convert false and falsy values to 0
        self.assertEqual(0, util.num_val(False))
        self.assertEqual(0, util.num_val([]))
        self.assertEqual(0, util.num_val(""))
        self.assertEqual(0, util.num_val(None))
        self.assertEqual(0, util.num_val({}))
        self.assertEqual(0, util.num_val(0))
        self.assertEqual(0, util.num_val(0.0))
