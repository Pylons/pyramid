from importlib.machinery import SOURCE_SUFFIXES
import os
import pkg_resources
import sys
from zope.interface import implementer

from pyramid.interfaces import IAssetDescriptor

init_names = ['__init__%s' % x for x in SOURCE_SUFFIXES]


def caller_path(path, level=2):
    if not os.path.isabs(path):
        module = caller_module(level + 1)
        prefix = package_path(module)
        path = os.path.join(prefix, path)
    return path


def caller_module(level=2, sys=sys):
    module_globals = sys._getframe(level).f_globals
    module_name = module_globals.get('__name__') or '__main__'
    module = sys.modules[module_name]
    return module


def package_name(pkg_or_module):
    """If this function is passed a module, return the dotted Python
    package name of the package in which the module lives.  If this
    function is passed a package, return the dotted Python package
    name of the package itself."""
    if pkg_or_module is None or pkg_or_module.__name__ == '__main__':
        return '__main__'
    pkg_name = pkg_or_module.__name__
    pkg_filename = getattr(pkg_or_module, '__file__', None)
    if pkg_filename is None:
        # Namespace packages do not have __init__.py* files,
        # and so have no __file__ attribute
        return pkg_name
    splitted = os.path.split(pkg_filename)
    if splitted[-1] in init_names:
        # it's a package
        return pkg_name
    return pkg_name.rsplit('.', 1)[0]


def package_of(pkg_or_module):
    """Return the package of a module or return the package itself"""
    pkg_name = package_name(pkg_or_module)
    __import__(pkg_name)
    return sys.modules[pkg_name]


def caller_package(level=2, caller_module=caller_module):
    # caller_module in arglist for tests
    module = caller_module(level + 1)
    f = getattr(module, '__file__', '')
    if ('__init__.py' in f) or ('__init__$py' in f):  # empty at >>>
        # Module is a package
        return module
    # Go up one level to get package
    package_name = module.__name__.rsplit('.', 1)[0]
    return sys.modules[package_name]


def package_path(package):
    # computing the abspath is actually kinda expensive so we memoize
    # the result
    prefix = getattr(package, '__abspath__', None)
    if prefix is None:
        prefix = pkg_resources.resource_filename(package.__name__, '')
        # pkg_resources doesn't care whether we feed it a package
        # name or a module name within the package, the result
        # will be the same: a directory name to the package itself
        try:
            package.__abspath__ = prefix
        except Exception:
            # this is only an optimization, ignore any error
            pass
    return prefix


class _CALLER_PACKAGE:
    def __repr__(self):  # pragma: no cover (for docs)
        return 'pyramid.path.CALLER_PACKAGE'


CALLER_PACKAGE = _CALLER_PACKAGE()


@implementer(IAssetDescriptor)
class PkgResourcesAssetDescriptor:
    pkg_resources = pkg_resources

    def __init__(self, pkg_name, path, overrides=None):
        self.pkg_name = pkg_name
        self.path = path
        self.overrides = overrides

    def absspec(self):
        return f'{self.pkg_name}:{self.path}'

    def abspath(self):
        if self.overrides is not None:
            filename = self.overrides.get_filename(self.path)
        else:
            filename = None
        if filename is None:
            filename = self.pkg_resources.resource_filename(
                self.pkg_name,
                self.path,
            )
        return os.path.abspath(filename)

    def stream(self):
        if self.overrides is not None:
            stream = self.overrides.get_stream(self.path)
            if stream is not None:
                return stream
        return self.pkg_resources.resource_stream(self.pkg_name, self.path)

    def isdir(self):
        if self.overrides is not None:
            result = self.overrides.isdir(self.path)
            if result is not None:
                return result
        return self.pkg_resources.resource_isdir(self.pkg_name, self.path)

    def listdir(self):
        if self.overrides is not None:
            result = self.overrides.listdir(self.path)
            if result is not None:
                return result
        return self.pkg_resources.resource_listdir(self.pkg_name, self.path)

    def exists(self):
        if self.overrides is not None:
            result = self.overrides.exists(self.path)
            if result is not None:
                return result
        return self.pkg_resources.resource_exists(self.pkg_name, self.path)


@implementer(IAssetDescriptor)
class FSAssetDescriptor:
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def absspec(self):
        raise NotImplementedError

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
