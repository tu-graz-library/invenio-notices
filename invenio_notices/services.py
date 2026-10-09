# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Decide which notices the current visitor gets.

All checks run server side, hidden notices never reach the client.
"""


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
        raise NotImplementedError

    def acknowledge(self, user_id: int, notice_key: str) -> None:
        """Record that the user acknowledged the notice."""
        raise NotImplementedError

    def _is_shown_to(self, notice: dict, *, authenticated: bool) -> bool:
        """Check the notice audience (``show_to``)."""
        raise NotImplementedError

    def _roles_match(self, roles: list[str] | None, held: set[str]) -> bool:
        """Check whether the visitor holds one of the required roles."""
        raise NotImplementedError

    def _visible_items(self, notice: dict, held: set[str]) -> list[str]:
        """Return the item texts the visitor is allowed to see."""
        raise NotImplementedError

    def _feature_on(self, name: str) -> bool:
        """Resolve a feature name via ``NOTICES_FEATURES``, unknown is off."""
        raise NotImplementedError

    def _in_time_window(self, notice: dict) -> bool:
        """Check ``starts_at``/``ends_at`` against now, in UTC."""
        raise NotImplementedError


def pending_notices() -> list[dict]:
    """Template helper, the notices for the current visitor."""
    raise NotImplementedError
