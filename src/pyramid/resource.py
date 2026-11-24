"""Backwards compatibility shim module."""

import warnings
from zope.deprecation import Suppressor

warnings.warn(
    (
        '`pyramid.resource` is a backwards compatibility shim for the '
        'functions in `pyramid.asset`.'
    ),
    DeprecationWarning,
    stacklevel=2,
)

with Suppressor():
    from pyramid.asset import (  # noqa: F401
        abspath_from_asset_spec,
        asset_spec_from_abspath,
        resolve_asset_spec,
    )

resolve_resource_spec = resolve_asset_spec
resource_spec_from_abspath = asset_spec_from_abspath
abspath_from_resource_spec = abspath_from_asset_spec
