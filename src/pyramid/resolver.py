import functools
from importlib import import_module
import os
import sys

from pyramid.interfaces import IPackageOverrides

from .path import (
    CALLER_PACKAGE,
    FSAssetDescriptor,
    PkgResourcesAssetDescriptor,
    caller_package,
    package_of,
)
from .threadlocal import get_current_registry


class Resolver:
    def __init__(self, package=CALLER_PACKAGE):
        if package in (None, CALLER_PACKAGE):
            self.package = package
        else:
            if isinstance(package, str):
                try:
                    __import__(package)
                except ImportError:
                    raise ValueError(
                        f'The dotted name {package!r} cannot be imported'
                    )
                package = sys.modules[package]
            self.package = package_of(package)

    def get_package_name(self):
        if self.package is CALLER_PACKAGE:
            package_name = caller_package().__name__
        else:
            package_name = self.package.__name__
        return package_name

    def get_package(self):
        if self.package is CALLER_PACKAGE:
            package = caller_package()
        else:
            package = self.package
        return package


class AssetResolver(Resolver):
    """A class used to resolve an :term:`asset specification` to an
    :term:`asset descriptor`.

    .. versionadded:: 1.3

    The constructor accepts a single argument named ``package`` which may be
    any of:

    - A fully qualified (not relative) dotted name to a module or package

    - a Python module or package object

    - The value ``None``

    - The constant value :attr:`pyramid.path.CALLER_PACKAGE`.

    The default value is :attr:`pyramid.path.CALLER_PACKAGE`.

    The ``package`` is used when a relative asset specification is supplied
    to the :meth:`~pyramid.path.AssetResolver.resolve` method.  An asset
    specification without a colon in it is treated as relative.

    If ``package`` is ``None``, the resolver will
    only be able to resolve fully qualified (not relative) asset
    specifications.  Any attempt to resolve a relative asset specification
    will result in an :exc:`ValueError` exception.

    If ``package`` is :attr:`pyramid.path.CALLER_PACKAGE`,
    the resolver will treat relative asset specifications as
    relative to the caller of the :meth:`~pyramid.path.AssetResolver.resolve`
    method.

    If ``package`` is a *module* or *module name* (as opposed to a package or
    package name), its containing package is computed and this
    package is used to derive the package name (all names are resolved relative
    to packages, never to modules).  For example, if the ``package`` argument
    to this type was passed the string ``xml.dom.expatbuilder``, and
    ``template.pt`` is supplied to the
    :meth:`~pyramid.path.AssetResolver.resolve` method, the resulting absolute
    asset spec would be ``xml.minidom:template.pt``, because
    ``xml.dom.expatbuilder`` is a module object, not a package object.

    If ``package`` is a *package* or *package name* (as opposed to a module or
    module name), this package will be used to compute relative
    asset specifications.  For example, if the ``package`` argument to this
    type was passed the string ``xml.dom``, and ``template.pt`` is supplied
    to the :meth:`~pyramid.path.AssetResolver.resolve` method, the resulting
    absolute asset spec would be ``xml.minidom:template.pt``.
    """

    def __init__(self, package=CALLER_PACKAGE, registry=None):
        self.registry = registry
        super().__init__(package=package)

    def resolve(self, spec):
        """
        Resolve the asset spec named as ``spec`` to an object that has the
        attributes and methods described in
        :class:`pyramid.interfaces.IAssetDescriptor`.

        If ``spec`` is an absolute filename
        (e.g. ``/path/to/myproject/templates/foo.pt``) or an absolute asset
        spec (e.g. ``myproject:templates.foo.pt``), an asset descriptor is
        returned without taking into account the ``package`` passed to this
        class' constructor.

        If ``spec`` is a *relative* asset specification (an asset
        specification without a ``:`` in it, e.g. ``templates/foo.pt``), the
        ``package`` argument of the constructor is used as the package
        portion of the asset spec.  For example:

        .. code-block:: python

           a = AssetResolver('myproject')
           resolver = a.resolve('templates/foo.pt')
           print(resolver.abspath())
           # -> /path/to/myproject/templates/foo.pt

        If the AssetResolver is constructed without a ``package`` argument of
        ``None``, and a relative asset specification is passed to
        ``resolve``, an :exc:`ValueError` exception is raised.
        """
        if os.path.isabs(spec):
            return FSAssetDescriptor(spec)
        path = spec
        if ':' in path:
            package_name, path = spec.split(':', 1)
        else:
            if self.package is CALLER_PACKAGE:
                package_name = caller_package().__name__
            else:
                package_name = getattr(self.package, '__name__', None)
            if package_name is None:
                raise ValueError(
                    f'relative spec {spec!r} irresolveable without package'
                )

        registry = self.registry or get_current_registry()
        overrides = registry.queryUtility(IPackageOverrides, package_name)
        return PkgResourcesAssetDescriptor(package_name, path, overrides)


class DottedNameResolver(Resolver):
    """A class used to resolve a :term:`dotted Python name` to a package or
    module object.

    .. versionadded:: 1.3

    The constructor accepts a single argument named ``package`` which may be
    any of:

    - A fully qualified (not relative) dotted name to a module or package

    - a Python module or package object

    - The value ``None``

    - The constant value :attr:`pyramid.path.CALLER_PACKAGE`.

    The default value is :attr:`pyramid.path.CALLER_PACKAGE`.

    The ``package`` is used when a relative dotted name is supplied to the
    :meth:`~pyramid.path.DottedNameResolver.resolve` method.  A dotted name
    which has a ``.`` (dot) or ``:`` (colon) as its first character is
    treated as relative.

    If ``package`` is ``None``, the resolver will only be able to resolve
    fully qualified (not relative) names.  Any attempt to resolve a
    relative name will result in an :exc:`ValueError` exception.

    If ``package`` is :attr:`pyramid.path.CALLER_PACKAGE`,
    the resolver will treat relative dotted names as relative to
    the caller of the :meth:`~pyramid.path.DottedNameResolver.resolve`
    method.

    If ``package`` is a *module* or *module name* (as opposed to a package or
    package name), its containing package is computed and this
    package used to derive the package name (all names are resolved relative
    to packages, never to modules).  For example, if the ``package`` argument
    to this type was passed the string ``xml.dom.expatbuilder``, and
    ``.mindom`` is supplied to the
    :meth:`~pyramid.path.DottedNameResolver.resolve` method, the resulting
    import would be for ``xml.minidom``, because ``xml.dom.expatbuilder`` is
    a module object, not a package object.

    If ``package`` is a *package* or *package name* (as opposed to a module or
    module name), this package will be used to relative compute
    dotted names.  For example, if the ``package`` argument to this type was
    passed the string ``xml.dom``, and ``.minidom`` is supplied to the
    :meth:`~pyramid.path.DottedNameResolver.resolve` method, the resulting
    import would be for ``xml.minidom``.
    """

    def resolve(self, dotted):
        """
        This method resolves a dotted name reference to a global Python
        object (an object which can be imported) to the object itself.

        Two dotted name styles are supported:

        - ``pkg_resources``-style dotted names where non-module attributes
          of a package are separated from the rest of the path using a ``:``
          e.g. ``package.module:attr``.

        - ``zope.dottedname``-style dotted names where non-module
          attributes of a package are separated from the rest of the path
          using a ``.`` e.g. ``package.module.attr``.

        These styles can be used interchangeably.  If the supplied name
        contains a ``:`` (colon), the ``pkg_resources`` resolution
        mechanism will be chosen, otherwise the ``zope.dottedname``
        resolution mechanism will be chosen.

        If the ``dotted`` argument passed to this method is not a string, a
        :exc:`ValueError` will be raised.

        When a dotted name cannot be resolved, a :exc:`ValueError` error is
        raised.

        Example:

        .. code-block:: python

           r = DottedNameResolver()
           v = r.resolve('xml') # v is the xml module

        """
        if not isinstance(dotted, str):
            raise ValueError(f'{dotted!r} is not a string')
        package = self.package
        if package is CALLER_PACKAGE:
            package = caller_package()
        return self._resolve(dotted, package)

    def maybe_resolve(self, dotted):
        """
        This method behaves just like
        :meth:`~pyramid.path.DottedNameResolver.resolve`, except if the
        ``dotted`` value passed is not a string, it is simply returned.  For
        example:

        .. code-block:: python

           import xml
           r = DottedNameResolver()
           v = r.maybe_resolve(xml)
           # v is the xml module; no exception raised
        """
        if isinstance(dotted, str):
            package = self.package
            if package is CALLER_PACKAGE:
                package = caller_package()
            return self._resolve(dotted, package)
        return dotted

    def _resolve(self, dotted, package):
        if ':' in dotted:
            return self._pkg_resources_style(dotted, package)
        else:
            return self._zope_dottedname_style(dotted, package)

    def _pkg_resources_style(self, value, package):
        """package.module:attr style"""
        if value.startswith(('.', ':')):
            if not package:
                raise ValueError(
                    f'relative name {value!r} irresolveable without package'
                )
            if value in ['.', ':']:
                value = package.__name__
            else:
                value = package.__name__ + value
        # logic below is similar to importlib.metadata.EntryPoint.load()
        module = value
        attrs = []
        parts = value.split(':', 1)
        if len(parts) == 2:
            module, attrs = parts
            attrs = attrs.split('.')
        module = import_module(module)
        try:
            return functools.reduce(getattr, attrs, module)
        except AttributeError as ex:
            raise ImportError(str(ex))

    def _zope_dottedname_style(self, value, package):
        """package.module.attr style"""
        module = getattr(package, '__name__', None)  # package may be None
        if not module:
            module = None
        if value == '.':
            if module is None:
                raise ValueError(
                    f'relative name {value!r} irresolveable without package'
                )
            name = module.split('.')
        else:
            name = value.split('.')
            if not name[0]:
                if module is None:
                    raise ValueError(
                        'relative name %r irresolveable without '
                        'package' % (value,)
                    )
                module = module.split('.')
                name.pop(0)
                while not name[0]:
                    module.pop()
                    name.pop(0)
                name = module + name

        used = name.pop(0)
        found = __import__(used)
        for n in name:
            used += '.' + n
            try:
                found = getattr(found, n)
            except AttributeError:
                __import__(used)
                found = getattr(found, n)  # pragma: no cover

        return found
