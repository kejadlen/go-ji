import re
from typing import Any

import sqlalchemy
from flask import Flask, abort, g, redirect, render_template, request, url_for
from sqlalchemy import select

from go_ji.db import Long, Short, User
from go_ji.db import create_session as create_db_session

VALID_SLUG = re.compile(r"^\w[-\w]*$", re.ASCII)


def create_app(config: dict[str, Any] = {}) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # defaults
    app.config["DB_URL"] = "sqlite:///go-ji.db"

    # overrides
    app.config.from_prefixed_env("GO_JI")
    app.config.from_mapping(config)

    # set up db
    db_session = create_db_session(app.config["DB_URL"])

    @app.before_request
    def require_user() -> None:
        # I think this is unnecessary, but it also doesn't hurt
        if "user" in g:
            return

        if not (login := request.headers.get("Tailscale-User-Login")):
            abort(403)

        name = request.headers["Tailscale-User-Name"]
        try:
            user = db_session.scalars(select(User).where(User.login == login)).one()
            user.name = name
        except sqlalchemy.exc.NoResultFound:
            user = User(login=login, name=name)
        db_session.add(user)
        db_session.commit()

        g.user = user

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.route("/")
    def index():
        return render_template("hello.html", name=g.user.login)

    @app.route("/links", methods=["POST"])
    def create_link():
        slug = request.form["slug"]
        url = request.form["url"]

        if not VALID_SLUG.match(slug):
            abort(400)

        try:
            short = db_session.scalars(select(Short).where(Short.slug == slug)).one()
        except sqlalchemy.exc.NoResultFound:
            short = Short(slug=slug)
            db_session.add(short)
            db_session.commit()

        long = Long(url=url, short=short, created_by=g.user)
        db_session.add_all([short, long])
        db_session.commit()

        return redirect(url_for("index"))

    @app.route("/<slug>")
    def go(slug: str):
        long = db_session.scalars(
            select(Long)
            .join(Long.short)
            .where(Short.slug == slug)
            .order_by(Long.created_at.desc())
        ).first()

        if long is None:
            abort(404)

        long.short.clicks += 1
        db_session.add(long.short)
        db_session.commit()

        return redirect(long.url)

    return app
