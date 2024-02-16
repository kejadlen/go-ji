import pytest
from flask import g
from sqlalchemy import select

from go_ji.db import Short, User


class TestAuth:
    def test_authenticates(self, app):
        with app.test_request_context(
            "/",
            headers={
                "Tailscale-User-Login": "foo@example",
                "Tailscale-User-Name": "Foo Bar",
            },
        ):
            app.preprocess_request()

            assert g.user.name == "Foo Bar"
            assert g.user.login == "foo@example"

    def test_requires_tailscale_headers(self, client):
        response = client.get("/")

        assert response.status_code == 403

    def test_requires_tailscale_name(self, client):
        with pytest.raises(KeyError):
            client.get("/", headers={"Tailscale-User-Login": "foo@example"})

    def test_updates_name(self, app, client, db_session):
        db_session.add(User(login="foo@example", name="Foo Bar"))
        db_session.commit()

        with app.test_request_context("/"):
            client.get(
                "/",
                headers={
                    "Tailscale-User-Login": "foo@example",
                    "Tailscale-User-Name": "Bar Foo",
                },
            )

            assert g.user.name == "Bar Foo"

    def test_skips_if_already_checked(self, app, client):
        with app.test_request_context("/"):
            g.user = User(login="foo@example", name="Foo Bar")

            client.get(
                "/",
                headers={
                    "Tailscale-User-Login": "foo@example",
                    "Tailscale-User-Name": "Bar Foo",
                },
            )

            assert g.user.name == "Foo Bar"
            assert g.user.login == "foo@example"


def test_index(authed, client):
    with authed:
        response = client.get("/")

        assert response.status_code == 200


class TestCreateLink:
    def test_create_link(self, authed, client, db_session):
        with authed:
            response = client.post(
                "/links", data={"slug": "foo", "url": "https://example.com"}
            )

            assert response.status_code == 302
            assert response.headers["Location"] == "/"

            short = db_session.scalars(select(Short).where(Short.slug == "foo")).one()
            assert [l.url for l in short.longs] == ["https://example.com"]

    def test_requires_slug(self, authed, client):
        with authed:
            response = client.post("/links", data={"url": "https://example.com"})

            assert response.status_code == 400

    def test_requires_url(self, authed, client):
        with authed:
            response = client.post("/links", data={"slug": "foo"})

            assert response.status_code == 400

    def test_invalid_slug(self, authed, client):
        with authed:
            response = client.post(
                "/links", data={"slug": "", "url": "https://example.com"}
            )
            assert response.status_code == 400

            response = client.post(
                "/links", data={"slug": "!", "url": "https://example.com"}
            )
            assert response.status_code == 400

            response = client.post(
                "/links", data={"slug": "!a", "url": "https://example.com"}
            )
            assert response.status_code == 400

            response = client.post(
                "/links", data={"slug": "a!", "url": "https://example.com"}
            )
            assert response.status_code == 400


class TestGo:
    def test_go(self, authed, client):
        with authed:
            client.post("/links", data={"slug": "foo", "url": "https://example.com"})

            response = client.get("/foo")

            assert response.status_code == 302
            assert response.headers["Location"] == "https://example.com"

    def test_no_slug(self, authed, client):
        with authed:
            response = client.get("/foo")

            assert response.status_code == 404
