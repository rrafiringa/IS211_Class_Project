#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

"""
Description
"""

from dbi import DBInterface as db
import os
import logging

from flask import Flask, request, g, redirect, url_for, \
    render_template, session, flash

DATABASE = 'blog.db'
DDL = 'schema.sql'
DEBUG = True
SECRET_KEY = 'My secret is safe'
USERNAME = 'admin'
PASSWORD = 'tmp@99!'
LOG = 'blogger.log'

app = Flask(__name__)

app.config.from_object(__name__)

mydb = db(app)


def getentries(conn, user=None, pid=None):
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
    return mydb.getdata(conn, query)


@app.before_request
def connect():
    """
    Create database connection object into g
    :return: None
    """
    g.db = mydb.db_connect(app)


@app.route('/')
def show():
    """
    Display blog
    :return: HTML document
    """
    sid = session.get('username')
    return render_template('blog.html', entries=getentries(g.db), user_id=sid)


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
        rows = mydb.getdata(g.db, query)
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
            mydb.update(g.db, 'posts', index, ('state',), (action,))
        user = session['username']
        return render_template('dashboard.html',
                               entries=getentries(g.db, user), user=user)
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
        mydb.insert(g.db, 'posts',
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


@app.route('/delete_post/<int:pid>', methods=['GET'])
def delete_post(pid):
    """
    Delete a blog post
    :param pid: (Int) - Post id.
    :return: Redirect
    """
    fields = ('pid',)
    values = (pid,)
    mydb.delete(g.db, 'posts', fields, values)
    return redirect(url_for('dashboard'))


@app.route('/edit_post/<int:pid>', methods=['GET'])
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
            mydb.update(g.db, 'posts', index, fields, values)
            return redirect(url_for('dashboard'))
        else:
            rows = getentries(g.db, pid=pid)
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
    if session.get('logged_in'):
        values = list()
        values.append(request.form['username'])
        values.append(request.form['fname'])
        values.append(request.form['lname'])
        values.append(request.form['password'])
        values.append(request.form['email'])
        values = tuple(values)
        fields = ('username', 'fname', 'lname', 'password', 'email')
        mydb.insert(g.db, 'users', fields, values)
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
