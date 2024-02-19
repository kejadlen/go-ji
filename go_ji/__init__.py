import re
from typing import Any

import sentry_sdk
import sqlalchemy
from flask import (
    Config,
    Flask,
    abort,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import select
from werkzeug.wrappers.response import Response

from go_ji.db import Long, Short, User
from go_ji.db import create_session as create_db_session

VALID_SLUG = re.compile(r"^\w[-\w]*$", re.ASCII)


CONFIG = Config("")
CONFIG["DB_URL"] = "sqlite:///go-ji.db"
CONFIG["TESTING"] = False
CONFIG["SENTRY"] = {}
CONFIG.from_prefixed_env("GO_JI")


def create_app(config_override: dict[str, Any] = {}) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(CONFIG)
    app.config.from_mapping(config_override)

    if sentry_config := app.config["SENTRY"]:  # pragma: no cover
        sentry_sdk.init(
            dsn=sentry_config["DSN"],
            environment=sentry_config["ENVIRONMENT"],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0,
        )

    # Should this go on `g`?
    db_session = create_db_session(app.config["DB_URL"])

    @app.before_request
    def require_user() -> None:
        # Allow anonymous requests for the healthcheck
        if request.path == "/up":
            return

        # I think this is unnecessary, but it also doesn't hurt
        if "user" in g:
            # Might need to set the sentry user here, we'll see?
            return

        if app.config["DEBUG"]:  # pragma: no cover
            login = "user@example"
            name = "A User"
        else:
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
        sentry_sdk.set_user(
            {"id": user.login, "username": user.name, "email": user.login}
        )

    @app.teardown_appcontext
    def shutdown_session(exception=None) -> None:  # noqa: ANN001
        db_session.remove()

    @app.route("/up")
    def up() -> str:
        return ""

    @app.route("/")
    def index() -> str:
        top_shorts = db_session.scalars(
            select(Short).order_by(Short.clicks.desc()).limit(10)
        ).all()
        return render_template("index.html", name=g.user.login, top_shorts=top_shorts)

    @app.route("/links", methods=["POST"])
    def create_link() -> Response:
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
    def go(slug: str) -> Response:
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

    # purely for testing Sentry
    @app.route("/die")
    def die() -> str:
        1 / 0  # raises an error
        return "<p>Hello, World!</p>"  # pragma: no cover

    return app
