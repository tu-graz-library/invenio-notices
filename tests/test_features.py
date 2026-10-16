# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Feature check tests."""

from flask import Flask

from invenio_notices import InvenioNotices
from invenio_notices.features import config_flag, endpoint_exists, extension_loaded
from invenio_notices.services import NoticesService

service = NoticesService()


def _app(**config: object) -> Flask:
    app = Flask("testapp")
    app.config.update(**config)
    InvenioNotices(app)
    return app


def test_config_flag() -> None:
    """The feature follows the config variable, missing is off."""
    app = _app(MY_FEATURE=True)
    with app.app_context():
        assert config_flag("MY_FEATURE")()
        assert not config_flag("OTHER_FEATURE")()

    app = _app(MY_FEATURE=False)
    with app.app_context():
        assert not config_flag("MY_FEATURE")()


def test_endpoint_exists() -> None:
    """The feature is on once the route is registered."""
    app = _app()
    app.add_url_rule("/ping", "ping", lambda: "pong")
    with app.app_context():
        assert endpoint_exists("ping")()
        assert not endpoint_exists("missing")()


def test_extension_loaded() -> None:
    """The feature is on once the extension is loaded."""
    app = _app()
    with app.app_context():
        assert extension_loaded("invenio-notices")()
        assert not extension_loaded("invenio-missing")()


def test_feature_on_resolves_by_name() -> None:
    """Feature names resolve via NOTICES_FEATURES."""
    app = _app(NOTICES_FEATURES={"on": lambda: True, "off": lambda: False})
    with app.app_context():
        assert service._feature_on("on")
        assert not service._feature_on("off")


def test_feature_on_unknown_fails_closed() -> None:
    """An unknown feature name keeps the notice hidden."""
    app = _app()
    with app.app_context():
        assert not service._feature_on("unknown")


def test_visible_items_filters_by_feature() -> None:
    """Feature gated items only show while the feature is on."""
    app = _app(NOTICES_FEATURES={"oer_v2": lambda: True, "old": lambda: False})
    notice = {
        "items": [
            "plain",
            {"text": "new upload form", "feature": "oer_v2"},
            {"text": "gone", "feature": "old"},
            {"text": "hidden", "feature": "unknown"},
        ],
    }
    with app.app_context():
        assert service._visible_items(notice, set()) == [
            {"text": "plain", "restricted": False},
            {"text": "new upload form", "restricted": False},
        ]
