#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

"""
Description
"""

from dbi import DBInterface as Db_Broker

from flask import Flask, request, g, redirect, url_for, \
    render_template, session

DATABASE = 'blog.db'
DDL = 'schema.sql'
DEBUG = True
SECRET_KEY = 'My secret is safe'
USERNAME = 'admin'
PASSWORD = 'tmp@99!'
LOG = 'blogger.log'

app = Flask(__name__)

app.config.from_object(__name__)

my_db = Db_Broker(app)


def get_entries(conn, user=None, pid=None):
    """
    Fetch blog posts
    :param conn: (Object) - Database connection object
    :param user: (String) - Username
    :param pid: (Int) - Post ID
    :return: (Object) - Database fetched results
    """
    query = 'SELECT * FROM posts'
    if user is not None:
        query += ' WHERE username = "{}"'.format(user)
    if pid is not None:
        query += ' WHERE pid = {}'.format(pid)
    query += ' ORDER BY ts DESC'
    return my_db.getdata(conn, query)


def get_userdata(conn, username=None):
    """
    Get user info
    :param conn: (Object) - Database connection
    :param username: (String) - Username of user to retrieve
    :return: (Object) - Database fetched results
    """
    query = 'SELECT * FROM users'
    if username is not None:
        query += ' WHERE username = "{}"'.format(username)
    return my_db.getdata(conn, query)


@app.before_request
def connect():
    """
    Create database connection object into g
    :return: None
    """
    g.db = my_db.db_connect(app)


@app.route('/')
def show():
    """
    Display blog
    :return: HTML document
    """
    sid = session.get('username')
    return render_template('blog.html', entries=get_entries(g.db), user_id=sid)


@app.route('/logout')
def logout():
    """
    Logout user
    :return: URL redirect
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('show'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login form processing
    On success: go to /dashboard
    On fail: Go to /login with error
    """
    error = None
    if request.method == 'POST':
        session['logged_in'] = False
        user = request.form['user'].strip()
        pwd = request.form['pass'].strip()

        query = 'SELECT * FROM users WHERE username = "{}"'.format(user)
        rows = my_db.getdata(g.db, query)
        for row in rows:
            if user == row['username'] and pwd == row['password']:
                session['username'] = row['username']
                session['logged_in'] = True
                return redirect(url_for('dashboard'))
            else:
                error = 'Wrong credentials, please try again.'
    return render_template('login.html', error=error)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    Manage posts
    :return:
    """
    if session.get('logged_in'):
        if request.method == 'POST':
            pid = request.form['pid']
            pub = request.form['state']
            index = {'field': 'pid', 'value': pid}
            if pub == 'Unpublish':
                action = 0
            else:
                action = 1
            my_db.update(g.db, 'posts', index, ('state',), (action,))

        user = session['username']
        if user == 'admin':
            entries = get_entries(g.db)
        else:
            entries = get_entries(g.db, user)

        g.db = my_db.db_connect(app)
        usr_data = get_userdata(g.db)
        return render_template('dashboard.html',
                               entries=entries,
                               userdata=usr_data,
                               user=user)
    else:
        return redirect(url_for('login'))


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    """
    Add a new blog post
    :return: Redirect|HTML
    """
    if request.method == 'POST':
        title = request.form['title']
        contents = request.form['post']
        username = request.form['username']
        my_db.insert(g.db, 'posts',
                     ('title', 'post', 'username'),
                     (title, contents, username))

    else:
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        else:
            form = dict()
            form['username'] = session['username']
            form['title'] = ''
            form['post'] = ''
            form['action'] = url_for('new_post')
            return render_template('newpost.html', entry=form)
    return redirect(url_for('dashboard'))


@app.route('/delete_post/<int:pid>', methods=['GET', 'POST'])
def delete_post(pid):
    """
    Delete a blog post
    :param pid: (Int) - Post id.
    :return: Redirect
    """
    fields = ('pid',)
    values = (pid,)
    my_db.delete(g.db, 'posts', fields, values)
    return redirect(url_for('dashboard'))


@app.route('/edit_post/<int:pid>', methods=['GET', 'POST'])
def edit_post(pid):
    """
    Update a post
    :param pid: (Int) - Blog post id
    :return: Redirect|HTML
    """
    if session.get('logged_in'):
        if request.method == 'POST':
            fields = ('title', 'post')
            values = (request.form['title'], request.form['post'])
            index = {'field': 'pid', 'value': pid}
            my_db.update(g.db, 'posts', index, fields, values)
            return redirect(url_for('dashboard'))
        else:
            rows = get_entries(g.db, pid=pid)
            form = dict()
            form['action'] = url_for('edit_post', pid=pid)
            for row in rows:
                form['title'] = row['title']
                form['post'] = row['post']
                form['username'] = row['username']
            return render_template('newpost.html', entry=form)
    else:
        return redirect(url_for('login'))


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Add a user
    :return: Redirect
    """
    if session.get('logged_in'):
        values = list()
        values.append(request.form['username'])
        values.append(request.form['fname'])
        values.append(request.form['lname'])
        values.append(request.form['password'])
        values.append(request.form['email'])
        values = tuple(values)
        fields = ('username', 'fname', 'lname', 'password', 'email')
        my_db.insert(g.db, 'users', fields, values)
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@app.route('/delete_user/<string:username>', methods=['GET', 'POST'])
def delete_user(username):
    """
    Delete a user
    :param username: (String) Username
    :return: Redirect
    """
    if session.get('logged_in'):
        my_db.delete(g.db, 'users', ('username',), (username,))
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
