from flask import render_template
from haplo import app

@app.route('/')
def index():
    return render_template('show_story.html')