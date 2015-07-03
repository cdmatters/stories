from flask import render_template, g, request, redirect, url_for, session
from haplo import app, connect_db


def get_story_from_id(m_id, user_id):
    cur = g.db.cursor()
    cur.execute('SELECT message FROM entries WHERE id = ? AND user_id=?', (m_id,user_id))
    message = cur.fetchone() 
    if not message:
        message=['DEFAULT']
    return  dict(id=m_id, message=message[0] )

def get_stories_from_parent(parent_id, user_id):
    cur = g.db.cursor() #user stuff to come
    cur.execute('SELECT id, message FROM entries WHERE parent=? AND user_id=? ORDER BY id ASC', (parent_id,user_id) )
    return [ {'id':row[0],'message':row[1]} for row in cur.fetchall() ]

def create_new_children(parent_id, user_id):
    cur = g.db.cursor()
    cur.executemany('INSERT INTO entries (children, message, parent, user_id) VALUES (NULL,NULL,?,?)',
        [(parent_id,user_id) for i in range(4)] )
    g.db.commit()

def update_parents_children(parent_id, user_id):
    cur = g.db.cursor()
    cur.execute('SELECT id FROM entries WHERE parent=? AND user_id=?', (parent_id,user_id))    
    
    kids = ','.join([str(i[0]) for i in cur.fetchall()])

    cur.execute('UPDATE entries SET children=? WHERE id=? AND user_id=?', (kids, parent_id, user_id) )
    g.db.commit()

def set_new_message(m_id, message, user_id):
    cur = g.db.cursor()
    cur.execute('UPDATE entries SET message=? WHERE id=? AND user_id=?', (message, m_id, user_id ))
    g.db.commit()





@app.before_request
def before_request():
    g.db = connect_db()


@app.route('/')
def index():

    if not session.get('logged_in'):
        return render_template('login.html')


    parent = get_story_from_id(session['user']['parent'],  session['user']['user_id'])
    storylist =  get_stories_from_parent(session['user']['parent'], session['user']['user_id'])

    if len (storylist)==0:
        create_new_children(0, session['user']['user_id'])
        storylist =  get_stories_from_parent(0, session['user']['user_id'])

    return render_template('show_story.html', storylist= storylist, parent=parent)

@app.route('/add', methods=['POST'])
def add_storyline():

    cur = g.db.cursor()   
    create_new_children(request.form['id'], session['user']['user_id']) 
    update_parents_children(request.form['id'], session['user']['user_id'])
    set_new_message(request.form['id'], request.form['message'], session['user']['user_id'] )
    
    return redirect( url_for('index'))

@app.route('/change/<parent_id>', methods=['GET'])
def change_storyline(parent_id):
    session['user']['parent'] = parent_id 
    return redirect( url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute('SELECT password, user_id FROM users WHERE username=?',
                     (request.form['username'],) )
        results = cur.fetchone()
        if len(results) == 0:
            error = 'Invalid Username'
        elif results[0] != request.form['password']:
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            session['user'] = {'user_id':results[1], 'parent':0}

            return redirect(url_for('index'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect(url_for('index'))





