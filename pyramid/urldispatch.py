import re
from zope.interface import implementer

from pyramid.interfaces import (
    IRoutesMapper,
    IRoute,
    )

from pyramid.compat import (
    native_,
    bytes_,
    text_type,
    string_types,
    is_nonstr_iter,
    url_quote,
    )

from pyramid.exceptions import URLDecodeError

from pyramid.traversal import (
    traversal_path_info,
    quote_path_segment,
    )

_marker = object()

@implementer(IRoute)
class Route(object):
    def __init__(self, name, pattern, factory=None, predicates=(),
                 pregenerator=None):
        self.pattern = pattern
        self.path = pattern # indefinite b/w compat, not in interface
        self.match, self.generate = _compile_route(pattern)
        self.name = name
        self.factory = factory
        self.predicates = predicates
        self.pregenerator = pregenerator

@implementer(IRoutesMapper)
class RoutesMapper(object):
    def __init__(self):
        self.routelist = []
        self.routes = {}

    def has_routes(self):
        return bool(self.routelist)

    def get_routes(self):
        return self.routelist

    def get_route(self, name):
        return self.routes.get(name)

    def connect(self, name, pattern, factory=None, predicates=(),
                pregenerator=None, static=False):
        if name in self.routes:
            oldroute = self.routes[name]
            if oldroute in self.routelist:
                self.routelist.remove(oldroute)
        route = Route(name, pattern, factory, predicates, pregenerator)
        if not static:
            self.routelist.append(route)
        self.routes[name] = route
        return route

    def generate(self, name, kw):
        return self.routes[name].generate(kw)

    def __call__(self, request):
        environ = request.environ
        try:
            # empty if mounted under a path in mod_wsgi, for example
            path = environ['PATH_INFO'] or '/' 
        except KeyError:
            path = '/'

        for route in self.routelist:
            match = route.match(path)
            if match is not None:
                preds = route.predicates
                info = {'match':match, 'route':route}
                if preds and not all((p(info, request) for p in preds)):
                    continue
                return info

        return {'route':None, 'match':None}

# stolen from bobo and modified
old_route_re = re.compile(r'(\:[_a-zA-Z]\w*)')
star_at_end = re.compile(r'\*\w*$')

# The torturous nature of the regex named ``route_re`` below is due to the
# fact that we need to support at least one level of "inner" squigglies
# inside the expr of a {name:expr} pattern.  This regex used to be just
# (\{[a-zA-Z][^\}]*\}) but that choked when supplied with e.g. {foo:\d{4}}.
route_re = re.compile(r'(\{[_a-zA-Z][^{}]*(?:\{[^{}]*\}[^{}]*)*\})')

def update_pattern(matchobj):
    name = matchobj.group(0)
    return '{%s}' % name[1:]

def _compile_route(route):
    if old_route_re.search(route) and not route_re.search(route):
        route = old_route_re.sub(update_pattern, route)

    if not route.startswith('/'):
        route = '/' + route

    star = None
    if star_at_end.search(route):
        route, star = route.rsplit('*', 1)

    pat = route_re.split(route)
    pat.reverse()
    rpat = []
    gen = []
    prefix = pat.pop() # invar: always at least one element (route='/'+route)
    rpat.append(re.escape(prefix))
    gen.append(prefix)

    s = None
    while pat:
        name = pat.pop()
        name = name[1:-1]
        if ':' in name:
            name, reg = name.split(':')
        else:
            reg = '[^/]+'
        gen.append('%%(%s)s' % name)
        name = '(?P<%s>%s)' % (name, reg)
        rpat.append(name)
        s = pat.pop()
        if s:
            rpat.append(re.escape(s))
            gen.append(s)

    if star:
        if route.endswith('/') or not s:
            rpat.append('(?P<%s>.*?)' % star)
        else:
            rpat.append('(?P<%s>(?:\/.*?)?)' % star)
        gen.append('%%(%s)s' % star)

    pattern = ''.join(rpat) + '$'

    match = re.compile(pattern).match
    def matcher(path):
        m = match(path)
        if m is None:
            return m
        d = {}
        for k, v in m.groupdict().items():
            if k == star:
                d[k] = traversal_path_info(v)
            else:
                try:
                    val = bytes_(v).decode('utf-8', 'strict')
                    d[k] = val
                except UnicodeDecodeError as e:
                    raise URLDecodeError(
                        e.encoding, e.object, e.start, e.end, e.reason
                        )
                        
                        
        return d
                    

    gen = ''.join(gen)
    def generator(dict):
        newdict = {}
        for k, v in dict.items():
            if v.__class__ is text_type:
                v = native_(v, 'utf-8')
            if k == star and is_nonstr_iter(v):
                v = '/'.join([quote_path_segment(x) for x in v])
            elif k != star:
                if v.__class__ not in string_types:
                    v = str(v)
                v = url_quote(v, safe='')
            newdict[k] = v
        return gen % newdict

    return matcher, generator
