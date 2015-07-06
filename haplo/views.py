from flask import render_template, g, request, redirect, url_for, session
from haplo import app, connect_db

######################
## DATABASE METHODS ##
######################

def get_story(node_id, user_id):
    """Return a story eg{id:12, message:'foo'} given message_id and user_id"""
    if node_id != 0:
        cur = g.db.execute('SELECT message FROM entries WHERE id = ? AND user_id=?', (node_id,user_id))
    else: #no nodes have id=0. it must be a root node for a user
        cur = g.db.execute('SELECT message FROM entries WHERE parent = -1 AND user_id=?', (user_id,))    
    message = cur.fetchone()
    
    if not message:
        message = ['DEFAULT']
    return  dict( id =node_id, message=message[0])

def get_children_stories(node_id, user_id):
    """Return list of stories [{id:13, message:'foo'}, ...] of immediate children 
given message_id and user_id"""

    cur = g.db.execute('SELECT id, message FROM entries \
        WHERE parent=? AND user_id=? ORDER BY id ASC', (node_id,user_id) )
    return [ {'id':row[0],'message':row[1]} for row in cur.fetchall() ]

def create_new_children(node_id, user_id, number=4):
    """Create new children entries into database, with NULL text, for given message"""
    g.db.executemany('INSERT INTO entries (children, message, parent, user_id)\
                     VALUES (NULL,NULL,?,?)', [(node_id,user_id) for i in range(number)] )
    g.db.commit()

def update_childlist(node_id, user_id):
    """Update node to hold str(list of its children)"""
    cur = g.db.execute('SELECT id FROM entries WHERE parent=? AND user_id=?', (node_id,user_id))    
    kids = ','.join([str(i[0]) for i in cur.fetchall()])
    cur.execute('UPDATE entries SET children=? WHERE id=? AND user_id=?', (kids, node_id, user_id) )
    g.db.commit()

def set_node_message(node_id, message, user_id):
    """ Update message text for a message"""
    cur = g.db.execute('UPDATE entries SET message=? WHERE id=? AND user_id=?', (message, node_id, user_id ))
    g.db.commit()

def return_userid_pass(user):
    """Return tuple of (user_id, password) for given username"""
    cur = g.db.execute('SELECT user_id, password FROM users WHERE username=?',
                     (user,) )
    results = cur.fetchone()
    if not results:
        return (None,None)
    else:
        return results

def add_login_details(username, password):
    """Creat new user"""
    g.db.execute('INSERT INTO  users (username, password) VALUES (?,?)', (username,password) )
    g.db.commit()

def add_first_words(user_id, message):
    """Create new message that is root sentence for new user"""
    g.db.execute('INSERT INTO entries (children, message, parent, user_id) VALUES (NULL, ?, ?, ?)', 
                   (message,-1,user_id))
    g.db.commit()

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
    """If logged in: (else login)
    - fetch node story corresponding to current node id, stored in session
    - fetch or generate children for node
    - render "show_story.html" with data """
    
    if not session.get('logged_in'):
        return render_template('login.html')

    node_story = get_story( **session['user'] )
    kids_storylist =  get_children_stories( **session['user'] )

    if len (kids_storylist)==0:
        create_new_children( **session['user'] )
        kids_storylist =  get_children_stories( **session['user'] )

    return render_template('show_story.html', kids=kids_storylist, parent=node_story)

@app.route('/change/<node_id>', methods=['GET'])
def change_parent(node_id):
    """Change current node id stored in session and reload main page"""
    if session.get('user') != None:
        session['user']['node_id'] = int(node_id)     
    return redirect( url_for('index'))

@app.route('/add', methods=['POST'])
def add_child_message():
    """Load message into database, create its empty children, reload original page """
    new_id = request.form['id']
    message = request.form['message']
    user_id = session['user']['user_id']

    if message:

        create_new_children( new_id, user_id ) 
        update_childlist( new_id, user_id)
        set_node_message(new_id, message, user_id )
    
    return redirect( url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Verify credentials, then set session to logged in, and set current node to root """
    error = None
    if request.method == 'POST':
        user_id, password = return_userid_pass(request.form['username'])

        if user_id == None:
            error = 'Invalid Username'
        elif password != request.form['password']:
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            session['user'] = {'user_id':user_id, 'node_id':0}

            return redirect(url_for('index'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Delete session variables logged_in and user"""
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/adduser', methods=['POST'])
def add_user():
    """Create new user details, insert root message, and proceed to main page"""
    username = request.form['username']
    password = request.form['password']
    first_words = request.form['message']

    if username and password and first_words:
        add_login_details(username, password)

        user_id, _  = return_userid_pass(request.form['username'])
        add_first_words(user_id, first_words)

        session['logged_in'] = True
        session['user'] = {'user_id':user_id, 'node_id':0}
        return redirect(url_for('index'))
    return render_template('login.html', error='No Empty Fields')











