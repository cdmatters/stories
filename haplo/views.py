from flask import render_template, g
from haplo import app, connect_db

def get_stories_from_id(parent_id):
    db = connect_db()
    cur = db.cursor()
    cur.execute('SELECT message, id FROM entries WHERE parent = ? ORDER BY id ASC', (parent_id,) )
    return [ {'id':row[0],'message':row[1]} for row in cur.fetchall() ]


@app.route('/')
def index():
    get_stories_from_id(parent_id=0)
    return render_template('show_story.html')

