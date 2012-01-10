""" Utility functions for dealing with URLs in pyramid """

import os

from repoze.lru import lru_cache

from pyramid.interfaces import (
    IContextURL,
    IRoutesMapper,
    IStaticURLInfo,
    )

from pyramid.compat import (
    native_,
    text_type,
    )
from pyramid.encode import urlencode
from pyramid.path import caller_package
from pyramid.threadlocal import get_current_registry

from pyramid.traversal import (
    TraversalContextURL,
    quote_path_segment,
    )

class URLMethodsMixin(object):
    """ Request methods mixin for BaseRequest having to do with URL
    generation """

    def route_url(self, route_name, *elements, **kw):
        """Generates a fully qualified URL for a named :app:`Pyramid`
        :term:`route configuration`.

        Use the route's ``name`` as the first positional argument.
        Additional positional arguments (``*elements``) are appended to the
        URL as path segments after it is generated.

        Use keyword arguments to supply values which match any dynamic
        path elements in the route definition.  Raises a :exc:`KeyError`
        exception if the URL cannot be generated for any reason (not
        enough arguments, for example).

        For example, if you've defined a route named "foobar" with the path
        ``{foo}/{bar}/*traverse``::

            request.route_url('foobar',
                               foo='1')             => <KeyError exception>
            request.route_url('foobar',
                               foo='1',
                               bar='2')             => <KeyError exception>
            request.route_url('foobar',
                               foo='1',
                               bar='2',
                               traverse=('a','b'))  => http://e.com/1/2/a/b
            request.route_url('foobar',
                               foo='1',
                               bar='2',
                               traverse='/a/b')     => http://e.com/1/2/a/b

        Values replacing ``:segment`` arguments can be passed as strings
        or Unicode objects.  They will be encoded to UTF-8 and URL-quoted
        before being placed into the generated URL.

        Values replacing ``*remainder`` arguments can be passed as strings
        *or* tuples of Unicode/string values.  If a tuple is passed as a
        ``*remainder`` replacement value, its values are URL-quoted and
        encoded to UTF-8.  The resulting strings are joined with slashes
        and rendered into the URL.  If a string is passed as a
        ``*remainder`` replacement value, it is tacked on to the URL
        after being URL-quoted-except-for-embedded-slashes.

        If a keyword argument ``_query`` is present, it will be used to
        compose a query string that will be tacked on to the end of the
        URL.  The value of ``_query`` must be a sequence of two-tuples
        *or* a data structure with an ``.items()`` method that returns a
        sequence of two-tuples (presumably a dictionary).  This data
        structure will be turned into a query string per the documentation
        of :func:`pyramid.encode.urlencode` function.  After the query
        data is turned into a query string, a leading ``?`` is prepended,
        and the resulting string is appended to the generated URL.

        .. note::

           Python data structures that are passed as ``_query`` which are
           sequences or dictionaries are turned into a string under the same
           rules as when run through :func:`urllib.urlencode` with the ``doseq``
           argument equal to ``True``.  This means that sequences can be passed
           as values, and a k=v pair will be placed into the query string for
           each value.

        If a keyword argument ``_anchor`` is present, its string
        representation will be used as a named anchor in the generated URL
        (e.g. if ``_anchor`` is passed as ``foo`` and the route URL is
        ``http://example.com/route/url``, the resulting generated URL will
        be ``http://example.com/route/url#foo``).

        .. note::

           If ``_anchor`` is passed as a string, it should be UTF-8 encoded. If
           ``_anchor`` is passed as a Unicode object, it will be converted to
           UTF-8 before being appended to the URL.  The anchor value is not
           quoted in any way before being appended to the generated URL.

        If both ``_anchor`` and ``_query`` are specified, the anchor
        element will always follow the query element,
        e.g. ``http://example.com?foo=1#bar``.

        If a keyword ``_app_url`` is present, it will be used as the
        protocol/hostname/port/leading path prefix of the generated URL.
        For example, using an ``_app_url`` of
        ``http://example.com:8080/foo`` would cause the URL
        ``http://example.com:8080/foo/fleeb/flub`` to be returned from
        this function if the expansion of the route pattern associated
        with the ``route_name`` expanded to ``/fleeb/flub``.  If
        ``_app_url`` is not specified, the result of
        ``request.application_url`` will be used as the prefix (the
        default).

        This function raises a :exc:`KeyError` if the URL cannot be
        generated due to missing replacement names.  Extra replacement
        names are ignored.

        If the route object which matches the ``route_name`` argument has
        a :term:`pregenerator`, the ``*elements`` and ``**kw`` arguments
        arguments passed to this function might be augmented or changed.
        """
        try:
            reg = self.registry
        except AttributeError:
            reg = get_current_registry() # b/c
        mapper = reg.getUtility(IRoutesMapper)
        route = mapper.get_route(route_name)

        if route is None:
            raise KeyError('No such route named %s' % route_name)

        if route.pregenerator is not None:
            elements, kw = route.pregenerator(self, elements, kw)

        anchor = ''
        qs = ''
        app_url = None

        if '_query' in kw:
            qs = '?' + urlencode(kw.pop('_query'), doseq=True)

        if '_anchor' in kw:
            anchor = kw.pop('_anchor')
            anchor = native_(anchor, 'utf-8')
            anchor = '#' + anchor

        if '_app_url' in kw:
            app_url = kw.pop('_app_url')

        path = route.generate(kw) # raises KeyError if generate fails

        if elements:
            suffix = _join_elements(elements)
            if not path.endswith('/'):
                suffix = '/' + suffix
        else:
            suffix = ''

        if app_url is None:
            # we only defer lookup of application_url until here because
            # it's somewhat expensive; we won't need to do it if we've
            # been passed _app_url
            app_url = self.application_url

        return app_url + path + suffix + qs + anchor

    def route_path(self, route_name, *elements, **kw):
        """
        Generates a path (aka a 'relative URL', a URL minus the host, scheme,
        and port) for a named :app:`Pyramid` :term:`route configuration`.

        This function accepts the same argument as
        :meth:`pyramid.request.Request.route_url` and performs the same duty.
        It just omits the host, port, and scheme information in the return
        value; only the script_name, path, query parameters, and anchor data
        are present in the returned string.

        For example, if you've defined a route named 'foobar' with the path
        ``/{foo}/{bar}``, this call to ``route_path``::

            request.route_path('foobar', foo='1', bar='2')

        Will return the string ``/1/2``.

        .. note::

           Calling ``request.route_path('route')`` is the same as calling
           ``request.route_url('route', _app_url=request.script_name)``.
           :meth:`pyramid.request.Request.route_path` is, in fact,
           implemented in terms of :meth:`pyramid.request.Request.route_url`
           in just this way. As a result, any ``_app_url`` passed within the
           ``**kw`` values to ``route_path`` will be ignored.
        """
        kw['_app_url'] = self.script_name
        return self.route_url(route_name, *elements, **kw)

    def resource_url(self, resource, *elements, **kw):
        """

        Generate a string representing the absolute URL of the
        :term:`resource` object based on the ``wsgi.url_scheme``,
        ``HTTP_HOST`` or ``SERVER_NAME`` in the request, plus any
        ``SCRIPT_NAME``.  The overall result of this method is always a
        UTF-8 encoded string (never Unicode).

        Examples::

            request.resource_url(resource) =>

                                       http://example.com/

            request.resource_url(resource, 'a.html') =>

                                       http://example.com/a.html

            request.resource_url(resource, 'a.html', query={'q':'1'}) =>

                                       http://example.com/a.html?q=1

            request.resource_url(resource, 'a.html', anchor='abc') =>

                                       http://example.com/a.html#abc

        Any positional arguments passed in as ``elements`` must be strings
        Unicode objects, or integer objects.  These will be joined by slashes
        and appended to the generated resource URL.  Each of the elements
        passed in is URL-quoted before being appended; if any element is
        Unicode, it will converted to a UTF-8 bytestring before being
        URL-quoted. If any element is an integer, it will be converted to its
        string representation before being URL-quoted.

        .. warning:: if no ``elements`` arguments are specified, the resource
                     URL will end with a trailing slash.  If any
                     ``elements`` are used, the generated URL will *not*
                     end in trailing a slash.

        If a keyword argument ``query`` is present, it will be used to
        compose a query string that will be tacked on to the end of the URL.
        The value of ``query`` must be a sequence of two-tuples *or* a data
        structure with an ``.items()`` method that returns a sequence of
        two-tuples (presumably a dictionary).  This data structure will be
        turned into a query string per the documentation of
        ``pyramid.url.urlencode`` function.  After the query data is turned
        into a query string, a leading ``?`` is prepended, and the resulting
        string is appended to the generated URL.

        .. note::

           Python data structures that are passed as ``query`` which are
           sequences or dictionaries are turned into a string under the same
           rules as when run through :func:`urllib.urlencode` with the ``doseq``
           argument equal to ``True``.  This means that sequences can be passed
           as values, and a k=v pair will be placed into the query string for
           each value.

        If a keyword argument ``anchor`` is present, its string
        representation will be used as a named anchor in the generated URL
        (e.g. if ``anchor`` is passed as ``foo`` and the resource URL is
        ``http://example.com/resource/url``, the resulting generated URL will
        be ``http://example.com/resource/url#foo``).

        .. note::

           If ``anchor`` is passed as a string, it should be UTF-8 encoded. If
           ``anchor`` is passed as a Unicode object, it will be converted to
           UTF-8 before being appended to the URL.  The anchor value is not
           quoted in any way before being appended to the generated URL.

        If both ``anchor`` and ``query`` are specified, the anchor element
        will always follow the query element,
        e.g. ``http://example.com?foo=1#bar``.

        If the ``resource`` passed in has a ``__resource_url__`` method, it
        will be used to generate the URL (scheme, host, port, path) that for
        the base resource which is operated upon by this function.  See also
        :ref:`overriding_resource_url_generation`.

        .. note::

           If the :term:`resource` used is the result of a :term:`traversal`, it
           must be :term:`location`-aware.  The resource can also be the context
           of a :term:`URL dispatch`; contexts found this way do not need to be
           location-aware.

        .. note::

           If a 'virtual root path' is present in the request environment (the
           value of the WSGI environ key ``HTTP_X_VHM_ROOT``), and the resource
           was obtained via :term:`traversal`, the URL path will not include the
           virtual root prefix (it will be stripped off the left hand side of
           the generated URL).

        .. note::

           For backwards compatibility purposes, this method is also
           aliased as the ``model_url`` method of request.
        """
        try:
            reg = self.registry
        except AttributeError:
            reg = get_current_registry() # b/c

        context_url = reg.queryMultiAdapter((resource, self), IContextURL)
        if context_url is None:
            context_url = TraversalContextURL(resource, self)
        resource_url = context_url()

        qs = ''
        anchor = ''

        if 'query' in kw:
            qs = '?' + urlencode(kw['query'], doseq=True)

        if 'anchor' in kw:
            anchor = kw['anchor']
            if isinstance(anchor, text_type):
                anchor = native_(anchor, 'utf-8')
            anchor = '#' + anchor

        if elements:
            suffix = _join_elements(elements)
        else:
            suffix = ''

        return resource_url + suffix + qs + anchor

    model_url = resource_url # b/w compat forever

    def static_url(self, path, **kw):
        """
        Generates a fully qualified URL for a static :term:`asset`.
        The asset must live within a location defined via the
        :meth:`pyramid.config.Configurator.add_static_view`
        :term:`configuration declaration` (see :ref:`static_assets_section`).

        Example::

            request.static_url('mypackage:static/foo.css') =>

                                    http://example.com/static/foo.css


        The ``path`` argument points at a file or directory on disk which
        a URL should be generated for.  The ``path`` may be either a
        relative path (e.g. ``static/foo.css``) or an absolute path (e.g.
        ``/abspath/to/static/foo.css``) or a :term:`asset specification`
        (e.g. ``mypackage:static/foo.css``).

        The purpose of the ``**kw`` argument is the same as the purpose of
        the :meth:`pyramid.request.Request.route_url` ``**kw`` argument.  See
        the documentation for that function to understand the arguments which
        you can provide to it.  However, typically, you don't need to pass
        anything as ``*kw`` when generating a static asset URL.

        This function raises a :exc:`ValueError` if a static view
        definition cannot be found which matches the path specification.

        """
        if not os.path.isabs(path):
            if not ':' in path:
                # if it's not a package:relative/name and it's not an
                # /absolute/path it's a relative/path; this means its relative
                # to the package in which the caller's module is defined.
                package = caller_package()
                path = '%s:%s' % (package.__name__, path)

        try:
            reg = self.registry
        except AttributeError:
            reg = get_current_registry() # b/c

        info = reg.queryUtility(IStaticURLInfo)
        if info is None:
            raise ValueError('No static URL definition matching %s' % path)

        return info.generate(path, self, **kw)

    def static_path(self, path, **kw):
        """
        Generates a path (aka a 'relative URL', a URL minus the host, scheme,
        and port) for a static resource.

        This function accepts the same argument as
        :meth:`pyramid.request.Request.static_url` and performs the
        same duty.  It just omits the host, port, and scheme information in
        the return value; only the script_name, path, query parameters, and
        anchor data are present in the returned string.

        Example::

            request.static_path('mypackage:static/foo.css') =>

                                    /static/foo.css

        .. note::

           Calling ``request.static_path(apath)`` is the same as calling
           ``request.static_url(apath, _app_url=request.script_name)``.
           :meth:`pyramid.request.Request.static_path` is, in fact, implemented
           in terms of `:meth:`pyramid.request.Request.static_url` in just this
           way. As a result, any ``_app_url`` passed within the ``**kw`` values
           to ``static_path`` will be ignored.
        """
        if not os.path.isabs(path):
            if not ':' in path:
                # if it's not a package:relative/name and it's not an
                # /absolute/path it's a relative/path; this means its relative
                # to the package in which the caller's module is defined.
                package = caller_package()
                path = '%s:%s' % (package.__name__, path)

        kw['_app_url'] = self.script_name
        return self.static_url(path, **kw)

    def current_route_url(self, *elements, **kw):
        """
        Generates a fully qualified URL for a named :app:`Pyramid`
        :term:`route configuration` based on the 'current route'.

        This function supplements
        :meth:`pyramid.request.Request.route_url`. It presents an easy way to
        generate a URL for the 'current route' (defined as the route which
        matched when the request was generated).

        The arguments to this method have the same meaning as those with the
        same names passed to :meth:`pyramid.request.Request.route_url`.  It
        also understands an extra argument which ``route_url`` does not named
        ``_route_name``.

        The route name used to generate a URL is taken from either the
        ``_route_name`` keyword argument or the name of the route which is
        currently associated with the request if ``_route_name`` was not
        passed.  Keys and values from the current request :term:`matchdict`
        are combined with the ``kw`` arguments to form a set of defaults
        named ``newkw``.  Then ``request.route_url(route_name, *elements,
        **newkw)`` is called, returning a URL.

        Examples follow.

        If the 'current route' has the route pattern ``/foo/{page}`` and the
        current url path is ``/foo/1`` , the matchdict will be
        ``{'page':'1'}``.  The result of ``request.current_route_url()`` in
        this situation will be ``/foo/1``.

        If the 'current route' has the route pattern ``/foo/{page}`` and the
        current url path is ``/foo/1``, the matchdict will be
        ``{'page':'1'}``.  The result of
        ``request.current_route_url(page='2')`` in this situation will be
        ``/foo/2``.

        Usage of the ``_route_name`` keyword argument: if our routing table
        defines routes ``/foo/{action}`` named 'foo' and
        ``/foo/{action}/{page}`` named ``fooaction``, and the current url
        pattern is ``/foo/view`` (which has matched the ``/foo/{action}``
        route), we may want to use the matchdict args to generate a URL to
        the ``fooaction`` route.  In this scenario,
        ``request.current_route_url(_route_name='fooaction', page='5')``
        Will return string like: ``/foo/view/5``.

        """
        if '_route_name' in kw:
            route_name = kw.pop('_route_name')
        else:
            route = getattr(self, 'matched_route', None)
            route_name = getattr(route, 'name', None)
            if route_name is None:
                raise ValueError('Current request matches no route')

        newkw = {}
        newkw.update(self.matchdict)
        newkw.update(kw)
        return self.route_url(route_name, *elements, **newkw)

    def current_route_path(self, *elements, **kw):
        """
        Generates a path (aka a 'relative URL', a URL minus the host, scheme,
        and port) for the :app:`Pyramid` :term:`route configuration` matched
        by the current request.

        This function accepts the same argument as
        :meth:`pyramid.request.Request.current_route_url` and performs the
        same duty.  It just omits the host, port, and scheme information in
        the return value; only the script_name, path, query parameters, and
        anchor data are present in the returned string.

        For example, if the route matched by the current request has the
        pattern ``/{foo}/{bar}``, this call to ``current_route_path``::

            request.current_route_path(foo='1', bar='2')

        Will return the string ``/1/2``.

        .. note::

           Calling ``request.current_route_path('route')`` is the same
           as calling ``request.current_route_url('route',
           _app_url=request.script_name)``.
           :meth:`pyramid.request.Request.current_route_path` is, in fact,
           implemented in terms of
           `:meth:`pyramid.request.Request.current_route_url` in just this
           way. As a result, any ``_app_url`` passed within the ``**kw``
           values to ``current_route_path`` will be ignored.
        """
        kw['_app_url'] = self.script_name
        return self.current_route_url(*elements, **kw)


def route_url(route_name, request, *elements, **kw):
    """
    This is a backwards compatibility function.  Its result is the same as
    calling::

        request.route_url(route_name, *elements, **kw)

    See :meth:`pyramid.request.Request.route_url` for more information.
    """
    return request.route_url(route_name, *elements, **kw)

def route_path(route_name, request, *elements, **kw):
    """
    This is a backwards compatibility function.  Its result is the same as
    calling::

        request.route_path(route_name, *elements, **kw)

    See :meth:`pyramid.request.Request.route_path` for more information.
    """
    return request.route_path(route_name, *elements, **kw)

def resource_url(resource, request, *elements, **kw):
    """
    This is a backwards compatibility function.  Its result is the same as
    calling::

        request.resource_url(resource, *elements, **kw)

    See :meth:`pyramid.request.Request.resource_url` for more information.
    """
    return request.resource_url(resource, *elements, **kw)

model_url = resource_url # b/w compat (forever)

def static_url(path, request, **kw):
    """
    This is a backwards compatibility function.  Its result is the same as
    calling::

        request.static_url(path, **kw)

    See :meth:`pyramid.request.Request.static_url` for more information.
    """
    if not os.path.isabs(path):
        if not ':' in path:
            # if it's not a package:relative/name and it's not an
            # /absolute/path it's a relative/path; this means its relative
            # to the package in which the caller's module is defined.
            package = caller_package()
            path = '%s:%s' % (package.__name__, path)
    return request.static_url(path, **kw)

def static_path(path, request, **kw):
    """
    This is a backwards compatibility function.  Its result is the same as
    calling::

        request.static_path(path, **kw)

    See :meth:`pyramid.request.Request.static_path` for more information.
    """
    if not os.path.isabs(path):
        if not ':' in path:
            # if it's not a package:relative/name and it's not an
            # /absolute/path it's a relative/path; this means its relative
            # to the package in which the caller's module is defined.
            package = caller_package()
            path = '%s:%s' % (package.__name__, path)
    return request.static_path(path, **kw)

def current_route_url(request, *elements, **kw):
    """
    This is a backwards compatibility function.  Its result is the same as
    calling::

        request.current_route_url(*elements, **kw)

    See :meth:`pyramid.request.Request.current_route_url` for more
    information.
    """
    return request.current_route_url(*elements, **kw)

def current_route_path(request, *elements, **kw):
    """
    This is a backwards compatibility function.  Its result is the same as
    calling::

        request.current_route_path(*elements, **kw)

    See :meth:`pyramid.request.Request.current_route_path` for more
    information.
    """
    return request.current_route_path(*elements, **kw)

@lru_cache(1000)
def _join_elements(elements):
    return '/'.join([quote_path_segment(s, safe=':@&+$,') for s in elements])
