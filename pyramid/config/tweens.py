from pyramid.interfaces import ITweens

from pyramid.exceptions import ConfigurationError
from pyramid.tweens import excview_tween_factory
from pyramid.tweens import Tweens
from pyramid.tweens import MAIN, INGRESS, EXCVIEW

from pyramid.config.util import action_method

class TweensConfiguratorMixin(object):
    @action_method
    def add_tween(self, tween_factory, alias=None, under=None, over=None):
        """
        Add a 'tween factory'.  A :term:`tween` (a contraction of 'between')
        is a bit of code that sits between the Pyramid router's main request
        handling function and the upstream WSGI component that uses
        :app:`Pyramid` as its 'app'.  Tweens are a feature that may be used
        by Pyramid framework extensions, to provide, for example,
        Pyramid-specific view timing support, bookkeeping code that examines
        exceptions before they are returned to the upstream WSGI application,
        or a variety of other features.  Tweens behave a bit like
        :term:`WSGI` 'middleware' but they have the benefit of running in a
        context in which they have access to the Pyramid :term:`application
        registry` as well as the Pyramid rendering machinery.

        .. note:: You can view the tween ordering configured into a given
                  Pyramid application by using the ``paster ptweens``
                  command.  See :ref:`displaying_tweens`.

        The ``tween_factory`` argument must be a :term:`dotted Python name`
        to a global object representing the tween factory.

        The ``alias`` argument, if it is not ``None``, should be a string.
        The string will represent a value that other callers of ``add_tween``
        may pass as an ``under`` and ``over`` argument instead of this
        tween's factory name.

        The ``under`` and ``over`` arguments allow the caller of
        ``add_tween`` to provide a hint about where in the tween chain this
        tween factory should be placed when an implicit tween chain is used.
        These hints are only used when an explicit tween chain is not used
        (when the ``pyramid.tweens`` configuration value is not set).
        Allowable values for ``under`` or ``over`` (or both) are:

        - ``None`` (the default).

        - A :term:`dotted Python name` to a tween factory: a string
          representing the dotted name of a tween factory added in a call to
          ``add_tween`` in the same configuration session.

        - A tween alias: a string representing the predicted value of
          ``alias`` in a separate call to ``add_tween`` in the same
          configuration session
        
        - One of the constants :attr:`pyramid.tweens.MAIN`,
          :attr:`pyramid.tweens.INGRESS`, or :attr:`pyramid.tweens.EXCVIEW`.

        - An iterable of any combination of the above. This allows the user
          to specify fallbacks if the desired tween is not included, as well
          as compatibility with multiple other tweens.
        
        ``under`` means 'closer to the main Pyramid application than',
        ``over`` means 'closer to the request ingress than'.

        For example, calling ``add_tween('myapp.tfactory',
        over=pyramid.tweens.MAIN)`` will attempt to place the tween factory
        represented by the dotted name ``myapp.tfactory`` directly 'above' (in
        ``paster ptweens`` order) the main Pyramid request handler.
        Likewise, calling ``add_tween('myapp.tfactory',
        over=pyramid.tweens.MAIN, under='someothertween')`` will attempt to
        place this tween factory 'above' the main handler but 'below' (a
        fictional) 'someothertween' tween factory (which was presumably added
        via ``add_tween('myapp.tfactory', alias='someothertween')``).

        If all options for ``under`` (or ``over``) cannot be found in the
        current configuration, it is an error. If some options are specified
        purely for compatibilty with other tweens, just add a fallback of
        MAIN or INGRESS. For example,
        ``under=('someothertween', 'someothertween2', INGRESS)``.
        This constraint will require the tween to be located under both the
        'someothertween' tween, the 'someothertween2' tween, and INGRESS. If
        any of these is not in the current configuration, this constraint will
        only organize itself based on the tweens that are present.

        Specifying neither ``over`` nor ``under`` is equivalent to specifying
        ``under=INGRESS``.

        Implicit tween ordering is obviously only best-effort.  Pyramid will
        attempt to present an implicit order of tweens as best it can, but
        the only surefire way to get any particular ordering is to use an
        explicit tween order.  A user may always override the implicit tween
        ordering by using an explicit ``pyramid.tweens`` configuration value
        setting.

        ``alias``, ``under``, and ``over`` arguments are ignored when an
        explicit tween chain is specified using the ``pyramid.tweens``
        configuration value.

        For more information, see :ref:`registering_tweens`.

        .. note:: This feature is new as of Pyramid 1.2.
        """
        return self._add_tween(tween_factory, alias=alias, under=under,
                               over=over, explicit=False)

    def _add_tween(self, tween_factory, alias=None, under=None, over=None,
                   explicit=False):

        if not isinstance(tween_factory, basestring):
            raise ConfigurationError(
                'The "tween_factory" argument to add_tween must be a '
                'dotted name to a globally importable object, not %r' %
                tween_factory)

        name = tween_factory
        tween_factory = self.maybe_dotted(tween_factory)

        def is_string_or_iterable(v):
            if isinstance(v, basestring):
                return True
            if hasattr(v, '__iter__'):
                return True

        for t, p in [('over', over), ('under', under)]:
            if p is not None:
                if not is_string_or_iterable(p):
                    raise ConfigurationError(
                        '"%s" must be a string or iterable, not %s' % (t, p))

        if alias in (MAIN, INGRESS):
            raise ConfigurationError('%s is a reserved tween name' % alias)

        if over is INGRESS or hasattr(over, '__iter__') and INGRESS in over:
            raise ConfigurationError('%s cannot be over INGRESS' % name)

        if under is MAIN or hasattr(under, '__iter__') and MAIN in under:
            raise ConfigurationError('%s cannot be under MAIN' % name)

        registry = self.registry
        tweens = registry.queryUtility(ITweens)
        if tweens is None:
            tweens = Tweens()
            registry.registerUtility(tweens, ITweens)
            tweens.add_implicit('pyramid.tweens.excview_tween_factory',
                                excview_tween_factory, alias=EXCVIEW,
                                over=MAIN)
        if explicit:
            tweens.add_explicit(name, tween_factory)
        else:
            tweens.add_implicit(name, tween_factory, alias=alias, under=under,
                                over=over)
        self.action(('tween', name, explicit))
        if not explicit and alias is not None:
            self.action(('tween', alias, explicit))

    @action_method
    def add_request_handler(self, factory, name): # pragma: no cover
        # XXX bw compat for debugtoolbar
        return self._add_tween(factory, explicit=False)
        
