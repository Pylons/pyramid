import pkg_resources
import sys
import weakref

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
        module = self.package_name
        if not module:
            module = None
        if value == '.':
            if module is None:
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

class WeakOrderedSet(object):
    """ Maintain a set of items.

    Each item is stored as a weakref to avoid extending their lifetime.

    The values may be iterated over or the last item added may be
    accessed via the ``last`` property.

    If items are added more than once, the most recent addition will
    be remembered in the order:

        order = WeakOrderedSet()
        order.add('1')
        order.add('2')
        order.add('1')

        list(order) == ['2', '1']
        order.last == '1'
    """

    def __init__(self):
        self._items = {}
        self._order = []

    def add(self, item):
        """ Add an item to the set."""
        oid = id(item)
        if oid in self._items:
            self._order.remove(oid)
            self._order.append(oid)
            return
        ref = weakref.ref(item, lambda x: self.remove(item))
        self._items[oid] = ref
        self._order.append(oid)

    def remove(self, item):
        """ Remove an item from the set."""
        oid = id(item)
        if oid in self._items:
            del self._items[oid]
            self._order.remove(oid)

    def empty(self):
        """ Clear all objects from the set."""
        self._items = {}
        self._order = []

    def __len__(self):
        return len(self._order)

    def __contains__(self, item):
        oid = id(item)
        return oid in self._items

    def __iter__(self):
        return (self._items[oid]() for oid in self._order)

    @property
    def last(self):
        if self._order:
            oid = self._order[-1]
            return self._items[oid]()

def topological_sort(items, partial_order, ignore_missing_partials=True):
    """
    Stolen from http://www.bitinformation.com/art/python_topsort.html
    (modified to sort initial roots in items order, and to ignore missing
    partials).

    Given the example list of items ['item2', 'item3', 'item1',
    'item4'] and a 'partial order' list in the form [(item1, item2),
    (item2, item3)], where the example tuples indicate that 'item1'
    should precede 'item2' and 'item2' should precede 'item3', return
    the sorted list of items ['item1', 'item2', 'item3', 'item4'].
    Note that since 'item4' is not mentioned in the partial ordering
    list, it will be at an arbitrary position in the returned list.
    """
    def add_node(graph, node, roots):
        if not graph.has_key(node):
            roots.append(node)
            graph[node] = [0] # 0 = number of arcs coming into this node

    def add_arc(graph, fromnode, tonode, roots):
        graph[fromnode].append(tonode)
        graph[tonode][0] = graph[tonode][0] + 1
        if tonode in roots:
            roots.remove(tonode)

    graph = {}
    roots = []

    for v in items:
        add_node(graph, v, roots)

    for a, b in partial_order:
        if ignore_missing_partials:
            # don't fail if a value is present in the partial_order
            # list but missing in items.  In this mode, we fake up a
            # value instead of raising a KeyError when trying to use
            # add_arc.  The result will contain the faked item.
            if not graph.has_key(a):
                add_node(graph, a, roots)
            elif not graph.has_key(b):
                add_node(graph, b, roots)
        add_arc(graph, a, b, roots)

    sorted = []

    while roots:
        root = roots.pop(0)
        sorted.append(root)
        for child in graph[root][1:]:
            graph[child][0] = graph[child][0] - 1
            if graph[child][0] == 0:
                roots.insert(0, child)
        del graph[root]

    if graph:
        # loop in input
        cycledeps = {}
        for k, v in graph.items():
            cycledeps[k] = v[1:]
        raise CyclicDependencyError(cycledeps)

    return [ x for x in sorted if x in items ]

class CyclicDependencyError(ConfigurationError):
    def __init__(self, cycles):
        self.cycles = cycles

    def __str__(self):
        L = []
        cycles = self.cycles
        for cycle in cycles:
            dependent = cycle
            dependees = cycles[cycle]
            L.append('%r depends on %r' % (dependent, dependees))
        msg = '; '.join(L)
        return msg
