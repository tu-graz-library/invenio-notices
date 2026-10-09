# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""JS/CSS Webpack bundles for invenio-notices."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "invenio-notices": "./js/invenio_notices/notices.js",
            },
            "dependencies": {
                "react": "^16.13.0",
                "react-dom": "^16.13.0",
            },
        },
    },
)
