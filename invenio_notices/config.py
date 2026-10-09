# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Configuration for invenio-notices.

``starts_at``/``ends_at`` are ISO-8601 strings and are compared in UTC.
"""

from invenio_i18n import lazy_gettext as _

NOTICES = []
"""Notice definitions, shown until acknowledged.

Each notice is a dict:

.. code-block:: python

    {
        "key": "onboarding-2026",  # changed content needs a new key
        "show_to": "users",  # "users" | "guests" | "all"
        "roles": ["trusted-user"],  # optional, only these roles see it
        "accent": True,  # optional, highlighted card
        "title": _("..."),
        "intro": _("..."),
        "items": [
            _("plain item, everyone sees it"),
            {"text": _("role based item"), "roles": ["trusted-user"]},
            {"text": _("feature gated item"), "feature": "oer_v2"},
        ],
        "outro": _("..."),
        "feature": "oer_v2",  # optional, show only when this feature is on
        "starts_at": "2026-11-01T08:00:00+01:00",  # optional
        "ends_at": "2026-12-01T00:00:00+01:00",  # optional
    }
"""

NOTICES_ACK_LABEL = _("Acknowledged")
"""Label for the notice acknowledge button."""

NOTICES_FEATURES = {}
"""Feature checks by name, e.g. ``{"oer_v2": config_flag("OER_V2")}``.

A check is a no-argument callable returning ``bool``, see
``invenio_notices.features`` for ready-made ones. Unknown feature names
fail closed: the notice stays hidden.
"""

NOTICES_TEMPLATE = "invenio_notices/notices.html"
"""Template that renders the pending notices, included by the theme."""
