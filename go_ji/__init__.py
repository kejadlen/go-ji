from flask import Flask

from go_ji.db import db_session

app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
