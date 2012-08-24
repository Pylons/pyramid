import traceback

from functools import update_wrapper

from zope.interface import implementer

from pyramid.interfaces import IActionInfo

from pyramid.compat import (
    bytes_,
    is_nonstr_iter,
    )

from pyramid.exceptions import ConfigurationError

from pyramid.registry import predvalseq

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

    if hasattr(wrapped, '__name__'):
        update_wrapper(wrapper, wrapped)
    wrapper.__docobj__ = wrapped
    return wrapper

def as_sorted_tuple(val):
    if not is_nonstr_iter(val):
        val = (val,)
    val = tuple(sorted(val))
    return val

# under = after
# over = before

class Singleton(object):
    def __init__(self, repr):
        self.repr = repr

    def __repr__(self):
        return self.repr

FIRST = Singleton('FIRST')
LAST = Singleton('LAST')

class TopologicalSorter(object):
    def __init__(
        self,
        default_before=LAST,
        default_after=None,
        first=FIRST,
        last=LAST,
        ):
        self.names = []
        self.req_before = set()
        self.req_after = set()
        self.name2before = {}
        self.name2after = {}
        self.name2val = {}
        self.order = []
        self.default_before = default_before
        self.default_after = default_after
        self.first = first
        self.last = last

    def remove(self, name):
        self.names.remove(name)
        del self.name2val[name]
        after = self.name2after.pop(name, [])
        if after:
            self.req_after.remove(name)
            for u in after:
                self.order.remove((u, name))
        before = self.name2before.pop(name, [])
        if before:
            self.req_before.remove(name)
            for u in before:
                self.order.remove((name, u))
                
    def add(self, name, val, after=None, before=None):
        if name in self.names:
            self.remove(name)
        self.names.append(name)
        self.name2val[name] = val
        if after is None and before is None:
            before = self.default_before
            after = self.default_after
        if after is not None:
            if not is_nonstr_iter(after):
                after = (after,)
            self.name2after[name] = after
            self.order += [(u, name) for u in after]
            self.req_after.add(name)
        if before is not None:
            if not is_nonstr_iter(before):
                before = (before,)
            self.name2before[name] = before
            self.order += [(name, o) for o in before]
            self.req_before.add(name)

    def sorted(self):
        order = [(self.first, self.last)]
        roots = []
        graph = {}
        names = [self.first, self.last]
        names.extend(self.names)

        for a, b in self.order:
            order.append((a, b))

        def add_node(node):
            if not node in graph:
                roots.append(node)
                graph[node] = [0] # 0 = number of arcs coming into this node

        def add_arc(fromnode, tonode):
            graph[fromnode].append(tonode)
            graph[tonode][0] += 1
            if tonode in roots:
                roots.remove(tonode)

        for name in names:
            add_node(name)

        has_before, has_after = set(), set()
        for a, b in order:
            if a in names and b in names: # deal with missing dependencies
                add_arc(a, b)
                has_before.add(a)
                has_after.add(b)

        if not self.req_before.issubset(has_before):
            raise ConfigurationError(
                'Unsatisfied before dependencies: %s'
                % (', '.join(sorted(self.req_before - has_before)))
            )
        if not self.req_after.issubset(has_after):
            raise ConfigurationError(
                'Unsatisfied after dependencies: %s'
                % (', '.join(sorted(self.req_after - has_after)))
            )

        sorted_names = []

        while roots:
            root = roots.pop(0)
            sorted_names.append(root)
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

        for name in sorted_names:
            if name in self.names:
                result.append((name, self.name2val[name]))

        return result

class CyclicDependencyError(Exception):
    def __init__(self, cycles):
        self.cycles = cycles

    def __str__(self):
        L = []
        cycles = self.cycles
        for cycle in cycles:
            dependent = cycle
            dependees = cycles[cycle]
            L.append('%r sorts before %r' % (dependent, dependees))
        msg = 'Implicit ordering cycle:' + '; '.join(L)
        return msg

class PredicateList(object):
    
    def __init__(self):
        self.sorter = TopologicalSorter()
        self.last_added = None

    def add(self, name, factory, weighs_more_than=None, weighs_less_than=None):
        # Predicates should be added to a predicate list in (presumed)
        # computation expense order.
        ## if weighs_more_than is None and weighs_less_than is None:
        ##     weighs_more_than = self.last_added or FIRST
        ##     weighs_less_than = LAST
        self.last_added = name
        self.sorter.add(name, factory, after=weighs_more_than,
                        before=weighs_less_than)

    def make(self, config, **kw):
        # Given a configurator and a list of keywords, a predicate list is
        # computed.  Elsewhere in the code, we evaluate predicates using a
        # generator expression.  All predicates associated with a view or
        # route must evaluate true for the view or route to "match" during a
        # request.  The fastest predicate should be evaluated first, then the
        # next fastest, and so on, as if one returns false, the remainder of
        # the predicates won't need to be evaluated.
        #
        # While we compute predicates, we also compute a predicate hash (aka
        # phash) that can be used by a caller to identify identical predicate
        # lists.
        ordered = self.sorter.sorted()
        phash = md5()
        weights = []
        preds = []
        for n, (name, predicate_factory) in enumerate(ordered):
            vals = kw.pop(name, None)
            if vals is None: # XXX should this be a sentinel other than None?
                continue
            if not isinstance(vals, predvalseq):
                vals = (vals,)
            for val in vals:
                pred = predicate_factory(val, config)
                hashes = pred.phash()
                if not is_nonstr_iter(hashes):
                    hashes = [hashes]
                for h in hashes:
                    phash.update(bytes_(h))
                weights.append(1 << n+1)
                preds.append(pred)
        if kw:
            raise ConfigurationError('Unknown predicate values: %r' % (kw,))
        # A "order" is computed for the predicate list.  An order is
        # a scoring.
        #
        # Each predicate is associated with a weight value.  The weight of a
        # predicate symbolizes the relative potential "importance" of the
        # predicate to all other predicates.  A larger weight indicates
        # greater importance.
        #
        # All weights for a given predicate list are bitwise ORed together
        # to create a "score"; this score is then subtracted from
        # MAX_ORDER and divided by an integer representing the number of
        # predicates+1 to determine the order.
        #
        # For views, the order represents the ordering in which a "multiview"
        # ( a collection of views that share the same context/request/name
        # triad but differ in other ways via predicates) will attempt to call
        # its set of views.  Views with lower orders will be tried first.
        # The intent is to a) ensure that views with more predicates are
        # always evaluated before views with fewer predicates and b) to
        # ensure a stable call ordering of views that share the same number
        # of predicates.  Views which do not have any predicates get an order
        # of MAX_ORDER, meaning that they will be tried very last.
        score = 0
        for bit in weights:
            score = score | bit
        order = (MAX_ORDER - score) / (len(preds) + 1)
        return order, preds, phash.hexdigest()

