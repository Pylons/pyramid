import re

from pyramid.exceptions import ConfigurationError
from pyramid.traversal import (
    find_interface,
    resource_path_tuple,
    traversal_path,
)
from pyramid.urldispatch import _compile_route
from pyramid.util import as_sorted_tuple, is_nonstr_iter, object_description

_marker = object()


class XHRPredicate:
    def __init__(self, val, config):
        self.val = bool(val)

    def text(self):
        return 'xhr = %s' % self.val

    phash = text

    def __call__(self, context, request):
        return bool(request.is_xhr) is self.val


class RequestMethodPredicate:
    def __init__(self, val, config):
        request_method = as_sorted_tuple(val)
        if 'GET' in request_method and 'HEAD' not in request_method:
            # GET implies HEAD too
            request_method = as_sorted_tuple(request_method + ('HEAD',))
        self.val = request_method

    def text(self):
        return 'request_method = %s' % (','.join(self.val))

    phash = text

    def __call__(self, context, request):
        return request.method in self.val


class PathInfoPredicate:
    def __init__(self, val, config):
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


class RequestParamPredicate:
    def __init__(self, val, config):
        val = as_sorted_tuple(val)
        reqs = []
        for p in val:
            k = p
            v = None
            if p.startswith('='):
                if '=' in p[1:]:
                    k, v = p[1:].split('=', 1)
                    k = '=' + k
                    k, v = k.strip(), v.strip()
            elif '=' in p:
                k, v = p.split('=', 1)
                k, v = k.strip(), v.strip()
            reqs.append((k, v))
        self.val = val
        self.reqs = reqs

    def text(self):
        return 'request_param %s' % ','.join(
            ['%s=%s' % (x, y) if y else x for x, y in self.reqs]
        )

    phash = text

    def __call__(self, context, request):
        for k, v in self.reqs:
            actual = request.params.get(k)
            if actual is None:
                return False
            if v is not None and actual != v:
                return False
        return True


class HeaderPredicate:
    def __init__(self, val, config):
        values = []

        val = as_sorted_tuple(val)
        for name in val:
            v, val_str = None, None
            if ':' in name:
                name, val_str = name.split(':', 1)
                try:
                    v = re.compile(val_str)
                except re.error as why:
                    raise ConfigurationError(why.args[0])

            values.append((name, v, val_str))

        self.val = values

    def text(self):
        return 'header %s' % ', '.join(
            '%s=%s' % (name, val_str) if val_str else name
            for name, _, val_str in self.val
        )

    phash = text

    def __call__(self, context, request):
        for name, val, _ in self.val:
            if val is None:
                if name not in request.headers:
                    return False
            else:
                value = request.headers.get(name)
                if value is None:
                    return False
                if val.match(value) is None:
                    return False

        return True


class AcceptPredicate:
    def __init__(self, values, config):
        if not is_nonstr_iter(values):
            values = (values,)
        self.values = values

    def text(self):
        return 'accept = %s' % (', '.join(self.values),)

    phash = text

    def __call__(self, context, request):
        return bool(request.accept.acceptable_offers(self.values))


class ContainmentPredicate:
    def __init__(self, val, config):
        self.val = config.maybe_dotted(val)

    def text(self):
        return 'containment = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        ctx = getattr(request, 'context', context)
        return find_interface(ctx, self.val) is not None


class RequestTypePredicate:
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'request_type = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        return self.val.providedBy(request)


class MatchParamPredicate:
    def __init__(self, val, config):
        val = as_sorted_tuple(val)
        self.val = val
        reqs = [p.split('=', 1) for p in val]
        self.reqs = [(x.strip(), y.strip()) for x, y in reqs]

    def text(self):
        return 'match_param %s' % ','.join(
            ['%s=%s' % (x, y) for x, y in self.reqs]
        )

    phash = text

    def __call__(self, context, request):
        if not request.matchdict:
            # might be None
            return False
        for k, v in self.reqs:
            if request.matchdict.get(k) != v:
                return False
        return True


class CustomPredicate:
    def __init__(self, func, config):
        self.func = func

    def text(self):
        return getattr(
            self.func,
            '__text__',
            'custom predicate: %s' % object_description(self.func),
        )

    def phash(self):
        # using hash() here rather than id() is intentional: we
        # want to allow custom predicates that are part of
        # frameworks to be able to define custom __hash__
        # functions for custom predicates, so that the hash output
        # of predicate instances which are "logically the same"
        # may compare equal.
        return 'custom:%r' % hash(self.func)

    def __call__(self, context, request):
        return self.func(context, request)


class TraversePredicate:
    # Can only be used as a *route* "predicate"; it adds 'traverse' to the
    # matchdict if it's specified in the routing args.  This causes the
    # ResourceTreeTraverser to use the resolved traverse pattern as the
    # traversal path.
    def __init__(self, val, config):
        _, self.tgenerate = _compile_route(val)
        self.val = val

    def text(self):
        return 'traverse matchdict pseudo-predicate'

    def phash(self):
        # This isn't actually a predicate, it's just a infodict modifier that
        # injects ``traverse`` into the matchdict.  As a result, we don't
        # need to update the hash.
        return ''

    def __call__(self, context, request):
        if 'traverse' in context:
            return True
        m = context['match']
        tvalue = self.tgenerate(m)  # tvalue will be urlquoted string
        m['traverse'] = traversal_path(tvalue)
        # This isn't actually a predicate, it's just a infodict modifier that
        # injects ``traverse`` into the matchdict.  As a result, we just
        # return True.
        return True


class PhysicalPathPredicate:
    def __init__(self, val, config):
        if is_nonstr_iter(val):
            self.val = tuple(val)
        else:
            val = tuple(filter(None, val.split('/')))
            self.val = ('',) + val

    def text(self):
        return 'physical_path = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        if getattr(context, '__name__', _marker) is not _marker:
            return resource_path_tuple(context) == self.val
        return False


class IsAuthenticatedPredicate:
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return "is_authenticated = %r" % (self.val,)

    phash = text

    def __call__(self, context, request):
        return request.is_authenticated == self.val


class EffectivePrincipalsPredicate:
    def __init__(self, val, config):
        if is_nonstr_iter(val):
            self.val = set(val)
        else:
            self.val = {val}

    def text(self):
        return 'effective_principals = %s' % sorted(list(self.val))

    phash = text

    def __call__(self, context, request):
        req_principals = request.effective_principals
        if is_nonstr_iter(req_principals):
            rpset = set(req_principals)
            if self.val.issubset(rpset):
                return True
        return False


class Notted:
    def __init__(self, predicate):
        self.predicate = predicate

    def _notted_text(self, val):
        # if the underlying predicate doesnt return a value, it's not really
        # a predicate, it's just something pretending to be a predicate,
        # so dont update the hash
        if val:
            val = '!' + val
        return val

    def text(self):
        return self._notted_text(self.predicate.text())

    def phash(self):
        return self._notted_text(self.predicate.phash())

    def __call__(self, context, request):
        result = self.predicate(context, request)
        phash = self.phash()
        if phash:
            result = not result
        return result
