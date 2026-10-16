# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Acknowledge endpoint tests, against a real database."""

from collections.abc import Iterator
from http import HTTPStatus
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask
from invenio_db import InvenioDB, db

from invenio_notices import InvenioNotices
from invenio_notices.records.models import NoticeAcknowledgment
from invenio_notices.resources import resources as resources_module
from invenio_notices.services import NoticesService
from invenio_notices.services import services as services_module
from invenio_notices.views import create_notices_bp


@pytest.fixture
def app(tmp_path: Path) -> Iterator[Flask]:
    """Application with a database and the notices blueprint."""
    app = Flask("testapp")
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path}/test.db",
    )
    InvenioDB(app)
    InvenioNotices(app)
    app.register_blueprint(create_notices_bp(app))
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _login(monkeypatch: pytest.MonkeyPatch, module: object, user_id: int = 7) -> None:
    monkeypatch.setattr(
        module,
        "current_user",
        SimpleNamespace(is_authenticated=True, id=user_id),
    )


def test_acknowledge_needs_login(app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
    """A guest cannot acknowledge."""
    monkeypatch.setattr(
        resources_module,
        "current_user",
        SimpleNamespace(is_authenticated=False),
    )
    response = app.test_client().post("/notices/welcome/acknowledge")
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_acknowledge_stores_once(app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
    """Acknowledging stores one row, repeating it stays one row."""
    _login(monkeypatch, resources_module)
    client = app.test_client()
    response = client.post("/notices/welcome/acknowledge")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {"acknowledged": "welcome"}

    client.post("/notices/welcome/acknowledge")
    rows = NoticeAcknowledgment.query.filter_by(user_id=7).all()
    assert [(row.user_id, row.notice_key) for row in rows] == [(7, "welcome")]


def test_acknowledged_notice_disappears(
    app: Flask,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """After acknowledging, pending() no longer returns the notice."""
    _login(monkeypatch, services_module)
    monkeypatch.setattr(services_module, "_current_roles", set)
    app.config["NOTICES"] = [{"key": "w", "title": "t", "intro": "i", "items": []}]
    service = NoticesService()
    with app.test_request_context():
        assert [notice["key"] for notice in service.pending()] == ["w"]
        service.acknowledge(7, "w")
        assert service.pending() == []
