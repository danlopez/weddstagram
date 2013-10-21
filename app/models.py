from app import db
from hashlib import md5


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    books = db.relationship('Book', backref = 'author', lazy = 'dynamic')
    last_seen = db.Column(db.DateTime)

    #In general this method should just return True unless the object represents a user that should not be allowed to authenticate for some reason.
    def is_authenticated(self): 
        return True

    #unless banned from DB
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pictures = db.relationship('Picture', backref = 'book', lazy = 'dynamic')

    def __repr__(self):
        return '<Post %r>' % (self.title)

class Picture(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #caption (eventually)
    url = db.Column(db.String(140))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))