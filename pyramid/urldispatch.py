import re
from zope.interface import implements

from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import IRoute

from pyramid.exceptions import URLDecodeError
from pyramid.traversal import split_path_info
from pyramid.traversal import quote_path_segment

_marker = object()

class Route(object):
    implements(IRoute)
    def __init__(self, name, pattern, factory=None, predicates=(),
                 pregenerator=None):
        self.pattern = pattern
        self.path = pattern # indefinite b/w compat, not in interface
        self.match, self.generate = _compile_route(pattern)
        self.name = name
        self.factory = factory
        self.predicates = predicates
        self.pregenerator = pregenerator

class RoutesMapper(object):
    implements(IRoutesMapper)
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
            path = (environ['PATH_INFO'] or '/' ).decode('utf-8')
        except KeyError:
            path = '/'
        except UnicodeDecodeError, e:
            raise URLDecodeError(e.encoding, e.object, e.start, e.end, e.reason)

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
    # This function really wants to consume Unicode patterns natively, but if
    # someone passes us a bytestring, we allow it by converting it to Unicode
    # using the ASCII decoding.  We decode it using ASCII because we dont
    # want to accept bytestrings with high-order characters in them here as
    # we have no idea what the encoding represents.
    if route.__class__ is not unicode:
        try:
            route = unicode(route, 'ascii')
        except UnicodeDecodeError:
            raise ValueError(
                'The pattern value passed to add_route must be '
                'either a Unicode string or a plain string without '
                'any non-ASCII characters (you provided %r).' % route)

    if old_route_re.search(route) and not route_re.search(route):
        route = old_route_re.sub(update_pattern, route)

    if not route.startswith('/'):
        route = '/' + route

    remainder = None
    if star_at_end.search(route):
        route, remainder = route.rsplit('*', 1)

    pat = route_re.split(route)

    # every element in "pat" will be Unicode (regardless of whether the
    # route_re regex pattern is itself Unicode or str)
    pat.reverse()
    rpat = []
    gen = []
    prefix = pat.pop() # invar: always at least one element (route='/'+route)


    # We want to generate URL-encoded URLs, so we url-quote the prefix, being
    # careful not to quote any embedded slashes.  We have to replace '%' with
    # '%%' afterwards, as the strings that go into "gen" are used as string
    # replacement targets.
    gen.append(quote_path_segment(prefix, safe='/').replace('%', '%%')) # native
    rpat.append(re.escape(prefix)) # unicode

    while pat:
        name = pat.pop() # unicode
        name = name[1:-1]
        if ':' in name:
            name, reg = name.split(':')
        else:
            reg = '[^/]+'
        gen.append('%%(%s)s' % name.encode('utf-8')) # native
        name = '(?P<%s>%s)' % (name, reg) # unicode
        rpat.append(name)
        s = pat.pop() # unicode
        if s:
            rpat.append(re.escape(s)) # unicode
            # We want to generate URL-encoded URLs, so we url-quote this
            # literal in the pattern, being careful not to quote the embedded
            # slashes.  We have to replace '%' with '%%' afterwards, as the
            # strings that go into "gen" are used as string replacement
            # targets.  What is appended to gen is a native string.
            gen.append(quote_path_segment(s, safe='/').replace('%', '%%'))

    if remainder:
        rpat.append('(?P<%s>.*?)' % remainder) # unicode
        gen.append('%%(%s)s' % remainder.encode('utf-8')) # native

    pattern = ''.join(rpat) + '$' # unicode

    match = re.compile(pattern).match
    def matcher(path):
        # This function really wants to consume Unicode patterns natively,
        # but if someone passes us a bytestring, we allow it by converting it
        # to Unicode using the ASCII decoding.  We decode it using ASCII
        # because we dont want to accept bytestrings with high-order
        # characters in them here as we have no idea what the encoding
        # represents.
        if path.__class__ is not unicode:
            path = unicode(path, 'ascii')
        m = match(path)
        if m is None:
            return None
        d = {}
        for k, v in m.groupdict().iteritems():
            # k and v will be Unicode 2.6.4 and lower doesnt accept unicode
            # kwargs as **kw, so we explicitly cast the keys to native
            # strings in case someone wants to pass the result as **kw
            nk = k.encode('ascii')
            if k == remainder:
                d[nk] = split_path_info(v)
            else:
                d[nk] = v
                        
        return d
                    

    gen = ''.join(gen)
    def generator(dict):
        newdict = {}
        for k, v in dict.items():
            if v.__class__ is unicode:
                # url_quote below needs bytes, not unicode on Py2
                v = v.encode('utf-8')

            if k == remainder:
                # a stararg argument
                if hasattr(v, '__iter__'):
                    v = '/'.join([quote_path_segment(x) for x in v]) # native
                else:
                    if v.__class__ not in (str, unicode):
                        v = str(v)
                    v = quote_path_segment(v, safe='/')
            else:
                if v.__class__ not in (str, unicode):
                    v = str(v)
                v = quote_path_segment(v)

            # at this point, the value will be a native string
            newdict[k] = v

        result = gen % newdict # native string result
        return result

    return matcher, generator
