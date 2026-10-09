# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Blueprint for the notices API."""

from typing import TYPE_CHECKING

from flask import Blueprint, Flask

if TYPE_CHECKING:
    from werkzeug.wrappers import Response as BaseResponse


def api_blueprint(_app: Flask) -> Blueprint:
    """Blueprint with the acknowledge endpoint."""
    blueprint = Blueprint("invenio_notices", __name__, url_prefix="/notices")

    @blueprint.route("/<key>/acknowledge", methods=["POST"])
    def acknowledge(key: str) -> BaseResponse:
        """Record that the current user acknowledged a notice."""
        raise NotImplementedError

    return blueprint
