import sys
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IExceptionViewClassifier
from pyramid.interfaces import IView
from pyramid.interfaces import ITweens

from zope.interface import providedBy
from zope.interface import implements

def excview_tween_factory(handler, registry):
    """ A :term:`tween` factory which produces a tween that catches an
    exception raised by downstream tweens (or the main Pyramid request
    handler) and, if possible, converts it into a Response using an
    :term:`exception view`."""
    adapters = registry.adapters

    def excview_tween(request):
        attrs = request.__dict__
        try:
            response = handler(request)
        except Exception, exc:
            # WARNING: do not assign the result of sys.exc_info() to a
            # local var here, doing so will cause a leak
            attrs['exc_info'] = sys.exc_info()
            attrs['exception'] = exc
            # clear old generated request.response, if any; it may
            # have been mutated by the view, and its state is not
            # sane (e.g. caching headers)
            if 'response' in attrs:
                del attrs['response']
            request_iface = attrs['request_iface']
            provides = providedBy(exc)
            for_ = (IExceptionViewClassifier, request_iface.combined, provides)
            view_callable = adapters.lookup(for_, IView, default=None)
            if view_callable is None:
                raise
            response = view_callable(exc, request)
        finally:
            # prevent leakage
            attrs['exc_info'] = None

        return response

    return excview_tween

class CyclicDependencyError(Exception):
    def __init__(self, cycles):
        self.cycles = cycles

    def __str__(self):
        L = []
        cycles = self.cycles
        for cycle in cycles:
            dependent = cycle
            dependees = cycles[cycle]
            L.append('%r sorts over %r' % (dependent, dependees))
        msg = '; '.join(L)
        return msg

class Tweens(object):
    implements(ITweens)
    def __init__(self):
        self.explicit = []
        self.names = []
        self.factories = {}
        self.order = []
        self.ingress_alias_names = []
        self.alias_to_name = {INGRESS:INGRESS, MAIN:MAIN}
        self.name_to_alias = {INGRESS:INGRESS, MAIN:MAIN}

    def add_explicit(self, name, factory):
        self.explicit.append((name, factory))

    def add_implicit(self, name, factory, alias=None, under=None, over=None):
        if alias is not None:
            self.alias_to_name[alias] = name
            self.name_to_alias[name] = alias
        else:
            alias = name
        self.names.append(name)
        self.factories[name] = factory
        if under is None and over is None:
            over = INGRESS
            self.ingress_alias_names.append(alias)
        if under is not None:
            self.order.append((under, alias))
        if over is not None:
            self.order.append((alias, over))

    def implicit(self):
        order = []
        roots = []
        graph = {}
        has_order = {}
        aliases = [MAIN, INGRESS]
        ingress_alias_names = self.ingress_alias_names[:]

        for name in self.names:
            aliases.append(self.name_to_alias.get(name, name))

        for a, b in self.order:
            # try to convert both a and b to an alias
            a = self.name_to_alias.get(a, a)
            b = self.name_to_alias.get(b, b)
            order.append((a, b))

        def add_node(graph, node):
            if not graph.has_key(node):
                roots.append(node)
                graph[node] = [0] # 0 = number of arcs coming into this node

        def add_arc(graph, fromnode, tonode):
            graph[fromnode].append(tonode)
            graph[tonode][0] += 1
            if tonode in roots:
                roots.remove(tonode)

        # remove ordering information that mentions unknown names/aliases
        for pos, (first, second) in enumerate(order):
            has_first = first in aliases
            has_second = second in aliases
            if (not has_first) or (not has_second):
                order[pos] = None, None 
            else:
                has_order[first] = has_order[second] = True

        for v in aliases:
            # any alias that doesn't have an ordering after we detect all
            # nodes with orders should get an ordering relative to INGRESS,
            # as if it were added with no under or over in add_implicit
            if (not v in has_order) and (v not in (INGRESS, MAIN)):
                order.append((v, INGRESS))
                ingress_alias_names.append(v)
            add_node(graph, v)

        for a, b in order:
            if a is not None and b is not None: # deal with removed orders
                add_arc(graph, a, b)

        def sortroots(alias):
            # sort roots so that roots (and their children) that depend only
            # on the ingress sort nearer the end (nearer the ingress)
            if alias in ingress_alias_names:
                return 1
            children = graph[alias][1:]
            for child in children:
                if sortroots(child) == 1:
                    return 1
            return -1

        roots.sort(key=sortroots)

        sorted_aliases = []

        while roots:
            root = roots.pop(0)
            sorted_aliases.append(root)
            children = graph[root][1:]
            for child in children:
                arcs = graph[child][0]
                arcs -= 1
                graph[child][0] = arcs 
                if arcs == 0:
                    roots.insert(0, child)
            del graph[root]

        if graph:
            # loop in input
            cycledeps = {}
            for k, v in graph.items():
                cycledeps[k] = v[1:]
            raise CyclicDependencyError(cycledeps)

        result = []

        for alias in sorted_aliases:
            if alias not in (MAIN, INGRESS):
                name = self.alias_to_name.get(alias, alias)
                result.append((name, self.factories[name]))

        return result

    def __call__(self, handler, registry):
        if self.explicit:
            use = self.explicit
        else:
            use = self.implicit()
        for name, factory in use:
            handler = factory(handler, registry)
        return handler
    
def tween_factory_name(factory):
    if (hasattr(factory, '__name__') and
        hasattr(factory, '__module__')):
        # function or class
        name = '.'.join([factory.__module__,
                         factory.__name__])
    elif hasattr(factory, '__module__'):
        # instance
        name = '.'.join([factory.__module__,
                         factory.__class__.__name__,
                         str(id(factory))])
    else:
        raise ConfigurationError(
            'A tween factory must be a class, an instance, or a function; '
            '%s is not a suitable tween factory' % factory)
    return name

MAIN = 'MAIN'
INGRESS = 'INGRESS'
EXCVIEW = 'excview'

