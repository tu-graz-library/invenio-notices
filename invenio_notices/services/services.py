# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Decide which notices the current visitor gets.

All checks run server side, hidden notices never reach the client.
"""

from datetime import UTC, datetime

from flask import current_app, g
from flask_login import current_user
from invenio_db import db

from invenio_notices.records.models import NoticeAcknowledgment


def _as_utc(value: str) -> datetime:
    """Parse an ISO-8601 string, naive values count as UTC."""
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _current_roles() -> set[str]:
    """Role names held by the current identity."""
    return {need.value for need in g.identity.provides if need.method == "role"}


class NoticesService:
    """Filters the configured notices and records acknowledgments."""

    def pending(self) -> list[dict]:
        """Return the notices to show the current visitor.

        A notice is shown only if all of these hold:

        * the audience matches (``show_to``),
        * the visitor holds one of the required roles (``roles``),
        * its feature is on, when one is set (``feature``),
        * now (UTC) is inside ``starts_at``/``ends_at``, when set,
        * it was not acknowledged yet.
        """
        authenticated = current_user.is_authenticated
        held = _current_roles() if authenticated else set()
        seen = set()
        if authenticated:
            seen = {
                ack.notice_key
                for ack in NoticeAcknowledgment.query.filter_by(
                    user_id=current_user.id,
                )
            }
        notices = []
        for notice in current_app.config.get("NOTICES", []):
            if notice["key"] in seen:
                continue
            if not self._is_shown_to(notice, authenticated=authenticated):
                continue
            if not self._roles_match(notice.get("roles"), held):
                continue
            feature = notice.get("feature")
            if feature and not self._feature_on(feature):
                continue
            if not self._in_time_window(notice):
                continue
            items = self._visible_items(notice, held)
            accent = bool(
                notice.get("accent")
                or notice.get("roles")
                or any(item["restricted"] for item in items),
            )
            notices.append(
                {
                    "key": notice["key"],
                    "title": str(notice["title"]),
                    "intro": str(notice["intro"]),
                    "items": [item["text"] for item in items],
                    "outro": str(notice["outro"]) if notice.get("outro") else "",
                    "accent": accent,
                },
            )
        return notices

    def acknowledge(self, user_id: int, notice_key: str) -> None:
        """Record that the user acknowledged the notice."""
        already = NoticeAcknowledgment.query.filter_by(
            user_id=user_id,
            notice_key=notice_key,
        ).count()
        if not already:
            db.session.add(
                NoticeAcknowledgment(user_id=user_id, notice_key=notice_key),
            )
            db.session.commit()

    def _is_shown_to(self, notice: dict, *, authenticated: bool) -> bool:
        """Check the notice audience (``show_to``)."""
        show_to = notice.get("show_to", "users")
        if show_to == "guests":
            return not authenticated
        if show_to == "users":
            return authenticated
        return True

    def _roles_match(self, roles: list[str] | None, held: set[str]) -> bool:
        """Check whether the visitor holds one of the required roles."""
        return not roles or any(role in held for role in roles)

    def _visible_items(self, notice: dict, held: set[str]) -> list[dict]:
        """Return the items the visitor is allowed to see.

        Role restricted items are marked so the card can show accented.
        """
        result = []
        for item in notice["items"]:
            if not isinstance(item, dict):
                result.append({"text": str(item), "restricted": False})
                continue
            if not self._roles_match(item.get("roles"), held):
                continue
            feature = item.get("feature")
            if feature and not self._feature_on(feature):
                continue
            result.append(
                {"text": str(item["text"]), "restricted": bool(item.get("roles"))},
            )
        return result

    def _feature_on(self, name: str) -> bool:
        """Resolve a feature name via ``NOTICES_FEATURES``, unknown is off."""
        check = current_app.config.get("NOTICES_FEATURES", {}).get(name)
        if check is None:
            return False
        return bool(check())

    def _in_time_window(self, notice: dict) -> bool:
        """Check ``starts_at``/``ends_at`` against now, in UTC."""
        now = datetime.now(tz=UTC)
        starts_at = notice.get("starts_at")
        if starts_at and now < _as_utc(starts_at):
            return False
        ends_at = notice.get("ends_at")
        return not (ends_at and now >= _as_utc(ends_at))


def pending_notices() -> list[dict]:
    """Template helper, the notices for the current visitor."""
    return NoticesService().pending()
