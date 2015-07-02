from flask import render_template, g, request, redirect, url_for
from haplo import app, connect_db

def get_stories_from_id(parent_id):
    db = connect_db()
    cur = db.cursor() #user stuff to come
    cur.execute('SELECT message, id FROM entries WHERE parent = ? ORDER BY id ASC', (parent_id,) )
    return [ {'id':row[0],'message':row[1]} for row in cur.fetchall() ]




@app.route('/')
def index():
    print get_stories_from_id(parent_id=0)
    return render_template('show_story.html' )

@app.route('/add', methods=['POST'])
def add_storyline():
    db = connect_db()
    cur = db.cursor()
    cur.execute('INSERT INTO entries (children, message, parent, user_id) VALUES (?,?,?,0)', 
                (None, request.form['message'], request.form['parent'] ))
    db.commit()
    return redirect( url_for('index'))

