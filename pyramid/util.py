import pkg_resources
import sys

from pyramid.exceptions import ConfigurationError
from pyramid.path import package_of

class DottedNameResolver(object):
    """ This class resolves dotted name references to 'global' Python
    objects (objects which can be imported) to those objects.

    Two dotted name styles are supported during deserialization:

    - ``pkg_resources``-style dotted names where non-module attributes
      of a package are separated from the rest of the path using a ':'
      e.g. ``package.module:attr``.

    - ``zope.dottedname``-style dotted names where non-module
      attributes of a package are separated from the rest of the path
      using a '.' e.g. ``package.module.attr``.

    These styles can be used interchangeably.  If the serialization
    contains a ``:`` (colon), the ``pkg_resources`` resolution
    mechanism will be chosen, otherwise the ``zope.dottedname``
    resolution mechanism will be chosen.

    The constructor accepts a single argument named ``package`` which
    should be a one of:

    - a Python module or package object

    - A fully qualified (not relative) dotted name to a module or package

    - The value ``None``

    The ``package`` is used when relative dotted names are supplied to
    the resolver's ``resolve`` and ``maybe_resolve`` methods.  A
    dotted name which has a ``.`` (dot) or ``:`` (colon) as its first
    character is treated as relative.

    If the value ``None`` is supplied as the package name, the
    resolver will only be able to resolve fully qualified (not
    relative) names.  Any attempt to resolve a relative name when the
    ``package`` is ``None`` will result in an
    :exc:`pyramid.config.ConfigurationError` exception.

    If a *module* or *module name* (as opposed to a package or package
    name) is supplied as ``package``, its containing package is
    computed and this package used to derive the package name (all
    names are resolved relative to packages, never to modules).  For
    example, if the ``package`` argument to this type was passed the
    string ``xml.dom.expatbuilder``, and ``.mindom`` is supplied to
    the ``resolve`` method, the resulting import would be for
    ``xml.minidom``, because ``xml.dom.expatbuilder`` is a module
    object, not a package object.

    If a *package* or *package name* (as opposed to a module or module
    name) is supplied as ``package``, this package will be used to
    relative compute dotted names.  For example, if the ``package``
    argument to this type was passed the string ``xml.dom``, and
    ``.minidom`` is supplied to the ``resolve`` method, the resulting
    import would be for ``xml.minidom``.

    When a dotted name cannot be resolved, a
    :class:`pyramid.exceptions.ConfigurationError` error is raised.
    """
    def __init__(self, package):
        if package is None:
            self.package_name = None
            self.package = None
        else:
            if isinstance(package, basestring):
                try:
                    __import__(package)
                except ImportError:
                    raise ConfigurationError(
                        'The dotted name %r cannot be imported' % (package,))
                package = sys.modules[package]
            self.package = package_of(package)
            self.package_name = self.package.__name__

    def _pkg_resources_style(self, value):
        """ package.module:attr style """
        if value.startswith('.') or value.startswith(':'):
            if not self.package_name:
                raise ConfigurationError(
                    'relative name %r irresolveable without '
                    'package_name' % (value,))
            if value in ['.', ':']:
                value = self.package_name
            else:
                value = self.package_name + value
        return pkg_resources.EntryPoint.parse(
            'x=%s' % value).load(False)

    def _zope_dottedname_style(self, value):
        """ package.module.attr style """
        module = self.package_name and self.package_name or None
        if value == '.':
            if self.package_name is None:
                raise ConfigurationError(
                    'relative name %r irresolveable without package' % (value,)
                )
            name = module.split('.')
        else:
            name = value.split('.')
            if not name[0]:
                if module is None:
                    raise ConfigurationError(
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
                found = getattr(found, n) # pragma: no cover

        return found

    def resolve(self, dotted):
        if not isinstance(dotted, basestring):
            raise ConfigurationError('%r is not a string' % (dotted,))
        return self.maybe_resolve(dotted)

    def maybe_resolve(self, dotted):
        if isinstance(dotted, basestring):
            if ':' in dotted:
                return self._pkg_resources_style(dotted)
            else:
                return self._zope_dottedname_style(dotted)
        return dotted


