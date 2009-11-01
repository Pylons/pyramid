import re
from urllib import unquote

from zope.interface import directlyProvides

from repoze.bfg.interfaces import IRouteRequest

from repoze.bfg.compat import all
from repoze.bfg.encode import url_quote
from repoze.bfg.traversal import traversal_path
from repoze.bfg.traversal import quote_path_segment

_marker = object()

class Route(object):
    def __init__(self, path, name=None, factory=None, predicates=()):
        self.path = path
        self.match, self.generate = _compile_route(path)
        self.name = name
        self.factory = factory
        self.predicates = predicates

class RoutesRootFactory(object):
    def __init__(self, default_root_factory):
        self.default_root_factory = default_root_factory
        self.routelist = []
        self.routes = {}

    def has_routes(self):
        return bool(self.routelist)

    def get_routes(self):
        return self.routelist

    def connect(self, path, name, factory=None, predicates=()):
        route = Route(path, name, factory, predicates)
        self.routelist.append(route)
        self.routes[name] = route
        return route

    def generate(self, name, kw):
        return self.routes[name].generate(kw)

    def __call__(self, request):
        try:
            # As of BFG 1.1a9, a root factory is now typically called
            # with a request object (instead of a WSGI environ, as in
            # previous versions) by the router.  Simultaneously, as of
            # 1.1a9, the RoutesRootFactory *requires* that the object
            # passed to it be a request, instead of an environ, as it
            # uses both the ``registry`` attribute of the request, and
            # if a route is found, it decorates the object with an
            # interface using directlyProvides.  However, existing app
            # code "in the wild" calls the root factory explicitly
            # with a dictionary argument (e.g. a subscriber to
            # WSGIApplicationCreatedEvent does
            # ``app.root_factory({})``).  It makes no sense for such
            # code to depend on the side effects of a
            # RoutesRootFactory, for bw compat purposes we catch the
            # exception that will be raised when passed a dictionary
            # and just return the result of the default root factory.
            environ = request.environ
            registry = request.registry
        except AttributeError:
            return self.default_root_factory(request)

        try:
            path = environ['PATH_INFO']
        except KeyError:
            path = '/'
        for route in self.routelist:
            match = route.match(path)
            if match is not None:
                preds = route.predicates
                if preds and not all((p(None, request) for p in preds)):
                    continue
                environ['wsgiorg.routing_args'] = ((), match)
                environ['bfg.routes.route'] = route
                environ['bfg.routes.matchdict'] = match
                request.matchdict = match
                iface = registry.queryUtility(IRouteRequest, name=route.name)
                if iface is not None:
                    directlyProvides(request, iface)
                factory = route.factory or self.default_root_factory
                return factory(environ)

        return self.default_root_factory(environ)

# stolen from bobo and modified
route_re = re.compile(r'(/:[a-zA-Z]\w*)')
def _compile_route(route):
    if not route.startswith('/'):
        route = '/' + route
    star = None
    if '*' in route:
        route, star = route.rsplit('*', 1)
    pat = route_re.split(route)
    pat.reverse()
    rpat = []
    gen = []
    prefix = pat.pop()
    if prefix:
        rpat.append(re.escape(prefix))
        gen.append(prefix)
    while pat:
        name = pat.pop()
        name = name[2:]
        gen.append('/%%(%s)s' % name)
        name = '/(?P<%s>[^/]*)' % name
        rpat.append(name)
        s = pat.pop()
        if s:
            rpat.append(re.escape(s))
            gen.append(s)

    if star:
        rpat.append('(?P<%s>.*?)' % star)
        gen.append('%%(%s)s' % star)

    pattern = ''.join(rpat) + '$'

    match = re.compile(pattern).match
    def matcher(path):
        m = match(path)
        if m is None:
            return m
        d = {}
        for k,v in m.groupdict().iteritems():
            if k is not None:
                if k == star:
                    d[k] = traversal_path(v)
                else:
                    d[k] = unquote(v).decode('utf-8')
        return d
                    

    gen = ''.join(gen)
    def generator(dict):
        newdict = {}
        for k, v in dict.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if k == star and hasattr(v, '__iter__'):
                v = '/'.join([quote_path_segment(x) for x in v])
            elif k != star:
                try:
                    v = url_quote(v)
                except TypeError:
                    pass
            newdict[k] = v
        return gen % newdict

    return matcher, generator
