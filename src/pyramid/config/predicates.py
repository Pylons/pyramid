from hashlib import md5
from webob.acceptparse import Accept

from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import PHASE1_CONFIG, IPredicateList
from pyramid.predicates import Notted
from pyramid.registry import predvalseq
from pyramid.util import TopologicalSorter, bytes_, is_nonstr_iter

MAX_ORDER = 1 << 30
DEFAULT_PHASH = md5().hexdigest()


class PredicateConfiguratorMixin:
    def get_predlist(self, name):
        predlist = self.registry.queryUtility(IPredicateList, name=name)
        if predlist is None:
            predlist = PredicateList()
            self.registry.registerUtility(predlist, IPredicateList, name=name)
        return predlist

    def _add_predicate(
        self, type, name, factory, weighs_more_than=None, weighs_less_than=None
    ):
        factory = self.maybe_dotted(factory)
        discriminator = ('%s option' % type, name)
        intr = self.introspectable(
            '%s predicates' % type,
            discriminator,
            '%s predicate named %s' % (type, name),
            '%s predicate' % type,
        )
        intr['name'] = name
        intr['factory'] = factory
        intr['weighs_more_than'] = weighs_more_than
        intr['weighs_less_than'] = weighs_less_than

        def register():
            predlist = self.get_predlist(type)
            predlist.add(
                name,
                factory,
                weighs_more_than=weighs_more_than,
                weighs_less_than=weighs_less_than,
            )

        self.action(
            discriminator,
            register,
            introspectables=(intr,),
            order=PHASE1_CONFIG,
        )  # must be registered early


class not_:
    """

    You can invert the meaning of any predicate value by wrapping it in a call
    to :class:`pyramid.config.not_`.

    .. code-block:: python
       :linenos:

       from pyramid.config import not_

       config.add_view(
           'mypackage.views.my_view',
           route_name='ok',
           request_method=not_('POST')
           )

    The above example will ensure that the view is called if the request method
    is *not* ``POST``, at least if no other view is more specific.

    This technique of wrapping a predicate value in ``not_`` can be used
    anywhere predicate values are accepted:

    - :meth:`pyramid.config.Configurator.add_view`

    - :meth:`pyramid.config.Configurator.add_route`

    - :meth:`pyramid.config.Configurator.add_subscriber`

    - :meth:`pyramid.view.view_config`

    - :meth:`pyramid.events.subscriber`

    .. versionadded:: 1.5
    """

    def __init__(self, value):
        self.value = value


# under = after
# over = before


class PredicateInfo:
    def __init__(self, package, registry, settings, maybe_dotted):
        self.package = package
        self.registry = registry
        self.settings = settings
        self.maybe_dotted = maybe_dotted


class PredicateList:
    def __init__(self):
        self.sorter = TopologicalSorter()
        self.last_added = None

    def add(self, name, factory, weighs_more_than=None, weighs_less_than=None):
        # Predicates should be added to a predicate list in (presumed)
        # computation expense order.
        # if weighs_more_than is None and weighs_less_than is None:
        #     weighs_more_than = self.last_added or FIRST
        #     weighs_less_than = LAST
        self.last_added = name
        self.sorter.add(
            name, factory, after=weighs_more_than, before=weighs_less_than
        )

    def names(self):
        # Return the list of valid predicate names.
        return self.sorter.names

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
        info = PredicateInfo(
            package=config.package,
            registry=config.registry,
            settings=config.get_settings(),
            maybe_dotted=config.maybe_dotted,
        )
        for n, (name, predicate_factory) in enumerate(ordered):
            vals = kw.pop(name, None)
            if vals is None:  # XXX should this be a sentinel other than None?
                continue
            if not isinstance(vals, predvalseq):
                vals = (vals,)
            for val in vals:
                realval = val
                notted = False
                if isinstance(val, not_):
                    realval = val.value
                    notted = True
                pred = predicate_factory(realval, info)
                if notted:
                    pred = Notted(pred)
                hashes = pred.phash()
                if not is_nonstr_iter(hashes):
                    hashes = [hashes]
                for h in hashes:
                    phash.update(bytes_(h))
                weights.append(1 << n + 1)
                preds.append(pred)
        if kw:
            from difflib import get_close_matches

            closest = []
            names = [name for name, _ in ordered]
            for name in kw:
                closest.extend(get_close_matches(name, names, 3))

            raise ConfigurationError(
                'Unknown predicate values: %r (did you mean %s)'
                % (kw, ','.join(closest))
            )
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
        order = (MAX_ORDER - score) // (len(preds) + 1)

        return order, preds, phash.hexdigest()


def normalize_accept_offer(offer):
    return str(Accept.parse_offer(offer))


def sort_accept_offers(offers, order=None):
    """
    Sort a list of offers by preference.

    For a given ``type/subtype`` category of offers, this algorithm will
    always sort offers with params higher than the bare offer.

    :param offers: A list of offers to be sorted.
    :param order: A weighted list of offers where items closer to the start of
                  the list will be a preferred over items closer to the end.
    :return: A list of offers sorted first by specificity (higher to lower)
             then by ``order``.

    """
    if order is None:
        order = []

    max_weight = len(offers)

    def find_order_index(value, default=None):
        return next((i for i, x in enumerate(order) if x == value), default)

    def offer_sort_key(value):
        """
        (type_weight, params_weight)

        type_weight:
            - index of specific ``type/subtype`` in order list
            - ``max_weight * 2`` if no match is found

        params_weight:
            - index of specific ``type/subtype;params`` in order list
            - ``max_weight`` if not found
            - ``max_weight + 1`` if no params at all

        """
        parsed = Accept.parse_offer(value)

        type_w = find_order_index(
            parsed.type + '/' + parsed.subtype, max_weight
        )

        if parsed.params:
            param_w = find_order_index(value, max_weight)

        else:
            param_w = max_weight + 1

        return (type_w, param_w)

    return sorted(offers, key=offer_sort_key)
