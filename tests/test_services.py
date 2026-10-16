# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Service tests."""

from datetime import UTC, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from flask import Flask

from invenio_notices import InvenioNotices
from invenio_notices.services import NoticesService, pending_notices
from invenio_notices.services import services as services_module

service = NoticesService()


def _iso(delta: timedelta, tz: timezone = UTC) -> str:
    return (datetime.now(tz=UTC) + delta).astimezone(tz).isoformat()


def _app(**config: object) -> Flask:
    app = Flask("testapp")
    app.config.update(**config)
    InvenioNotices(app)
    return app


def _login(monkeypatch: pytest.MonkeyPatch, roles: set[str], seen: set[str]) -> None:
    """Fake an authenticated visitor with roles and acknowledged keys."""
    monkeypatch.setattr(
        services_module,
        "current_user",
        SimpleNamespace(is_authenticated=True, id=7),
    )
    monkeypatch.setattr(services_module, "_current_roles", lambda: roles)
    acks = [SimpleNamespace(notice_key=key) for key in seen]
    monkeypatch.setattr(
        services_module,
        "NoticeAcknowledgment",
        SimpleNamespace(query=SimpleNamespace(filter_by=lambda **_: acks)),
    )


def _logout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fake an anonymous visitor."""
    monkeypatch.setattr(
        services_module,
        "current_user",
        SimpleNamespace(is_authenticated=False),
    )


def test_is_shown_to_users() -> None:
    """A users notice is only shown to authenticated visitors."""
    notice = {"show_to": "users"}
    assert service._is_shown_to(notice, authenticated=True)
    assert not service._is_shown_to(notice, authenticated=False)


def test_is_shown_to_guests() -> None:
    """A guests notice is only shown to anonymous visitors."""
    notice = {"show_to": "guests"}
    assert not service._is_shown_to(notice, authenticated=True)
    assert service._is_shown_to(notice, authenticated=False)


def test_is_shown_to_all() -> None:
    """An all notice is shown to everyone."""
    notice = {"show_to": "all"}
    assert service._is_shown_to(notice, authenticated=True)
    assert service._is_shown_to(notice, authenticated=False)


def test_is_shown_to_defaults_to_users() -> None:
    """Without show_to the notice is treated as a users notice."""
    assert service._is_shown_to({}, authenticated=True)
    assert not service._is_shown_to({}, authenticated=False)


def test_roles_match_without_required_roles() -> None:
    """A notice without roles matches every visitor."""
    assert service._roles_match(None, set())
    assert service._roles_match([], {"curator"})


def test_roles_match_with_required_roles() -> None:
    """A notice with roles needs at least one of them."""
    assert service._roles_match(["curator"], {"curator", "admin"})
    assert not service._roles_match(["curator"], {"admin"})
    assert not service._roles_match(["curator"], set())


def test_visible_items_plain() -> None:
    """Plain items are shown to everyone."""
    notice = {"items": ["first", "second"]}
    assert service._visible_items(notice, set()) == [
        {"text": "first", "restricted": False},
        {"text": "second", "restricted": False},
    ]


def test_visible_items_filters_by_role() -> None:
    """Role gated items are dropped for visitors without the role."""
    notice = {
        "items": [
            "plain",
            {"text": "for curators", "roles": ["curator"]},
        ],
    }
    assert service._visible_items(notice, set()) == [
        {"text": "plain", "restricted": False},
    ]
    assert service._visible_items(notice, {"curator"}) == [
        {"text": "plain", "restricted": False},
        {"text": "for curators", "restricted": True},
    ]


def test_in_time_window_without_window() -> None:
    """A notice without starts_at/ends_at always shows."""
    assert service._in_time_window({})


def test_in_time_window_starts_at() -> None:
    """A notice shows once starts_at has passed."""
    assert service._in_time_window({"starts_at": _iso(timedelta(hours=-1))})
    assert not service._in_time_window({"starts_at": _iso(timedelta(hours=1))})


def test_in_time_window_ends_at() -> None:
    """A notice stops showing after ends_at."""
    assert service._in_time_window({"ends_at": _iso(timedelta(hours=1))})
    assert not service._in_time_window({"ends_at": _iso(timedelta(hours=-1))})


def test_in_time_window_handles_timezones() -> None:
    """Offsets are converted, naive values count as UTC."""
    vienna = timezone(timedelta(hours=1))
    assert service._in_time_window(
        {
            "starts_at": _iso(timedelta(hours=-1), tz=vienna),
            "ends_at": _iso(timedelta(hours=1), tz=vienna),
        },
    )
    naive_past = (datetime.now(tz=UTC) - timedelta(hours=1)).replace(tzinfo=None)
    assert service._in_time_window({"starts_at": naive_past.isoformat()})


def test_pending_for_guests(monkeypatch: pytest.MonkeyPatch) -> None:
    """A guest gets the guests and all notices, rendered as plain data."""
    _logout(monkeypatch)
    app = _app(
        NOTICES=[
            {"key": "a", "show_to": "users", "title": "t", "intro": "i", "items": []},
            {"key": "b", "show_to": "guests", "title": "t", "intro": "i", "items": []},
            {"key": "c", "show_to": "all", "title": "t", "intro": "i", "items": ["x"]},
        ],
    )
    with app.test_request_context():
        pending = service.pending()
    assert [notice["key"] for notice in pending] == ["b", "c"]
    assert pending[1] == {
        "key": "c",
        "title": "t",
        "intro": "i",
        "items": ["x"],
        "outro": "",
        "accent": False,
    }


def test_pending_accents_role_content(monkeypatch: pytest.MonkeyPatch) -> None:
    """A card accents when role gated content is shown."""
    _login(monkeypatch, roles={"curator"}, seen=set())
    app = _app(
        NOTICES=[
            {
                "key": "a",
                "title": "t",
                "intro": "i",
                "items": ["plain", {"text": "extra", "roles": ["curator"]}],
            },
            {
                "key": "b",
                "roles": ["curator"],
                "title": "t",
                "intro": "i",
                "items": [],
            },
            {"key": "c", "title": "t", "intro": "i", "items": ["plain"]},
        ],
    )
    with app.test_request_context():
        pending = service.pending()
    assert [notice["accent"] for notice in pending] == [True, True, False]


def test_pending_skips_acknowledged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Acknowledged notices are not shown again."""
    _login(monkeypatch, roles=set(), seen={"old"})
    app = _app(
        NOTICES=[
            {"key": "old", "title": "t", "intro": "i", "items": []},
            {"key": "new", "title": "t", "intro": "i", "items": []},
        ],
    )
    with app.test_request_context():
        pending = service.pending()
    assert [notice["key"] for notice in pending] == ["new"]


def test_pending_applies_all_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    """Roles, feature and time window all have to match."""
    _login(monkeypatch, roles={"curator"}, seen=set())
    base = {"title": "t", "intro": "i", "items": []}
    app = _app(
        NOTICES=[
            {"key": "role-ok", "roles": ["curator"], **base},
            {"key": "role-no", "roles": ["admin"], **base},
            {"key": "feature-off", "feature": "off", **base},
            {"key": "too-early", "starts_at": _iso(timedelta(hours=1)), **base},
        ],
        NOTICES_FEATURES={"off": lambda: False},
    )
    with app.test_request_context():
        pending = service.pending()
    assert [notice["key"] for notice in pending] == ["role-ok"]


def test_pending_notices_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    """The template helper returns the pending notices."""
    _logout(monkeypatch)
    app = _app(
        NOTICES=[
            {"key": "a", "show_to": "all", "title": "t", "intro": "i", "items": []},
        ],
    )
    with app.test_request_context():
        assert [notice["key"] for notice in pending_notices()] == ["a"]
