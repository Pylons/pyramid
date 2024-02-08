import os

from pyramid.path import AssetResolver, package_name, package_path


def resolve_asset_spec(spec, pname='__main__'):
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


def asset_spec_from_abspath(abspath, package):
    """Try to convert an absolute path to a resource in a package to
    a resource specification if possible; otherwise return the
    absolute path."""
    if getattr(package, '__name__', None) == '__main__':
        return abspath
    pp = package_path(package) + os.path.sep
    if abspath.startswith(pp):
        relpath = abspath[len(pp) :]
        return '{}:{}'.format(
            package_name(package),
            relpath.replace(os.path.sep, '/'),
        )
    return abspath


# bw compat only; use pyramid.path.AssetResolver().resolve(spec).abspath()
def abspath_from_asset_spec(spec, pname='__main__'):
    if pname is None:
        return spec
    return AssetResolver(pname).resolve(spec).abspath()
