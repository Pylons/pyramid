"""
Vendored subset of setuptools pkg_resources for Pyramid's asset system.

This module contains the minimal set of pkg_resources functionality needed
by Pyramid for asset resolution, asset overrides, and the provider system.
It eliminates the runtime dependency on setuptools, which removed
pkg_resources entirely in version 82.0.0.

Extracted from setuptools 80.x (pkg_resources/__init__.py).

License (MIT):
    Copyright Jason R. Coombs

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.

Not included (not needed by Pyramid):
    - EntryPoint, Distribution, WorkingSet, Requirement
    - EggProvider intermediate class (flattened into DefaultProvider)
    - Egg/zip extraction (get_cache_path, extraction_error, etc.)
    - Metadata methods (has_metadata, get_metadata, etc.)
    - All extern imports (packaging, platformdirs, etc.)
"""

import importlib.machinery as importlib_machinery
import inspect
import io
import ntpath
import os
import posixpath
import sys
import warnings

# --- Provider factory registry ---

_provider_factories = {}


def register_loader_type(loader_type, provider_factory):
    """Register `provider_factory` to make providers for `loader_type`

    `loader_type` is the type or class of a PEP 302 ``module.__loader__``,
    and `provider_factory` is a function that, passed a *module* object,
    returns an ``IResourceProvider`` for that module.
    """
    _provider_factories[loader_type] = provider_factory


def _always_object(classes):
    """
    Ensure object appears in the mro even
    for old-style classes.
    """
    if object not in classes:
        return classes + (object,)
    return classes


def _find_adapter(registry, ob):
    """Return an adapter factory for `ob` from `registry`"""
    types = _always_object(
        inspect.getmro(getattr(ob, '__class__', type(ob)))
    )
    for t in types:
        if t in registry:
            return registry[t]


def get_provider(moduleOrReq):
    """Return an IResourceProvider for the named module or requirement"""
    try:
        module = sys.modules[moduleOrReq]
    except KeyError:
        __import__(moduleOrReq)
        module = sys.modules[moduleOrReq]
    loader = getattr(module, '__loader__', None)
    return _find_adapter(_provider_factories, loader)(module)


# --- Resource manager ---


class ResourceManager:
    """Manage resource extraction and packages"""

    def __init__(self):
        self.cached_files = {}

    def resource_exists(self, package_or_requirement, resource_name):
        """Does the named resource exist?"""
        return get_provider(package_or_requirement).has_resource(
            resource_name
        )

    def resource_isdir(self, package_or_requirement, resource_name):
        """Is the named resource an existing directory?"""
        return get_provider(package_or_requirement).resource_isdir(
            resource_name
        )

    def resource_filename(self, package_or_requirement, resource_name):
        """Return a true filesystem path for specified resource"""
        return get_provider(package_or_requirement).get_resource_filename(
            self, resource_name
        )

    def resource_stream(self, package_or_requirement, resource_name):
        """Return a readable file-like object for specified resource"""
        return get_provider(package_or_requirement).get_resource_stream(
            self, resource_name
        )

    def resource_string(self, package_or_requirement, resource_name):
        """Return specified resource as a string"""
        return get_provider(package_or_requirement).get_resource_string(
            self, resource_name
        )

    def resource_listdir(self, package_or_requirement, resource_name):
        """List the contents of the named resource directory"""
        return get_provider(package_or_requirement).resource_listdir(
            resource_name
        )


_manager = ResourceManager()


# --- Module-level convenience functions ---


def resource_exists(package_or_requirement, resource_name):
    return _manager.resource_exists(package_or_requirement, resource_name)


def resource_isdir(package_or_requirement, resource_name):
    return _manager.resource_isdir(package_or_requirement, resource_name)


def resource_filename(package_or_requirement, resource_name):
    return _manager.resource_filename(package_or_requirement, resource_name)


def resource_stream(package_or_requirement, resource_name):
    return _manager.resource_stream(package_or_requirement, resource_name)


def resource_string(package_or_requirement, resource_name):
    return _manager.resource_string(package_or_requirement, resource_name)


def resource_listdir(package_or_requirement, resource_name):
    return _manager.resource_listdir(package_or_requirement, resource_name)


# --- Providers ---


def _issue_warning(*args, **kw):
    level = 1
    g = globals()
    try:
        while sys._getframe(level).f_globals is g:
            level += 1
    except ValueError:
        pass
    warnings.warn(stacklevel=level + 1, *args, **kw)


class NullProvider:
    """Try to implement resources and metadata for arbitrary PEP 302
    loaders"""

    egg_name = None
    egg_info = None
    loader = None

    def __init__(self, module):
        self.loader = getattr(module, '__loader__', None)
        self.module_path = os.path.dirname(
            getattr(module, '__file__', '') or ''
        )

    def get_resource_filename(self, manager, resource_name):
        return self._fn(self.module_path, resource_name)

    def get_resource_stream(self, manager, resource_name):
        return io.BytesIO(
            self.get_resource_string(manager, resource_name)
        )

    def get_resource_string(self, manager, resource_name):
        return self._get(self._fn(self.module_path, resource_name))

    def has_resource(self, resource_name):
        return self._has(self._fn(self.module_path, resource_name))

    def resource_isdir(self, resource_name):
        return self._isdir(self._fn(self.module_path, resource_name))

    def resource_listdir(self, resource_name):
        return self._listdir(self._fn(self.module_path, resource_name))

    def _fn(self, base, resource_name):
        self._validate_resource_path(resource_name)
        if resource_name:
            return os.path.join(base, *resource_name.split('/'))
        return base

    @staticmethod
    def _validate_resource_path(path):
        """
        Validate the resource paths according to the docs.
        https://setuptools.pypa.io/en/latest/pkg_resources.html#basic-resource-access
        """
        invalid = (
            os.path.pardir in path.split(posixpath.sep)
            or posixpath.isabs(path)
            or ntpath.isabs(path)
        )
        if not invalid:
            return

        msg = (
            "Use of .. or absolute path in a resource path is not allowed."
        )

        # Aggressively disallow Windows absolute paths
        if ntpath.isabs(path) and not posixpath.isabs(path):
            raise ValueError(msg)

        # for compatibility, warn; in future
        # raise ValueError(msg)
        _issue_warning(
            msg[:-1] + " and will raise exceptions in a future release.",
            DeprecationWarning,
        )

    def _has(self, path):
        raise NotImplementedError(
            "Can't perform this operation for unregistered loader type"
        )

    def _isdir(self, path):
        raise NotImplementedError(
            "Can't perform this operation for unregistered loader type"
        )

    def _listdir(self, path):
        raise NotImplementedError(
            "Can't perform this operation for unregistered loader type"
        )

    def _get(self, path):
        if hasattr(self.loader, 'get_data'):
            return self.loader.get_data(path)
        raise NotImplementedError(
            "Can't perform this operation for loaders without 'get_data()'"
        )


class DefaultProvider(NullProvider):
    """Provides access to package resources in the filesystem"""

    def _has(self, path):
        return os.path.exists(path)

    def _isdir(self, path):
        return os.path.isdir(path)

    def _listdir(self, path):
        return os.listdir(path)

    def get_resource_stream(self, manager, resource_name):
        return open(self._fn(self.module_path, resource_name), 'rb')

    def _get(self, path):
        with open(path, 'rb') as stream:
            return stream.read()

    @classmethod
    def _register(cls):
        loader_names = (
            'SourceFileLoader',
            'SourcelessFileLoader',
        )
        for name in loader_names:
            loader_cls = getattr(importlib_machinery, name, type(None))
            register_loader_type(loader_cls, cls)


# --- Auto-registration ---

register_loader_type(object, NullProvider)
DefaultProvider._register()
