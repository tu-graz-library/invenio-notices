# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Views for invenio-notices."""

from flask import Blueprint, Flask

from .resources import NoticesResource, NoticesResourceConfig

blueprint = Blueprint(
    "invenio_notices_ext",
    __name__,
    template_folder="templates",
)
"""Blueprint used to register the templates folder."""


def create_notices_bp(_app: Flask) -> Blueprint:
    """Create the notices resource blueprint."""
    return NoticesResource(NoticesResourceConfig()).as_blueprint()
