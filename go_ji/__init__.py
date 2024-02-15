import os

import sqlalchemy
from flask import Flask, abort, request, session
from sqlalchemy import select

from go_ji.db import User, db_session

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


@app.before_request
def require_user() -> None:
    if "user_id" in session:
        return

    if login := request.headers.get("Tailscale-User-Login"):
        try:
            user = db_session.scalars(select(User).where(User.login == login)).one()
        except sqlalchemy.exc.NoResultFound:
            user = User(login=login)
            db_session.add(user)
            db_session.commit()
        session["user_id"] = user.id
        return

    abort(403)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
