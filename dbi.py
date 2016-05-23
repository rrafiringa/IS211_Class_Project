#!/usr/bin/env python
# -*- Coding: Utf-8 -*-

"""
Database interface
"""

import os
import sqlite3
from contextlib import closing


class DBInterface(object):
    """"
    Database interface
    """

    def __init__(self, app):
        """
        Constructor
        """
        self.table = ''
        if not os.path.exists(app.config['DATABASE']):
            self.db_init(app)

    def db_connect(self, app):
        """
        Connect to database
        :param app: Flask app object
        :return: Sqlite connection or False
        """
        if app.config['DATABASE'] is not None:
            conn = sqlite3.connect(app.config['DATABASE'])
            conn.row_factory = sqlite3.Row
            return conn
        return False

    def db_init(self, app):
        """
        Initialize database
        :param app: (
        :return: Commit status 0: success | non-zero: rollback
        """
        with closing(self.db_connect(app)) as db:
            with app.open_resource(
                    app.config['DDL'],
                    mode='r') as schema:
                db.cursor().executescript(schema.read())
                db.commit()

    def getdata(self, conn, query):
        """
        Select query
        :param conn: (Object) Database connection
        :param query: (String) SQL string
        :return: (Object) Query results
        """
        with closing(conn) as db:
            db.row_factory = sqlite3.Row
            cur = db.cursor()
            res = cur.execute(query).fetchall()
            return res

    def insert(self, conn, table, fields=(), values=()):
        """
        Insert record into table
        :param conn: (Object) sqlite3 database connection
        :param table: (String) Table name
        :param fields: (Tuple) List of fields
        :param values: (Tuple) List of values
        :return: (Int) Affected rows
        """
        self.table = table
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            self.table, ', '.join(fields),
            ', '.join(['?'] * len(values)))
        cur = conn.execute(query, values)
        conn.commit()
        stat = cur.lastrowid
        cur.close()
        return stat

    def update(self, conn, table, index, fields, values):
        """
        Update a blog post
        :param conn:
        :param table:
        :param index:
        :param fields:
        :param values:
        :return:
        """
        self.table = table
        query = 'UPDATE {} SET '.format(self.table)
        query += ', '.join([' = '.join(items)
                            for items in zip(fields,
                                             '?' * len(values))])
        query += ' WHERE {} = {}'.format(index.get('field'),
                                           index.get('value'))

        cur = conn.cursor()
        cur.execute(query, values)
        stat = conn.commit()
        cur.close()
        return stat

    def delete(self, conn, table, fields=(), values=(), operator=None):
        """
        Delete from table
        :param conn: (Object) - Database connection
        :param table: (String) - Table name
        :param fields: (Tuple) - Column list
        :param values: (Tuple) - Values list
        :param operator: (String) - Conditional operator (AND|OR)
        :return:
        """
        self.table = table
        query = 'DELETE FROM ' + self.table

        if len(fields) > 0 and len(fields) == len(values):
            cond = ' WHERE '
            if operator is not None:
                cond += operator.join(
                    [' = '.join(items) for items in
                     zip(fields, '?' * len(values))])
            else:
                cond += ' = '.join([str(fields[0]), '?' * len(values)])
            query += cond
        cur = conn.cursor()
        cur.execute(query, values)
        stat = conn.commit()
        cur.close()
        return stat
