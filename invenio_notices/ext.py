# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Flask extension for invenio-notices."""

from typing import TYPE_CHECKING

from . import config
from .services import pending_notices

if TYPE_CHECKING:
    from flask import Flask


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


def finalize_app(_app: Flask) -> None:
    """Finalize app.

    Validates at boot that every feature name referenced in ``NOTICES``
    exists in ``NOTICES_FEATURES``.
    """
    raise NotImplementedError
