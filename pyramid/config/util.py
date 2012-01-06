import re
import traceback

from zope.interface import implementer

from pyramid.interfaces import IActionInfo

from pyramid.compat import (
    string_types,
    bytes_,
    is_nonstr_iter,
    )

from pyramid.exceptions import ConfigurationError

from pyramid.traversal import (
    find_interface,
    traversal_path,
    )

from hashlib import md5

MAX_ORDER = 1 << 30
DEFAULT_PHASH = md5().hexdigest()

@implementer(IActionInfo)
class ActionInfo(object):
    def __init__(self, file, line, function, src):
        self.file = file
        self.line = line
        self.function = function
        self.src = src

    def __str__(self):
        srclines = self.src.split('\n')
        src = '\n'.join('    %s' % x for x in srclines)
        return 'Line %s of file %s:\n%s' % (self.line, self.file, src)

def action_method(wrapped):
    """ Wrapper to provide the right conflict info report data when a method
    that calls Configurator.action calls another that does the same"""
    def wrapper(self, *arg, **kw):
        if self._ainfo is None:
            self._ainfo = []
        info = kw.pop('_info', None)
        # backframes for outer decorators to actionmethods
        backframes = kw.pop('_backframes', 2) 
        if is_nonstr_iter(info) and len(info) == 4:
            # _info permitted as extract_stack tuple
            info = ActionInfo(*info)
        if info is None:
            try:
                f = traceback.extract_stack(limit=3)
                info = ActionInfo(*f[-backframes])
            except: # pragma: no cover
                info = ActionInfo(None, 0, '', '')
        self._ainfo.append(info)
        try:
            result = wrapped(self, *arg, **kw)
        finally:
            self._ainfo.pop()
        return result
    wrapper.__name__ = wrapped.__name__
    wrapper.__doc__ = wrapped.__doc__
    wrapper.__docobj__ = wrapped # for sphinx
    return wrapper

def make_predicates(xhr=None, request_method=None, path_info=None,
                    request_param=None, match_param=None, header=None,
                    accept=None, containment=None, request_type=None,
                    traverse=None, custom=()):

    # PREDICATES
    # ----------
    #
    # Given an argument list, a predicate list is computed.
    # Predicates are added to a predicate list in (presumed)
    # computation expense order.  All predicates associated with a
    # view or route must evaluate true for the view or route to
    # "match" during a request.  Elsewhere in the code, we evaluate
    # predicates using a generator expression.  The fastest predicate
    # should be evaluated first, then the next fastest, and so on, as
    # if one returns false, the remainder of the predicates won't need
    # to be evaluated.
    #
    # While we compute predicates, we also compute a predicate hash
    # (aka phash) that can be used by a caller to identify identical
    # predicate lists.
    #
    # ORDERING
    # --------
    #
    # A "order" is computed for the predicate list.  An order is
    # a scoring.
    #
    # Each predicate is associated with a weight value, which is a
    # multiple of 2.  The weight of a predicate symbolizes the
    # relative potential "importance" of the predicate to all other
    # predicates.  A larger weight indicates greater importance.
    #
    # All weights for a given predicate list are bitwise ORed together
    # to create a "score"; this score is then subtracted from
    # MAX_ORDER and divided by an integer representing the number of
    # predicates+1 to determine the order.
    #
    # The order represents the ordering in which a "multiview" ( a
    # collection of views that share the same context/request/name
    # triad but differ in other ways via predicates) will attempt to
    # call its set of views.  Views with lower orders will be tried
    # first.  The intent is to a) ensure that views with more
    # predicates are always evaluated before views with fewer
    # predicates and b) to ensure a stable call ordering of views that
    # share the same number of predicates.  Views which do not have
    # any predicates get an order of MAX_ORDER, meaning that they will
    # be tried very last.

    predicates = []
    weights = []
    h = md5()

    if xhr:
        def xhr_predicate(context, request):
            return request.is_xhr
        xhr_predicate.__text__ = "xhr = True"
        weights.append(1 << 1)
        predicates.append(xhr_predicate)
        h.update(bytes_('xhr:%r' % bool(xhr)))

    if request_method is not None:
        if not is_nonstr_iter(request_method):
            request_method = (request_method,)
        request_method = sorted(request_method)
        def request_method_predicate(context, request):
            return request.method in request_method
        text = "request method = %s" % repr(request_method)
        request_method_predicate.__text__ = text
        weights.append(1 << 2)
        predicates.append(request_method_predicate)
        for m in request_method:
            h.update(bytes_('request_method:%r' % m))

    if path_info is not None:
        try:
            path_info_val = re.compile(path_info)
        except re.error as why:
            raise ConfigurationError(why.args[0])
        def path_info_predicate(context, request):
            return path_info_val.match(request.upath_info) is not None
        text = "path_info = %s"
        path_info_predicate.__text__ = text % path_info
        weights.append(1 << 3)
        predicates.append(path_info_predicate)
        h.update(bytes_('path_info:%r' % path_info))

    if request_param is not None:
        request_param_val = None
        if '=' in request_param:
            request_param, request_param_val = request_param.split('=', 1)
        if request_param_val is None:
            text = "request_param %s" % request_param
        else:
            text = "request_param %s = %s" % (request_param, request_param_val)
        def request_param_predicate(context, request):
            if request_param_val is None:
                return request_param in request.params
            return request.params.get(request_param) == request_param_val
        request_param_predicate.__text__ = text
        weights.append(1 << 4)
        predicates.append(request_param_predicate)
        h.update(
            bytes_('request_param:%r=%r' % (request_param, request_param_val)))

    if header is not None:
        header_name = header
        header_val = None
        if ':' in header:
            header_name, header_val = header.split(':', 1)
            try:
                header_val = re.compile(header_val)
            except re.error as why:
                raise ConfigurationError(why.args[0])
        if header_val is None:
            text = "header %s" % header_name
        else:
            text = "header %s = %s" % (header_name, header_val)
        def header_predicate(context, request):
            if header_val is None:
                return header_name in request.headers
            val = request.headers.get(header_name)
            if val is None:
                return False
            return header_val.match(val) is not None
        header_predicate.__text__ = text
        weights.append(1 << 5)
        predicates.append(header_predicate)
        h.update(bytes_('header:%r=%r' % (header_name, header_val)))

    if accept is not None:
        def accept_predicate(context, request):
            return accept in request.accept
        accept_predicate.__text__ = "accept = %s" % accept
        weights.append(1 << 6)
        predicates.append(accept_predicate)
        h.update(bytes_('accept:%r' % accept))

    if containment is not None:
        def containment_predicate(context, request):
            return find_interface(context, containment) is not None
        containment_predicate.__text__ = "containment = %s" % containment
        weights.append(1 << 7)
        predicates.append(containment_predicate)
        h.update(bytes_('containment:%r' % hash(containment)))

    if request_type is not None:
        def request_type_predicate(context, request):
            return request_type.providedBy(request)
        text = "request_type = %s"
        request_type_predicate.__text__ = text % request_type
        weights.append(1 << 8)
        predicates.append(request_type_predicate)
        h.update(bytes_('request_type:%r' % hash(request_type)))

    if match_param is not None:
        if isinstance(match_param, string_types):
            match_param, match_param_val = match_param.split('=', 1)
            match_param = {match_param: match_param_val}
        text = "match_param %s" % match_param
        def match_param_predicate(context, request):
            for k, v in match_param.items():
                if request.matchdict.get(k) != v:
                    return False
            return True
        match_param_predicate.__text__ = text
        weights.append(1 << 9)
        predicates.append(match_param_predicate)
        h.update(bytes_('match_param:%r' % match_param))

    if custom:
        for num, predicate in enumerate(custom):
            if getattr(predicate, '__text__', None) is None:
                text = '<unknown custom predicate>'
                try:
                    predicate.__text__ = text
                except AttributeError:
                    # if this happens the predicate is probably a classmethod
                    if hasattr(predicate, '__func__'):
                        predicate.__func__.__text__ = text
                    else: # pragma: no cover ; 2.5 doesn't have __func__
                        predicate.im_func.__text__ = text
            predicates.append(predicate)
            # using hash() here rather than id() is intentional: we
            # want to allow custom predicates that are part of
            # frameworks to be able to define custom __hash__
            # functions for custom predicates, so that the hash output
            # of predicate instances which are "logically the same"
            # may compare equal.
            h.update(bytes_('custom%s:%r' % (num, hash(predicate))))
        weights.append(1 << 10)

    if traverse is not None:
        # ``traverse`` can only be used as a *route* "predicate"; it
        # adds 'traverse' to the matchdict if it's specified in the
        # routing args.  This causes the ResourceTreeTraverser to use
        # the resolved traverse pattern as the traversal path.
        from pyramid.urldispatch import _compile_route
        _, tgenerate = _compile_route(traverse)
        def traverse_predicate(context, request):
            if 'traverse' in context:
                return True
            m = context['match']
            tvalue = tgenerate(m) # tvalue will be urlquoted string
            m['traverse'] = traversal_path(tvalue) # will be seq of unicode
            return True
        # This isn't actually a predicate, it's just a infodict
        # modifier that injects ``traverse`` into the matchdict.  As a
        # result, the ``traverse_predicate`` function above always
        # returns True, and we don't need to update the hash or attach
        # a weight to it
        predicates.append(traverse_predicate)

    score = 0
    for bit in weights:
        score = score | bit
    order = (MAX_ORDER - score) / (len(predicates) + 1)
    phash = h.hexdigest()
    return order, predicates, phash

def as_sorted_tuple(val):
    if not is_nonstr_iter(val):
        val = (val,)
    val = tuple(sorted(val))
    return val

