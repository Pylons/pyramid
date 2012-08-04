import re

from pyramid.compat import is_nonstr_iter

from pyramid.exceptions import ConfigurationError

from pyramid.traversal import (
    find_interface,
    traversal_path,
    )

from pyramid.urldispatch import _compile_route

from .util import as_sorted_tuple

class XHRPredicate(object):
    def __init__(self, val):
        self.val = bool(val)

    def text(self):
        return 'xhr = %s' % self.val

    phash = text

    def __call__(self, context, request):
        return bool(request.is_xhr) is self.val

class RequestMethodPredicate(object):
    def __init__(self, val):
        self.val = as_sorted_tuple(val)

    def text(self):
        return 'request_method = %s' % (','.join(self.val))

    phash = text

    def __call__(self, context, request):
        return request.method in self.val

class PathInfoPredicate(object):
    def __init__(self, val):
        self.orig = val
        try:
            val = re.compile(val)
        except re.error as why:
            raise ConfigurationError(why.args[0])
        self.val = val

    def text(self):
        return 'path_info = %s' % (self.orig,)

    phash = text

    def __call__(self, context, request):
        return self.val.match(request.upath_info) is not None
    
class RequestParamPredicate(object):
    def __init__(self, val):
        name = val
        v = None
        if '=' in name:
            name, v = name.split('=', 1)
            name, v = name.strip(), v.strip()
        if v is None:
            self._text = 'request_param %s' % (name,)
        else:
            self._text = 'request_param %s = %s' % (name, v)
        self.name = name
        self.val = v

    def text(self):
        return self._text

    phash = text

    def __call__(self, context, request):
        if self.val is None:
            return self.name in request.params
        return request.params.get(self.name) == self.val
    

class HeaderPredicate(object):
    def __init__(self, val):
        name = val
        v = None
        if ':' in name:
            name, v = name.split(':', 1)
            try:
                v = re.compile(v)
            except re.error as why:
                raise ConfigurationError(why.args[0])
        if v is None:
            self._text = 'header %s' % (name,)
        else:
            self._text = 'header %s = %s' % (name, v)
        self.name = name
        self.val = v

    def text(self):
        return self._text

    phash = text

    def __call__(self, context, request):
        if self.val is None:
            return self.name in request.headers
        val = request.headers.get(self.name)
        if val is None:
            return False
        return self.val.match(val) is not None

class AcceptPredicate(object):
    def __init__(self, val):
        self.val = val

    def text(self):
        return 'accept = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return self.val in request.accept

class ContainmentPredicate(object):
    def __init__(self, val):
        self.val = val

    def text(self):
        return 'containment = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        ctx = getattr(request, 'context', context)
        return find_interface(ctx, self.val) is not None
    
class RequestTypePredicate(object):
    def __init__(self, val):
        self.val = val

    def text(self):
        return 'request_type = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return self.val.providedBy(request)
    
class MatchParamPredicate(object):
    def __init__(self, val):
        if not is_nonstr_iter(val):
            val = (val,)
        val = sorted(val)
        self.val = val
        reqs = [ p.split('=', 1) for p in val ]
        self.reqs = [ (x.strip(), y.strip()) for x, y in reqs ]

    def text(self):
        return 'match_param %s' % ','.join(
            ['%s=%s' % (x,y) for x, y in self.reqs]
            )

    phash = text

    def __call__(self, context, request):
        for k, v in self.reqs:
            if request.matchdict.get(k) != v:
                return False
        return True
    
class CustomPredicate(object):
    def __init__(self, func):
        self.func = func

    def text(self):
        return getattr(self.func, '__text__', repr(self.func))

    def phash(self):
        return 'custom:%r' % hash(self.func)

    def __call__(self, context, request):
        return self.func(context, request)
    
    
class TraversePredicate(object):
    def __init__(self, val):
        _, self.tgenerate = _compile_route(val)
        self.val = val
        
    def text(self):
        return 'traverse matchdict pseudo-predicate'

    def phash(self):
        return ''

    def __call__(self, context, request):
        if 'traverse' in context:
            return True
        m = context['match']
        tvalue = self.tgenerate(m)
        m['traverse'] = traversal_path(tvalue)
        return True
