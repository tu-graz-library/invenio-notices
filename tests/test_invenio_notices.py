# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Module tests."""

import pytest
from flask import Flask

from invenio_notices import InvenioNotices, __version__
from invenio_notices.ext import UnknownFeatureError, finalize_app


def test_version() -> None:
    """Test version import."""
    assert __version__


def test_init() -> None:
    """Test extension initialization."""
    app = Flask("testapp")
    InvenioNotices(app)
    assert "invenio-notices" in app.extensions

    app = Flask("testapp")
    ext = InvenioNotices()
    assert "invenio-notices" not in app.extensions
    ext.init_app(app)
    assert "invenio-notices" in app.extensions


def test_init_config() -> None:
    """Test config defaults."""
    app = Flask("testapp")
    InvenioNotices(app)
    assert app.config["NOTICES"] == []
    assert app.config["NOTICES_FEATURES"] == {}


def test_finalize_app_known_features() -> None:
    """Test boot validation accepts known feature names."""
    app = Flask("testapp")
    InvenioNotices(app)
    app.config["NOTICES"] = [
        {
            "key": "k",
            "feature": "oer",
            "items": ["plain", {"text": "gated", "feature": "oer"}],
        },
    ]
    app.config["NOTICES_FEATURES"] = {"oer": lambda: True}
    finalize_app(app)


def test_finalize_app_unknown_notice_feature() -> None:
    """Test boot validation rejects an unknown notice feature."""
    app = Flask("testapp")
    InvenioNotices(app)
    app.config["NOTICES"] = [{"key": "k", "feature": "typo", "items": []}]
    with pytest.raises(UnknownFeatureError, match="typo"):
        finalize_app(app)


def test_finalize_app_unknown_item_feature() -> None:
    """Test boot validation rejects an unknown item feature."""
    app = Flask("testapp")
    InvenioNotices(app)
    app.config["NOTICES"] = [
        {"key": "k", "items": [{"text": "gated", "feature": "typo"}]},
    ]
    with pytest.raises(UnknownFeatureError, match="typo"):
        finalize_app(app)
