import sqlalchemy
from flask import Flask, abort, g, redirect, render_template, request, url_for
from sqlalchemy import select

from go_ji.db import User, db_session

app = Flask(__name__)


@app.before_request
def require_user() -> None:
    if "user" in g:
        return

    if login := request.headers.get("Tailscale-User-Login"):
        try:
            user = db_session.scalars(select(User).where(User.login == login)).one()
        except sqlalchemy.exc.NoResultFound:
            user = User(login=login)
            db_session.add(user)
            db_session.commit()
        g.user = user
        return

    abort(403)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def index():
    return render_template("hello.html", name=g.user.login)


@app.route("/links", methods=["POST"])
def create_link():
    return redirect(url_for("index"))
