What's New In Pyramid 1.1
=========================

This article explains the new features in Pyramid version 1.1 as compared to
its predecessor, :app:`Pyramid` 1.0.  It also documents backwards
incompatibilities between the two versions and deprecations added to Pyramid
1.1, as well as software dependency changes and notable documentation
additions.

Major Feature Additions
-----------------------

The major feature additions in Pyramid 1.1 are:

- Support for the ``request.response`` attribute.

- New views introspection feature: ``paster pviews``.

- Support for "static" routes.

``request.response``
~~~~~~~~~~~~~~~~~~~~

- Accessing the ``response`` attribute of a :class:`pyramid.request.Request`
  object (e.g. ``request.response`` within a view) now produces a new
  :class:`pyramid.response.Response` object.  This feature is meant to be
  used mainly when a view configured with a renderer needs to set response
  attributes: all renderers will use the Response object implied by
  ``request.response`` as the response object returned to the router.

  ``request.response`` can also be used by code in a view that does not use a
  renderer, however the response object that is produced by
  ``request.response`` must be returned when a renderer is not in play (it is
  not a "global" response).

``paster pviews``
~~~~~~~~~~~~~~~~~

- A new paster command named ``paster pviews`` was added.  This command
  prints a summary of potentially matching views for a given path.  See
  documentation the section entitled :ref:`displaying_matching_views` for
  more information.

Static Routes
~~~~~~~~~~~~~

- The ``add_route`` method of the Configurator now accepts a ``static``
  argument.  If this argument is ``True``, the added route will never be
  considered for matching when a request is handled.  Instead, it will only
  be useful for URL generation via ``route_url`` and ``route_path``.  See the
  section entitled :ref:`static_route_narr` for more information.

Minor Feature Additions
-----------------------

- New authentication policy:
  :ref:`pyramid.authentication.SessionAuthenticationPolicy`, which uses a
  session to store credentials.

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
     config.add_view('mypackage.views.myview', route_name='home')
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

- A custom request factory is now required to return a response object that
  has a ``response`` attribute (or "reified"/lazy property) if they the
  request is meant to be used in a view that uses a renderer.  This
  ``response`` attribute should be an instance of the class
  :class:`pyramid.response.Response`.

- The JSON and string renderer factories now assign to
  ``request.response.content_type`` rather than
  ``request.response_content_type``.  Each renderer factory determines
  whether it should change the content type of the response by comparing the
  response's content type against the response's default content type; if the
  content type is not the default content type (usually ``text/html``), the
  renderer changes the content type (to ``application/json`` or
  ``text/plain`` for JSON and string renderers respectively).

- The :func:`pyramid.wsgi.wsgiapp2` now uses a slightly different method of
  figuring out how to "fix" ``SCRIPT_NAME`` and ``PATH_INFO`` for the
  downstream application.  As a result, those values may differ slightly from
  the perspective of the downstream application (for example, ``SCRIPT_NAME``
  will now never possess a trailing slash).

- Previously, :class:`pyramid.request.Request` inherited from
  :class:`webob.request.Request` and implemented ``__getattr__``,
  ``__setattr__`` and ``__delattr__`` itself in order to overidde "adhoc
  attr" WebOb behavior where attributes of the request are stored in the
  environ.  Now, :class:`pyramid.request.Request inherits from (the more
  recent) :class:`webob.request.BaseRequest`` instead of
  :class:`webob.request.Request`, which provides the same behavior.
  :class:`pyramid.request.Request` no longer implements its own
  ``__getattr__``, ``__setattr__`` or ``__delattr__`` as a result.

Dependency Changes
------------------

- Pyramid now depends on :term:`WebOb` >= 1.0.2 as tests depend on the bugfix
  in that release: "Fix handling of WSGI environs with missing
  ``SCRIPT_NAME``".  (Note that in reality, everyone should probably be using
  1.0.4 or better though, as WebOb 1.0.2 and 1.0.3 were effectively brownbag
  releases.)

Documentation Enhancements
--------------------------

- The term "template" used to refer to both "paster templates" and "rendered
  templates" (templates created by a rendering engine.  i.e. Mako, Chameleon,
  Jinja, etc.).  "Paster templates" will now be refered to as "scaffolds",
  whereas the name for "rendered templates" will remain as "templates."

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
