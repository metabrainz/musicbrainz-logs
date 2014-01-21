from flask import render_template
from mblogs import app

@app.route("/")
def index():
    return render_template("index", title="MusicBrainz Logs")
