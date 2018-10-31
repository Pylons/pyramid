""" Backwards compatibility shim module (forever). """
from pyramid.asset import *  # noqa b/w compat

resolve_resource_spec = resolve_asset_spec  # noqa
resource_spec_from_abspath = asset_spec_from_abspath  # noqa
abspath_from_resource_spec = abspath_from_asset_spec  # noqa
