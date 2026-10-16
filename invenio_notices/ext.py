# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Flask extension for invenio-notices."""

from flask import Flask

from . import config
from .services import pending_notices


class InvenioNotices:
    """invenio-notices extension."""

    def __init__(self, app: Flask | None = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.init_config(app)
        app.context_processor(lambda: {"notices": pending_notices()})
        app.extensions["invenio-notices"] = self

    def init_config(self, app: Flask) -> None:
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("NOTICES"):
                app.config.setdefault(k, getattr(config, k))


class UnknownFeatureError(KeyError):
    """A notice references a feature name missing from ``NOTICES_FEATURES``."""

    def __init__(self, notice_key: str, feature: str) -> None:
        """Construct."""
        super().__init__(
            f"Notice {notice_key!r} references unknown feature {feature!r}.",
        )


def finalize_app(app: Flask) -> None:
    """Finalize app.

    Validates at boot that every feature name referenced in ``NOTICES``
    exists in ``NOTICES_FEATURES``, so a typo fails fast instead of
    silently hiding the notice.
    """
    features = app.config.get("NOTICES_FEATURES", {})
    for notice in app.config.get("NOTICES", []):
        items = (item for item in notice.get("items", []) if isinstance(item, dict))
        names = [notice.get("feature"), *(item.get("feature") for item in items)]
        for name in names:
            if name is not None and name not in features:
                raise UnknownFeatureError(notice.get("key", ""), name)
