# The implementation of this module exists over at `_path.py`.  This is because
# the `pyramid.resolver` APIs are exported by this module as well for backwards
# compatibility, and `_path.py` prevents a circular dependency.  See
# https://github.com/Pylons/pyramid/issues/3731 for more details.
from pyramid._path import (
    CALLER_PACKAGE,
    caller_module,
    caller_package,
    caller_path,
    package_name,
    package_of,
    package_path,
)
from pyramid.resolver import (
    AssetResolver,
    DottedNameResolver,
    FSAssetDescriptor,
    PkgResourcesAssetDescriptor,
    Resolver,
)

__all__ = [
    'AssetResolver',
    'caller_module',
    'caller_package',
    'CALLER_PACKAGE',
    'caller_path',
    'DottedNameResolver',
    'FSAssetDescriptor',
    'package_name',
    'package_of',
    'package_path',
    'PkgResourcesAssetDescriptor',
    'Resolver',
]
