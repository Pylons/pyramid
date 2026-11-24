import os
from zope.deprecation import deprecated

from pyramid.path import AssetResolver


def resolve_asset_spec(spec, pname='__main__'):
    """
    Return a two-tuple of package name and path for an asset specification.  If
    the specification is a file path, the package name will be ``None``.

    .. deprecated:: 2.2

        ``resolve_asset_spec`` has been deprecated.  Use the new
        :ref:`asset APIs <accessing_assets>` instead, which accept asset
        specifications directly and can make parsing specification strings
        unnecessary in many cases.
    """
    if pname and not isinstance(pname, str):
        pname = pname.__name__  # as package
    if os.path.isabs(spec):
        return None, spec
    filename = spec
    if ':' in spec:
        pname, filename = spec.split(':', 1)
    elif pname is None:
        pname, filename = None, spec
    return pname, filename


deprecated(
    'resolve_asset_spec',
    (
        '`resolve_asset_spec` has been deprecated.  Use the new asset APIs '
        'instead, which accept asset specifications directly and can make '
        'parsing specification strings unnecessary in many cases.'
    ),
)


def asset_spec_from_abspath(abspath, package):
    """
    Try to convert an absolute path to a resource in a package to
    a resource specification if possible; otherwise return the
    absolute path.

    .. deprecated:: 2.2

        ``asset_spec_from_abspath`` has been deprecated with no replacement.
        Accessing package contents via file paths is discouraged, as the
        package may not exist in the filesystem and need to be unpacked to
        a temporary directory.  Consider whether the new :ref:`asset APIs
        <accessing_assets>` can meet your needs.
    """
    if getattr(package, '__name__', None) == '__main__':
        return abspath
    resolver = AssetResolver(package)
    pp = resolver.resolve('').abspath() + os.path.sep
    if abspath.startswith(pp):
        relpath = abspath[len(pp) :]
        return resolver.resolve(relpath).absspec()
    return abspath


deprecated(
    'asset_spec_from_abspath',
    (
        '`asset_spec_from_abspath` has been deprecated with no replacement.  '
        'Accessing package contents via file paths is discouraged, as the '
        'package may not exist in the filesystem and need to be unpacked to '
        'a temporary directory.  Consider whether the new asset APIs can '
        'meet your needs.'
    ),
)


def abspath_from_asset_spec(spec, pname='__main__'):
    """
    Return a filesystem path for an asset specification.

    .. deprecated:: 2.2

        ``abspath_from_asset_spec`` has been deprecated; instead use
        :meth:`pyramid.interfaces.IAssetDescriptor.abspath` via the new
        :ref:`asset APIs <accessing_assets>`, e.g.,
        ``request.resolve_asset(spec).abspath()``.
    """
    if pname is None:
        return spec
    return AssetResolver(pname).resolve(spec).abspath()


deprecated(
    'abspath_from_asset_spec',
    (
        '`abspath_from_asset_spec` has been deprecated; instead use '
        '`IAssetDescriptor.abspath()` via the new asset APIs, e.g., '
        '`request.resolve_asset(spec).abspath()`.'
    ),
)
