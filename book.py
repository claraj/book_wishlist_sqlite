class Book:

    ''' Represents one book in a user's list of books'''

    NO_ID = -1

    def __init__(self, title, author, read=False, id=NO_ID):
        '''Default book is unread, and has no ID'''
        self.title = title
        self.author = author
        self.read = read
        self.id=id


    def set_id(self, id):
        self.id = id


    def __str__(self):

        read_str = 'yes' if self.read else 'no'
        id_str = '(no id)' if self.id == -1 else self.id

        template = 'id: {} Title: {} Author: {} Read: {}'
        return template.format(id_str, self.title, self.author, read_str)

    def __repr__(self):
        return 'id: {} | title: {} | author: {} | read: {}'.format(self.id, self.title, self.author, self.read)


    def __eq__(self, other):
        if isinstance(other, Book):
            return self.id == other.id and self.title == other.title and self.author == other.author and self.read==other.read

    def __ne__(self, other):
        return not self == other
