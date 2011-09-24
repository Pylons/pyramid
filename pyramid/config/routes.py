import warnings

from pyramid.interfaces import IRequest
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IRoutesMapper
from pyramid.interfaces import PHASE2_CONFIG

from pyramid.exceptions import ConfigurationError
from pyramid.request import route_request_iface
from pyramid.urldispatch import RoutesMapper

from pyramid.config.util import action_method
from pyramid.config.util import make_predicates

class RoutesConfiguratorMixin(object):
    @action_method
    def add_route(self,
                  name,
                  pattern=None,
                  view=None,
                  view_for=None,
                  permission=None,
                  factory=None,
                  for_=None,
                  header=None,
                  xhr=False,
                  accept=None,
                  path_info=None,
                  request_method=None,
                  request_param=None,
                  traverse=None,
                  custom_predicates=(),
                  view_permission=None,
                  renderer=None,
                  view_renderer=None,
                  view_context=None,
                  view_attr=None,
                  use_global_views=False,
                  path=None,
                  pregenerator=None,
                  static=False,
                  ):
        """ Add a :term:`route configuration` to the current
        configuration state, as well as possibly a :term:`view
        configuration` to be used to specify a :term:`view callable`
        that will be invoked when this route matches.  The arguments
        to this method are divided into *predicate*, *non-predicate*,
        and *view-related* types.  :term:`Route predicate` arguments
        narrow the circumstances in which a route will be match a
        request; non-predicate arguments are informational.

        Non-Predicate Arguments

        name

          The name of the route, e.g. ``myroute``.  This attribute is
          required.  It must be unique among all defined routes in a given
          application.

        factory

          A Python object (often a function or a class) or a :term:`dotted
          Python name` which refers to the same object that will generate a
          :app:`Pyramid` root resource object when this route matches. For
          example, ``mypackage.resources.MyFactory``.  If this argument is
          not specified, a default root factory will be used.  See
          :ref:`the_resource_tree` for more information about root factories.

        traverse

          If you would like to cause the :term:`context` to be
          something other than the :term:`root` object when this route
          matches, you can spell a traversal pattern as the
          ``traverse`` argument.  This traversal pattern will be used
          as the traversal path: traversal will begin at the root
          object implied by this route (either the global root, or the
          object returned by the ``factory`` associated with this
          route).

          The syntax of the ``traverse`` argument is the same as it is
          for ``pattern``. For example, if the ``pattern`` provided to
          ``add_route`` is ``articles/{article}/edit``, and the
          ``traverse`` argument provided to ``add_route`` is
          ``/{article}``, when a request comes in that causes the route
          to match in such a way that the ``article`` match value is
          '1' (when the request URI is ``/articles/1/edit``), the
          traversal path will be generated as ``/1``.  This means that
          the root object's ``__getitem__`` will be called with the
          name ``1`` during the traversal phase.  If the ``1`` object
          exists, it will become the :term:`context` of the request.
          :ref:`traversal_chapter` has more information about
          traversal.

          If the traversal path contains segment marker names which
          are not present in the ``pattern`` argument, a runtime error
          will occur.  The ``traverse`` pattern should not contain
          segment markers that do not exist in the ``pattern``
          argument.

          A similar combining of routing and traversal is available
          when a route is matched which contains a ``*traverse``
          remainder marker in its pattern (see
          :ref:`using_traverse_in_a_route_pattern`).  The ``traverse``
          argument to add_route allows you to associate route patterns
          with an arbitrary traversal path without using a a
          ``*traverse`` remainder marker; instead you can use other
          match information.

          Note that the ``traverse`` argument to ``add_route`` is
          ignored when attached to a route that has a ``*traverse``
          remainder marker in its pattern.

        pregenerator

           This option should be a callable object that implements the
           :class:`pyramid.interfaces.IRoutePregenerator` interface.  A
           :term:`pregenerator` is a callable called by the
           :meth:`pyramid.request.Request.route_url` function to augment or
           replace the arguments it is passed when generating a URL for the
           route.  This is a feature not often used directly by applications,
           it is meant to be hooked by frameworks that use :app:`Pyramid` as
           a base.

        use_global_views

          When a request matches this route, and view lookup cannot
          find a view which has a ``route_name`` predicate argument
          that matches the route, try to fall back to using a view
          that otherwise matches the context, request, and view name
          (but which does not match the route_name predicate).

        static

          If ``static`` is ``True``, this route will never match an incoming
          request; it will only be useful for URL generation.  By default,
          ``static`` is ``False``.  See :ref:`static_route_narr`.

          .. note:: New in :app:`Pyramid` 1.1.

        Predicate Arguments

        pattern

          The pattern of the route e.g. ``ideas/{idea}``.  This
          argument is required.  See :ref:`route_pattern_syntax`
          for information about the syntax of route patterns.  If the
          pattern doesn't match the current URL, route matching
          continues.

          .. note::

             For backwards compatibility purposes (as of :app:`Pyramid` 1.0), a
             ``path`` keyword argument passed to this function will be used to
             represent the pattern value if the ``pattern`` argument is
             ``None``.  If both ``path`` and ``pattern`` are passed, ``pattern``
             wins.

        xhr

          This value should be either ``True`` or ``False``.  If this
          value is specified and is ``True``, the :term:`request` must
          possess an ``HTTP_X_REQUESTED_WITH`` (aka
          ``X-Requested-With``) header for this route to match.  This
          is useful for detecting AJAX requests issued from jQuery,
          Prototype and other Javascript libraries.  If this predicate
          returns ``False``, route matching continues.

        request_method

          A string representing an HTTP method name, e.g. ``GET``, ``POST``,
          ``HEAD``, ``DELETE``, ``PUT`` or a tuple of elements containing
          HTTP method names.  If this argument is not specified, this route
          will match if the request has *any* request method.  If this
          predicate returns ``False``, route matching continues.

          .. note:: The ability to pass a tuple of items as
                   ``request_method`` is new as of Pyramid 1.2.  Previous
                   versions allowed only a string.

        path_info

          This value represents a regular expression pattern that will
          be tested against the ``PATH_INFO`` WSGI environment
          variable.  If the regex matches, this predicate will return
          ``True``.  If this predicate returns ``False``, route
          matching continues.

        request_param

          This value can be any string.  A view declaration with this
          argument ensures that the associated route will only match
          when the request has a key in the ``request.params``
          dictionary (an HTTP ``GET`` or ``POST`` variable) that has a
          name which matches the supplied value.  If the value
          supplied as the argument has a ``=`` sign in it,
          e.g. ``request_param="foo=123"``, then the key
          (``foo``) must both exist in the ``request.params`` dictionary, and
          the value must match the right hand side of the expression (``123``)
          for the route to "match" the current request.  If this predicate
          returns ``False``, route matching continues.

        header

          This argument represents an HTTP header name or a header
          name/value pair.  If the argument contains a ``:`` (colon),
          it will be considered a name/value pair
          (e.g. ``User-Agent:Mozilla/.*`` or ``Host:localhost``).  If
          the value contains a colon, the value portion should be a
          regular expression.  If the value does not contain a colon,
          the entire value will be considered to be the header name
          (e.g. ``If-Modified-Since``).  If the value evaluates to a
          header name only without a value, the header specified by
          the name must be present in the request for this predicate
          to be true.  If the value evaluates to a header name/value
          pair, the header specified by the name must be present in
          the request *and* the regular expression specified as the
          value must match the header value.  Whether or not the value
          represents a header name or a header name/value pair, the
          case of the header name is not significant.  If this
          predicate returns ``False``, route matching continues.

        accept

          This value represents a match query for one or more
          mimetypes in the ``Accept`` HTTP request header.  If this
          value is specified, it must be in one of the following
          forms: a mimetype match token in the form ``text/plain``, a
          wildcard mimetype match token in the form ``text/*`` or a
          match-all wildcard mimetype match token in the form ``*/*``.
          If any of the forms matches the ``Accept`` header of the
          request, this predicate will be true.  If this predicate
          returns ``False``, route matching continues.

        custom_predicates

          This value should be a sequence of references to custom
          predicate callables.  Use custom predicates when no set of
          predefined predicates does what you need.  Custom predicates
          can be combined with predefined predicates as necessary.
          Each custom predicate callable should accept two arguments:
          ``info`` and ``request`` and should return either ``True``
          or ``False`` after doing arbitrary evaluation of the info
          and/or the request.  If all custom and non-custom predicate
          callables return ``True`` the associated route will be
          considered viable for a given request.  If any predicate
          callable returns ``False``, route matching continues.  Note
          that the value ``info`` passed to a custom route predicate
          is a dictionary containing matching information; see
          :ref:`custom_route_predicates` for more information about
          ``info``.

        View-Related Arguments

        .. warning::

           The arguments described below have been deprecated as of
           :app:`Pyramid` 1.1. *Do not use these for new development; they
           should only be used to support older code bases which depend upon
           them.* Use a separate call to
           :meth:`pyramid.config.Configurator.add_view` to associate a view
           with a route using the ``route_name`` argument.

        view

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          A Python object or :term:`dotted Python name` to the same
          object that will be used as a view callable when this route
          matches. e.g. ``mypackage.views.my_view``.

        view_context

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          A class or an :term:`interface` or :term:`dotted Python
          name` to the same object which the :term:`context` of the
          view should match for the view named by the route to be
          used.  This argument is only useful if the ``view``
          attribute is used.  If this attribute is not specified, the
          default (``None``) will be used.

          If the ``view`` argument is not provided, this argument has
          no effect.

          This attribute can also be spelled as ``for_`` or ``view_for``.

        view_permission

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          The permission name required to invoke the view associated
          with this route.  e.g. ``edit``. (see
          :ref:`using_security_with_urldispatch` for more information
          about permissions).

          If the ``view`` attribute is not provided, this argument has
          no effect.

          This argument can also be spelled as ``permission``.

        view_renderer

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          This is either a single string term (e.g. ``json``) or a
          string implying a path or :term:`asset specification`
          (e.g. ``templates/views.pt``).  If the renderer value is a
          single term (does not contain a dot ``.``), the specified
          term will be used to look up a renderer implementation, and
          that renderer implementation will be used to construct a
          response from the view return value.  If the renderer term
          contains a dot (``.``), the specified term will be treated
          as a path, and the filename extension of the last element in
          the path will be used to look up the renderer
          implementation, which will be passed the full path.  The
          renderer implementation will be used to construct a response
          from the view return value.  See
          :ref:`views_which_use_a_renderer` for more information.

          If the ``view`` argument is not provided, this argument has
          no effect.

          This argument can also be spelled as ``renderer``.

        view_attr

          .. warning:: Deprecated as of :app:`Pyramid` 1.1.

          The view machinery defaults to using the ``__call__`` method
          of the view callable (or the function itself, if the view
          callable is a function) to obtain a response dictionary.
          The ``attr`` value allows you to vary the method attribute
          used to obtain the response.  For example, if your view was
          a class, and the class has a method named ``index`` and you
          wanted to use this method instead of the class' ``__call__``
          method to return the response, you'd say ``attr="index"`` in
          the view configuration for the view.  This is
          most useful when the view definition is a class.

          If the ``view`` argument is not provided, this argument has no
          effect.

        """
        # these are route predicates; if they do not match, the next route
        # in the routelist will be tried
        ignored, predicates, ignored = make_predicates(
            xhr=xhr,
            request_method=request_method,
            path_info=path_info,
            request_param=request_param,
            header=header,
            accept=accept,
            traverse=traverse,
            custom=custom_predicates
            )

        factory = self.maybe_dotted(factory)
        if pattern is None:
            pattern = path
        if pattern is None:
            raise ConfigurationError('"pattern" argument may not be None')

        if self.route_prefix:
            pattern = self.route_prefix.rstrip('/') + '/' + pattern.lstrip('/')

        mapper = self.get_routes_mapper()

        def register_route_request_iface():
            request_iface = self.registry.queryUtility(IRouteRequest, name=name)
            if request_iface is None:
                if use_global_views:
                    bases = (IRequest,)
                else:
                    bases = ()
                request_iface = route_request_iface(name, bases)
                self.registry.registerUtility(
                    request_iface, IRouteRequest, name=name)

        def register_connect():
            return mapper.connect(name, pattern, factory, predicates=predicates,
                                  pregenerator=pregenerator, static=static)


        # We have to connect routes in the order they were provided;
        # we can't use a phase to do that, because when the actions are
        # sorted, actions in the same phase lose relative ordering
        self.action(('route-connect', name), register_connect)

        # But IRouteRequest interfaces must be registered before we begin to
        # process view registrations (in phase 3)
        self.action(('route', name), register_route_request_iface,
                    order=PHASE2_CONFIG)

        # deprecated adding views from add_route; must come after
        # route registration for purposes of autocommit ordering
        if any([view, view_context, view_permission, view_renderer,
                view_for, for_, permission, renderer, view_attr]):
            self._add_view_from_route(
                route_name=name,
                view=view,
                permission=view_permission or permission,
                context=view_context or view_for or for_,
                renderer=view_renderer or renderer,
                attr=view_attr,
            )

    def get_routes_mapper(self):
        """ Return the :term:`routes mapper` object associated with
        this configurator's :term:`registry`."""
        mapper = self.registry.queryUtility(IRoutesMapper)
        if mapper is None:
            mapper = RoutesMapper()
            self.registry.registerUtility(mapper, IRoutesMapper)
        return mapper

    def _add_view_from_route(self,
                             route_name,
                             view,
                             context,
                             permission,
                             renderer,
                             attr,
                             ):
        if view:
            self.add_view(
                permission=permission,
                context=context,
                view=view,
                name='',
                route_name=route_name,
                renderer=renderer,
                attr=attr,
                )
        else:
            # prevent mistakes due to misunderstanding of how hybrid calls to
            # add_route and add_view interact
            if attr:
                raise ConfigurationError(
                    'view_attr argument not permitted without view '
                    'argument')
            if context:
                raise ConfigurationError(
                    'view_context argument not permitted without view '
                    'argument')
            if permission:
                raise ConfigurationError(
                    'view_permission argument not permitted without view '
                    'argument')
            if renderer:
                raise ConfigurationError(
                    'view_renderer argument not permitted without '
                    'view argument')

        warnings.warn(
            'Passing view-related arguments to add_route() is deprecated as of '
            'Pyramid 1.1.  Use add_view() to associate a view with a route '
            'instead.  See "Deprecations" in "What\'s New in Pyramid 1.1" '
            'within the general Pyramid documentation for further details.',
            DeprecationWarning,
            4)

