from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, SearchForm, BookForm
from models import User, Book, Picture
from datetime import datetime

from instagram.client import InstagramAPI

@app.before_request
def before_request():
    g.user = current_user #current_user set by Flask-Login
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()



@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    books = Book.query.filter_by(author = g.user)
    return render_template('index.html',
        title = 'Home',
        user = user,
        books = books)

@app.route('/search', methods = ['GET', 'POST'])
@app.route('/search/<int:max_tag_id>')
@login_required
def search(max_tag_id = 0):
    form = SearchForm()
    if max_tag_id > 0 or form.validate_on_submit():
        api = InstagramAPI(client_id=app.config['INSTAGRAM_ID'], client_secret = app.config['INSTAGRAM_SECRET'])
        if max_tag_id > 0:
            if request.args['query']:
                tag_name = request.args['query']
            tag_media, next = api.tag_recent_media(count = 20, max_id = max_tag_id, tag_name = request.args['query'])
        else:
            tag_media, next = api.tag_recent_media(count = 20, tag_name = form.query.data)
        photos = []
        for media in tag_media:
            photos.append(media.images['thumbnail'].url)
        try:
            max_tag_id = next.split('&')[2].split('max_tag_id=')[1]
        except: 
            max_tag_id = None
        return render_template('search_results.html',
            query = form.query.data,
            photos = photos,
            next = max_tag_id)
    else:
        return render_template('search.html',
            form = form)



@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    books = [
        { 'author': user, 'title': 'Test book #1' },
        { 'author': user, 'title': 'Test book #2' }
    ]
    return render_template('user.html',
        user = user,
        books = books)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit(): #instead of checking POST, this includes validation
        g.user.nickname = form.nickname.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        return render_template('edit.html',
            form = form)

@app.route('/create_book', methods = ['GET', 'POST'])
@login_required
def create_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(title = form.title.data, timestamp = datetime.utcnow(), author = g.user)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('search'))
    else:
        return render_template('create_book.html', 
            form = form)

@app.route('/book/<int:book_id>', methods =['POST', 'GET'])
@login_required
def book(book_id):
    form = SearchForm()
    book = Book.query.filter_by(id = book_id).first()
    pics = Picture.query.filter_by(book_id = book_id)
    if book == None:
        flash('Book not found')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        api = InstagramAPI(client_id=app.config['INSTAGRAM_ID'], client_secret = app.config['INSTAGRAM_SECRET'])
        # if max_tag_id > 0:
        #     if request.args['query']:
        #         tag_name = request.args['query']
        #     tag_media, next = api.tag_recent_media(count = 20, max_id = max_tag_id, tag_name = request.args['query'])
        # else:
        tag_media, next = api.tag_recent_media(count = 20, tag_name = form.query.data)
        instagram_results = []
        for media in tag_media:
            instagram_results.append(media.images['thumbnail'].url)
        try:
            max_tag_id = next.split('&')[2].split('max_tag_id=')[1]
        except: 
            max_tag_id = None
        return render_template('book.html',
            query = form.query.data,
            instagram_results = tag_media,
            pics = pics,
            form = form,
            next = max_tag_id,
            book = book)

    return render_template('book.html',
        book = book,
        pics = pics,
        form = form)

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "": #validation
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me) #standard flask-login
    return redirect(request.args.get('next') or url_for('index'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')
def shutdown():
    if app.config['ENV'] =='local':
        shutdown_server()
        return 'Server shutting down...'


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() #do this to bring db back to working state
    return render_template('500.html'), 500


@app.route('/add_pic_to_book', methods=['POST'])
@login_required
def add_to_book():
    thumb_url = request.form['thumb_url']
    full_url = request.form['full_url']
    book_id = request.form['book_id']
    username = request.form['username']
    pic = Picture(thumb_url = thumb_url,full_url = full_url, instagram_user = username, book_id = book_id)
    db.session.add(pic)
    db.session.commit()
    return jsonify({
        'error': 'none'
        })

@app.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    book = Book.query.filter_by(id = book_id).first()
    if book.user_id !=g.user.id:
        flash("You don't have permission to delete this book.")
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))