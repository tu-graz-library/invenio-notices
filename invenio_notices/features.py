# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Ready-made feature checks for ``NOTICES_FEATURES``.

A feature check is a no-argument callable returning ``bool``, the notice
shows only while it returns ``True``.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def config_flag(key: str) -> Callable[[], bool]:
    """Feature is on when the config variable is truthy, flip it at go-live."""
    raise NotImplementedError


def endpoint_exists(endpoint: str) -> Callable[[], bool]:
    """Feature is on when the route is registered, presence detection."""
    raise NotImplementedError


def extension_loaded(name: str) -> Callable[[], bool]:
    """Feature is on when the Flask extension is loaded."""
    raise NotImplementedError
