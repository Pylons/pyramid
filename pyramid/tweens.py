import sys
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IExceptionViewClassifier
from pyramid.interfaces import IView
from pyramid.interfaces import ITweens

from pyramid.events import NewResponse
from zope.interface import providedBy
from zope.interface import implements

def excview_tween_factory(handler, registry):
    """ A :term:`tween` factory which produces a tween that catches an
    exception raised by downstream tweens (or the main Pyramid request
    handler) and, if possible, converts it into a Response using an
    :term:`exception view`."""
    has_listeners = registry.has_listeners
    adapters = registry.adapters
    notify = registry.notify

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
            has_listeners and notify(NewResponse(request, response))
        finally:
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
            L.append('%r sorts atop %r' % (dependent, dependees))
        msg = '; '.join(L)
        return msg

MAIN = 'main'
INGRESS = 'ingress'

class Tweens(object):
    implements(ITweens)
    def __init__(self):
        self.explicit = []
        self.implicit_names = []
        self.implicit_factories = {}
        self.implicit_order = []
        self.implicit_ingress_names = []

    def add_explicit(self, name, factory):
        self.explicit.append((name, factory))

    def add_implicit(self, name, factory, below=None, atop=None):
        if below is None and atop is None:
            atop = 'ingress'
            self.implicit_ingress_names.append(name)
        if below is not None:
            order = (below, name)
            self.implicit_order.append(order)
        if atop is not None:
            order = (name, atop)
            self.implicit_order.append(order)
        self.implicit_names.append(name)
        self.implicit_factories[name] = factory

    def implicit(self):
        roots = []
        graph = {}

        def add_node(graph, node):
            if not graph.has_key(node):
                roots.append(node)
                graph[node] = [0] # 0 = number of arcs coming into this node

        def add_arc(graph, fromnode, tonode):
            graph[fromnode].append(tonode)
            graph[tonode][0] += 1
            if tonode in roots:
                roots.remove(tonode)

        names = [MAIN, INGRESS] + self.implicit_names

        orders = {}

        for pos, (first, second) in enumerate(self.implicit_order):
            has_first = first in names
            has_second = second in names
            if (not has_first) or (not has_second):
                self.implicit_order[pos] = None, None # FFF
            else:
                orders[first] = orders[second] = True

        for v in names:
            # any name that doesn't have an ordering after we detect all
            # nodes with orders should get an ordering relative to INGRESS,
            # as if it were added with no below or atop
            if (not v in orders) and (v not in (INGRESS, MAIN)):
                self.implicit_order.append((v, INGRESS))
                self.implicit_ingress_names.append(v)
            add_node(graph, v)

        for a, b in self.implicit_order:
            if a is not None and b is not None: # see FFF above
                add_arc(graph, a, b)

        def sortroots(name):
            # sort roots so that roots (and their children) that depend only on
            # the ingress sort nearer the end (nearer the ingress)
            if name in self.implicit_ingress_names:
                return 1
            children = graph[name][1:]
            for child in children:
                if sortroots(child) == 1:
                    return 1
            return -1

        roots.sort(key=sortroots)

        sorted_tweens = []

        while roots:
            root = roots.pop(0)
            sorted_tweens.append(root)
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

        return [ (name, self.implicit_factories[name]) for name in
                 sorted_tweens if name not in (MAIN, INGRESS) ]

    def __call__(self, handler, registry):
        if self.explicit:
            factories = self.explicit
        else:
            factories = self.implicit()
        for name, factory in factories:
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
