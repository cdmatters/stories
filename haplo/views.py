from flask import render_template, g, request, redirect, url_for, session
from haplo import app, connect_db

######################
## DATABASE METHODS ##
######################

def get_parent_story(parent_id, user_id):
    cur = g.db.execute('SELECT message FROM entries WHERE id = ? AND user_id=?', (parent_id,user_id))
    message = cur.fetchone() 
    if not message:
        message=['DEFAULT']
    return  dict(id=parent_id, message=message[0])

def get_children_stories(parent_id, user_id):
    cur = g.db.execute('SELECT id, message FROM entries WHERE parent=? AND user_id=? ORDER BY id ASC', (parent_id,user_id) )
    return [ {'id':row[0],'message':row[1]} for row in cur.fetchall() ]

def create_new_children(parent_id, user_id):
    g.db.executemany('INSERT INTO entries (children, message, parent, user_id) VALUES (NULL,NULL,?,?)',
        [(parent_id,user_id) for i in range(4)] )
    g.db.commit()

def update_parents_childlist(parent_id, user_id):
    cur = g.db.execute('SELECT id FROM entries WHERE parent=? AND user_id=?', (parent_id,user_id))    
    kids = ','.join([str(i[0]) for i in cur.fetchall()])
    cur.execute('UPDATE entries SET children=? WHERE id=? AND user_id=?', (kids, parent_id, user_id) )
    g.db.commit()

def set_new_message(m_id, message, user_id):
    cur = g.db.execute('UPDATE entries SET message=? WHERE id=? AND user_id=?', (message, m_id, user_id ))
    g.db.commit()

def return_userid_pass(user):
    cur = g.db.execute('SELECT user_id, password FROM users WHERE username=?',
                     (user,) )
    results = cur.fetchone()
    if not results:
        return (None,None)
    else:
        return results

###############
##   VIEWS   ##
###############

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')

    parent = get_parent_story( **session['user'] )
    storylist =  get_children_stories( **session['user'] )

    if len (storylist)==0:
        create_new_children( **session['user'])
        storylist =  get_children_stories( **session['user'] )

    return render_template('show_story.html', storylist= storylist, parent=parent)

@app.route('/change/<parent_id>', methods=['GET'])
def change_parent(parent_id):
    if session.get('user') != None:
        session['user']['parent_id'] = parent_id     
    return redirect( url_for('index'))

@app.route('/add', methods=['POST'])
def add_child_message():
    new_id = request.form['id']
    message = request.form['message']
    user_id = session['user']['user_id']

    create_new_children( new_id, user_id ) 
    update_parents_childlist( new_id, user_id)
    set_new_message(new_id, message, user_id )
    
    return redirect( url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_id, password = return_userid_pass(request.form['username'])

        if user_id == None:
            error = 'Invalid Username'
        elif password != request.form['password']:
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            session['user'] = {'user_id':user_id, 'parent_id':0}

            return redirect(url_for('index'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect(url_for('index'))





