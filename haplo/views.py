from flask import render_template, g, request, redirect, url_for
from haplo import app, connect_db



def get_stories_from_id(parent_id):
    cur = g.db.cursor() #user stuff to come
    cur.execute('SELECT id, message FROM entries WHERE parent = ? ORDER BY id ASC', (parent_id,) )
    return [ {'id':row[0],'message':row[1]} for row in cur.fetchall() ]

def create_new_children(parent_id):
    cur = g.db.cursor()
    cur.executemany('INSERT INTO entries (children, message, parent, user_id) VALUES (NULL,NULL,?,0)',
        [(parent_id,) for i in range(4)] )
    g.db.commit()

def update_parents_children(parent_id):
    cur = g.db.cursor()
    cur.execute('SELECT id FROM entries WHERE parent = ?', (parent_id,))    
    
    kids = ','.join([str(i[0]) for i in cur.fetchall()])

    cur.execute('UPDATE entries SET children=? WHERE id=?', (kids, parent_id) )
    g.db.commit()

def set_new_message(m_id, message):
    cur = g.db.cursor()
    cur.execute('UPDATE entries SET message=? WHERE id=?', (message, m_id ))
    g.db.commit()



@app.before_request
def before_request():
    g.db = connect_db()


@app.route('/')
def index(parent_id=0):
    print parent_id
    storylist =  get_stories_from_id(parent_id)
    if len (storylist)==0:
        create_new_children(0)
        storylist =  get_stories_from_id(0)
    print storylist

    return render_template('show_story.html', storylist= storylist)

@app.route('/add', methods=['POST'])
def add_storyline():
    print 'hey', request.form['id'], 'rehkr'
    cur = g.db.cursor()   
    create_new_children(request.form['id']) 
    update_parents_children(request.form['id'])
    set_new_message(request.form['id'], request.form['message'])
    
    return redirect( url_for('index'))

