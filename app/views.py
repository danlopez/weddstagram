from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, EditForm, SearchForm
from models import User
from datetime import datetime

from instagram.client import InstagramAPI

import pprint

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
    books = [
        { 
            'author': { 'nickname': 'John' }, 
            'title': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'title': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template('index.html',
        title = 'Home',
        user = user,
        books = books)

@app.route('/search', methods = ['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # api = InstagramAPI(access_token=app.config['ACCESS_TOKEN'])
        api = InstagramAPI(client_id=app.config['INSTAGRAM_ID'], client_secret = app.config['INSTAGRAM_SECRET'])
        tag_media, next = api.tag_recent_media(count = 20, tag_name = form.query.data)
        photos = []
        for media in tag_media:
            photos.append(media.images['thumbnail'].url)
        max_tag_id = next.split('&')[2].split('max_tag_id=')[1]
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
    form = EditForm()
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