import os
basedir = os.path.abspath(os.path.dirname(__file__))


ENV = 'local'
CSRF_ENABLED = True
SECRET_KEY = "}c)ico\xaf\xe9\x86_%\x03\xa3\r\xe8i\x0cc\xe8B\x99.\x1a\x8b"
OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

INSTAGRAM_ID = '622c8eca4ee94312ad1ae1c7607f5d75'
INSTAGRAM_SECRET = 'd5e20fd7d13c4da68529b63b717296d9'
ACCESS_TOKEN = '31011942.622c8ec.c39d307b1c5d4111ac06c304d789a199'

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['you@example.com']
