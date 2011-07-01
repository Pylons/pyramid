What's New In Pyramid 1.1
=========================

This article explains the new features in Pyramid version 1.1 as compared to
its predecessor, :app:`Pyramid` 1.0.  It also documents backwards
incompatibilities between the two versions and deprecations added to Pyramid
1.1, as well as software dependency changes and notable documentation
additions.

Terminology Changes
-------------------

The term "template" used by the Pyramid documentation used to refer to both
"paster templates" and "rendered templates" (templates created by a rendering
engine.  i.e. Mako, Chameleon, Jinja, etc.).  "Paster templates" will now be
refered to as "scaffolds", whereas the name for "rendered templates" will
remain as "templates."

Major Feature Additions
-----------------------

The major feature additions in Pyramid 1.1 are:

- Support for the ``request.response`` attribute.

- New views introspection feature: ``paster pviews``.

- Support for "static" routes.

- Default HTTP exception view.

``request.response``
~~~~~~~~~~~~~~~~~~~~

- Instances of the :class:`pyramid.request.Request` class now have a
  ``response`` attribute.

  The object passed to a view callable as ``request`` is an instance of
  :class:`pyramid.request.Request`. ``request.response`` is an instance of
  the class :class:`pyramid.request.Response`.  View callables that are
  configured with a :term:`renderer` will return this response object to the
  Pyramid router.  Therefore, code in a renderer-using view callable can set
  response attributes such as ``request.response.content_type`` (before they
  return, e.g. a dictionary to the renderer) and this will influence the HTTP
  return value of the view callable.

  ``request.response`` can also be used in view callable code that is not
  configured to use a renderer.  For example, a view callable might do
  ``request.response.body = '123'; return request.response``.  However, the
  response object that is produced by ``request.response`` must be *returned*
  when a renderer is not in play in order to have any effect on the HTTP
  response (it is not a "global" response, and modifications to it are not
  somehow merged into a separately returned response object).

  The ``request.response`` object is lazily created, so its introduction does
  not negatively impact performance.

``paster pviews``
~~~~~~~~~~~~~~~~~

- A new paster command named ``paster pviews`` was added.  This command
  prints a summary of potentially matching views for a given path.  See
  the section entitled :ref:`displaying_matching_views` for more
  information.

Static Routes
~~~~~~~~~~~~~

- The ``add_route`` method of the Configurator now accepts a ``static``
  argument.  If this argument is ``True``, the added route will never be
  considered for matching when a request is handled.  Instead, it will only
  be useful for URL generation via ``route_url`` and ``route_path``.  See the
  section entitled :ref:`static_route_narr` for more information.

Default HTTP Exception View
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- A default exception view for the interface
  :class:`pyramid.interfaces.IExceptionResponse` is now registered by
  default.  This means that an instance of any exception class imported from
  :mod:`pyramid.httpexceptions` (such as ``HTTPFound``) can now be raised
  from within view code; when raised, this exception view will render the
  exception to a response.

  To allow for configuration of this feature, the :term:`Configurator` now
  accepts an additional keyword argument named ``exceptionresponse_view``.
  By default, this argument is populated with a default exception view
  function that will be used when an HTTP exception is raised.  When ``None``
  is passed for this value, an exception view for HTTP exceptions will not be
  registered.  Passing ``None`` returns the behavior of raising an HTTP
  exception to that of Pyramid 1.0 (the exception will propagate to
  middleware and to the WSGI server).

Minor Feature Additions
-----------------------

- A `JSONP <http://en.wikipedia.org/wiki/JSONP>`_ renderer.  See
  :ref:`jsonp_renderer` for more details.

- New authentication policy:
  :class:`pyramid.authentication.SessionAuthenticationPolicy`, which uses a
  session to store credentials.

- A function named :func:`pyramid.httpexceptions.exception_response` is a
  shortcut that can be used to create HTTP exception response objects using
  an HTTP integer status code.

- Integers and longs passed as ``elements`` to
  :func:`pyramid.url.resource_url` or
  :meth:`pyramid.request.Request.resource_url` e.g. ``resource_url(context,
  request, 1, 2)`` (``1`` and ``2`` are the ``elements``) will now be
  converted implicitly to strings in the result.  Previously passing integers
  or longs as elements would cause a TypeError.

- ``pyramid_alchemy`` scaffold now uses ``query.get`` rather than
  ``query.filter_by`` to take better advantage of identity map caching.

- ``pyramid_alchemy`` scaffold now has unit tests.

- Added a :func:`pyramid.i18n.make_localizer` API.

- An exception raised by a :class:`pyramid.events.NewRequest` event
  subscriber can now be caught by an exception view.

- It is now possible to get information about why Pyramid raised a Forbidden
  exception from within an exception view.  The ``ACLDenied`` object returned
  by the ``permits`` method of each stock authorization policy
  (:meth:`pyramid.interfaces.IAuthorizationPolicy.permits`) is now attached
  to the Forbidden exception as its ``result`` attribute.  Therefore, if
  you've created a Forbidden exception view, you can see the ACE, ACL,
  permission, and principals involved in the request as
  eg. ``context.result.permission``, ``context.result.acl``, etc within the
  logic of the Forbidden exception view.

- Don't explicitly prevent the ``timeout`` from being lower than the
  ``reissue_time`` when setting up an
  :class:`pyramid.authentication.AuthTktAuthenticationPolicy` (previously
  such a configuration would raise a ``ValueError``, now it's allowed,
  although typically nonsensical).  Allowing the nonsensical configuration
  made the code more understandable and required fewer tests.

- The :class:`pyramid.request.Request` class now has a ``ResponseClass``
  attribute which points at :class:`pyramid.response.Response`.

- The :class:`pyramid.response.Response` class now has a ``RequestClass``
  interface which points at :class:`pyramid.request.Request`.

- It is now possible to return an arbitrary object from a Pyramid view
  callable even if a renderer is not used, as long as a suitable adapter to
  :class:`pyramid.interfaces.IResponse` is registered for the type of the
  returned object by using the new
  :meth:`pyramid.config.Configurator.add_response_adapter` API.  See the
  section in the Hooks chapter of the documentation entitled
  :ref:`using_iresponse`.

- The Pyramid router will now, by default, call the ``__call__`` method of
  response objects when returning a WSGI response.  This means that, among
  other things, the ``conditional_response`` feature response objects
  inherited from WebOb will now behave properly.

- New method named :meth:`pyramid.request.Request.is_response`.  This method
  should be used instead of the :func:`pyramid.view.is_response` function,
  which has been deprecated.

- :class:`pyramid.exceptions.NotFound` is now just an alias for
  :class:`pyramid.httpexceptions.HTTPNotFound`.

- :class:`pyramid.exceptions.Forbidden` is now just an alias for
  :class:`pyramid.httpexceptions.HTTPForbidden`.

- Added ``mako.preprocessor`` config file parameter; allows for a Mako
  preprocessor to be specified as a Python callable or Python dotted name.
  See https://github.com/Pylons/pyramid/pull/183 for rationale.

Backwards Incompatibilities
---------------------------

- Pyramid no longer supports Python 2.4.  Python 2.5 or better is required to
  run Pyramid 1.1+.  Pyramid, however, does not work under any version of
  Python 3 yet.

- The Pyramid router now, by default, expects response objects returned from
  view callables to implement the :class:`pyramid.interfaces.IResponse`
  interface.  Unlike the Pyramid 1.0 version of this interface, objects which
  implement IResponse now must define a ``__call__`` method that accepts
  ``environ`` and ``start_response``, and which returns an ``app_iter``
  iterable, among other things.  Previously, it was possible to return any
  object which had the three WebOb ``app_iter``, ``headerlist``, and
  ``status`` attributes as a response, so this is a backwards
  incompatibility.  It is possible to get backwards compatibility back by
  registering an adapter to IResponse from the type of object you're now
  returning from view callables.  See the section in the Hooks chapter of the
  documentation entitled :ref:`using_iresponse`.

- The :class:`pyramid.interfaces.IResponse` interface is now much more
  extensive.  Previously it defined only ``app_iter``, ``status`` and
  ``headerlist``; now it is basically intended to directly mirror the
  ``webob.Response`` API, which has many methods and attributes.

- The :mod:`pyramid.httpexceptions` classes named ``HTTPFound``,
  ``HTTPMultipleChoices``, ``HTTPMovedPermanently``, ``HTTPSeeOther``,
  ``HTTPUseProxy``, and ``HTTPTemporaryRedirect`` now accept ``location`` as
  their first positional argument rather than ``detail``.  This means that
  you can do, e.g. ``return pyramid.httpexceptions.HTTPFound('http://foo')``
  rather than ``return
  pyramid.httpexceptions.HTTPFound(location='http//foo')`` (the latter will
  of course continue to work).

- The pyramid Router attempted to set a value into the key
  ``environ['repoze.bfg.message']`` when it caught a view-related exception
  for backwards compatibility with applications written for :mod:`repoze.bfg`
  during error handling.  It did this by using code that looked like so::

                    # "why" is an exception object
                    try: 
                        msg = why[0]
                    except:
                        msg = ''

                    environ['repoze.bfg.message'] = msg

  Use of the value ``environ['repoze.bfg.message']`` was docs-deprecated in
  Pyramid 1.0.  Our standing policy is to not remove features after a
  deprecation for two full major releases, so this code was originally slated
  to be removed in Pyramid 1.2.  However, computing the
  ``repoze.bfg.message`` value was the source of at least one bug found in
  the wild (https://github.com/Pylons/pyramid/issues/199), and there isn't a
  foolproof way to both preserve backwards compatibility and to fix the bug.
  Therefore, the code which sets the value has been removed in this release.
  Code in exception views which relies on this value's presence in the
  environment should now use the ``exception`` attribute of the request
  (e.g. ``request.exception[0]``) to retrieve the message instead of relying
  on ``request.environ['repoze.bfg.message']``.

Deprecations and Behavior Differences
-------------------------------------

- The default Mako renderer is now configured to escape all HTML in
  expression tags. This is intended to help prevent XSS attacks caused by
  rendering unsanitized input from users. To revert this behavior in user's
  templates, they need to filter the expression through the 'n' filter::

     ${ myhtml | n }.

  See https://github.com/Pylons/pyramid/issues/193.

- Deprecated all assignments to ``request.response_*`` attributes (for
  example ``request.response_content_type = 'foo'`` is now deprecated).
  Assignments and mutations of assignable request attributes that were
  considered by the framework for response influence are now deprecated:
  ``response_content_type``, ``response_headerlist``, ``response_status``,
  ``response_charset``, and ``response_cache_for``.  Instead of assigning
  these to the request object for later detection by the rendering machinery,
  users should use the appropriate API of the Response object created by
  accessing ``request.response`` (e.g. code which does
  ``request.response_content_type = 'abc'`` should be changed to
  ``request.response.content_type = 'abc'``).

- Passing view-related parameters to
  :meth:`pyramid.config.Configurator.add_route` is now deprecated.
  Previously, a view was permitted to be connected to a route using a set of
  ``view*`` parameters passed to the ``add_route`` method of the
  Configurator.  This was a shorthand which replaced the need to perform a
  subsequent call to ``add_view``. For example, it was valid (and often
  recommended) to do::

     config.add_route('home', '/', view='mypackage.views.myview',
                       view_renderer='some/renderer.pt')

  Passing ``view*`` arguments to ``add_route`` is now deprecated in favor of
  connecting a view to a predefined route via
  :meth:`pyramid.config.Configurator.add_view` using the route's
  ``route_name`` parameter.  As a result, the above example should now be
  spelled::

     config.add_route('home', '/')
     config.add_view('mypackage.views.myview', route_name='home',
                     renderer='some/renderer.pt')

  This deprecation was done to reduce confusion observed in IRC, as well as
  to (eventually) reduce documentation burden (see also
  https://github.com/Pylons/pyramid/issues/164).  A deprecation warning is
  now issued when any view-related parameter is passed to
  ``add_route``.

- Passing an ``environ`` dictionary to the ``__call__`` method of a
  "traverser" (e.g. an object that implements
  :class:`pyramid.interfaces.ITraverser` such as an instance of
  :class:`pyramid.traversal.ResourceTreeTraverser`) as its ``request``
  argument now causes a deprecation warning to be emitted.  Consumer code
  should pass a ``request`` object instead.  The fact that passing an environ
  dict is permitted has been documentation-deprecated since ``repoze.bfg``
  1.1, and this capability will be removed entirely in a future version.

- The following (undocumented, dictionary-like) methods of the
  :class:`pyramid.request.Request` object have been deprecated:
  ``__contains__``, ``__delitem__``, ``__getitem__``, ``__iter__``,
  ``__setitem__``, ``get``, ``has_key``, ``items``, ``iteritems``,
  ``itervalues``, ``keys``, ``pop``, ``popitem``, ``setdefault``, ``update``,
  and ``values``.  Usage of any of these methods will cause a deprecation
  warning to be emitted.  These methods were added for internal compatibility
  in ``repoze.bfg`` 1.1 (code that currently expects a request object
  expected an environ object in BFG 1.0 and before).  In a future version,
  these methods will be removed entirely.

- A custom request factory is now required to return a request object that
  has a ``response`` attribute (or "reified"/lazy property) if they the
  request is meant to be used in a view that uses a renderer.  This
  ``response`` attribute should be an instance of the class
  :class:`pyramid.response.Response`.

- The JSON and string renderer factories now assign to
  ``request.response.content_type`` rather than
  ``request.response_content_type``.

- Each built-in renderer factory now determines whether it should change the
  content type of the response by comparing the response's content type
  against the response's default content type; if the content type is the
  default content type (usually ``text/html``), the renderer changes the
  content type (to ``application/json`` or ``text/plain`` for JSON and string
  renderers respectively).

- The :func:`pyramid.wsgi.wsgiapp2` now uses a slightly different method of
  figuring out how to "fix" ``SCRIPT_NAME`` and ``PATH_INFO`` for the
  downstream application.  As a result, those values may differ slightly from
  the perspective of the downstream application (for example, ``SCRIPT_NAME``
  will now never possess a trailing slash).

- Previously, :class:`pyramid.request.Request` inherited from
  :class:`webob.request.Request` and implemented ``__getattr__``,
  ``__setattr__`` and ``__delattr__`` itself in order to override "adhoc
  attr" WebOb behavior where attributes of the request are stored in the
  environ.  Now, :class:`pyramid.request.Request` inherits from (the more
  recent) :class:`webob.request.BaseRequest` instead of
  :class:`webob.request.Request`, which provides the same behavior.
  :class:`pyramid.request.Request` no longer implements its own
  ``__getattr__``, ``__setattr__`` or ``__delattr__`` as a result.

- Deprecated :func:`pyramid.view.is_response` function in favor of
  (newly-added) :meth:`pyramid.request.Request.is_response` method.
  Determining if an object is truly a valid response object now requires
  access to the registry, which is only easily available as a request
  attribute.  The :func:`pyramid.view.is_response` function will still work
  until it is removed, but now may return an incorrect answer under some
  (very uncommon) circumstances.

- :class:`pyramid.response.Response` is now a *subclass* of
  ``webob.response.Response`` (in order to directly implement the
  :class:`pyramid.interfaces.IResponse` interface, to speed up response
  generation).

- The "exception response" objects importable from ``pyramid.httpexceptions``
  (e.g. ``HTTPNotFound``) are no longer just import aliases for classes that
  actually live in ``webob.exc``.  Instead, we've defined our own exception
  classes within the module that mirror and emulate the ``webob.exc``
  exception response objects almost entirely.  See
  :ref:`http_exception_hierarchy` in the Design Defense chapter for more
  information.

- When visiting a URL that represented a static view which resolved to a
  subdirectory, the ``index.html`` of that subdirectory would not be served
  properly.  Instead, a redirect to ``/subdir`` would be issued.  This has
  been fixed, and now visiting a subdirectory that contains an ``index.html``
  within a static view returns the index.html properly.  See also
  https://github.com/Pylons/pyramid/issues/67.

- Deprecated the
  :meth:`pyramid.config.Configurator.set_renderer_globals_factory` method and
  the ``renderer_globals`` Configurator constructor parameter.  Users should
  use convert code using this feature to use a BeforeRender event als
  :ref:`beforerender_event`.

Dependency Changes
------------------

- Pyramid now depends on :term:`WebOb` >= 1.0.2 as tests depend on the bugfix
  in that release: "Fix handling of WSGI environs with missing
  ``SCRIPT_NAME``".  (Note that in reality, everyone should probably be using
  1.0.4 or better though, as WebOb 1.0.2 and 1.0.3 were effectively brownbag
  releases.)

Documentation Enhancements
--------------------------

- The :ref:`bfg_wiki_tutorial` was updated slightly.

- The :ref:`bfg_sql_wiki_tutorial` was updated slightly.

- Made :class:`pyramid.interfaces.IAuthenticationPolicy` and
  :class:`pyramid.interfaces.IAuthorizationPolicy` public interfaces, and
  they are now referred to within the :mod:`pyramid.authentication` and
  :mod:`pyramid.authorization` API docs.

- Render the function definitions for each exposed interface in
  :mod:`pyramid.interfaces`.

- Add missing docs reference to
  :meth:`pyramid.config.Configurator.set_view_mapper` and refer to it within
  the documentation section entitled :ref:`using_a_view_mapper`.

- Added section to the "Environment Variables and ``.ini`` File Settings"
  chapter in the narrative documentation section entitled
  :ref:`adding_a_custom_setting`.

- Added documentation for a :term:`multidict` as
  :class:`pyramid.interfaces.IMultiDict`.

- Added a section to the "URL Dispatch" narrative chapter regarding the new
  "static" route feature entitled :ref:`static_route_narr`.

- Added API docs for :func:`pyramid.httpexceptions.exception_response`.

- Added :ref:`http_exceptions` section to Views narrative chapter including a
  description of :func:`pyramid.httpexceptions.exception_response`.

- Added API docs for
  :class:`pyramid.authentication.SessionAuthenticationPolicy`.
