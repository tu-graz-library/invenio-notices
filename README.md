<!--
SPDX-FileCopyrightText: 2026 Graz University of Technology.
SPDX-License-Identifier: MIT
-->

# invenio-notices

[![License](https://img.shields.io/github/license/tu-graz-library/invenio-notices.svg)](https://github.com/tu-graz-library/invenio-notices/blob/master/LICENSE)

Invenio module to show notices to users.

A notice is shown to visitors until they acknowledge it, once per user
or once per browser for guests.

Features:

- notices are plain configuration
- targeting by audience (users or guests) and by role
- optional feature check and time window to control when a notice shows
- acknowledgment stored per user, per browser for guests

## Installation

```console
$ uv add invenio-notices
```

## Development

```console
$ uv sync --extra tests
$ uv run ./run-tests.sh
```
