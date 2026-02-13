"""
Public resource API for the Pylons ecosystem.

This module provides override-aware resource access functions that work
without setuptools. It is the migration target for all Pylons packages
that previously imported from ``pkg_resources``.

These functions respect Pyramid's asset override system
(:meth:`pyramid.config.Configurator.override_asset`). Using
``importlib.resources`` directly would bypass overrides.

Usage::

    from pyramid.compat_resources import resource_filename
    path = resource_filename('mypackage', 'templates/foo.pt')

.. versionadded:: 2.1
"""

from pyramid._pkg_resources import (
    DefaultProvider,
    NullProvider,
    ResourceManager,
    get_provider,
    register_loader_type,
    resource_exists,
    resource_filename,
    resource_isdir,
    resource_listdir,
    resource_stream,
    resource_string,
)

__all__ = [
    'resource_exists',
    'resource_filename',
    'resource_isdir',
    'resource_listdir',
    'resource_stream',
    'resource_string',
    'get_provider',
    'register_loader_type',
    'DefaultProvider',
    'NullProvider',
    'ResourceManager',
]
