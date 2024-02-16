# https://flask.palletsprojects.com/en/3.0.x/tutorial/tests/
import os
import tempfile

import pytest

from go_ji import create_app
from go_ji.db import create_session as create_db_session


@pytest.fixture
def authed(app, client):
    with app.test_request_context("/") as context:
        client.get(
            "/",
            headers={
                "Tailscale-User-Login": "foo@example",
                "Tailscale-User-Name": "Foo Bar",
            },
        )

        yield context


@pytest.fixture
def app(db_url):
    app = create_app(
        {
            "TESTING": True,
            "DB_URL": db_url,
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def db_session(db_url):
    return create_db_session(db_url)


@pytest.fixture
def db_url():
    db_fd, db_path = tempfile.mkstemp()

    yield f"sqlite:////{db_path}"

    os.close(db_fd)
    os.unlink(db_path)
