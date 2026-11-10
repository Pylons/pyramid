import atexit
from contextlib import ExitStack
import functools
from importlib.machinery import SOURCE_SUFFIXES
import importlib.resources
import os
import sys
from zope.interface import implementer

from pyramid.interfaces import IAssetDescriptor

init_names = ['__init__%s' % x for x in SOURCE_SUFFIXES]


@functools.lru_cache(maxsize=None)
def ref_filename(ref):
    """Return a filename on the filesystem for the given resource.

    If the resource does not exist in the filesystem (e.g. in a zipped egg), it
    will be extracted to a temporary directory and cleaned up when the
    application exits.

    Accessing resources via filesystem is discouraged, instead consider
    directly accessing contents via the ``importlib.resources`` APIs.

    :param ref:  A reference pointing to the desired resource.
    :type ref: importlib.resources.abc.Traversable
    :return:  The filename on the filesystem.
    :rtype:  str

    """
    manager = ExitStack()
    atexit.register(manager.close)
    path = manager.enter_context(importlib.resources.as_file(ref))
    return str(path)


def resource_filename(package, name):
    """Return a filename on the filesystem for the given resource.

    If the resource does not exist in the filesystem (e.g. in a zipped egg), it
    will be extracted to a temporary directory and cleaned up when the
    application exits.

    This function is equivalent to the now-deprecated
    ``pkg_resources.resource_filename``.

    This function is only included in order to provide legacy functionality;
    use should be avoided.  Instead prefer to use ``importlib.resources`` APIs
    directly.

    :param package:  The package containing the resource.
    :type package: str
    :param name:  The name of the resource within the package.
    :type name: str
    :return:  The filename on the filesystem.
    :rtype:  str

    """
    ref = importlib.resources.files(package) / name
    return ref_filename(ref)


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
        prefix = resource_filename(package_name(package), '')
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
    def __init__(self, pkg_name, path, overrides=None):
        self.pkg_name = pkg_name
        self.path = path
        self.overrides = overrides

    def _ref(self):
        base = importlib.resources.files(self.pkg_name)
        if self.path:
            return base / self.path
        return base

    def absspec(self):
        return f'{self.pkg_name}:{self.path}'

    def abspath(self):
        if self.overrides is not None:
            filename = self.overrides.get_filename(self.path)
            if filename is not None:
                return os.path.abspath(filename)
        return os.path.abspath(ref_filename(self._ref()))

    def stream(self):
        if self.overrides is not None:
            stream = self.overrides.get_stream(self.path)
            if stream is not None:
                return stream
        return self._ref().open('rb')

    def isdir(self):
        if self.overrides is not None:
            result = self.overrides.isdir(self.path)
            if result is not None:
                return result
        return self._ref().is_dir()

    def listdir(self):
        if self.overrides is not None:
            result = self.overrides.listdir(self.path)
            if result is not None:
                return result
        return [x.name for x in self._ref().iterdir()]

    def exists(self):
        if self.overrides is not None:
            result = self.overrides.has_resource(self.path)
            if result is not None:
                return result
        ref = self._ref()
        return ref.is_file() or ref.is_dir()


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


def __getattr__(name):
    """Lazy re-exports for backwards compatibility."""
    if name == 'AssetResolver':
        from pyramid.resolver import AssetResolver

        return AssetResolver
    if name == 'DottedNameResolver':
        from pyramid.resolver import DottedNameResolver

        return DottedNameResolver
    if name == 'Resolver':
        from pyramid.resolver import Resolver

        return Resolver
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
