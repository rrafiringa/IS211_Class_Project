#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

"""
Description
"""

from dbi import DBInterface as db
import os
import logging

from flask import Flask, request, g, redirect, url_for, \
    render_template, session

DATABASE = 'blog.db'
DDL = 'schema.sql'
DEBUG = True
SECRET_KEY = 'My secret is safe'
USERNAME = 'admin'
PASSWORD = 'password'
LOG = 'blogger.log'

app = Flask(__name__)

app.config.from_object(__name__)

mydb = db(app)


@app.route('/')
def show():
    """
    First page
    Display blog
    """
    table = 'posts'
    query = 'SELECT * FROM {} ORDER BY ts DESC'.format(table)
    g.db = mydb.db_connect(app)
    entries = mydb.getdata(g.db, query)
    return render_template('blog.html', entries=entries)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register new user
    :return:
    """
    if request.method == 'POST':
        pass
    return url_for('login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login form processing
    On success: go to /dashboard
    On fail: Go to /login with error
    """
    error = None
    if request.method == 'POST':
        user = request.form['user'].strip()
        pwd = request.form['pass'].strip()
        if user == app.config['USERNAME'] and pwd == app.config['PASSWORD']:
            return redirect('/posts')
        else:
            error = 'Wrong credentials, please try again.'
    return render_template('login.html', error=error)


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        contents = request.form['contents']
    else:
        render_template('entry.html')
    return redirect(url_for('show'))


if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
