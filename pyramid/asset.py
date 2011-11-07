import os
import pkg_resources
from zope.interface import implements

from pyramid.compat import string_types
from pyramid.interfaces import IAssetResolver
from pyramid.interfaces import IAssetDescriptor
from pyramid.path import package_path
from pyramid.path import package_name


def resolve_asset_spec(spec, pname='__main__'):
    if pname and not isinstance(pname, string_types):
        pname = pname.__name__ # as package
    if os.path.isabs(spec):
        return None, spec
    filename = spec
    if ':' in spec:
        pname, filename = spec.split(':', 1)
    elif pname is None:
        pname, filename = None, spec
    return pname, filename


def asset_spec_from_abspath(abspath, package):
    """ Try to convert an absolute path to a resource in a package to
    a resource specification if possible; otherwise return the
    absolute path.  """
    if getattr(package, '__name__', None) == '__main__':
        return abspath
    pp = package_path(package) + os.path.sep
    if abspath.startswith(pp):
        relpath = abspath[len(pp):]
        return '%s:%s' % (package_name(package),
                          relpath.replace(os.path.sep, '/'))
    return abspath


def abspath_from_asset_spec(spec, pname='__main__'):
    if pname is None:
        return spec
    pname, filename = resolve_asset_spec(spec, pname)
    if pname is None:
        return filename
    return pkg_resources.resource_filename(pname, filename)


def lookup_asset(registry, path_or_spec, pkg_name='__main__', request=None):
    """
    XXX.
    """
    resolver = registry.queryUtility(IAssetResolver,
                                     default=default_asset_resolver)
    pkg_name, path = resolve_asset_spec(path_or_spec, pkg_name)
    return resolver(pkg_name, path, request)


def default_asset_resolver(pkg_name, path, request):
    if pkg_name:
        return PkgResourcesAssetDescriptor(pkg_name, path)
    return FSAssetDescriptor(path)


class PkgResourcesAssetDescriptor(object):
    implements(IAssetDescriptor)

    def __init__(self, pkg_name, path):
        self.pkg_name = pkg_name
        self.path = path

    def abspath(self):
        pkg_resources.resource_filename(self.pkg_name, self.path)

    def stream(self):
        pkg_resources.resource_stream(self.pkg_name, self.path)

    def isdir(self):
        pkg_resources.resource_isdir(self.pkg_name, self.path)

    def listdir(self):
        pkg_resources.resource_listdir(self.pkg_name, self.path)

    def exists(self):
        pkg_resources.resource_exists(self.pkg_name, self.path)


class FSAssetDescriptor(object):
    implements(IAssetDescriptor)

    def __init__(self, path):
        self.path = os.path.abspath(path)

    def abspath(self):
        return self.path

    def stream(self):
        return open(self.path, 'rb')

    def isdir(self):
        return os.path.isdir(self.path)

    def listdir(self):
        return os.listdir(self.path)

    def exists(self):
        return os.path.exists(self.path)
