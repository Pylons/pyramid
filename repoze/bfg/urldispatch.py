import re
from urllib import unquote

from repoze.bfg.traversal import _url_quote
from repoze.bfg.traversal import traversal_path
from repoze.bfg.traversal import quote_path_segment

_marker = object()

class Route(object):
    def __init__(self, path, name=None, factory=None):
        self.path = path
        self.matcher, self.generator = _compile_route(path)
        self.name = name
        self.factory = factory

    def match(self, path):
        return self.matcher(path)

    def generate(self, kw):
        return self.generator(kw)

class RoutesRootFactory(object):
    def __init__(self, default_root_factory):
        self.default_root_factory = default_root_factory
        self.routelist = []
        self.routes = {}

    def has_routes(self):
        return bool(self.routelist)

    def get_routes(self):
        return self.routelist

    def connect(self, path, name, factory=None):
        route = Route(path, name, factory)
        self.routelist.append(route)
        self.routes[name] = route
        return route

    def generate(self, name, kw):
        return self.routes[name].generate(kw)

    def __call__(self, environ):
        path = environ.get('PATH_INFO', '/')
        for route in self.routelist:
            match = route.match(path)
            if match is not None:
                environ['wsgiorg.routing_args'] = ((), match)
                environ['bfg.routes.route'] = route
                environ['bfg.routes.matchdict'] = match
                adhoc_attrs = environ.setdefault('webob.adhoc_attrs', {})
                adhoc_attrs['matchdict'] = match
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
                    v = _url_quote(v)
                except TypeError:
                    pass
            newdict[k] = v
        return gen % newdict

    return matcher, generator
