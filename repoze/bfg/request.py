from zope.deprecation import deprecated
from zope.interface import implements
from zope.interface.interface import InterfaceClass

from webob import Request as WebobRequest

from repoze.bfg.interfaces import IRequest

def make_request_ascii(event):
    """ An function that is useful as a
    :class:`repoze.bfg.interfaces.INewRequest` :term:`event`
    :term:`subscriber` that causes the request charset to be ASCII so
    code written before :mod:`repoze.bfg` 0.7.0 can continue to work
    without a change"""
    request = event.request
    request.default_charset = None

class Request(WebobRequest):
    implements(IRequest)
    default_charset = 'utf-8'

    # override default WebOb "environ['adhoc_attr']" mutation behavior
    __getattr__ = object.__getattribute__
    __setattr__ = object.__setattr__
    __delattr__ = object.__delattr__

    # b/c dict interface for "root factory" code that expects a bare
    # environ.  Explicitly omitted dict methods: clear (unnecessary),
    # copy (implemented by WebOb), fromkeys (unnecessary)
    
    def __contains__(self, k):
        return self.environ.__contains__(k)

    def __delitem__(self, k):
        return self.environ.__delitem__(k)

    def __getitem__(self, k):
        return self.environ.__getitem__(k)

    def __iter__(self):
        return iter(self.environ)

    def __setitem__(self, k, v):
        self.environ[k] = v

    def get(self, k, default=None):
        return self.environ.get(k, default)

    def has_key(self, k):
        return self.environ.has_key(k)

    def items(self):
        return self.environ.items()

    def iteritems(self):
        return self.environ.iteritems()

    def iterkeys(self):
        return self.environ.iterkeys()

    def itervalues(self):
        return self.environ.itervalues()

    def keys(self):
        return self.environ.keys()

    def pop(self, k):
        return self.environ.pop(k)

    def popitem(self):
        return self.environ.popitem()

    def setdefault(self, v, default):
        return self.environ.setdefault(v, default)

    def update(self, v, **kw):
        return self.environ.update(v, **kw)

    def values(self):
        return self.environ.values()

def route_request_iface(name, bases=()):
    return InterfaceClass('%s_IRequest' % name, bases=bases)

def add_global_response_headers(request, headerlist):
    attrs = request.__dict__
    response_headers = attrs.setdefault('global_response_headers', [])
    response_headers.extend(headerlist)

from repoze.bfg.threadlocal import get_current_request as get_request # b/c

get_request # prevent PyFlakes complaints

deprecated('get_request',
           'As of repoze.bfg 1.0, any import of get_request from'
           '``repoze.bfg.request`` is '
           'deprecated.  Use ``from repoze.bfg.threadlocal import '
           'get_current_request instead.')

