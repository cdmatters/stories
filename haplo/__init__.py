import os
import sqlite3

from flask import Flask


app = Flask(__name__)
app.config.from_pyfile('config.py')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    """Initialize database with schema.sql"""
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            cur = db.cursor()
            cur.executescript(f.read())
        db.commit()

if not os.path.isfile('./haplo/haplo.db'):
    init_db()

import haplo.views




