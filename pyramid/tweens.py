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
            # prevent leakage (wrt exc_info)
            if 'exc_info' in attrs:
                del attrs['exc_info']
            if 'exception' in attrs:
                del attrs['exception']

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
        msg = 'Implicit tween ordering cycle:' + '; '.join(L)
        return msg

class Tweens(object):
    implements(ITweens)
    def __init__(self):
        self.explicit = []
        self.names = []
        self.req_over = set()
        self.req_under = set()
        self.factories = {}
        self.order = []
        self.alias_to_name = {INGRESS:INGRESS, MAIN:MAIN}
        self.name_to_alias = {INGRESS:INGRESS, MAIN:MAIN}

    def add_explicit(self, name, factory):
        self.explicit.append((name, factory))

    def add_implicit(self, name, factory, alias=None, under=None, over=None):
        if alias is None:
            alias = name
        self.alias_to_name[alias] = name
        self.name_to_alias[name] = alias
        self.names.append(name)
        self.factories[name] = factory
        if under is None and over is None:
            under = INGRESS
        if under is not None:
            if not hasattr(under, '__iter__'):
                under = (under,)
            self.order += [(u, alias) for u in under]
            self.req_under.add(alias)
        if over is not None:
            if not hasattr(over, '__iter__'):
                over = (over,)
            self.order += [(alias, o) for o in over]
            self.req_over.add(alias)

    def implicit(self):
        order = [(INGRESS, MAIN)]
        roots = []
        graph = {}
        aliases = [INGRESS, MAIN]

        for name in self.names:
            aliases.append(self.name_to_alias[name])

        for a, b in self.order:
            # try to convert both a and b to an alias
            a = self.name_to_alias.get(a, a)
            b = self.name_to_alias.get(b, b)
            order.append((a, b))

        def add_node(node):
            if not graph.has_key(node):
                roots.append(node)
                graph[node] = [0] # 0 = number of arcs coming into this node

        def add_arc(fromnode, tonode):
            graph[fromnode].append(tonode)
            graph[tonode][0] += 1
            if tonode in roots:
                roots.remove(tonode)

        for alias in aliases:
            add_node(alias)

        has_over, has_under = set(), set()
        for a, b in order:
            if a in aliases and b in aliases: # deal with missing dependencies
                add_arc(a, b)
                has_over.add(a)
                has_under.add(b)

        if not self.req_over.issubset(has_over):
            raise ConfigurationError(
                'Detected tweens with no satisfied over dependencies: %s'
                % (', '.join(sorted(self.req_over - has_over)))
            )
        if not self.req_under.issubset(has_under):
            raise ConfigurationError(
                'Detected tweens with no satisfied under dependencies: %s'
                % (', '.join(sorted(self.req_under - has_under)))
            )

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
            name = self.alias_to_name.get(alias, alias)
            if name in self.names:
                result.append((name, self.factories[name]))

        return result

    def __call__(self, handler, registry):
        if self.explicit:
            use = self.explicit
        else:
            use = self.implicit()
        for name, factory in use[::-1]:
            handler = factory(handler, registry)
        return handler
    
MAIN = 'MAIN'
INGRESS = 'INGRESS'
EXCVIEW = 'excview'

