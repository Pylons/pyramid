import re

_marker = object()

class Route(object):
    def __init__(self, name, matcher, generator, factory):
        self.name = name
        self.matcher = matcher
        self.generator = generator
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

    def connect(self, name, path, factory=None):
        matcher, generator = _compile_route(path)
        route = Route(name, matcher, generator, factory)
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
        return dict(item for item in m.groupdict().iteritems()
                    if item[1] is not None)

    gen = ''.join(gen)
    def generator(dict):
        newdict = {}
        for k, v in dict.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            newdict[k] = v
        return gen % newdict

    return matcher, generator
