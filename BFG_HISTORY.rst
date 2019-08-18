1.3b1 (2010-10-25)
==================

Features
--------

- The ``paster`` template named ``bfg_routesalchemy`` has been updated
  to use SQLAlchemy declarative syntax.  Thanks to Ergo^.

Bug Fixes
---------

- When a renderer factory could not be found, a misleading error
  message was raised if the renderer name was not a string.

Documentation
-------------

- The ""bfgwiki2" (SQLAlchemy + url dispatch) tutorial has been
  updated slightly.  In particular, the source packages no longer
  attempt to use a private index, and the recommended Python version
  is now 2.6.  It was also updated to take into account the changes to
  the ``bfg_routesalchemy`` template used to set up an environment.

- The "bfgwiki" (ZODB + traversal) tutorial has been updated slightly.
  In particular, the source packages no longer attempt to use a
  private index, and the recommended Python version is now 2.6.

1.3a15 (2010-09-30)
===================

Features
--------

- The ``repoze.bfg.traversal.traversal_path`` API now eagerly attempts
  to encode a Unicode ``path`` into ASCII before attempting to split
  it and decode its segments.  This is for convenience, effectively to
  allow a (stored-as-Unicode-in-a-database, or
  retrieved-as-Unicode-from-a-request-parameter) Unicode path to be
  passed to ``find_model``, which eventually internally uses the
  ``traversal_path`` function under the hood.  In version 1.2 and
  prior, if the ``path`` was Unicode, that Unicode was split on
  slashes and each resulting segment value was Unicode.  An
  inappropriate call to the ``decode()`` method of a resulting Unicode
  path segment could cause a ``UnicodeDecodeError`` to occur even if
  the Unicode representation of the path contained no 'high order'
  characters (it effectively did a "double decode").  By converting
  the Unicode path argument to ASCII before we attempt to decode and
  split, genuine errors will occur in a more obvious place while also
  allowing us to handle (for convenience) the case that it's a Unicode
  representation formed entirely from ASCII-compatible characters.

1.3a14 (2010-09-14)
===================

Bug Fixes
---------

- If an exception view was registered through the legacy
  ``set_notfound_view`` or ``set_forbidden_view`` APIs, the context
  sent to the view was incorrect (could be ``None`` inappropriately).

Features
--------

- Compatibility with WebOb 1.0.

Requirements
------------

- Now requires WebOb >= 1.0.

Backwards Incompatibilities
---------------------------

- Due to changes introduced WebOb 1.0, the
  ``repoze.bfg.request.make_request_ascii`` event subscriber no longer
  works, so it has been removed.  This subscriber was meant to be used
  in a deployment so that code written before BFG 0.7.0 could run
  unchanged.  At this point, such code will need to be rewritten to
  expect Unicode from ``request.GET``, ``request.POST`` and
  ``request.params`` or it will need to be changed to use
  ``request.str_POST``, ``request.str_GET`` and/or
  ``request.str_params`` instead of the non-``str`` versions of same,
  as the non-``str`` versions of the same APIs always now perform
  decoding to Unicode.

Errata
------

- A prior changelog entry asserted that the ``INewResponse`` event was
  not sent to listeners if the response was not "valid" (if a view or
  renderer returned a response object that did not have a
  status/headers/app_iter).  This is not true in this release, nor was
  it true in 1.3a13.

1.3a13 (2010-09-14)
===================

Bug Fixes
---------

- The ``traverse`` route predicate could not successfully generate a
  traversal path.

Features
--------

- In support of making it easier to configure applications which are
  "secure by default", a default permission feature was added.  If
  supplied, the default permission is used as the permission string to
  all view registrations which don't otherwise name a permission.
  These APIs are in support of that:

  - A new constructor argument was added to the Configurator:
    ``default_permission``.

  - A new method was added to the Configurator:
    ``set_default_permission``.

  - A new ZCML directive was added: ``default_permission``.

- Add a new request API: ``request.add_finished_callback``.  Finished
  callbacks are called by the router unconditionally near the very end
  of request processing.  See the "Using Finished Callbacks" section
  of the "Hooks" narrative chapter of the documentation for more
  information.

- A ``request.matched_route`` attribute is now added to the request
  when a route has matched.  Its value is the "route" object that
  matched (see the ``IRoute`` interface within
  ``repoze.bfg.interfaces`` API documentation for the API of a route
  object).

- The ``exception`` attribute of the request is now set slightly
  earlier and in a slightly different set of scenarios, for benefit of
  "finished callbacks" and "response callbacks".  In previous
  versions, the ``exception`` attribute of the request was not set at
  all if an exception view was not found.  In this version, the
  ``request.exception`` attribute is set immediately when an exception
  is caught by the router, even if an exception view could not be
  found.

- The ``add_route`` method of a Configurator now accepts a
  ``pregenerator`` argument.  The pregenerator for the resulting route
  is called by ``route_url`` in order to adjust the set of arguments
  passed to it by the user for special purposes, such as Pylons
  'subdomain' support.  It will influence the URL returned by
  ``route_url``.  See the ``repoze.bfg.interfaces.IRoutePregenerator``
  interface for more information.

Backwards Incompatibilities
---------------------------

- The router no longer sets the value ``wsgiorg.routing_args`` into
  the environ when a route matches. The value used to be something
  like ``((), matchdict)``.  This functionality was only ever
  obliquely referred to in change logs; it was never documented as an
  API.

- The ``exception`` attribute of the request now defaults to ``None``.
  In prior versions, the ``request.exception`` attribute did not exist
  if an exception was not raised by user code during request
  processing; it only began existence once an exception view was
  found.

Deprecations
------------

- The ``repoze.bfg.interfaces.IWSGIApplicationCreatedEvent`` event
  interface was renamed to
  ``repoze.bfg.interfaces.IApplicationCreated``.  Likewise, the
  ``repoze.bfg.events.WSGIApplicationCreatedEvent`` class was renamed
  to ``repoze.bfg.events.ApplicationCreated``.  The older aliases will
  continue to work indefinitely.

- The ``repoze.bfg.interfaces.IAfterTraversal`` event interface was
  renamed to ``repoze.bfg.interfaces.IContextFound``.  Likewise, the
  ``repoze.bfg.events.AfterTraversal`` class was renamed to
  ``repoze.bfg.events.ContextFound``.  The older aliases will continue
  to work indefinitely.

- References to the WSGI environment values ``bfg.routes.matchdict``
  and ``bfg.routes.route`` were removed from documentation.  These
  will stick around internally for several more releases, but it is
  ``request.matchdict`` and ``request.matched_route`` are now the
  "official" way to obtain the matchdict and the route object which
  resulted in the match.

Documentation
-------------

- Added documentation for the ``default_permission`` ZCML directive.

- Added documentation for the ``default_permission`` constructor value
  and the ``set_default_permission`` method in the Configurator API
  documentation.

- Added a new section to the "security" chapter named "Setting a
  Default Permission".

- Document ``renderer_globals_factory`` and ``request_factory``
  arguments to Configurator constructor.

- Added two sections to the "Hooks" chapter of the documentation:
  "Using Response Callbacks" and "Using Finished Callbacks".

- Added documentation of the ``request.exception`` attribute to the
  ``repoze.bfg.request.Request`` API documentation.

- Added glossary entries for "response callback" and "finished
  callback".

- The "Request Processing" narrative chapter has been updated to note
  finished and response callback steps.

- New interface in interfaces API documentation: ``IRoutePregenerator``.

- Added a "The Matched Route" section to the URL Dispatch narrative
  docs chapter, detailing the ``matched_route`` attribute.

1.3a12 (2010-09-08)
===================

Bug Fixes
---------

- Fix a bug in ``repoze.bfg.url.static_url`` URL generation: if two
  resource specifications were used to create two separate static
  views, but they shared a common prefix, it was possible that
  ``static_url`` would generate an incorrect URL.

- Fix another bug in ``repoze.bfg.static_url`` URL generation: too
  many slashes in generated URL.

- Prevent a race condition which could result in a ``RuntimeError``
  when rendering a Chameleon template that has not already been
  rendered once.  This would usually occur directly after a restart,
  when more than one person or thread is trying to execute the same
  view at the same time: https://bugs.launchpad.net/karl3/+bug/621364

Features
--------

- The argument to ``repoze.bfg.configuration.Configurator.add_route``
  which was previously called ``path`` is now called ``pattern`` for
  better explicability.  For backwards compatibility purposes, passing
  a keyword argument named ``path`` to ``add_route`` will still work
  indefinitely.

- The ``path`` attribute to the ZCML ``route`` directive is now named
  ``pattern`` for better explicability.  The older ``path`` attribute
  will continue to work indefinitely.

Documentation
-------------

- All narrative, API, and tutorial docs which referred to a route
  pattern as a ``path`` have now been updated to refer to them as a
  ``pattern``.

- The ``repoze.bfg.interfaces`` API documentation page is now rendered
  via ``repoze.sphinx.autointerface``.

- The URL Dispatch narrative chapter now refers to the ``interfaces``
  chapter to explain the API of an ``IRoute`` object.

Paster Templates
----------------

- The routesalchemy template has been updated to use ``pattern`` in
  its route declarations rather than ``path``.

Dependencies
------------

- ``tests_require`` now includes ``repoze.sphinx.autointerface`` as a
  dependency.

Internal
--------

- Add an API to the ``Configurator`` named ``get_routes_mapper``.
  This returns an object implementing the ``IRoutesMapper`` interface.

- The ``repoze.bfg.urldispatch.RoutesMapper`` object now has a
  ``get_route`` method which returns a single Route object or
  ``None``.

- A new interface ``repoze.bfg.interfaces.IRoute`` was added.  The
  ``repoze.bfg.urldispatch.Route`` object implements this interface.

- The canonical attribute for accessing the routing pattern from a
  route object is now ``pattern`` rather than ``path``.

- Use ``hash()`` rather than ``id()`` when computing the "phash" of a
  custom route/view predicate in order to allow the custom predicate
  some control over which predicates are "equal".

- Use ``response.headerlist.append`` instead of
  ``response.headers.add`` in
  ``repoze.bfg.request.add_global_response_headers`` in case the
  response is not a WebOb response.

- The ``repoze.bfg.urldispatch.Route`` constructor (not an API) now
  accepts a different ordering of arguments.  Previously it was
  ``(pattern, name, factory=None, predicates=())``.  It is now
  ``(name, pattern, factory=None, predicates=())``.  This is in
  support of consistency with ``configurator.add_route``.

- The ``repoze.bfg.urldispatch.RoutesMapper.connect`` method (not an
  API) now accepts a different ordering of arguments.  Previously it
  was ``(pattern, name, factory=None, predicates=())``.  It is now
  ``(name, pattern, factory=None, predicates=())``.  This is in
  support of consistency with ``configurator.add_route``.

1.3a11 (2010-09-05)
===================

Bug Fixes
---------

- Process the response callbacks and the NewResponse event earlier, to
  enable mutations to the response to take effect.

1.3a10 (2010-09-05)
===================

Features
--------

- A new ``repoze.bfg.request.Request.add_response_callback`` API has
  been added.  This method is documented in the new
  ``repoze.bfg.request`` API chapter.  It can be used to influence
  response values before a concrete response object has been created.

- The ``repoze.bfg.interfaces.INewResponse`` interface now includes a
  ``request`` attribute; as a result, a handler for INewResponse now
  has access to the request which caused the response.

- Each of the follow methods of the Configurator now allow the
  below-named arguments to be passed as "dotted name strings"
  (e.g. "foo.bar.baz") rather than as actual implementation objects
  that must be imported:

  setup_registry
     root_factory, authentication_policy, authorization_policy,
     debug_logger, locale_negotiator, request_factory,
     renderer_globals_factory

  add_subscriber
     subscriber, iface

  derive_view
     view

  add_view
     view, ``for_``, context, request_type, containment

  add_route()
     view, view_for, factory, ``for_``, view_context

  scan
     package

  add_renderer
     factory

  set_forbidden_view
     view

  set_notfound_view
     view

  set_request_factory
     factory

  set_renderer_globals_factory()
     factory

  set_locale_negotiator
     negotiator

  testing_add_subscriber
     event_iface

Bug Fixes
---------

- The route pattern registered internally for a local "static view"
  (either via the ``static`` ZCML directive or via the
  ``add_static_view`` method of the configurator) was incorrect.  It
  was registered for e.g. ``static*traverse``, while it should have
  been registered for ``static/*traverse``.  Symptom: two static views
  could not reliably be added to a system when they both shared the
  same path prefix (e.g. ``/static`` and ``/static2``).

Backwards Incompatibilities
---------------------------

- The INewResponse event is now not sent to listeners if the response
  returned by view code (or a renderer) is not a "real" response
  (e.g. if it does not have ``.status``, ``.headerlist`` and
  ``.app_iter`` attribtues).

Documentation
-------------

- Add an API chapter for the ``repoze.bfg.request`` module, which
  includes documentation for the ``repoze.bfg.request.Request`` class
  (the "request object").

- Modify the "Request and Response" narrative chapter to reference the
  new ``repoze.bfg.request`` API chapter.  Some content was moved from
  this chapter into the API documentation itself.

- Various changes to denote that Python dotted names are now allowed
  as input to Configurator methods.

Internal
--------

- The (internal) feature which made it possible to attach a
  ``global_response_headers`` attribute to the request (which was
  assumed to contain a sequence of header key/value pairs which would
  later be added to the response by the router), has been removed.
  The functionality of
  ``repoze.bfg.request.Request.add_response_callback`` takes its
  place.

- The ``repoze.bfg.events.NewResponse`` class's construct has changed:
  it now must be created with ``(request, response)`` rather than
  simply ``(response)``.

1.3a9 (2010-08-22)
==================

Features
--------

- The Configurator now accepts a dotted name *string* to a package as
  a ``package`` constructor argument. The ``package`` argument was
  previously required to be a package *object* (not a dotted name
  string).

- The ``repoze.bfg.configuration.Configurator.with_package`` method
  was added.  This method returns a new Configurator using the same
  application registry as the configurator object it is called
  upon. The new configurator is created afresh with its ``package``
  constructor argument set to the value passed to ``with_package``.
  This feature will make it easier for future BFG versions to allow
  dotted names as arguments in places where currently only object
  references are allowed (the work to allow dotted names instead of
  object references everywhere has not yet been done, however).

- The new ``repoze.bfg.configuration.Configurator.maybe_dotted``
  method resolves a Python dotted name string supplied as its
  ``dotted`` argument to a global Python object.  If the value cannot
  be resolved, a ``repoze.bfg.configuration.ConfigurationError`` is
  raised.  If the value supplied as ``dotted`` is not a string, the
  value is returned unconditionally without any resolution attempted.

- The new
  ``repoze.bfg.configuration.Configurator.absolute_resource_spec``
  method resolves a potentially relative "resource specification"
  string into an absolute version.  If the value supplied as
  ``relative_spec`` is not a string, the value is returned
  unconditionally without any resolution attempted.

Backwards Incompatibilities
---------------------------

- The functions in ``repoze.bfg.renderers`` named ``render`` and
  ``render_to_response`` introduced in 1.3a6 previously took a set of
  ``**values`` arguments for the values to be passed to the renderer.
  This was wrong, as renderers don't need to accept only dictionaries
  (they can accept any type of object).  Now, the value sent to the
  renderer must be supplied as a positional argument named ``value``.
  The ``request`` argument is still a keyword argument, however.

- The functions in ``repoze.bfg.renderers`` named ``render`` and
  ``render_to_response`` now accept an additional keyword argument
  named ``package``.

- The ``get_renderer`` API in ``repoze.bfg.renderers`` now accepts a
  ``package`` argument.

Documentation
-------------

- The ZCML ``include`` directive docs were incorrect: they specified
  ``filename`` rather than (the correct) ``file`` as an allowable
  attribute.

Internal
--------

- The ``repoze.bfg.resource.resolve_resource_spec`` function can now
  accept a package object as its ``pname`` argument instead of just a
  package name.

- The ``_renderer_factory_from_name`` and ``_renderer_from_name``
  methods of the Configurator were removed.  These were never APIs.

- The ``_render``, ``_render_to_response`` and ``_make_response``
  functions with ``repoze.bfg.render`` (added in 1.3a6) have been
  removed.

- A new helper class ``repoze.bfg.renderers.RendererHelper`` was
  added.

- The _map_view function of ``repoze.bfg.configuration`` now takes
  only a renderer_name argument instead of both a ``renderer`` and
  ``renderer``_name argument.  It also takes a ``package`` argument
  now.

- Use ``imp.get_suffixes`` indirection in
  ``repoze.bfg.path.package_name`` instead of hardcoded ``.py``
  ``.pyc`` and ``.pyo`` to use for comparison when attempting to
  decide if a directory is a package.

- Make tests runnable again under Jython (although they do not all
  pass currently).

- The reify decorator now maintains the docstring of the function it
  wraps.

1.3a8 (2010-08-08)
==================

Features
--------

- New public interface: ``repoze.bfg.exceptions.IExceptionResponse``.
  This interface is provided by all internal exception classes (such
  as ``repoze.bfg.exceptions.NotFound`` and
  ``repoze.bfg.exceptions.Forbidden``), instances of which are both
  exception objects and can behave as WSGI response objects.  This
  interface is made public so that exception classes which are also
  valid WSGI response factories can be configured to implement them or
  exception instances which are also or response instances can be
  configured to provide them.

- New API class: ``repoze.bfg.view.AppendSlashNotFoundViewFactory``.

  There can only be one Not Found view in any ``repoze.bfg``
  application.  Even if you use
  ``repoze.bfg.view.append_slash_notfound_view`` as the Not Found
  view, ``repoze.bfg`` still must generate a ``404 Not Found``
  response when it cannot redirect to a slash-appended URL; this not
  found response will be visible to site users.

  If you don't care what this 404 response looks like, and you only
  need redirections to slash-appended route URLs, you may use the
  ``repoze.bfg.view.append_slash_notfound_view`` object as the Not
  Found view.  However, if you wish to use a *custom* notfound view
  callable when a URL cannot be redirected to a slash-appended URL,
  you may wish to use an instance of the
  ``repoze.bfg.view.AppendSlashNotFoundViewFactory`` class as the Not
  Found view, supplying the notfound view callable as the first
  argument to its constructor.  For instance::

       from repoze.bfg.exceptions import NotFound
       from repoze.bfg.view import AppendSlashNotFoundViewFactory

       def notfound_view(context, request):
           return HTTPNotFound('It aint there, stop trying!')

       custom_append_slash = AppendSlashNotFoundViewFactory(notfound_view)
       config.add_view(custom_append_slash, context=NotFound)

  The ``notfound_view`` supplied must adhere to the two-argument view
  callable calling convention of ``(context, request)`` (``context``
  will be the exception object).

Documentation
-------------

- Expanded the "Cleaning Up After a Request" section of the URL
  Dispatch narrative chapter.

- Expanded the "Redirecting to Slash-Appended Routes" section of the
  URL Dispatch narrative chapter.

Internal
--------

- Previously, two default view functions were registered at
  Configurator setup (one for ``repoze.bfg.exceptions.NotFound`` named
  ``default_notfound_view`` and one for
  ``repoze.bfg.exceptions.Forbidden`` named
  ``default_forbidden_view``) to render internal exception responses.
  Those default view functions have been removed, replaced with a
  generic default view function which is registered at Configurator
  setup for the ``repoze.bfg.interfaces.IExceptionResponse`` interface
  that simply returns the exception instance; the ``NotFound`` and
  ``Forbidden`` classes are now still exception factories but they are
  also response factories which generate instances that implement the
  new ``repoze.bfg.interfaces.IExceptionResponse`` interface.

1.3a7 (2010-08-01)
==================

Features
--------

- The ``repoze.bfg.configuration.Configurator.add_route`` API now
  returns the route object that was added.

- A ``repoze.bfg.events.subscriber`` decorator was added.  This
  decorator decorates module-scope functions, which are then treated
  as event listeners after a scan() is performed.  See the Events
  narrative documentation chapter and the ``repoze.bfg.events`` module
  documentation for more information.

Bug Fixes
---------

- When adding a view for a route which did not yet exist ("did not yet
  exist" meaning, temporally, a view was added with a route name for a
  route which had not yet been added via add_route), the value of the
  ``custom_predicate`` argument to ``add_view`` was lost.  Symptom:
  wrong view matches when using URL dispatch and custom view
  predicates together.

- Pattern matches for a ``:segment`` marker in a URL dispatch route
  pattern now always match at least one character.  See "Backwards
  Incompatibilities" below in this changelog.

Backwards Incompatibilities
---------------------------

- A bug existed in the regular expression to do URL matching.  As an
  example, the URL matching machinery would cause the pattern
  ``/{foo}`` to match the root URL ``/`` resulting in a match
  dictionary of ``{'foo':u''}`` or the pattern ``/{fud}/edit might
  match the URL ``//edit`` resulting in a match dictionary of
  ``{'fud':u''}``.  It was always the intent that ``:segment`` markers
  in the pattern would need to match *at least one* character, and
  never match the empty string.  This, however, means that in certain
  circumstances, a routing match which your application inadvertently
  depended upon may no longer happen.

Documentation
-------------

- Added description of the ``repoze.bfg.events.subscriber`` decorator
  to the Events narrative chapter.

- Added ``repoze.bfg.events.subscriber`` API documentation to
  ``repoze.bfg.events`` API docs.

- Added a section named "Zope 3 Enforces 'TTW' Authorization Checks By
  Default; BFG Does Not" to the "Design Defense" chapter.

1.3a6 (2010-07-25)
==================

Features
--------

- New argument to ``repoze.bfg.configuration.Configurator.add_route``
  and the ``route`` ZCML directive: ``traverse``.  If you would like
  to cause the ``context`` to be something other than the ``root``
  object when this route matches, you can spell a traversal pattern as
  the ``traverse`` argument.  This traversal pattern will be used as
  the traversal path: traversal will begin at the root object implied
  by this route (either the global root, or the object returned by the
  ``factory`` associated with this route).

  The syntax of the ``traverse`` argument is the same as it is for
  ``path``. For example, if the ``path`` provided is
  ``articles/:article/edit``, and the ``traverse`` argument provided
  is ``/:article``, when a request comes in that causes the route to
  match in such a way that the ``article`` match value is '1' (when
  the request URI is ``/articles/1/edit``), the traversal path will be
  generated as ``/1``.  This means that the root object's
  ``__getitem__`` will be called with the name ``1`` during the
  traversal phase.  If the ``1`` object exists, it will become the
  ``context`` of the request.  The Traversal narrative has more
  information about traversal.

  If the traversal path contains segment marker names which are not
  present in the path argument, a runtime error will occur.  The
  ``traverse`` pattern should not contain segment markers that do not
  exist in the ``path``.

  A similar combining of routing and traversal is available when a
  route is matched which contains a ``*traverse`` remainder marker in
  its path.  The ``traverse`` argument allows you to associate route
  patterns with an arbitrary traversal path without using a
  ``*traverse`` remainder marker; instead you can use other match
  information.

  Note that the ``traverse`` argument is ignored when attached to a
  route that has a ``*traverse`` remainder marker in its path.

- A new method of the ``Configurator`` exists:
  ``set_request_factory``.  If used, this method will set the factory
  used by the ``repoze.bfg`` router to create all request objects.

- The ``Configurator`` constructor takes an additional argument:
  ``request_factory``.  If used, this argument will set the factory
  used by the ``repoze.bfg`` router to create all request objects.

- The ``Configurator`` constructor takes an additional argument:
  ``request_factory``.  If used, this argument will set the factory
  used by the ``repoze.bfg`` router to create all request objects.

- A new method of the ``Configurator`` exists:
  ``set_renderer_globals_factory``.  If used, this method will set the
  factory used by the ``repoze.bfg`` router to create renderer
  globals.

- A new method of the ``Configurator`` exists: ``get_settings``.  If
  used, this method will return the current settings object (performs
  the same job as the ``repoze.bfg.settings.get_settings`` API).

- The ``Configurator`` constructor takes an additional argument:
  ``renderer_globals_factory``.  If used, this argument will set the
  factory used by the ``repoze.bfg`` router to create renderer
  globals.

- Add ``repoze.bfg.renderers.render``,
  ``repoze.bfg.renderers.render_to_response`` and
  ``repoze.bfg.renderers.get_renderer`` functions.  These are
  imperative APIs which will use the same rendering machinery used by
  view configurations with a ``renderer=`` attribute/argument to
  produce a rendering or renderer.  Because these APIs provide a
  central API for all rendering, they now form the preferred way to
  perform imperative template rendering.  Using functions named
  ``render_*`` from modules such as ``repoze.bfg.chameleon_zpt`` and
  ``repoze.bfg.chameleon_text`` is now discouraged (although not
  deprecated).  The code the backing older templating-system-specific
  APIs now calls into the newer ``repoze.bfg.renderer`` code.

- The ``repoze.bfg.configuration.Configurator.testing_add_template``
  has been renamed to ``testing_add_renderer``.  A backwards
  compatibility alias is present using the old name.

Documentation
-------------

- The ``Hybrid`` narrative chapter now contains a description of the
  ``traverse`` route argument.

- The ``Hooks`` narrative chapter now contains sections about
  changing the request factory and adding a renderer globals factory.

- The API documentation includes a new module:
  ``repoze.bfg.renderers``.

- The ``Templates`` chapter was updated; all narrative that used
  templating-specific APIs within examples to perform rendering (such
  as the ``repoze.bfg.chameleon_zpt.render_template_to_response``
  method) was changed to use ``repoze.bfg.renderers.render_*``
  functions.

Bug Fixes
---------

- The ``header`` predicate (when used as either a view predicate or a
  route predicate) had a problem when specified with a name/regex
  pair.  When the header did not exist in the headers dictionary, the
  regex match could be fed ``None``, causing it to throw a
  ``TypeError: expected string or buffer`` exception.  Now, the
  predicate returns False as intended.

Deprecations
------------

- The ``repoze.bfg.renderers.rendered_response`` function was never an
  official API, but may have been imported by extensions in the wild.
  It is officially deprecated in this release.  Use
  ``repoze.bfg.renderers.render_to_response`` instead.

- The following APIs are *documentation* deprecated (meaning they are
  officially deprecated in documentation but do not raise a
  deprecation error upon their usage, and may continue to work for an
  indefinite period of time):

  In the ``repoze.bfg.chameleon_zpt`` module: ``get_renderer``,
  ``get_template``, ``render_template``,
  ``render_template_to_response``.  The suggested alternatives are
  documented within the docstrings of those methods (which are still
  present in the documentation).

  In the ``repoze.bfg.chameleon_text`` module: ``get_renderer``,
  ``get_template``, ``render_template``,
  ``render_template_to_response``.  The suggested alternatives are
  documented within the docstrings of those methods (which are still
  present in the documentation).

  In general, to perform template-related functions, one should now
  use the various methods in the ``repoze.bfg.renderers`` module.

Backwards Incompatibilities
---------------------------

- A new internal exception class (*not* an API) named
  ``repoze.bfg.exceptions.PredicateMismatch`` now exists.  This
  exception is currently raised when no constituent view of a
  multiview can be called (due to no predicate match).  Previously, in
  this situation, a ``repoze.bfg.exceptions.NotFound`` was raised.  We
  provide backwards compatibility for code that expected a
  ``NotFound`` to be raised when no predicates match by causing
  ``repoze.bfg.exceptions.PredicateMismatch`` to inherit from
  ``NotFound``.  This will cause any exception view registered for
  ``NotFound`` to be called when a predicate mismatch occurs, as was
  the previous behavior.

  There is however, one perverse case that will expose a backwards
  incompatibility.  If 1) you had a view that was registered as a
  member of a multiview 2) this view explicitly raised a ``NotFound``
  exception *in order to* proceed to the next predicate check in the
  multiview, that code will now behave differently: rather than
  skipping to the next view match, a NotFound will be raised to the
  top-level exception handling machinery instead.  For code to be
  depending upon the behavior of a view raising ``NotFound`` to
  proceed to the next predicate match, would be tragic, but not
  impossible, given that ``NotFound`` is a public interface.
  ``repoze.bfg.exceptions.PredicateMismatch`` is not a public API and
  cannot be depended upon by application code, so you should not
  change your view code to raise ``PredicateMismatch``.  Instead, move
  the logic which raised the ``NotFound`` exception in the view out
  into a custom view predicate.

- If, when you run your application's unit test suite under BFG 1.3, a
  ``KeyError`` naming a template or a ``ValueError`` indicating that a
  'renderer factory' is not registered may is raised
  (e.g. ``ValueError: No factory for renderer named '.pt' when looking
  up karl.views:templates/snippets.pt``), you may need to perform some
  extra setup in your test code.

  The best solution is to use the
  ``repoze.bfg.configuration.Configurator.testing_add_renderer`` (or,
  alternately the deprecated
  ``repoze.bfg.testing.registerTemplateRenderer`` or
  ``registerDummyRenderer``) API within the code comprising each
  individual unit test suite to register a "dummy" renderer for each
  of the templates and renderers used by code under test.  For
  example::

    config = Configurator()
    config.testing_add_renderer('karl.views:templates/snippets.pt')

  This will register a basic dummy renderer for this particular
  missing template.  The ``testing_add_renderer`` API actually
  *returns* the renderer, but if you don't care about how the render
  is used, you don't care about having a reference to it either.

  A more rough way to solve the issue exists.  It causes the "real"
  template implementations to be used while the system is under test,
  which is suboptimal, because tests will run slower, and unit tests
  won't actually *be* unit tests, but it is easier.  Always ensure you
  call the ``setup_registry()`` method of the Configurator .  Eg::

    reg = MyRegistry()
    config = Configurator(registry=reg)
    config.setup_registry()

  Calling ``setup_registry`` only has an effect if you're *passing in*
  a ``registry`` argument to the Configurator constructor.
  ``setup_registry`` is called by the course of normal operations
  anyway if you do not pass in a ``registry``.

  If your test suite isn't using a Configurator yet, and is still
  using the older ``repoze.bfg.testing`` APIs name ``setUp`` or
  ``cleanUp``, these will register the renderers on your behalf.

  A variant on the symptom for this theme exists: you may already be
  dutifully registering a dummy template or renderer for a template
  used by the code you're testing using ``testing_register_renderer``
  or ``registerTemplateRenderer``, but (perhaps unbeknownst to you)
  the code under test expects to be able to use a "real" template
  renderer implementation to retrieve or render *another* template
  that you forgot was being rendered as a side effect of calling the
  code you're testing.  This happened to work because it found the
  *real* template while the system was under test previously, and now
  it cannot.  The solution is the same.

  It may also help reduce confusion to use a *resource specification*
  to specify the template path in the test suite and code rather than
  a relative path in either.  A resource specification is unambiguous,
  while a relative path needs to be relative to "here", where "here"
  isn't always well-defined ("here" in a test suite may or may not be
  the same as "here" in the code under test).

1.3a5 (2010-07-14)
==================

Features
--------

- New internal exception: ``repoze.bfg.exceptions.URLDecodeError``.
  This URL is a subclass of the built-in Python exception named
  ``UnicodeDecodeError``.

- When decoding a URL segment to Unicode fails, the exception raised
  is now ``repoze.bfg.exceptions.URLDecodeError`` instead of
  ``UnicodeDecodeError``.  This makes it possible to register an
  exception view invoked specifically when ``repoze.bfg`` cannot
  decode a URL.

Bug Fixes
---------

- Fix regression in
  ``repoze.bfg.configuration.Configurator.add_static_view``.  Before
  1.3a4, view names that contained a slash were supported as route
  prefixes. 1.3a4 broke this by trying to treat them as full URLs.

Documentation
-------------

- The ``repoze.bfg.exceptions.URLDecodeError`` exception was added to
  the exceptions chapter of the API documentation.

Backwards Incompatibilities
---------------------------

- in previous releases, when a URL could not be decoded from UTF-8
  during traversal, a ``TypeError`` was raised.  Now the error which
  is raised is a ``repoze.bfg.exceptions.URLDecodeError``.

1.3a4 (2010-07-03)
==================

Features
--------

- Undocumented hook: make ``get_app`` and ``get_root`` of the
  ``repoze.bfg.paster.BFGShellCommand`` hookable in cases where
  endware may interfere with the default versions.

- In earlier versions, a custom route predicate associated with a url
  dispatch route (each of the predicate functions fed to the
  ``custom_predicates`` argument of
  ``repoze.bfg.configuration.Configurator.add_route``) has always
  required a 2-positional argument signature, e.g. ``(context,
  request)``.  Before this release, the ``context`` argument was
  always ``None``.

  As of this release, the first argument passed to a predicate is now
  a dictionary conventionally named ``info`` consisting of ``route``,
  and ``match``.  ``match`` is a dictionary: it represents the
  arguments matched in the URL by the route.  ``route`` is an object
  representing the route which was matched.

  This is useful when predicates need access to the route match.  For
  example::

    def any_of(segment_name, *args):
        def predicate(info, request):
            if info['match'][segment_name] in args:
                return True
        return predicate

    num_one_two_or_three = any_of('num, 'one', 'two', 'three')

    add_route('num', '/:num', custom_predicates=(num_one_two_or_three,))

  The ``route`` object is an object that has two useful attributes:
  ``name`` and ``path``.  The ``name`` attribute is the route name.
  The ``path`` attribute is the route pattern.  An example of using
  the route in a set of route predicates::

    def twenty_ten(info, request):
        if info['route'].name in ('ymd', 'ym', 'y'):
            return info['match']['year'] == '2010'

    add_route('y', '/:year', custom_predicates=(twenty_ten,))
    add_route('ym', '/:year/:month', custom_predicates=(twenty_ten,))
    add_route('ymd', '/:year/:month:/day', custom_predicates=(twenty_ten,))

- The ``repoze.bfg.url.route_url`` API has changed.  If a keyword
  ``_app_url`` is present in the arguments passed to ``route_url``,
  this value will be used as the protocol/hostname/port/leading path
  prefix of the generated URL.  For example, using an ``_app_url`` of
  ``http://example.com:8080/foo`` would cause the URL
  ``http://example.com:8080/foo/fleeb/flub`` to be returned from this
  function if the expansion of the route pattern associated with the
  ``route_name`` expanded to ``/fleeb/flub``.

- It is now possible to use a URL as the ``name`` argument fed to
  ``repoze.bfg.configuration.Configurator.add_static_view``.  When the
  name argument is a URL, the ``repoze.bfg.url.static_url`` API will
  generate join this URL (as a prefix) to a path including the static
  file name.  This makes it more possible to put static media on a
  separate webserver for production, while keeping static media
  package-internal and served by the development webserver during
  development.

Documentation
-------------

- The authorization chapter of the ZODB Wiki Tutorial
  (docs/tutorials/bfgwiki) was changed to demonstrate authorization
  via a group rather than via a direct username (thanks to Alex
  Marandon).

- The authorization chapter of the SQLAlchemy Wiki Tutorial
  (docs/tutorials/bfgwiki2) was changed to demonstrate authorization
  via a group rather than via a direct username.

- Redirect requests for tutorial sources to
  https://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki/index.html and
  https://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/index.html respectively.

- A section named ``Custom Route Predicates`` was added to the URL
  Dispatch narrative chapter.

- The Static Resources chapter has been updated to mention using
  ``static_url`` to generate URLs to external webservers.

Internal
--------

- Removed ``repoze.bfg.static.StaticURLFactory`` in favor of a new
  abstraction revolving around the (still-internal)
  ``repoze.bfg.static.StaticURLInfo`` helper class.

1.3a3 (2010-05-01)
==================

Paster Templates
----------------

- The ``bfg_alchemy`` and ``bfg_routesalchemy`` templates no longer
  register a ``handle_teardown`` event listener which calls
  ``DBSession.remove``.  This was found by Chris Withers to be
  unnecessary.

Documentation
-------------

- The "bfgwiki2" (URL dispatch wiki) tutorial code and documentation
  was changed to remove the ``handle_teardown`` event listener which
  calls ``DBSession.remove``.

- Any mention of the ``handle_teardown`` event listener as used by the
  paster templates was removed from the URL Dispatch narrative chapter.

- A section entitled Detecting Available Languages was added to the
  i18n narrative docs chapter.

1.3a2 (2010-04-28)
==================

Features
--------

- A locale negotiator no longer needs to be registered explicitly. The
  default locale negotiator at
  ``repoze.bfg.i18n.default_locale_negotiator`` is now used
  unconditionally as... um, the default locale negotiator.

- The default locale negotiator has become more complex.

  * First, the negotiator looks for the ``_LOCALE_`` attribute of
    the request object (possibly set by a view or an event listener).
  
  * Then it looks for the ``request.params['_LOCALE_']`` value.

  * Then it looks for the ``request.cookies['_LOCALE_']`` value.

Backwards Incompatibilities
---------------------------

- The default locale negotiator now looks for the parameter named
  ``_LOCALE_`` rather than a parameter named ``locale`` in
  ``request.params``.

Behavior Changes
----------------

- A locale negotiator may now return ``None``, signifying that the
  default locale should be used.

Documentation
-------------

- Documentation concerning locale negotiation in the
  Internationalizationa and Localization chapter was updated.

- Expanded portion of i18n narrative chapter docs which discuss
  working with gettext files.

1.3a1 (2010-04-26)
==================

Features
--------

- Added "exception views".  When you use an exception (anything that
  inherits from the Python ``Exception`` builtin) as view context
  argument, e.g.::

      from repoze.bfg.view import bfg_view
      from repoze.bfg.exceptions import NotFound
      from webob.exc import HTTPNotFound

      @bfg_view(context=NotFound)
      def notfound_view(request):
          return HTTPNotFound()

  For the above example, when the ``repoze.bfg.exceptions.NotFound``
  exception is raised by any view or any root factory, the
  ``notfound_view`` view callable will be invoked and its response
  returned.

  Other normal view predicates can also be used in combination with an
  exception view registration::

      from repoze.bfg.view import bfg_view
      from repoze.bfg.exceptions import NotFound
      from webob.exc import HTTPNotFound

      @bfg_view(context=NotFound, route_name='home')
      def notfound_view(request):
          return HTTPNotFound()

  The above exception view names the ``route_name`` of ``home``,
  meaning that it will only be called when the route matched has a
  name of ``home``.  You can therefore have more than one exception
  view for any given exception in the system: the "most specific" one
  will be called when the set of request circumstances which match the
  view registration.  The only predicate that cannot be not be used
  successfully is ``name``.  The name used to look up an exception
  view is always the empty string.

  Existing (pre-1.3) normal views registered against objects
  inheriting from ``Exception`` will continue to work.  Exception
  views used for user-defined exceptions and system exceptions used as
  contexts will also work.

  The feature can be used with any view registration mechanism
  (``@bfg_view`` decorator, ZCML, or imperative ``config.add_view``
  styles).

  This feature was kindly contributed by Andrey Popp.

- Use "Venusian" (`https://docs.pylonsproject.org/projects/venusian/en/latest/
  <https://docs.pylonsproject.org/projects/venusian/en/latest/>`_) to perform ``bfg_view``
  decorator scanning rather than relying on a BFG-internal decorator
  scanner.  (Truth be told, Venusian is really just a generalization
  of the BFG-internal decorator scanner).

- Internationalization and localization features as documented in the
  narrative documentation chapter entitled ``Internationalization and
  Localization``.

- A new deployment setting named ``default_locale_name`` was added.
  If this string is present as a Paster ``.ini`` file option, it will
  be considered the default locale name.  The default locale name is
  used during locale-related operations such as language translation.

- It is now possible to turn on Chameleon template "debugging mode"
  for all Chameleon BFG templates by setting a BFG-related Paster
  ``.ini`` file setting named ``debug_templates``. The exceptions
  raised by Chameleon templates when a rendering fails are sometimes
  less than helpful.  ``debug_templates`` allows you to configure your
  application development environment so that exceptions generated by
  Chameleon during template compilation and execution will contain
  more helpful debugging information.  This mode is on by default in
  all new projects.

- Add a new method of the Configurator named ``derive_view`` which can
  be used to generate a BFG view callable from a user-supplied
  function, instance, or class. This useful for external framework and
  plugin authors wishing to wrap callables supplied by their users
  which follow the same calling conventions and response conventions
  as objects that can be supplied directly to BFG as a view callable.
  See the ``derive_view`` method in the
  ``repoze.bfg.configuration.Configurator`` docs.

ZCML
----

- Add a ``translationdir`` ZCML directive to support localization.

- Add a ``localenegotiator`` ZCML directive to support localization.

Deprecations
------------

-  The exception views feature replaces the need for the
   ``set_notfound_view`` and ``set_forbidden_view`` methods of the
   ``Configurator`` as well as the ``notfound`` and ``forbidden`` ZCML
   directives.  Those methods and directives will continue to work for
   the foreseeable future, but they are deprecated in the
   documentation.

Dependencies
------------

- A new install-time dependency on the ``venusian`` distribution was
  added.

- A new install-time dependency on the ``translationstring``
  distribution was added.

- Chameleon 1.2.3 or better is now required (internationalization and
  per-template debug settings).

Internal
--------

- View registrations and lookups are now done with three "requires"
  arguments instead of two to accommodate orthogonality of exception
  views.

- The ``repoze.bfg.interfaces.IForbiddenView`` and
  ``repoze.bfg.interfaces.INotFoundView`` interfaces were removed;
  they weren't APIs and they became vestigial with the addition of
  exception views.

- Remove ``repoze.bfg.compat.pkgutil_26.py`` and import alias
  ``repoze.bfg.compat.walk_packages``.  These were only required by
  internal scanning machinery; Venusian replaced the internal scanning
  machinery, so these are no longer required.

Documentation
-------------

- Exception view documentation was added to the ``Hooks`` narrative
  chapter.

- A new narrative chapter entitled ``Internationalization and
  Localization`` was added.

- The "Environment Variables and ``ini`` File Settings" chapter was
  changed: documentation about the ``default_locale_name`` setting was
  added.

- A new API chapter for the ``repoze.bfg.i18n`` module was added.

- Documentation for the new ``translationdir`` and
  ``localenegotiator`` ZCML directives were added.

- A section was added to the Templates chapter entitled "Nicer
  Exceptions in Templates" describing the result of setting
  ``debug_templates = true``.

Paster Templates
----------------

- All paster templates now create a ``setup.cfg`` which includes
  commands related to nose testing and Babel message catalog
  extraction/compilation.

- A ``default_locale_name = en`` setting was added to each existing paster
  template.

- A ``debug_templates = true`` setting was added to each existing
  paster template.

Licensing
---------

- The Edgewall (BSD) license was added to the LICENSES.txt file, as
  some code in the ``repoze.bfg.i18n`` derives from Babel source.

1.2 (2010-02-10)
================

- No changes from 1.2b6.

1.2b6 (2010-02-06)
==================

Backwards Incompatibilities
---------------------------

- Remove magical feature of ``repoze.bfg.url.model_url`` which
  prepended a fully-expanded urldispatch route URL before a the
  model's path if it was noticed that the request had matched a route.
  This feature was ill-conceived, and didn't work in all scenarios.

Bug Fixes
---------

- More correct conversion of provided ``renderer`` values to resource
  specification values (internal).

1.2b5 (2010-02-04)
==================

Bug Fixes
---------

- 1.2b4 introduced a bug whereby views added via a route configuration
  that named a view callable and also a ``view_attr`` became broken.
  Symptom: ``MyViewClass is not callable`` or the ``__call__`` of a
  class was being called instead of the method named via
  ``view_attr``.

- Fix a bug whereby a ``renderer`` argument to the ``@bfg_view``
  decorator that provided a package-relative template filename might
  not have been resolved properly.  Symptom: inappropriate ``Missing
  template resource`` errors.

1.2b4 (2010-02-03)
==================

Documentation
-------------

- Update GAE tutorial to use Chameleon instead of Jinja2 (now that
  it's possible).

Bug Fixes
---------

- Ensure that ``secure`` flag for AuthTktAuthenticationPolicy
  constructor does what it's documented to do (merge Daniel Holth's
  fancy-cookies-2 branch).

Features
--------

- Add ``path`` and ``http_only`` options to
  AuthTktAuthenticationPolicy constructor (merge Daniel Holth's
  fancy-cookies-2 branch).

Backwards Incompatibilities
---------------------------

- Remove ``view_header``, ``view_accept``, ``view_xhr``,
  ``view_path_info``, ``view_request_method``, ``view_request_param``,
  and ``view_containment`` predicate arguments from the
  ``Configurator.add_route`` argument list.  These arguments were
  speculative.  If you need the features exposed by these arguments,
  add a view associated with a route using the ``route_name`` argument
  to the ``add_view`` method instead.

- Remove ``view_header``, ``view_accept``, ``view_xhr``,
  ``view_path_info``, ``view_request_method``, ``view_request_param``,
  and ``view_containment`` predicate arguments from the ``route`` ZCML
  directive attribute set.  These attributes were speculative.  If you
  need the features exposed by these attributes, add a view associated
  with a route using the ``route_name`` attribute of the ``view`` ZCML
  directive instead.

Dependencies
------------

- Remove dependency on ``sourcecodegen`` (not depended upon by
  Chameleon 1.1.1+).

1.2b3 (2010-01-24)
==================

Bug Fixes
---------

- When "hybrid mode" (both traversal and urldispatch) is in use,
  default to finding route-related views even if a non-route-related
  view registration has been made with a more specific context.  The
  default used to be to find views with a more specific context first.
  Use the new ``use_global_views`` argument to the route definition to
  get back the older behavior.

Features
--------

- Add ``use_global_views`` argument to ``add_route`` method of
  Configurator.  When this argument is true, views registered for *no*
  route will be found if no more specific view related to the route is
  found.

- Add ``use_global_views`` attribute to ZCML ``<route>`` directive
  (see above).

Internal
--------

- When registering a view, register the view adapter with the
  "requires" interfaces as ``(request_type, context_type)`` rather
  than ``(context_type, request_type)``.  This provides for saner
  lookup, because the registration will always be made with a specific
  request interface, but registration may not be made with a specific
  context interface.  In general, when creating multiadapters, you
  want to order the requires interfaces so that the elements which
  are more likely to be registered using specific interfaces are
  ordered before those which are less likely.

1.2b2 (2010-01-21)
==================

Bug Fixes
---------

- When the ``Configurator`` is passed an instance of
  ``zope.component.registry.Components`` as a ``registry`` constructor
  argument, fix the instance up to have the attributes we expect of an
  instance of ``repoze.bfg.registry.Registry`` when ``setup_registry``
  is called.  This makes it possible to use the global Zope component
  registry as a BFG application registry.

- When WebOb 0.9.7.1 was used, a deprecation warning was issued for
  the class attribute named ``charset`` within
  ``repoze.bfg.request.Request``.  BFG now *requires* WebOb >= 0.9.7,
  and code was added so that this deprecation warning has disappeared.

- Fix a view lookup ordering bug whereby a view with a larger number
  of predicates registered first (literally first, not "earlier") for
  a triad would lose during view lookup to one registered with fewer.

- Make sure views with exactly N custom predicates are always called
  before views with exactly N non-custom predicates given all else is
  equal in the view configuration.

Documentation
-------------

- Change renderings of ZCML directive documentation.

- Add a narrative documentation chapter: "Using the Zope Component
  Architecture in repoze.bfg".

Dependencies
------------

- Require WebOb >= 0.9.7

1.2b1 (2010-01-18)
==================

Bug Fixes
---------

- In ``bfg_routesalchemy``, ``bfg_alchemy`` paster templates and the
  ``bfgwiki2`` tutorial, clean up the SQLAlchemy connection by
  registering a ``repoze.tm.after_end`` callback instead of relying on
  a ``__del__`` method of a ``Cleanup`` class added to the WSGI
  environment.  The ``__del__`` strategy was fragile and caused
  problems in the wild.  Thanks to Daniel Holth for testing.

Features
--------

- Read logging configuration from PasteDeploy config file ``loggers``
  section (and related) when ``paster bfgshell`` is invoked.

Documentation
-------------

- Major rework in preparation for book publication.

1.2a11 (2010-01-05)
===================

Bug Fixes
---------

- Make ``paster bfgshell`` and ``paster create -t bfg_xxx`` work on
  Jython (fix minor incompatibility with treatment of ``__doc__`` at
  the class level).

- Updated dependency on ``WebOb`` to require a version which supports
  features now used in tests.

Features
--------

- Jython compatibility (at least when repoze.bfg.jinja2 is used as the
  templating engine; Chameleon does not work under Jython).

- Show the derived abspath of template resource specifications in the
  traceback when a renderer template cannot be found.

- Show the original traceback when a Chameleon template cannot be
  rendered due to a platform incompatibility.

1.2a10 (2010-01-04)
===================

Features
--------

- The ``Configurator.add_view`` method now accepts an argument named
  ``context``.  This is an alias for the older argument named
  ``for_``; it is preferred over ``for_``, but ``for_`` will continue
  to be supported "forever".

- The ``view`` ZCML directive now accepts an attribute named
  ``context``.  This is an alias for the older attribute named
  ``for``; it is preferred over ``for``, but ``for`` will continue to
  be supported "forever".

- The ``Configurator.add_route`` method now accepts an argument named
  ``view_context``.  This is an alias for the older argument named
  ``view_for``; it is preferred over ``view_for``, but ``view_for``
  will continue to be supported "forever".

- The ``route`` ZCML directive now accepts an attribute named
  ``view_context``.  This is an alias for the older attribute named
  ``view_for``; it is preferred over ``view_for``, but ``view_for``
  will continue to be supported "forever".

Documentation and Paster Templates
----------------------------------

- LaTeX rendering tweaks.

- All uses of the ``Configurator.add_view`` method that used its
  ``for_`` argument now use the ``context`` argument instead.

- All uses of the ``Configurator.add_route`` method that used its
  ``view_for`` argument now use the ``view_context`` argument instead.

- All uses of the ``view`` ZCML directive that used its ``for``
  attribute now use the ``context`` attribute instead.

- All uses of the ``route`` ZCML directive that used its ``view_for``
  attribute now use the ``view_context`` attribute instead.

- Add a (minimal) tutorial dealing with use of ``repoze.catalog`` in a
  ``repoze.bfg`` application.

Documentation Licensing
-----------------------

- Loosen the documentation licensing to allow derivative works: it is
  now offered under the `Creative Commons
  Attribution-Noncommercial-Share Alike 3.0 United States License
  <https://creativecommons.org/licenses/by-nc-sa/3.0/us/>`_.  This is
  only a documentation licensing change; the ``repoze.bfg`` software
  continues to be offered under the Repoze Public License at
  https://web.archive.org/web/20190401024809/http://repoze.org/license.html (BSD-like).

1.2a9 (2009-12-27)
==================

Documentation Licensing
-----------------------

- The *documentation* (the result of ``make <html|latex|htmlhelp>``
  within the ``docs`` directory) in this release is now offered under
  the Creative Commons Attribution-Noncommercial-No Derivative Works
  3.0 United States License as described by
  https://creativecommons.org/licenses/by-nc-nd/3.0/us/ .  This is only
  a licensing change for the documentation; the ``repoze.bfg``
  software continues to be offered under the Repoze Public License
  at https://web.archive.org/web/20190401024809/http://repoze.org/license.html (BSD-like).

Documentation
-------------

- Added manual index entries to generated index.

- Document the previously existing (but non-API)
  ``repoze.bfg.configuration.Configurator.setup_registry`` method as
  an official API of a ``Configurator``.

- Fix syntax errors in various documentation code blocks.

- Created new top-level documentation section: "ZCML Directives".
  This section contains detailed ZCML directive information, some of
  which was removed from various narrative chapters.

- The LaTeX rendering of the documentation has been improved.

- Added a "Fore-Matter" section with author, copyright, and licensing
  information.

1.2a8 (2009-12-24)
==================

Features
--------

- Add a ``**kw`` arg to the ``Configurator.add_settings`` API.

- Add ``hook_zca`` and ``unhook_zca`` methods to the ``Configurator``
  API.

- The ``repoze.bfg.testing.setUp`` method now returns a
  ``Configurator`` instance which can be used to do further
  configuration during unit tests.

Bug Fixes
---------

- The ``json`` renderer failed to set the response content type to
  ``application/json``.  It now does, by setting
  ``request.response_content_type`` unless this attribute is already
  set.

- The ``string`` renderer failed to set the response content type to
  ``text/plain``.  It now does, by setting
  ``request.response_content_type`` unless this attribute is already
  set.

Documentation
-------------

- General documentation improvements by using better Sphinx roles such
  as "class", "func", "meth", and so on.  This means that there are
  many more hyperlinks pointing to API documentation for API
  definitions in all narrative, tutorial, and API documentation
  elements.

- Added a description of imperative configuration in various places
  which only described ZCML configuration.

- A syntactical refreshing of various tutorials.

- Added the ``repoze.bfg.authentication``,
  ``repoze.bfg.authorization``, and ``repoze.bfg.interfaces`` modules
  to API documentation.

Deprecations
------------

- The ``repoze.bfg.testing.registerRoutesMapper`` API (added in an
  early 1.2 alpha) was deprecated.  Its import now generates a
  deprecation warning.

1.2a7 (2009-12-20)
==================

Features
--------

- Add four new testing-related APIs to the
  ``repoze.bfg.configuration.Configurator`` class:
  ``testing_securitypolicy``, ``testing_models``,
  ``testing_add_subscriber``, and ``testing_add_template``.  These
  were added in order to provide more direct access to the
  functionality of the ``repoze.bfg.testing`` APIs named
  ``registerDummySecurityPolicy``, ``registerModels``,
  ``registerEventListener``, and ``registerTemplateRenderer`` when a
  configurator is used.  The ``testing`` APIs named are nominally
  deprecated (although they will likely remain around "forever", as
  they are in heavy use in the wild).

- Add a new API to the ``repoze.bfg.configuration.Configurator``
  class: ``add_settings``.  This API can be used to add "settings"
  (information returned within via the
  ``repoze.bfg.settings.get_settings`` API) after the configurator has
  been initially set up.  This is most useful for testing purposes.

- Add a ``custom_predicates`` argument to the ``Configurator``
  ``add_view`` method, the ``bfg_view`` decorator and the attribute
  list of the ZCML ``view`` directive.  If ``custom_predicates`` is
  specified, it must be a sequence of predicate callables (a predicate
  callable accepts two arguments: ``context`` and ``request`` and
  returns ``True`` or ``False``).  The associated view callable will
  only be invoked if all custom predicates return ``True``.  Use one
  or more custom predicates when no existing predefined predicate is
  useful.  Predefined and custom predicates can be mixed freely.

- Add a ``custom_predicates`` argument to the ``Configurator``
  ``add_route`` and the attribute list of the ZCML ``route``
  directive.  If ``custom_predicates`` is specified, it must be a
  sequence of predicate callables (a predicate callable accepts two
  arguments: ``context`` and ``request`` and returns ``True`` or
  ``False``).  The associated route will match will only be invoked if
  all custom predicates return ``True``, else route matching
  continues.  Note that the value ``context`` will always be ``None``
  when passed to a custom route predicate.  Use one or more custom
  predicates when no existing predefined predicate is useful.
  Predefined and custom predicates can be mixed freely.

Internal
--------

- Remove the ``repoze.bfg.testing.registerTraverser`` function.  This
  function was never an API.

Documentation
-------------

- Doc-deprecated most helper functions in the ``repoze.bfg.testing``
  module.  These helper functions likely won't be removed any time
  soon, nor will they generate a warning any time soon, due to their
  heavy use in the wild, but equivalent behavior exists in methods of
  a Configurator.

1.2a6 (2009-12-18)
==================

Features
--------

- The ``Configurator`` object now has two new methods: ``begin`` and
  ``end``.  The ``begin`` method is meant to be called before any
  "configuration" begins (e.g. before ``add_view``, et. al are
  called).  The ``end`` method is meant to be called after all
  "configuration" is complete.

  Previously, before there was imperative configuration at all (1.1
  and prior), configuration begin and end was invariably implied by
  the process of loading a ZCML file.  When a ZCML load happened, the
  threadlocal data structure containing the request and registry was
  modified before the load, and torn down after the load, making sure
  that all framework code that needed ``get_current_registry`` for the
  duration of the ZCML load was satisfied.

  Some API methods called during imperative configuration, (such as
  ``Configurator.add_view`` when a renderer is involved) end up for
  historical reasons calling ``get_current_registry``.  However, in
  1.2a5 and below, the Configurator supplied no functionality that
  allowed people to make sure that ``get_current_registry`` returned
  the registry implied by the configurator being used.  ``begin`` now
  serves this purpose.  Inversely, ``end`` pops the thread local
  stack, undoing the actions of ``begin``.

  We make this boundary explicit to reduce the potential for confusion
  when the configurator is used in different circumstances (e.g. in
  unit tests and app code vs. just in initial app setup).

  Existing code written for 1.2a1-1.2a5 which does not call ``begin``
  or ``end`` continues to work in the same manner it did before.  It
  is however suggested that this code be changed to call ``begin`` and
  ``end`` to reduce the potential for confusion in the future.

- All ``paster`` templates which generate an application skeleton now
  make use of the new ``begin`` and ``end`` methods of the
  Configurator they use in their respective copies of ``run.py`` and
  ``tests.py``.

Documentation
-------------

- All documentation that makes use of a ``Configurator`` object to do
  application setup and test setup now makes use of the new ``begin``
  and ``end`` methods of the configurator.

Bug Fixes
---------

- When a ``repoze.bfg.exceptions.NotFound`` or
  ``repoze.bfg.exceptions.Forbidden`` *class* (as opposed to instance)
  was raised as an exception within a root factory (or route root
  factory), the exception would not be caught properly by the
  ``repoze.bfg.`` Router and it would propagate to up the call stack,
  as opposed to rendering the not found view or the forbidden view as
  would have been expected.

- When Chameleon page or text templates used as renderers were added
  imperatively (via ``Configurator.add_view`` or some derivative),
  they too-eagerly attempted to look up the ``reload_templates``
  setting via ``get_settings``, meaning they were always registered in
  non-auto-reload-mode (the default).  Each now waits until its
  respective ``template`` attribute is accessed to look up the value.

- When a route with the same name as a previously registered route was
  added, the old route was not removed from the mapper's routelist.
  Symptom: the old registered route would be used (and possibly
  matched) during route lookup when it should not have had a chance to
  ever be used.

1.2a5 (2009-12-10)
==================

Features
--------

- When the ``repoze.bfg.exceptions.NotFound`` or
  ``repoze.bfg.exceptions.Forbidden`` error is raised from within a
  custom root factory or the ``factory`` of a route, the appropriate
  response is now sent to the requesting user agent (the result of the
  notfound view or the forbidden view, respectively).  When these
  errors are raised from within a root factory, the ``context`` passed
  to the notfound or forbidden view will be ``None``.  Also, the
  request will not be decorated with ``view_name``, ``subpath``,
  ``context``, etc. as would normally be the case if traversal had
  been allowed to take place.

Internals
---------

- The exception class representing the error raised by various methods
  of a ``Configurator`` is now importable as
  ``repoze.bfg.exceptions.ConfigurationError``.

Documentation
-------------

- General documentation freshening which takes imperative
  configuration into account in more places and uses glossary
  references more liberally.

- Remove explanation of changing the request type in a new request
  event subscriber, as other predicates are now usually an easier way
  to get this done.

- Added "Thread Locals" narrative chapter to documentation, and added
  a API chapter documenting the ``repoze.bfg.threadlocals`` module.

- Added a "Special Exceptions" section to the "Views" narrative
  documentation chapter explaining the effect of raising
  ``repoze.bfg.exceptions.NotFound`` and
  ``repoze.bfg.exceptions.Forbidden`` from within view code.

Dependencies
------------

- A new dependency on the ``twill`` package was added to the
  ``setup.py`` ``tests_require`` argument (Twill will only be
  downloaded when ``repoze.bfg`` ``setup.py test`` or ``setup.py
  nosetests`` is invoked).

1.2a4 (2009-12-07)
==================

Features
--------

- ``repoze.bfg.testing.DummyModel`` now accepts a new constructor
  keyword argument: ``__provides__``.  If this constructor argument is
  provided, it should be an interface or a tuple of interfaces.  The
  resulting model will then provide these interfaces (they will be
  attached to the constructed model via
  ``zope.interface.alsoProvides``).

Bug Fixes
---------

- Operation on GAE was broken, presumably because the
  ``repoze.bfg.configuration`` module began to attempt to import the
  ``repoze.bfg.chameleon_zpt`` and ``repoze.bfg.chameleon_text``
  modules, and these cannot be used on non-CPython platforms.  It now
  tolerates startup time import failures for these modules, and only
  raise an import error when a template from one of these packages is
  actually used.

1.2a3 (2009-12-02)
==================

Bug Fixes
---------

- The ``repoze.bfg.url.route_url`` function inappropriately passed
  along ``_query`` and/or ``_anchor`` arguments to the
  ``mapper.generate`` function, resulting in blowups.

- When two views were registered with differering ``for`` interfaces
  or classes, and the ``for`` of first view registered was a
  superclass of the second, the ``repoze.bfg`` view machinery would
  incorrectly associate the two views with the same "multiview".
  Multiviews are meant to be collections of views that have *exactly*
  the same for/request/viewname values, without taking inheritance
  into account.  Symptom: wrong view callable found even when you had
  correctly specified a ``for_`` interface/class during view
  configuration for one or both view configurations.

Backwards Incompatibilities
---------------------------

- The ``repoze.bfg.templating`` module has been removed; it had been
  deprecated in 1.1 and never actually had any APIs in it.

1.2a2 (2009-11-29)
==================

Bug Fixes
---------

- The long description of this package (as shown on PyPI) was not
  valid reStructuredText, and so was not renderable.

- Trying to use an HTTP method name string such as ``GET`` as a
  ``request_type`` predicate argument caused a startup time failure
  when it was encountered in imperative configuration or in a
  decorator (symptom: ``Type Error: Required specification must be a
  specification``).  This now works again, although ``request_method``
  is now the preferred predicate argument for associating a view
  configuration with an HTTP request method.

Documentation
-------------

- Fixed "Startup" narrative documentation chapter; it was explaining
  "the old way" an application constructor worked.

1.2a1 (2009-11-28)
==================

Features
--------

- An imperative configuration mode.

  A ``repoze.bfg`` application can now begin its life as a single
  Python file.  Later, the application might evolve into a set of
  Python files in a package.  Even later, it might start making use of
  other configuration features, such as ``ZCML``.  But neither the use
  of a package nor the use of non-imperative configuration is required
  to create a simple ``repoze.bfg`` application any longer.

  Imperative configuration makes ``repoze.bfg`` competitive with
  "microframeworks" such as `Bottle <https://bottlepy.org/docs/dev/>`_ and
  `Tornado <https://www.tornadoweb.org/en/stable/>`_.  ``repoze.bfg`` has a good
  deal of functionality that most microframeworks lack, so this is
  hopefully a "best of both worlds" feature.

  The simplest possible ``repoze.bfg`` application is now::

     from webob import Response
     from wsgiref import simple_server
     from repoze.bfg.configuration import Configurator

     def hello_world(request):
         return Response('Hello world!')

     if __name__ == '__main__':
         config = Configurator()
         config.add_view(hello_world)
         app = config.make_wsgi_app()
         simple_server.make_server('', 8080, app).serve_forever()

- A new class now exists: ``repoze.bfg.configuration.Configurator``.
  This class forms the basis for sharing machinery between
  "imperatively" configured applications and traditional
  declaratively-configured applications.

- The ``repoze.bfg.testing.setUp`` function now accepts three extra
  optional keyword arguments: ``registry``, ``request`` and
  ``hook_zca``.

  If the ``registry`` argument is not ``None``, the argument will be
  treated as the registry that is set as the "current registry" (it
  will be returned by ``repoze.bfg.threadlocal.get_current_registry``)
  for the duration of the test.  If the ``registry`` argument is
  ``None`` (the default), a new registry is created and used for the
  duration of the test.

  The value of the ``request`` argument is used as the "current
  request" (it will be returned by
  ``repoze.bfg.threadlocal.get_current_request``) for the duration of
  the test; it defaults to ``None``.

  If ``hook_zca`` is ``True`` (the default), the
  ``zope.component.getSiteManager`` function will be hooked with a
  function that returns the value of ``registry`` (or the
  default-created registry if ``registry`` is ``None``) instead of the
  registry returned by ``zope.component.getGlobalSiteManager``,
  causing the Zope Component Architecture API (``getSiteManager``,
  ``getAdapter``, ``getUtility``, and so on) to use the testing
  registry instead of the global ZCA registry.

- The ``repoze.bfg.testing.tearDown`` function now accepts an
  ``unhook_zca`` argument.  If this argument is ``True`` (the
  default), ``zope.component.getSiteManager.reset()`` will be called.
  This will cause the result of the ``zope.component.getSiteManager``
  function to be the global ZCA registry (the result of
  ``zope.component.getGlobalSiteManager``) once again.

- The ``run.py`` module in various ``repoze.bfg`` ``paster`` templates
  now use a ``repoze.bfg.configuration.Configurator`` class instead of
  the (now-legacy) ``repoze.bfg.router.make_app`` function to produce
  a WSGI application.

Documentation
-------------

- The documentation now uses the "request-only" view calling
  convention in most examples (as opposed to the ``context, request``
  convention).  This is a documentation-only change; the ``context,
  request`` convention is also supported and documented, and will be
  "forever".

- ``repoze.bfg.configuration`` API documentation has been added.

- A narrative documentation chapter entitled "Creating Your First
  ``repoze.bfg`` Application" has been added.  This chapter details
  usage of the new ``repoze.bfg.configuration.Configurator`` class,
  and demonstrates a simplified "imperative-mode" configuration; doing
  ``repoze.bfg`` application configuration imperatively was previously
  much more difficult.

- A narrative documentation chapter entitled "Configuration,
  Decorations and Code Scanning" explaining ZCML- vs. imperative-
  vs. decorator-based configuration equivalence.

- The "ZCML Hooks" chapter has been renamed to "Hooks"; it documents
  how to override hooks now via imperative configuration and ZCML.

- The explanation about how to supply an alternate "response factory"
  has been removed from the "Hooks" chapter.  This feature may be
  removed in a later release (it still works now, it's just not
  documented).

- Add a section entitled "Test Set Up and Tear Down" to the
  unittesting chapter.

Bug Fixes
----------

- The ACL authorization policy debugging output when
  ``debug_authorization`` console debugging output was turned on
  wasn't as clear as it could have been when a view execution was
  denied due to an authorization failure resulting from the set of
  principals passed never having matched any ACE in any ACL in the
  lineage.  Now in this case, we report ``<default deny>`` as the ACE
  value and either the root ACL or ``<No ACL found on any object in
  model lineage>`` if no ACL was found.

- When two views were registered with the same ``accept`` argument,
  but were otherwise registered with the same arguments, if a request
  entered the application which had an ``Accept`` header that accepted
  *either* of the media types defined by the set of views registered
  with predicates that otherwise matched, a more or less "random" one
  view would "win".  Now, we try harder to use the view callable
  associated with the view configuration that has the most specific
  ``accept`` argument.  Thanks to Alberto Valverde for an initial
  patch.

Internals
---------

- The routes mapper is no longer a root factory wrapper.  It is now
  consulted directly by the router.

- The ``repoze.bfg.registry.make_registry`` callable has been removed.

- The ``repoze.bfg.view.map_view`` callable has been removed.

- The ``repoze.bfg.view.owrap_view`` callable has been removed.

- The ``repoze.bfg.view.predicate_wrap`` callable has been removed.

- The ``repoze.bfg.view.secure_view`` callable has been removed.

- The ``repoze.bfg.view.authdebug_view`` callable has been removed.

- The ``repoze.bfg.view.renderer_from_name`` callable has been
  removed.  Use ``repoze.bfg.configuration.Configurator.renderer_from_name``
  instead (still not an API, however).

- The ``repoze.bfg.view.derive_view`` callable has been removed.  Use
  ``repoze.bfg.configuration.Configurator.derive_view`` instead (still
  not an API, however).

- The ``repoze.bfg.settings.get_options`` callable has been removed.
  Its job has been subsumed by the ``repoze.bfg.settings.Settings``
  class constructor.

- The ``repoze.bfg.view.requestonly`` function has been moved to
  ``repoze.bfg.configuration.requestonly``.

- The ``repoze.bfg.view.rendered_response`` function has been moved to
  ``repoze.bfg.configuration.rendered_response``.

- The ``repoze.bfg.view.decorate_view`` function has been moved to
  ``repoze.bfg.configuration.decorate_view``.

- The ``repoze.bfg.view.MultiView`` class has been moved to
  ``repoze.bfg.configuration.MultiView``.

- The ``repoze.bfg.zcml.Uncacheable`` class has been removed.

- The ``repoze.bfg.resource.resource_spec`` function has been removed.

- All ZCML directives which deal with attributes which are paths now
  use the ``path`` method of the ZCML context to resolve a relative
  name to an absolute one (imperative configuration requirement).

- The ``repoze.bfg.scripting.get_root`` API now uses a 'real' WebOb
  request rather than a FakeRequest when it sets up the request as a
  threadlocal.

- The ``repoze.bfg.traversal.traverse`` API now uses a 'real' WebOb
  request rather than a FakeRequest when it calls the traverser.

- The ``repoze.bfg.request.FakeRequest`` class has been removed.

- Most uses of the ZCA threadlocal API (the ``getSiteManager``,
  ``getUtility``, ``getAdapter``, ``getMultiAdapter`` threadlocal API)
  have been removed from the core.  Instead, when a threadlocal is
  necessary, the core uses the
  ``repoze.bfg.threadlocal.get_current_registry`` API to obtain the
  registry.

- The internal ILogger utility named ``repoze.bfg.debug`` is now just
  an IDebugLogger unnamed utility.  A named utility with the old name
  is registered for b/w compat.

- The ``repoze.bfg.interfaces.ITemplateRendererFactory`` interface was
  removed; it has become unused.

- Instead of depending on the ``martian`` package to do code scanning,
  we now just use our own scanning routines.

- We now no longer have a dependency on ``repoze.zcml`` package;
  instead, the ``repoze.bfg`` package includes implementations of the
  ``adapter``, ``subscriber`` and ``utility`` directives.

- Relating to the following functions:

  ``repoze.bfg.view.render_view``

  ``repoze.bfg.view.render_view_to_iterable``

  ``repoze.bfg.view.render_view_to_response``

  ``repoze.bfg.view.append_slash_notfound_view``

  ``repoze.bfg.view.default_notfound_view``

  ``repoze.bfg.view.default_forbidden_view``

  ``repoze.bfg.configuration.rendered_response``

  ``repoze.bfg.security.has_permission``

  ``repoze.bfg.security.authenticated_userid``

  ``repoze.bfg.security.effective_principals``

  ``repoze.bfg.security.view_execution_permitted``

  ``repoze.bfg.security.remember``

  ``repoze.bfg.security.forget``

  ``repoze.bfg.url.route_url``

  ``repoze.bfg.url.model_url``

  ``repoze.bfg.url.static_url``

  ``repoze.bfg.traversal.virtual_root``

  Each of these functions now expects to be called with a request
  object that has a ``registry`` attribute which represents the
  current ``repoze.bfg`` registry.  They fall back to obtaining the
  registry from the threadlocal API.

Backwards Incompatibilities
---------------------------

- Unit tests which use ``zope.testing.cleanup.cleanUp`` for the
  purpose of isolating tests from one another may now begin to fail
  due to lack of isolation between tests.

  Here's why: In repoze.bfg 1.1 and prior, the registry returned by
  ``repoze.bfg.threadlocal.get_current_registry`` when no other
  registry had been pushed on to the threadlocal stack was the
  ``zope.component.globalregistry.base`` global registry (aka the
  result of ``zope.component.getGlobalSiteManager()``).  In repoze.bfg
  1.2+, however, the registry returned in this situation is the new
  module-scope ``repoze.bfg.registry.global_registry`` object.  The
  ``zope.testing.cleanup.cleanUp`` function clears the
  ``zope.component.globalregistry.base`` global registry
  unconditionally.  However, it does not know about the
  ``repoze.bfg.registry.global_registry`` object, so it does not clear
  it.

  If you use the ``zope.testing.cleanup.cleanUp`` function in the
  ``setUp`` of test cases in your unit test suite instead of using the
  (more correct as of 1.1) ``repoze.bfg.testing.setUp``, you will need
  to replace all calls to ``zope.testing.cleanup.cleanUp`` with a call
  to ``repoze.bfg.testing.setUp``.

  If replacing all calls to ``zope.testing.cleanup.cleanUp`` with a
  call to ``repoze.bfg.testing.setUp`` is infeasible, you can put this
  bit of code somewhere that is executed exactly **once** (*not* for
  each test in a test suite; in the `` __init__.py`` of your package
  or your package's ``tests`` subpackage would be a reasonable
  place)::

    import zope.testing.cleanup
    from repoze.bfg.testing import setUp
    zope.testing.cleanup.addCleanUp(setUp)

- When there is no "current registry" in the
  ``repoze.bfg.threadlocal.manager`` threadlocal data structure (this
  is the case when there is no "current request" or we're not in the
  midst of a ``r.b.testing.setUp``-bounded unit test), the ``.get``
  method of the manager returns a data structure containing a *global*
  registry.  In previous releases, this function returned the global
  Zope "base" registry: the result of
  ``zope.component.getGlobalSiteManager``, which is an instance of the
  ``zope.component.registry.Component`` class.  In this release,
  however, the global registry returns a globally importable instance
  of the ``repoze.bfg.registry.Registry`` class.  This registry
  instance can always be imported as
  ``repoze.bfg.registry.global_registry``.

  Effectively, this means that when you call
  ``repoze.bfg.threadlocal.get_current_registry`` when no request or
  ``setUp`` bounded unit test is in effect, you will always get back
  the global registry that lives in
  ``repoze.bfg.registry.global_registry``.  It also means that
  ``repoze.bfg`` APIs that *call* ``get_current_registry`` will use
  this registry.

  This change was made because ``repoze.bfg`` now expects the registry
  it uses to have a slightly different API than a bare instance of
  ``zope.component.registry.Components``.

- View registration no longer registers a
  ``repoze.bfg.interfaces.IViewPermission`` adapter (it is no longer
  checked by the framework; since 1.1, views have been responsible for
  providing their own security).

- The ``repoze.bfg.router.make_app`` callable no longer accepts the
  ``authentication_policy`` nor the ``authorization_policy``
  arguments.  This feature was deprecated in version 1.0 and has been
  removed.

- Obscure: the machinery which configured views with a
  ``request_type`` *and* a ``route_name`` would ignore the request
  interface implied by ``route_name`` registering a view only for the
  interface implied by ``request_type``.  In the unlikely event that
  you were trying to use these two features together, the symptom
  would have been that views that named a ``request_type`` but which
  were also associated with routes were not found when the route
  matched.  Now if a view is configured with both a ``request_type``
  and a ``route_name``, an error is raised.

- The ``route`` ZCML directive now no longer accepts the
  ``request_type`` or ``view_request_type`` attributes.  These
  attributes didn't actually work in any useful way (see entry above
  this one).

- Because the ``repoze.bfg`` package now includes implementations of
  the ``adapter``, ``subscriber`` and ``utility`` ZCML directives, it
  is now an error to have ``<include package="repoze.zcml"
  file="meta.zcml"/>`` in the ZCML of a ``repoze.bfg`` application.  A
  ZCML conflict error will be raised if your ZCML does so.  This
  shouldn't be an issue for "normal" installations; it has always been
  the responsibility of the ``repoze.bfg.includes`` ZCML to include
  this file in the past; it now just doesn't.

- The ``repoze.bfg.testing.zcml_configure`` API was removed.  Use
  the ``Configurator.load_zcml`` API instead.

Deprecations
------------

- The ``repoze.bfg.router.make_app`` function is now nominally
  deprecated.  Its import and usage does not throw a warning, nor will
  it probably ever disappear.  However, using a
  ``repoze.bfg.configuration.Configurator`` class is now the preferred
  way to generate a WSGI application.

  Note that ``make_app`` calls
  ``zope.component.getSiteManager.sethook(
  repoze.bfg.threadlocal.get_current_registry)`` on the caller's
  behalf, hooking ZCA global API lookups, for backwards compatibility
  purposes.  If you disuse ``make_app``, your calling code will need
  to perform this call itself, at least if your application uses the
  ZCA global API (``getSiteManager``, ``getAdapter``, etc).

Dependencies
------------

- A dependency on the ``martian`` package has been removed (its
  functionality is replaced internally).

- A dependency on the ``repoze.zcml`` package has been removed (its
  functionality is replaced internally).

1.1.1 (2009-11-21)
==================

Bug Fixes
---------

- "Hybrid mode" applications (applications which explicitly used
  traversal *after* url dispatch via ``<route>`` paths containing the
  ``*traverse`` element) were broken in 1.1-final and all 1.1 alpha
  and beta releases.  Views registered without a ``route_name`` route
  shadowed views registered with a ``route_name`` inappropriately.

1.1 (2009-11-15)
================

Internals
---------

- Remove dead IRouteRequirement interface from ``repoze.bfg.zcml``
  module.

Documentation
-------------

- Improve the "Extending an Existing Application" narrative chapter.

- Add more sections to the "Defending Design" chapter.

1.1b4 (2009-11-12)
==================

Bug Fixes
---------

- Use ``alsoProvides`` in the urldispatch module to attach an
  interface to the request rather than ``directlyProvides`` to avoid
  disturbing interfaces set in a NewRequest event handler.

Documentation
-------------

- Move 1.0.1 and previous changelog to HISTORY.txt.

- Add examples to ``repoze.bfg.url.model_url`` docstring.

- Add "Defending BFG Design" chapter to frontpage docs.

Templates
---------

- Remove ``ez_setup.py`` and its import from all paster templates,
  samples, and tutorials for ``distribute`` compatibility.  The
  documentation already explains how to install virtualenv (which will
  include some ``setuptools`` package), so these files, imports and
  usages were superfluous.

Deprecations
------------

- The ``options`` kw arg to the ``repoze.bfg.router.make_app``
  function is deprecated.  In its place is the keyword argument
  ``settings``.  The ``options`` keyword continues to work, and a
  deprecation warning is not emitted when it is detected.  However,
  the paster templates, code samples, and documentation now make
  reference to ``settings`` rather than ``options``.  This
  change/deprecation was mainly made for purposes of clarity and
  symmetry with the ``get_settings()`` API and discussions of
  "settings" in various places in the docs: we want to use the same
  name to refer to the same thing everywhere.

1.1b3 (2009-11-06)
==================

Features
--------

- ``repoze.bfg.testing.registerRoutesMapper`` testing facility added.
  This testing function registers a routes "mapper" object in the
  registry, for tests which require its presence.  This function is
  documented in the ``repoze.bfg.testing`` API documentation.

Bug Fixes
---------

- Compound statements that used an assignment entered into in an
  interactive IPython session invoked via ``paster bfgshell`` no
  longer fail to mutate the shell namespace correctly.  For example,
  this set of statements used to fail::

    In [2]: def bar(x): return x
      ...:
    In [3]: list(bar(x) for x in 'abc')
    Out[3]: NameError: 'bar'

  In this release, the ``bar`` function is found and the correct
  output is now sent to the console.  Thanks to Daniel Holth for the
  patch.

- The ``bfgshell`` command did not function properly; it was still
  expecting to be able to call the root factory with a bare
  ``environ`` rather than a request object.

Backwards Incompatibilities
---------------------------

- The ``repoze.bfg.scripting.get_root`` function now expects a
  ``request`` object as its second argument rather than an
  ``environ``.

1.1b2 (2009-11-02)
==================

Bug Fixes
---------

- Prevent PyPI installation failure due to ``easy_install`` trying way
  too hard to guess the best version of Paste.  When ``easy_install``
  pulls from PyPI it reads links off various pages to determine "more
  up to date" versions. It incorrectly picks up a link for an ancient
  version of a package named "Paste-Deploy-0.1" (note the dash) when
  trying to find the "Paste" distribution and somehow believes it's
  the latest version of "Paste".  It also somehow "helpfully" decides
  to check out a version of this package from SVN.  We pin the Paste
  dependency version to a version greater than 1.7 to work around
  this ``easy_install`` bug.

Documentation
-------------

- Fix "Hybrid" narrative chapter: stop claiming that ``<view>``
  statements that mention a route_name need to come afer (in XML
  order) the ``<route>`` statement which creates the route.  This
  hasn't been true since 1.1a1.

- "What's New in ``repoze.bfg`` 1.1" document added to narrative
  documentation.

Features
--------

- Add a new event type: ``repoze.bfg.events.AfterTraversal``.  Events
  of this type will be sent after traversal is completed, but before
  any view code is invoked.  Like ``repoze.bfg.events.NewRequest``,
  This event will have a single attribute: ``request`` representing
  the current request.  Unlike the request attribute of
  ``repoze.bfg.events.NewRequest`` however, during an AfterTraversal
  event, the request object will possess attributes set by the
  traverser, most notably ``context``, which will be the context used
  when a view is found and invoked.  The interface
  ``repoze.bfg.events.IAfterTraversal`` can be used to subscribe to
  the event.  For example::

    <subscriber for="repoze.bfg.interfaces.IAfterTraversal"
                handler="my.app.handle_after_traverse"/>

  Like any framework event, a subscriber function should expect one
  parameter: ``event``.

Dependencies
------------

- Rather than depending on ``chameleon.core`` and ``chameleon.zpt``
  distributions individually, depend on Malthe's repackaged
  ``Chameleon`` distribution (which includes both ``chameleon.core``
  and ``chameleon.zpt``).

1.1b1 (2009-11-01)
==================

Bug Fixes
---------

- The routes root factory called route factories and the default route
  factory with an environ rather than a request.  One of the symptoms
  of this bug: applications generated using the ``bfg_zodb`` paster
  template in 1.1a9 did not work properly.

- Reinstate ``renderer`` alias for ``view_renderer`` in the
  ``<route>`` ZCML directive (in-the-wild 1.1a bw compat).

- ``bfg_routesalchemy`` paster template: change ``<route>``
  declarations: rename ``renderer`` attribute to ``view_renderer``.

- Header values returned by the ``authtktauthenticationpolicy``
  ``remember`` and ``forget`` methods would be of type ``unicode``.
  This violated the WSGI spec, causing a ``TypeError`` to be raised
  when these headers were used under ``mod_wsgi``.

- If a BFG app that had a route matching the root URL was mounted
  under a path in modwsgi, ala ``WSGIScriptAlias /myapp
  /Users/chrism/projects/modwsgi/env/bfg.wsgi``, the home route (a
  route with the path of ``'/'`` or ``''``) would not match when the
  path ``/myapp`` was visited (only when the path ``/myapp/`` was
  visited).  This is now fixed: if the urldispatch root factory notes
  that the PATH_INFO is empty, it converts it to a single slash before
  trying to do matching.

Documentation
-------------

- In ``<route>`` declarations in tutorial ZCML, rename ``renderer``
  attribute to ``view_renderer`` (fwd compat).

- Fix various tutorials broken by 1.1a9 ``<route>`` directive changes.

Internal
--------

- Deal with a potential circref in the traversal module.

1.1a9 (2009-10-31)
==================

Bug Fixes
---------

- An incorrect ZCML conflict would be encountered when the
  ``request_param`` predicate attribute was used on the ZCML ``view``
  directive if any two otherwise same-predicated views had the
  combination of a predicate value with an ``=`` sign and one without
  (e.g. ``a`` vs. ``a=123``).

Features
--------

- In previous versions of BFG, the "root factory" (the ``get_root``
  callable passed to ``make_app`` or a function pointed to by the
  ``factory`` attribute of a route) was called with a "bare" WSGI
  environment.  In this version, and going forward, it will be called
  with a ``request`` object.  The request object passed to the factory
  implements dictionary-like methods in such a way that existing root
  factory code which expects to be passed an environ will continue to
  work.

- The ``__call__`` of a plugin "traverser" implementation (registered
  as an adapter for ``ITraverser`` or ``ITraverserFactory``) will now
  receive a *request* as the single argument to its ``__call__``
  method.  In previous versions it was passed a WSGI ``environ``
  object.  The request object passed to the factory implements
  dictionary-like methods in such a way that existing traverser code
  which expects to be passed an environ will continue to work.

- The ZCML ``route`` directive's attributes ``xhr``,
  ``request_method``, ``path_info``, ``request_param``, ``header`` and
  ``accept`` are now *route* predicates rather than *view* predicates.
  If one or more of these predicates is specified in the route
  configuration, all of the predicates must return true for the route
  to match a request.  If one or more of the route predicates
  associated with a route returns ``False`` when checked during a
  request, the route match fails, and the next match in the routelist
  is tried.  This differs from the previous behavior, where no route
  predicates existed and all predicates were considered view
  predicates, because in that scenario, the next route was not tried.

Documentation
-------------

- Various changes were made to narrative and API documentation
  supporting the change from passing a request rather than an environ
  to root factories and traversers.

Internal
--------

- The request implements dictionary-like methods that mutate and query
  the WSGI environ.  This is only for the purpose of backwards
  compatibility with root factories which expect an ``environ`` rather
  than a request.

- The ``repoze.bfg.request.create_route_request_factory`` function,
  which returned a request factory was removed in favor of a
  ``repoze.bfg.request.route_request_interface`` function, which
  returns an interface.

- The ``repoze.bfg.request.Request`` class, which is a subclass of
  ``webob.Request`` now defines its own ``__setattr__``,
  ``__getattr__`` and ``__delattr__`` methods, which override the
  default WebOb behavior.  The default WebOb behavior stores
  attributes of the request in ``self.environ['webob.adhoc_attrs']``,
  and retrieves them from that dictionary during a ``__getattr__``.
  This behavior was undesirable for speed and "expectation" reasons.
  Now attributes of the ``request`` are stored in ``request.__dict__``
  (as you otherwise might expect from an object that did not override
  these methods).

- The router no longer calls ``repoze.bfg.traversal._traverse`` and
  does its work "inline" (speed).

- Reverse the order in which the router calls the request factory and
  the root factory.  The request factory is now called first; the
  resulting request is passed to the root factory.

- The ``repoze.bfg.request.request_factory`` function has been
  removed.  Its functionality is no longer required.

- The "routes root factory" that wraps the default root factory when
  there are routes mentioned in the configuration now attaches an
  interface to the request via ``zope.interface.directlyProvides``.
  This replaces logic in the (now-gone)
  ``repoze.bfg.request.request_factory`` function.

- The ``route`` and ``view`` ZCML directives now register an interface
  as a named utility (retrieved from
  ``repoze.bfg.request.route_request_interface``) rather than a
  request factory (the previous return value of the now-missing 
  ``repoze.bfg.request.create_route_request_factory``.

- The ``repoze.bfg.functional`` module was renamed to
  ``repoze.bfg.compat``.

Backwards Incompatibilities
---------------------------

- Explicitly revert the feature introduced in 1.1a8: where the name
  ``root`` is available as an attribute of the request before a
  NewRequest event is emitted.  This makes some potential future
  features impossible, or at least awkward (such as grouping traversal
  and view lookup into a single adapter lookup).

- The ``containment``, ``attr`` and ``renderer`` attributes of the
  ``route`` ZCML directive were removed.

1.1a8 (2009-10-27)
==================

Features
--------

- Add ``path_info`` view configuration predicate.

- ``paster bfgshell`` now supports IPython if it's available for
  import.  Thanks to Daniel Holth for the initial patch.

- Add ``repoze.bfg.testing.registerSettings`` API, which is documented
  in the "repoze.bfg.testing" API chapter.  This allows for
  registration of "settings" values obtained via
  ``repoze.bfg.settings.get_settings()`` for use in unit tests.

- The name ``root`` is available as an attribute of the request
  slightly earlier now (before a NewRequest event is emitted).
  ``root`` is the result of the application "root factory".

- Added ``max_age`` parameter to ``authtktauthenticationpolicy`` ZCML
  directive.  If this value is set, it must be an integer representing
  the number of seconds which the auth tkt cookie will survive.
  Mainly, its existence allows the auth_tkt cookie to survive across
  browser sessions.

Bug Fixes
---------

- Fix bug encountered during "scan" (when ``<scan ..>`` directive is
  used in ZCML) introduced in 1.1a7.  Symptom: ``AttributeError:
  object has no attribute __provides__`` raised at startup time.

- The ``reissue_time`` argument to the ``authtktauthenticationpolicy``
  ZCML directive now actually works.  When it is set to an integer
  value, an authticket set-cookie header is appended to the response
  whenever a request requires authentication and 'now' minus the
  authticket's timestamp is greater than ``reissue_time`` seconds.

Documentation
-------------

- Add a chapter titled "Request and Response" to the narrative
  documentation, content cribbed from the WebOb documentation.

- Call out predicate attributes of ZCML directive within "Views"
  chapter.

- Fix route_url documentation (``_query`` argument documented as
  ``query`` and ``_anchor`` argument documented as ``anchor``).

Backwards Incompatibilities
---------------------------

- The ``authtkt`` authentication policy ``remember`` method now no
  longer honors ``token`` or ``userdata`` keyword arguments.

Internal
--------

- Change how ``bfg_view`` decorator works when used as a class method
  decorator.  In 1.1a7, the``scan``directive actually tried to grope
  every class in scanned package at startup time, calling ``dir``
  against each found class, and subsequently invoking ``getattr``
  against each thing found by ``dir`` to see if it was a method.  This
  led to some strange symptoms (e.g. ``AttributeError: object has no
  attribute __provides__``), and was generally just a bad idea.  Now,
  instead of groping classes for methods at startup time, we just
  cause the ``bfg_view`` decorator itself to populate the method's
  class' ``__dict__`` when it is used as a method decorator.  This
  also requires a nasty _getframe thing but it's slightly less nasty
  than the startup time groping behavior.  This is essentially a
  reversion back to 1.1a6 "grokking" behavior plus some special magic
  for using the ``bfg_view`` decorator as method decorator inside the
  ``bfg_view`` class itself.

- The router now checks for a ``global_response_headers`` attribute of
  the request object before returning a response.  If this value
  exists, it is presumed to be a sequence of two-tuples, representing
  a set of headers to append to the 'normal' response headers.  This
  feature is internal, rather than exposed externally, because it's
  unclear whether it will stay around in the long term.  It was added
  to support the ``reissue_time`` feature of the authtkt
  authentication policy.

- The interface ITraverserFactory is now just an alias for ITraverser.

1.1a7 (2009-10-18)
==================

Features
--------

- More than one ``@bfg_view`` decorator may now be stacked on top of
  any number of others.  Each invocation of the decorator registers a
  single view configuration.  For instance, the following combination
  of decorators and a function will register two view configurations
  for the same view callable::

    from repoze.bfg.view import bfg_view

    @bfg_view(name='edit')
    @bfg_view(name='change')
    def edit(context, request):
        pass

  This makes it possible to associate more than one view configuration
  with a single callable without requiring any ZCML.

- The ``@bfg_view`` decorator can now be used against a class method::

    from webob import Response
    from repoze.bfg.view import bfg_view

    class MyView(object):
        def __init__(self, context, request):
            self.context = context
            self.request = request

        @bfg_view(name='hello')
        def amethod(self):
            return Response('hello from %s!' % self.context)

  When the bfg_view decorator is used against a class method, a view
  is registered for the *class* (it's a "class view" where the "attr"
  happens to be the name of the method it is attached to), so the
  class it's defined within must have a suitable constructor: one that
  accepts ``context, request`` or just ``request``.

Documentation
-------------

- Added ``Changing the Traverser`` and ``Changing How
  :mod:`repoze.bfg.url.model_url` Generates a URL`` to the "Hooks"
  narrative chapter of the docs.

Internal
--------

- Remove ``ez_setup.py`` and imports of it within ``setup.py``.  In
  the new world, and as per virtualenv setup instructions, people will
  already have either setuptools or distribute.

1.1a6 (2009-10-15)
==================

Features
--------

- Add ``xhr``, ``accept``, and ``header`` view configuration
  predicates to ZCML view declaration, ZCML route declaration, and
  ``bfg_view`` decorator.  See the ``Views`` narrative documentation
  chapter for more information about these predicates.

- Add ``setUp`` and ``tearDown`` functions to the
  ``repoze.bfg.testing`` module.  Using ``setUp`` in a test setup and
  ``tearDown`` in a test teardown is now the recommended way to do
  component registry setup and teardown.  Previously, it was
  recommended that a single function named
  ``repoze.bfg.testing.cleanUp`` be called in both the test setup and
  tear down.  ``repoze.bfg.testing.cleanUp`` still exists (and will
  exist "forever" due to its widespread use); it is now just an alias
  for ``repoze.bfg.testing.setUp`` and is nominally deprecated.

- The BFG component registry is now available in view and event
  subscriber code as an attribute of the request
  ie. ``request.registry``.  This fact is currently undocumented
  except for this note, because BFG developers never need to interact
  with the registry directly anywhere else.

- The BFG component registry now inherits from ``dict``, meaning that
  it can optionally be used as a simple dictionary.  *Component*
  registrations performed against it via e.g. ``registerUtility``,
  ``registerAdapter``, and similar API methods are kept in a
  completely separate namespace than its dict members, so using the
  its component API methods won't effect the keys and values in the
  dictionary namespace.  Likewise, though the component registry
  "happens to be" a dictionary, use of mutating dictionary methods
  such as ``__setitem__`` will have no influence on any component
  registrations made against it.  In other words, the registry object
  you obtain via e.g. ``repoze.bfg.threadlocal.get_current_registry``
  or ``request.registry`` happens to be both a component registry and
  a dictionary, but using its component-registry API won't impact data
  added to it via its dictionary API and vice versa.  This is a
  forward compatibility move based on the goals of "marco".

- Expose and document ``repoze.bfg.testing.zcml_configure`` API.  This
  function populates a component registry from a ZCML file for testing
  purposes.  It is documented in the "Unit and Integration Testing"
  chapter.

Documentation
-------------

- Virtual hosting narrative docs chapter updated with info about
  ``mod_wsgi``.

- Point all index URLs at the literal 1.1 index (this alpha cycle may
  go on a while).

- Various tutorial test modules updated to use
  ``repoze.bfg.testing.setUp`` and ``repoze.bfg.testing.tearDown``
  methods in order to encourage this as best practice going forward.

- Added "Creating Integration Tests" section to unit testing narrative
  documentation chapter.  As a result, the name of the unittesting
  chapter is now "Unit and Integration Testing".

Backwards Incompatibilities
---------------------------

- Importing ``getSiteManager`` and ``get_registry`` from
  ``repoze.bfg.registry`` is no longer supported.  These imports were
  deprecated in repoze.bfg 1.0.  Import of ``getSiteManager`` should
  be done as ``from zope.component import getSiteManager``.  Import of
  ``get_registry`` should be done as ``from repoze.bfg.threadlocal
  import get_current_registry``.  This was done to prevent a circular
  import dependency.

- Code bases which alternately invoke both
  ``zope.testing.cleanup.cleanUp`` and ``repoze.bfg.testing.cleanUp``
  (treating them equivalently, using them interchangeably) in the
  setUp/tearDown of unit tests will begin to experience test failures
  due to lack of test isolation.  The "right" mechanism is
  ``repoze.bfg.testing.cleanUp`` (or the combination of
  ``repoze.bfg.testing.setUp`` and
  ``repoze.bfg.testing.tearDown``). but a good number of legacy
  codebases will use ``zope.testing.cleanup.cleanUp`` instead.  We
  support ``zope.testing.cleanup.cleanUp`` but not in combination with
  ``repoze.bfg.testing.cleanUp`` in the same codebase.  You should use
  one or the other test cleanup function in a single codebase, but not
  both.

Internal
--------

- Created new ``repoze.bfg.configuration`` module which assumes
  responsibilities previously held by the ``repoze.bfg.registry`` and
  ``repoze.bfg.router`` modules (avoid a circular import dependency).

- The result of the ``zope.component.getSiteManager`` function in unit
  tests set up with ``repoze.bfg.testing.cleanUp`` or
  ``repoze.bfg.testing.setUp`` will be an instance of
  ``repoze.bfg.registry.Registry`` instead of the global
  ``zope.component.globalregistry.base`` registry.  This also means
  that the threadlocal ZCA API functions such as ``getAdapter`` and
  ``getUtility`` as well as internal BFG machinery (such as
  ``model_url`` and ``route_url``) will consult this registry within
  unit tests. This is a forward compatibility move based on the goals
  of "marco".

- Removed ``repoze.bfg.testing.addCleanUp`` function and associated
  module-scope globals.  This was never an API.

1.1a5 (2009-10-10)
==================

Documentation
-------------

- Change "Traversal + ZODB" and "URL Dispatch + SQLAlchemy" Wiki
  tutorials to make use of the new-to-1.1 "renderer" feature (return
  dictionaries from all views).

- Add tests to the "URL Dispatch + SQLAlchemy" tutorial after the
  "view" step.

- Added a diagram of model graph traversal to the "Traversal"
  narrative chapter of the documentation.

- An ``exceptions`` API chapter was added, documenting the new
  ``repoze.bfg.exceptions`` module.

- Describe "request-only" view calling conventions inside the
  urldispatch narrative chapter, where it's most helpful.

- Add a diagram which explains the operation of the BFG router to the
  "Router" narrative chapter.

Features
--------

- Add a new ``repoze.bfg.testing`` API: ``registerRoute``, for
  registering routes to satisfy calls to
  e.g. ``repoze.bfg.url.route_url`` in unit tests.

- The ``notfound`` and ``forbidden`` ZCML directives now accept the
  following additional attributes: ``attr``, ``renderer``, and
  ``wrapper``.  These have the same meaning as they do in the context
  of a ZCML ``view`` directive.

- For behavior like Django's ``APPEND_SLASH=True``, use the
  ``repoze.bfg.view.append_slash_notfound_view`` view as the Not Found
  view in your application.  When this view is the Not Found view
  (indicating that no view was found), and any routes have been
  defined in the configuration of your application, if the value of
  ``PATH_INFO`` does not already end in a slash, and if the value of
  ``PATH_INFO`` *plus* a slash matches any route's path, do an HTTP
  redirect to the slash-appended PATH_INFO.  Note that this will
  *lose* ``POST`` data information (turning it into a GET), so you
  shouldn't rely on this to redirect POST requests.

- Speed up ``repoze.bfg.location.lineage`` slightly.

- Speed up ``repoze.bfg.encode.urlencode`` (nee'
  ``repoze.bfg.url.urlencode``) slightly.

- Speed up ``repoze.bfg.traversal.model_path``.

- Speed up ``repoze.bfg.traversal.model_path_tuple`` slightly.

- Speed up ``repoze.bfg.traversal.traverse`` slightly.

- Speed up ``repoze.bfg.url.model_url`` slightly.

- Speed up ``repoze.bfg.url.route_url`` slightly.

- Sped up ``repoze.bfg.traversal.ModelGraphTraverser:__call__``
  slightly.

- Minor speedup of ``repoze.bfg.router.Router.__call__``.

- New ``repoze.bfg.exceptions`` module was created to house exceptions
  that were previously sprinkled through various modules.

Internal
--------

- Move ``repoze.bfg.traversal._url_quote`` into ``repoze.bfg.encode``
  as ``url_quote``.

Deprecations
------------

- The import of ``repoze.bfg.view.NotFound`` is deprecated in favor of
  ``repoze.bfg.exceptions.NotFound``.  The old location still
  functions, but emits a deprecation warning.

- The import of ``repoze.bfg.security.Unauthorized`` is deprecated in
  favor of ``repoze.bfg.exceptions.Forbidden``.  The old location
  still functions but emits a deprecation warning.  The rename from
  ``Unauthorized`` to ``Forbidden`` brings parity to the name of
  the exception and the system view it invokes when raised.

Backwards Incompatibilities
---------------------------

- We previously had a Unicode-aware wrapper for the
  ``urllib.urlencode`` function named ``repoze.bfg.url.urlencode``
  which delegated to the stdlib function, but which marshalled all
  unicode values to utf-8 strings before calling the stdlib version.
  A newer replacement now lives in ``repoze.bfg.encode`` The
  replacement does not delegate to the stdlib.

  The replacement diverges from the stdlib implementation and the
  previous ``repoze.bfg.url`` url implementation inasmuch as its
  ``doseq`` argument is now a decoy: it always behaves in the
  ``doseq=True`` way (which is the only sane behavior) for speed
  purposes.

  The old import location (``repoze.bfg.url.urlencode``) still
  functions and has not been deprecated.

- In 0.8a7, the return value expected from an object implementing
  ``ITraverserFactory`` was changed from a sequence of values to a
  dictionary containing the keys ``context``, ``view_name``,
  ``subpath``, ``traversed``, ``virtual_root``, ``virtual_root_path``,
  and ``root``.  Until now, old-style traversers which returned a
  sequence have continued to work but have generated a deprecation
  warning.  In this release, traversers which return a sequence
  instead of a dictionary will no longer work.

1.1a4 (2009-09-23)
==================

Bug Fixes
---------

- On 64-bit Linux systems, views that were members of a multiview
  (orderings of views with predicates) were not evaluated in the
  proper order.  Symptom: in a configuration that had two views with
  the same name but one with a ``request_method=POST`` predicate and
  one without, the one without the predicate would be called
  unconditionally (even if the request was a POST request).  Thanks
  much to Sebastien Douche for providing the buildbots that pointed
  this out.

Documentation
-------------

- Added a tutorial which explains how to use ``repoze.session``
  (ZODB-based sessions) in a ZODB-based repoze.bfg app.

- Added a tutorial which explains how to add ZEO to a ZODB-based
  ``repoze.bfg`` application.

- Added a tutorial which explains how to run a ``repoze.bfg``
  application under `mod_wsgi <https://modwsgi.readthedocs.io/en/develop/>`_.
  See "Running a repoze.bfg Application under mod_wsgi" in the
  tutorials section of the documentation.

Features
--------

- Add a ``repoze.bfg.url.static_url`` API which is capable of
  generating URLs to static resources defined by the ``<static>`` ZCML
  directive.  See the "Views" narrative chapter's section titled
  "Generating Static Resource URLs" for more information.

- Add a ``string`` renderer.  This renderer converts a non-Response
  return value of any view callble into a string.  It is documented in
  the "Views" narrative chapter.

- Give the ``route`` ZCML directive the ``view_attr`` and
  ``view_renderer`` parameters (bring up to speed with 1.1a3
  features).  These can also be spelled as ``attr`` and ``renderer``.

Backwards Incompatibilities
---------------------------

- An object implementing the ``IRenderer`` interface (and
  ``ITemplateRenderer`, which is a subclass of ``IRenderer``) must now
  accept an extra ``system`` argument in its ``__call__`` method
  implementation.  Values computed by the system (as opposed to by the
  view) are passed by the system in the ``system`` parameter, which
  will always be a dictionary.  Keys in the dictionary include:
  ``view`` (the view object that returned the value),
  ``renderer_name`` (the template name or simple name of the
  renderer), ``context`` (the context object passed to the view), and
  ``request`` (the request object passed to the view).  Previously
  only ITemplateRenderers received system arguments as elements inside
  the main ``value`` dictionary.

Internal
--------

- The way ``bfg_view`` declarations are scanned for has been modified.
  This should have no external effects.

- Speed: do not register an ITraverserFactory in configure.zcml;
  instead rely on queryAdapter and a manual default to
  ModelGraphTraverser.

- Speed: do not register an IContextURL in configure.zcml; instead
  rely on queryAdapter and a manual default to TraversalContextURL.

- General speed microimprovements for helloworld benchmark: replace
  try/excepts with statements which use 'in' keyword.

1.1a3 (2009-09-16)
==================

Documentation
-------------

- The "Views" narrative chapter in the documentation has been updated
  extensively to discuss "renderers".

Features
--------

- A ``renderer`` attribute has been added to view configurations,
  replacing the previous (1.1a2) version's ``template`` attribute.  A
  "renderer" is an object which accepts the return value of a view and
  converts it to a string.  This includes, but is not limited to,
  templating systems.

- A new interface named ``IRenderer`` was added.  The existing
  interface, ``ITemplateRenderer`` now derives from this new
  interface.  This interface is internal.

- A new interface named ``IRendererFactory`` was added.  An existing
  interface named ``ITemplateRendererFactory`` now derives from this
  interface.  This interface is internal.

- The ``view`` attribute of the ``view`` ZCML directive is no longer
  required if the ZCML directive also has a ``renderer`` attribute.
  This is useful when the renderer is a template renderer and no names
  need be passed to the template at render time.

- A new zcml directive ``renderer`` has been added.  It is documented
  in the "Views" narrative chapter of the documentation.

- A ZCML ``view`` directive (and the associated ``bfg_view``
  decorator) can now accept a "wrapper" value.  If a "wrapper" value
  is supplied, it is the value of a separate view's *name* attribute.
  When a view with a ``wrapper`` attribute is rendered, the "inner"
  view is first rendered normally.  Its body is then attached to the
  request as "wrapped_body", and then a wrapper view name is looked up
  and rendered (using ``repoze.bfg.render_view_to_response``), passed
  the request and the context.  The wrapper view is assumed to do
  something sensible with ``request.wrapped_body``, usually inserting
  its structure into some other rendered template.  This feature makes
  it possible to specify (potentially nested) "owrap" relationships
  between views using only ZCML or decorators (as opposed always using
  ZPT METAL and analogues to wrap view renderings in outer wrappers).

Dependencies
------------

- When used under Python < 2.6, BFG now has an installation time
  dependency on the ``simplejson`` package.

Deprecations
------------

- The ``repoze.bfg.testing.registerDummyRenderer`` API has been
  deprecated in favor of
  ``repoze.bfg.testing.registerTemplateRenderer``.  A deprecation
  warning is *not* issued at import time for the former name; it will
  exist "forever"; its existence has been removed from the
  documentation, however.

- The ``repoze.bfg.templating.renderer_from_cache`` function has been
  moved to ``repoze.bfg.renderer.template_renderer_factory``.  This
  was never an API, but code in the wild was spotted that used it.  A
  deprecation warning is issued at import time for the former.

Backwards Incompatibilities
---------------------------

- The ``ITemplateRenderer`` interface has been changed.  Previously
  its ``__call__`` method accepted ``**kw``.  It now accepts a single
  positional parameter named ``kw`` (REVISED: it accepts two
  positional parameters as of 1.1a4: ``value`` and ``system``).  This
  is mostly an internal change, but it was exposed in APIs in one
  place: if you've used the
  ``repoze.bfg.testing.registerDummyRenderer`` API in your tests with
  a custom "renderer" argument with your own renderer implementation,
  you will need to change that renderer implementation to accept
  ``kw`` instead of ``**kw`` in its ``__call__`` method (REVISED: make
  it accept ``value`` and ``system`` positional arguments as of 1.1a4).

- The ``ITemplateRendererFactory`` interface has been changed.
  Previously its ``__call__`` method accepted an ``auto_reload``
  keyword parameter.  Now its ``__call__`` method accepts no keyword
  parameters.  Renderers are now themselves responsible for
  determining details of auto-reload.  This is purely an internal
  change.  This interface was never external.

- The ``template_renderer`` ZCML directive introduced in 1.1a2 has
  been removed.  It has been replaced by the ``renderer`` directive.

- The previous release (1.1a2) added a view configuration attribute
  named ``template``.  In this release, the attribute has been renamed
  to ``renderer``.  This signifies that the attribute is more generic:
  it can now be not just a template name but any renderer name (ala
  ``json``).  

- In the previous release (1.1a2), the Chameleon text template
  renderer was used if the system didn't associate the ``template``
  view configuration value with a filename with a "known" extension.
  In this release, you must use a ``renderer`` attribute which is a
  path that ends with a ``.txt`` extension
  (e.g. ``templates/foo.txt``) to use the Chameleon text renderer.

1.1a2 (2009-09-14)
==================

Features
--------

- A ZCML ``view`` directive (and the associated ``bfg_view``
  decorator) can now accept an "attr" value.  If an "attr" value is
  supplied, it is considered a method named of the view object to be
  called when the response is required.  This is typically only good
  for views that are classes or instances (not so useful for
  functions, as functions typically have no methods other than
  ``__call__``).

- A ZCML ``view`` directive (and the associated ``bfg_view``
  decorator) can now accept a "template" value.  If a "template" value
  is supplied, and the view callable returns a dictionary, the
  associated template is rendered with the dictionary as keyword
  arguments.  See the section named "Views That Have a ``template``"
  in the "Views" narrative documentation chapter for more information.

1.1a1 (2009-09-06)
==================

Bug Fixes
---------

- "tests" module removed from the bfg_alchemy paster template; these
  tests didn't work.

- Bugfix: the ``discriminator`` for the ZCML "route" directive was
  incorrect.  It was possible to register two routes that collided
  without the system spitting out a ConfigurationConflictError at
  startup time.

Features
--------

- Feature addition: view predicates.  These are exposed as the
  ``request_method``, ``request_param``, and ``containment``
  attributes of a ZCML ``view`` declaration, or the respective
  arguments to a ``@bfg_view`` decorator.  View predicates can be used
  to register a view for a more precise set of environment parameters
  than was previously possible.  For example, you can register two
  views with the same ``name`` with different ``request_param``
  attributes.  If the ``request.params`` dict contains 'foo'
  (request_param="foo"), one view might be called; if it contains
  'bar' (request_param="bar"), another view might be called.
  ``request_param`` can also name a key/value pair ala ``foo=123``.
  This will match only when the ``foo`` key is in the request.params
  dict and it has the value '123'.  This particular example makes it
  possible to write separate view functions for different form
  submissions.  The other predicates, ``containment`` and
  ``request_method`` work similarly.  ``containment`` is a view
  predicate that will match only when the context's graph lineage has
  an object possessing a particular class or interface, for example.
  ``request_method`` is a view predicate that will match when the HTTP
  ``REQUEST_METHOD`` equals some string (eg. 'POST').

- The ``@bfg_view`` decorator now accepts three additional arguments:
  ``request_method``, ``request_param``, and ``containment``.
  ``request_method`` is used when you'd like the view to match only a
  request with a particular HTTP ``REQUEST_METHOD``; a string naming
  the ``REQUEST_METHOD`` can also be supplied as ``request_type`` for
  backwards compatibility.  ``request_param`` is used when you'd like
  a view to match only a request that contains a particular
  ``request.params`` key (with or without a value).  ``containment``
  is used when you'd like to match a request that has a context that
  has some class or interface in its graph lineage.  These are
  collectively known as "view predicates".

- The ``route`` ZCML directive now honors ``view_request_method``,
  ``view_request_param`` and ``view_containment`` attributes, which
  pass along these values to the associated view if any is provided.
  Additionally, the ``request_type`` attribute can now be spelled as
  ``view_request_type``, and ``permission`` can be spelled as
  ``view_permission``.  Any attribute which starts with ``view_`` can
  now be spelled without the ``view_`` prefix, so ``view_for`` can be
  spelled as ``for`` now, etc.  Both forms are documented in the
  urldispatch narrative documentation chapter.

- The ``request_param`` ZCML view directive attribute (and its
  ``bfg_view`` decorator cousin) can now specify both a key and a
  value.  For example, ``request_param="foo=123"`` means that the foo
  key must have a value of ``123`` for the view to "match".

- Allow ``repoze.bfg.traversal.find_interface`` API to use a class
  object as the argument to compare against the ``model`` passed in.
  This means you can now do ``find_interface(model, SomeClass)`` and
  the first object which is found in the lineage which has
  ``SomeClass`` as its class (or the first object found which has
  ``SomeClass`` as any of its superclasses) will be returned.

- Added ``static`` ZCML directive which registers a route for a view
  that serves up files in a directory.  See the "Views" narrative
  documentation chapter's "Serving Static Resources Using a ZCML
  Directive" section for more information.

- The ``repoze.bfg.view.static`` class now accepts a string as its
  first argument ("root_dir") that represents a package-relative name
  e.g. ``somepackage:foo/bar/static``.  This is now the preferred
  mechanism for spelling package-relative static paths using this
  class.  A ``package_name`` keyword argument has been left around for
  backwards compatibility.  If it is supplied, it will be honored.

- The API ``repoze.bfg.testing.registerView`` now takes a
  ``permission`` argument.  Use this instead of using
  ``repoze.bfg.testing.registerViewPermission``.

- The ordering of route declarations vs. the ordering of view
  declarations that use a "route_name" in ZCML no longer matters.
  Previously it had been impossible to use a route_name from a route
  that had not yet been defined in ZCML (order-wise) within a "view"
  declaration.

- The repoze.bfg router now catches both
  ``repoze.bfg.security.Unauthorized`` and
  ``repoze.bfg.view.NotFound`` exceptions while rendering a view.
  When the router catches an ``Unauthorized``, it returns the
  registered forbidden view.  When the router catches a ``NotFound``,
  it returns the registered notfound view.

Internal
--------

- Change urldispatch internals: Route object is now constructed using
  a path, a name, and a factory instead of a name, a matcher, a
  generator, and a factory.

- Move (non-API) default_view, default_forbidden_view, and
  default_notfound_view functions into the ``repoze.bfg.view`` module
  (moved from ``repoze.bfg.router``).

- Removed ViewPermissionFactory from ``repoze.bfg.security``.  View
  permission checking is now done by registering and looking up an
  ISecuredView.

- The ``static`` ZCML directive now uses a custom root factory when
  constructing a route.

- The interface ``IRequestFactories`` was removed from the
  repoze.bfg.interfaces module.  This interface was never an API.

- The function named ``named_request_factories`` and the data
  structure named ``DEFAULT_REQUEST_FACTORIES`` have been removed from
  the ``repoze.bfg.request`` module.  These were never APIs.

- The ``IViewPermissionFactory`` interface has been removed.  This was
  never an API.

Documentation
-------------

- Request-only-convention examples in the "Views" narrative
  documentation were broken.

- Fixed documentation bugs related to forget and remember in security API
  docs.

- Fixed documentation for ``repoze.bfg.view.static`` (in narrative
  ``Views`` chapter).

Deprecations
------------

- The API ``repoze.bfg.testing.registerViewPermission`` has been
  deprecated.

Backwards Incompatibilities
---------------------------

- The interfaces ``IPOSTRequest``, ``IGETRequest``, ``IPUTRequest``,
  ``IDELETERequest``, and ``IHEADRequest`` have been removed from the
  ``repoze.bfg.interfaces`` module.  These were not documented as APIs
  post-1.0.  Instead of using one of these, use a ``request_method``
  ZCML attribute or ``request_method`` bfg_view decorator parameter
  containing an HTTP method name (one of ``GET``, ``POST``, ``HEAD``,
  ``PUT``, ``DELETE``) instead of one of these interfaces if you were
  using one explicitly.  Passing a string in the set (``GET``,
  ``HEAD``, ``PUT``, ``POST``, ``DELETE``) as a ``request_type``
  argument will work too.  Rationale: instead of relying on interfaces
  attached to the request object, BFG now uses a "view predicate" to
  determine the request type.

- Views registered without the help of the ZCML ``view`` directive are
  now responsible for performing their own authorization checking.

- The ``registry_manager`` backwards compatibility alias importable
  from "repoze.bfg.registry", deprecated since repoze.bfg 0.9 has been
  removed.  If you are tring to use the registry manager within a
  debug script of your own, use a combination of the
  "repoze.bfg.paster.get_app" and "repoze.bfg.scripting.get_root" APIs
  instead.

- The ``INotFoundAppFactory`` interface has been removed; it has
  been deprecated since repoze.bfg 0.9.  If you have something like
  the following in your ``configure.zcml``::

   <utility provides="repoze.bfg.interfaces.INotFoundAppFactory"
            component="helloworld.factories.notfound_app_factory"/>

  Replace it with something like::

   <notfound 
       view="helloworld.views.notfound_view"/>

  See "Changing the Not Found View" in the "Hooks" chapter of the
  documentation for more information.

- The ``IUnauthorizedAppFactory`` interface has been removed; it has
  been deprecated since repoze.bfg 0.9.  If you have something like
  the following in your ``configure.zcml``::

   <utility provides="repoze.bfg.interfaces.IUnauthorizedAppFactory"
            component="helloworld.factories.unauthorized_app_factory"/>

  Replace it with something like::

   <forbidden
       view="helloworld.views.forbidden_view"/>

  See "Changing the Forbidden View" in the "Hooks" chapter of the
  documentation for more information.

- ``ISecurityPolicy``-based security policies, deprecated since
  repoze.bfg 0.9, have been removed.  If you have something like this
  in your ``configure.zcml``, it will no longer work::

     <utility
       provides="repoze.bfg.interfaces.ISecurityPolicy"
       factory="repoze.bfg.security.RemoteUserInheritingACLSecurityPolicy"
      />

  If ZCML like the above exists in your application, you will receive
  an error at startup time.  Instead of the above, you'll need
  something like::

     <remoteuserauthenticationpolicy/>
     <aclauthorizationpolicy/>

  This is just an example.  See the "Security" chapter of the
  repoze.bfg documentation for more information about configuring
  security policies.

- Custom ZCML directives which register an authentication or
  authorization policy (ala "authtktauthenticationpolicy" or
  "aclauthorizationpolicy") should register the policy "eagerly" in
  the ZCML directive instead of from within a ZCML action.  If an
  authentication or authorization policy is not found in the component
  registry by the view machinery during deferred ZCML processing, view
  security will not work as expected.

1.0.1 (2009-07-22)
==================

- Added support for ``has_resource``, ``resource_isdir``, and
  ``resource_listdir`` to the resource "OverrideProvider"; this fixes
  a bug with a symptom that a file could not be overridden in a
  resource directory unless a file with the same name existed in the
  original directory being overridden.

- Fixed documentation bug showing invalid test for values from the
  ``matchdict``:  they are stored as attributes of the ``Article``, rather
  than subitems.

- Fixed documentation bug showing wrong environment key for the ``matchdict``
  produced by the matching route.

- Added a workaround for a bug in Python 2.6, 2.6.1, and 2.6.2 having
  to do with a recursion error in the mimetypes module when trying to
  serve static files from Paste's FileApp:
  https://bugs.python.org/issue5853.  Symptom: File
  "/usr/lib/python2.6/mimetypes.py", line 244, in guess_type return
  guess_type(url, strict) RuntimeError: maximum recursion depth
  exceeded.  Thanks to Armin Ronacher for identifying the symptom and
  pointing out a fix.

- Minor edits to tutorials for accuracy based on feedback.

- Declared Paste and PasteDeploy dependencies.

1.0 (2009-07-05)
================

- Retested and added some content to GAE tutorial.

- Edited "Extending" narrative docs chapter.

- Added "Deleting the Database" section to the "Defining Models"
  chapter of the traversal wiki tutorial.

- Spell checking of narratives and tutorials.

1.0b2 (2009-07-03)
==================

- ``remoteuserauthenticationpolicy`` ZCML directive didn't work
  without an ``environ_key`` directive (didn't match docs).

- Fix ``configure_zcml`` filespec check on Windows.  Previously if an
  absolute filesystem path including a drive letter was passed as
  ``filename`` (or as ``configure_zcml`` in the options dict) to
  ``repoze.bfg.router.make_app``, it would be treated as a
  package:resource_name specification.

- Fix inaccuracies and import errors in bfgwiki (traversal+ZODB) and
  bfgwiki2 (urldispatch+SA) tutorials.

- Use bfgsite index for all tutorial setup.cfg files.

- Full documentation grammar/style/spelling audit.

1.0b1 (2009-07-02)
==================

Features
--------

- Allow a Paste config file (``configure_zcml``) value or an
  environment variable (``BFG_CONFIGURE_ZCML``) to name a ZCML file
  (optionally package-relative) that will be used to bootstrap the
  application.  Previously, the integrator could not influence which
  ZCML file was used to do the boostrapping (only the original
  application developer could do so).

Documentation
-------------

- Added a "Resources" chapter to the narrative documentation which
  explains how to override resources within one package from another
  package.

- Added an "Extending" chapter to the narrative documentation which
  explains how to extend or modify an existing BFG application using
  another Python package and ZCML.

1.0a9 (2009-07-01)
==================

Features
--------

- Make it possible to pass strings in the form
  "package_name:relative/path" to APIs like ``render_template``,
  ``render_template_to_response``, and ``get_template``.  Sometimes
  the package in which a caller lives is a direct namespace package,
  so the module which is returned is semi-useless for navigating from.
  In this way, the caller can control the horizontal and vertical of
  where things get looked up from.

1.0a8 (2009-07-01)
==================

Deprecations
------------

- Deprecate the ``authentication_policy`` and ``authorization_policy``
  arguments to ``repoze.bfg.router.make_app``.  Instead, developers
  should use the various authentication policy ZCML directives
  (``repozewho1authenticationpolicy``,
  ``remoteuserauthenticationpolicy`` and
  ``authtktauthenticationpolicy``) and the `aclauthorizationpolicy``
  authorization policy directive as described in the changes to the
  "Security" narrative documentation chapter and the wiki tutorials.

Features
--------

- Add three new ZCML directives which configure authentication
  policies:

  - ``repozewho1authenticationpolicy``

  - ``remoteuserauthenticationpolicy``

  - ``authtktauthenticationpolicy``

- Add a new ZCML directive which configures an ACL authorization
  policy named ``aclauthorizationpolicy``.

Bug Fixes
---------

- Bug fix: when a ``repoze.bfg.resource.PackageOverrides`` class was
  instantiated, and the package it was overriding already had a
  ``__loader__`` attribute, it would fail at startup time, even if the
  ``__loader__`` attribute was another PackageOverrides instance.  We
  now replace any ``__loader__`` that is also a PackageOverrides
  instance.  Symptom: ``ConfigurationExecutionError: <type
  'exceptions.TypeError'>: Package <module 'karl.views' from
  '/Users/chrism/projects/osi/bfgenv/src/karl/karl/views/__init__.pyc'>
  already has a __loader__ (probably a module in a zipped egg)``.

1.0a7 (2009-06-30)
==================

Features
--------

- Add a ``reload_resources`` configuration file setting (aka the
  ``BFG_RELOAD_RESOURCES`` environment variable).  When this is set to
  true, the server never needs to be restarted when moving files
  between directory resource overrides (esp. for templates currently).

- Add a ``reload_all`` configuration file setting (aka the
  ``BFG_RELOAD_ALL`` environment variable) that implies both
  ``reload_resources`` and ``reload_templates``.

- The ``static`` helper view class now uses a ``PackageURLParser`` in
  order to allow for the overriding of static resources (CSS / logo
  files, etc) using the ``resource`` ZCML directive.  The
  ``PackageURLParser`` class was added to a (new) ``static`` module in
  BFG; it is a subclass of the ``StaticURLParser`` class in
  ``paste.urlparser``.

- The ``repoze.bfg.templating.renderer_from_cache`` function now
  checks for the ``reload_resources`` setting; if it's true, it does
  not register a template renderer (it won't use the registry as a
  template renderer cache).

Documentation
-------------

- Add ``pkg_resources`` to the glossary.

- Update the "Environment" docs to note the existence of
  ``reload_resources`` and ``reload_all``.

- Updated the ``bfg_alchemy`` paster template to include two views:
  the view on the root shows a list of links to records;  the view on
  a record shows the details for that object.

Internal
--------

- Use a colon instead of a tab as the separator between package name
  and relpath to form the "spec" when register a ITemplateRenderer.

- Register a ``repoze.bfg.resource.OverrideProvider`` as a
  pkg_resources provider only for modules which are known to have
  overrides, instead of globally, when a <resource> directive is used
  (performance).

1.0a6 (2009-06-29)
==================

Bug Fixes
---------

- Use ``caller_package`` function instead of ``caller_module``
  function within ``templating`` to avoid needing to name the caller
  module in resource overrides (actually match docs).

- Make it possible to override templates stored directly in a module
  with templates in a subdirectory of the same module, stored directly
  within another module, or stored in a subdirectory of another module
  (actually match docs).

1.0a5 (2009-06-28)
==================

Features
--------

- A new ZCML directive exists named "resource".  This ZCML directive
  allows you to override Chameleon templates within a package (both
  directories full of templates and individual template files) with
  other templates in the same package or within another package.  This
  allows you to "fake out" a view's use of a template, causing it to
  retrieve a different template than the one actually named by a
  relative path to a call like
  ``render_template_to_response('templates/mytemplate.pt')``.  For
  example, you can override a template file by doing::

    <resource
      to_override="some.package:templates/mytemplate.pt"
      override_with="another.package:othertemplates/anothertemplate.pt"
     />

  The string passed to "to_override" and "override_with" is named a
  "specification".  The colon separator in a specification separates
  the package name from a package-relative directory name.  The colon
  and the following relative path are optional.  If they are not
  specified, the override attempts to resolve every lookup into a
  package from the directory of another package.  For example::

    <resource
      to_override="some.package"
      override_with="another.package"
     />


  Individual subdirectories within a package can also be overridden::

    <resource
      to_override="some.package:templates/"
      override_with="another.package:othertemplates/"
     />

  If you wish to override a directory with another directory, you must
  make sure to attach the slash to the end of both the ``to_override``
  specification and the ``override_with`` specification.  If you fail
  to attach a slash to the end of a specification that points a
  directory, you will get unexpected results.  You cannot override a
  directory specification with a file specification, and vice versa (a
  startup error will occur if you try).

  You cannot override a resource with itself (a startup error will
  occur if you try).

  Only individual *package* resources may be overridden.  Overrides
  will not traverse through subpackages within an overridden package.
  This means that if you want to override resources for both
  ``some.package:templates``, and ``some.package.views:templates``,
  you will need to register two overrides.

  The package name in a specification may start with a dot, meaning
  that the package is relative to the package in which the ZCML file
  resides.  For example::

    <resource
      to_override=".subpackage:templates/"
      override_with="another.package:templates/"
     />

  Overrides for the same ``to_overrides`` specification can be named
  multiple times within ZCML.  Each ``override_with`` path will be
  consulted in the order defined within ZCML, forming an override
  search path.

  Resource overrides can actually override resources other than
  templates.  Any software which uses the ``pkg_resources``
  ``get_resource_filename``, ``get_resource_stream`` or
  ``get_resource_string`` APIs will obtain an overridden file when an
  override is used.  However, the only built-in facility which uses
  the ``pkg_resources`` API within BFG is the templating stuff, so we
  only call out template overrides here.

- Use the ``pkg_resources`` API to locate template filenames instead
  of dead-reckoning using the ``os.path`` module.

- The ``repoze.bfg.templating`` module now uses ``pkg_resources`` to
  locate and register template files instead of using an absolute
  path name.

1.0a4 (2009-06-25)
==================

Features
--------

- Cause ``:segment`` matches in route paths to put a Unicode-decoded
  and URL-dequoted value in the matchdict for the value matched.
  Previously a non-decoded non-URL-dequoted string was placed in the
  matchdict as the value.

- Cause ``*remainder`` matches in route paths to put a *tuple* in the
  matchdict dictionary in order to be able to present Unicode-decoded
  and URL-dequoted values for the traversal path.  Previously a
  non-decoded non-URL-dequoted string was placed in the matchdict as
  the value.

- Add optional ``max_age`` keyword value to the ``remember`` method of
  ``repoze.bfg.authentication.AuthTktAuthenticationPolicy``; if this
  value is passed to ``remember``, the generated cookie will have a
  corresponding Max-Age value.

Documentation
-------------

- Add information to the URL Dispatch narrative documentation about
  path pattern matching syntax.

Bug Fixes
---------

- Make ``route_url`` URL-quote segment replacements during generation.
  Remainder segments are not quoted.

1.0a3 (2009-06-24)
==================

Implementation Changes
----------------------

- ``repoze.bfg`` no longer relies on the Routes package to interpret
  URL paths.  All known existing ``path`` patterns will continue to
  work with the reimplemented logic, which lives in
  ``repoze.bfg.urldispatch``.  ``<route>`` ZCML directives which use
  certain attributes (uncommon ones) may not work (see "Backwards
  Incompatibilities" below).

Bug Fixes
---------

- ``model_url`` when passed a request that was generated as a result
  of a route match would fail in a call to ``route.generate``.

- BFG-on-GAE didn't work due to a corner case bug in the fallback
  Python implementation of ``threading.local`` (symptom:
  "Initialization arguments are not supported").  Thanks to Michael
  Bernstein for the bug report.

Documentation
-------------

- Added a "corner case" explanation to the "Hybrid Apps" chapter
  explaining what to do when "the wrong" view is matched.

- Use ``repoze.bfg.url.route_url`` API in tutorials rather than Routes
  ``url_for`` API.

Features
--------

- Added the ``repoze.bfg.url.route_url`` API.  This API allows you to
  generate URLs based on ``<route>`` declarations.  See the URL
  Dispatch narrative chapter and the "repoze.bfg.url" module API
  documentation for more information.

Backwards Incompatibilities
---------------------------

- As a result of disusing Routes, using the Routes ``url_for`` API
  inside a BFG application (as was suggested by previous iterations of
  tutorials) will no longer work.  Use the
  ``repoze.bfg.url.route_url`` method instead.

- The following attributes on the ``<route>`` ZCML directive no longer
  work: ``encoding``, ``static``, ``filter``, ``condition_method``,
  ``condition_subdomain``, ``condition_function``, ``explicit``, or
  ``subdomains``.  These were all Routes features.

- The ``<route>`` ZCML directive no longer supports the
  ``<requirement>`` subdirective.  This was a Routes feature.

1.0a2 (2009-06-23)
==================

Bug Fixes
---------

- The ``bfg_routesalchemy`` paster template app tests failed due to a
  mismatch between test and view signatures.

Features
--------

- Add a ``view_for`` attribute to the ``route`` ZCML directive.  This
  attribute should refer to an interface or a class (ala the ``for``
  attribute of the ``view`` ZCML directive).

Documentation
-------------

- Conditional documentation in installation section ("how to install a
  Python interpreter").

Backwards Incompatibilities
---------------------------

- The ``callback`` argument of the ``repoze.bfg.authentication``
  authentication policies named ``RepozeWho1AuthenticationPolicy``,
  ``RemoteUserAuthenticationPolicy``, and
  ``AuthTktAuthenticationPolicy`` now must accept two positional
  arguments: the original argument accepted by each (userid or
  identity) plus a second argument, which will be the current request.
  Apologies, this is required to service finding groups when there is
  no "global" database connection.

1.0a1 (2009-06-22)
==================

Features
--------

- A new ZCML directive was added named ``notfound``.  This ZCML
  directive can be used to name a view that should be invoked when the
  request can't otherwise be resolved to a view callable.  For example::

    <notfound 
        view="helloworld.views.notfound_view"/>

- A new ZCML directive was added named ``forbidden``.  This ZCML
  directive can be used to name a view that should be invoked when a
  view callable for a request is found, but cannot be invoked due to
  an authorization failure.  For example::

   <forbidden
       view="helloworld.views.forbidden_view"/>

- Allow views to be *optionally* defined as callables that accept only
  a request object, instead of both a context and a request (which
  still works, and always will).  The following types work as views in
  this style:

  - functions that accept a single argument ``request``, e.g.::

      def aview(request):
          pass

  - new and old-style classes that have an ``__init__`` method that
    accepts ``self, request``, e.g.::

      def View(object):
          __init__(self, request):
             pass

  - Arbitrary callables that have a ``__call__`` method that accepts
    ``self, request``, e.g.::

      def AView(object):
          def __call__(self, request):
             pass
      view = AView()

  This likely should have been the calling convention all along, as
  the request has ``context`` as an attribute already, and with views
  called as a result of URL dispatch, having the context in the
  arguments is not very useful.  C'est la vie.

- Cache the absolute path in the caller's package globals within
  ``repoze.bfg.path`` to get rid of repeated (expensive) calls to
  os.path.abspath.

- Add ``reissue_time`` and ``timeout`` parameters to
  ``repoze.bfg.authentication.AuthTktAuthenticationPolicy``
  constructor.  If these are passed, cookies will be reset every so
  often (cadged from the same change to repoze.who lately).

- The matchdict related to the matching of a Routes route is available
  on the request as the ``matchdict`` attribute:
  ``request.matchdict``.  If no route matched, this attribute will be
  None.

- Make 404 responses slightly cheaper by showing
  ``environ["PATH_INFO"]`` on the notfound result page rather than the
  fullly computed URL.

- Move LRU cache implementation into a separate package
  (``repoze.lru``).

- The concepts of traversal and URL dispatch have been unified.  It is
  now possible to use the same sort of factory as both a traversal
  "root factory" and what used to be referred to as a urldispatch
  "context factory".

- When the root factory argument (as a first argument) passed to
  ``repoze.bfg.router.make_app`` is ``None``, a *default* root factory
  is used.  This is in support of using routes as "root finders"; it
  supplants the idea that there is a default
  ``IRoutesContextFactory``.

- The `view`` ZCML statement and the ``repoze.bfg.view.bfg_view``
  decorator now accept an extra argument: ``route_name``.  If a
  ``route_name`` is specified, it must match the name of a previously
  defined ``route`` statement.  When it is specified, the view will
  only be called when that route matches during a request.

- It is now possible to perform traversal *after* a route has matched.
  Use the pattern ``*traverse`` in a ``<route>`` ``path`` attribute
  within ZCML, and the path remainder which it matches will be used as
  a traversal path.

- When any route defined matches, the WSGI environment will now
  contain a key ``bfg.routes.route`` (the Route object which matched),
  and a key ``bfg.routes.matchdict`` (the result of calling route.match).

Deprecations
------------

- Utility registrations against
  ``repoze.bfg.interfaces.INotFoundView`` and
  ``repoze.bfg.interfaces.IForbiddenView`` are now deprecated.  Use
  the ``notfound`` and ``forbidden`` ZCML directives instead (see the
  "Hooks" chapter for more information).  Such registrations will
  continue to work, but the notfound and forbidden directives do
  "extra work" to ensure that the callable named by the directive can
  be called by the router even if it's a class or
  request-argument-only view.

Removals
--------

- The ``IRoutesContext``, ``IRoutesContextFactory``, and
  ``IContextNotFound`` interfaces were removed from
  ``repoze.bfg.interfaces``.  These were never APIs.

- The ``repoze.bfg.urldispatch.RoutesContextNotFound``,
  ``repoze.bfg.urldispatch.RoutesModelTraverser`` and
  ``repoze.bfg.urldispatch.RoutesContextURL`` classes were removed.
  These were also never APIs.

Backwards Incompatibilities
---------------------------

- Moved the ``repoze.bfg.push`` module, which implemented the ``pushpage``
  decorator, into a separate distribution, ``repoze.bfg.pushpage``.
  Applications which used this decorator should continue to work after
  adding that distribution to their installation requirements.

- Changing the default request factory via an IRequestFactory utility
  registration (as used to be documented in the "Hooks" chapter's
  "Changing the request factory" section) is no longer supported.  The
  dance to manufacture a request is complicated as a result of
  unifying traversal and url dispatch, making it highly unlikely for
  anyone to be able to override it properly.  For those who just want
  to decorate or modify a request, use a NewRequestEvent subscriber
  (see the Events chapter in the documentation).

- The ``repoze.bfg.IRequestFactory`` interface was removed.  See the
  bullet above for why.

- Routes "context factories" (spelled as the factory argument to a
  route statement in ZCML) must now expect the WSGI environ as a
  single argument rather than a set of keyword arguments.  They can
  obtain the match dictionary by asking for
  environ['bfg.routes.matchdict'].  This is the same set of keywords
  that used to be passed to urldispatch "context factories" in BFG 0.9
  and below.

- Using the ``@zope.component.adapter`` decorator on a bfg view
  function no longer works.  Use the ``@repoze.bfg.view.bfg_view``
  decorator instead to mark a function (or a class) as a view.

- The name under which the matching route object is found in the
  environ was changed from ``bfg.route`` to ``bfg.routes.route``.

- Finding the root is now done *before* manufacturing a request object
  (and sending a new request event) within the router (it used to be
  performed afterwards).

- Adding ``*path_info`` to a route no longer changes the PATH_INFO for
  a request that matches using URL dispatch.  This feature was only
  there to service the ``repoze.bfg.wsgi.wsgiapp2`` decorator and it
  did it wrong; use ``*subpath`` instead now.

- The values of ``subpath``, ``traversed``, and ``virtual_root_path``
  attached to the request object are always now tuples instead of
  lists (performance).

Bug Fixes
---------

- The ``bfg_alchemy`` Paster template named "repoze.tm" in its
  pipeline rather than "repoze.tm2", causing the startup to fail.

- Move BBB logic for registering an
  IAuthenticationPolicy/IForbiddenView/INotFoundView based on older
  concepts from the router module's ``make_app`` function into the
  ``repoze.bfg.zcml.zcml_configure`` callable, to service
  compatibility with scripts that use "zope.configuration.xmlconfig"
  (replace with ``repoze.bfg.zml.zcml_configure`` as necessary to get
  BBB logic)

Documentation
-------------

- Add interface docs related to how to create authentication policies
  and authorization policies to the "Security" narrative chapter.

- Added a (fairly sad) "Combining Traversal and URL Dispatch" chapter
  to the narrative documentation.  This explains the usage of
  ``*traverse`` and ``*subpath`` in routes URL patters.

- A "router" chapter explaining the request/response lifecycle at a
  high level was added.

- Replaced all mentions and explanations of a routes "context factory"
  with equivalent explanations of a "root factory" (context factories
  have been disused).

- Updated Routes bfgwiki2 tutorial to reflect the fact that context
  factories are now no longer used.

0.9.1 (2009-06-02)
==================

Features
--------

- Add API named ``repoze.bfg.settings.get_settings`` which retrieves a
  derivation of values passed as the ``options`` value of
  ``repoze.bfg.router.make_app``.  This API should be preferred
  instead of using getUtility(ISettings).  I added a new
  ``repoze.bfg.settings`` API document as well.

Bug Fixes
---------

- Restored missing entry point declaration for bfg_alchemy paster
  template, which was accidentally removed in 0.9.

Documentation
-------------

- Fix a reference to ``wsgiapp`` in the ``wsgiapp2`` API documentation
  within the ``repoze.bfg.wsgi`` module.

API Removals
------------

- The ``repoze.bfg.location.locate`` API was removed: it didn't do
  enough to be very helpful and had a misleading name.

0.9 (2009-06-01)
================

Bug Fixes
---------

- It was not possible to register a custom ``IRoutesContextFactory``
  for use as a default context factory as documented in the "Hooks"
  chapter.

Features
--------

- The ``request_type`` argument of ZCML ``view`` declarations and
  ``bfg_view`` decorators can now be one of the strings ``GET``,
  ``POST``, ``PUT``, ``DELETE``, or ``HEAD`` instead of a reference to
  the respective interface type imported from
  ``repoze.bfg.interfaces``.

- The ``route`` ZCML directive now accepts ``request_type`` as an
  alias for its ``condition_method`` argument for symmetry with the
  ``view`` directive.

- The ``bfg_routesalchemy`` paster template now provides a unit test
  and actually uses the database during a view rendering.

Removals
--------

- Remove ``repoze.bfg.threadlocal.setManager``.  It was only used in
  unit tests.

- Remove ``repoze.bfg.wsgi.HTTPException``,
  ``repoze.bfg.wsgi.NotFound``, and ``repoze.bfg.wsgi.Unauthorized``.
  These classes were disused with the introduction of the
  ``IUnauthorizedView`` and ``INotFoundView`` machinery.

Documentation
-------------

- Add description to narrative templating chapter about how to use
  Chameleon text templates.

- Changed Views narrative chapter to use method strings rather than
  interface types, and moved advanced interface type usage to Events
  narrative chapter.

- Added a Routes+SQLAlchemy wiki tutorial.

0.9a8 (2009-05-31)
==================

Features
--------

- It is now possible to register a custom
  ``repoze.bfg.interfaces.INotFoundView`` for a given application.
  This feature replaces the
  ``repoze.bfg.interfaces.INotFoundAppFactory`` feature previously
  described in the Hooks chapter.  The INotFoundView will be called
  when the framework detects that a view lookup done as a result of a
  request fails; it should accept a context object and a request
  object; it should return an IResponse object (a webob response,
  basically).  See the Hooks narrative chapter of the BFG docs for
  more info.

- The error presented when a view invoked by the router returns a
  non-response object now includes the view's name for troubleshooting
  purposes.

Bug Fixes
---------

- A "new response" event is emitted for forbidden and notfound views.

Deprecations
------------

- The ``repoze.bfg.interfaces.INotFoundAppFactory`` interface has been
  deprecated in favor of using the new
  ``repoze.bfg.interfaces.INotFoundView`` mechanism.

Renames
-------

- Renamed ``repoze.bfg.interfaces.IForbiddenResponseFactory`` to
  ``repoze.bfg.interfaces.IForbiddenView``.

0.9a7 (2009-05-30)
==================

Features
--------

- Remove "context" argument from ``effective_principals`` and
  ``authenticated_userid`` function APIs in ``repoze.bfg.security``,
  effectively a doing reversion to 0.8 and before behavior.  Both
  functions now again accept only the ``request`` parameter.

0.9a6 (2009-05-29)
==================

Documentation
-------------

- Changed "BFG Wiki" tutorial to use AuthTktAuthenticationPolicy
  rather than repoze.who.

Features
--------

- Add an AuthTktAuthenticationPolicy.  This policy retrieves
  credentials from an auth_tkt cookie managed by the application
  itself (instead of relying on an upstream data source for
  authentication data).  See the Security API chapter of the
  documentation for more info.

- Allow RemoteUserAuthenticationPolicy and
  RepozeWho1AuthenticationPolicy to accept various constructor
  arguments.  See the Security API chapter of the documentation for
  more info.

0.9a5 (2009-05-28)
==================

Features
--------

- Add a ``get_app`` API functions to the ``paster`` module.  This
  obtains a WSGI application from a config file given a config file
  name and a section name.  See the ``repoze.bfg.paster`` API docs for
  more information.

- Add a new module named ``scripting``.  It contains a ``get_root``
  API function, which, provided a Router instance, returns a traversal
  root object and a "closer".  See the ``repoze.bfg.scripting`` API
  docs for more info.

0.9a4 (2009-05-27)
==================

Bug Fixes
---------

- Try checking for an "old style" security policy *after* we parse
  ZCML (thinko).

0.9a3 (2009-05-27)
==================

Features
--------

- Allow IAuthenticationPolicy and IAuthorizationPolicy to be
  overridden via ZCML registrations (do ZCML parsing after
  registering these in router.py).

Documentation
-------------

- Added "BFG Wiki" tutorial to documentation; it describes
  step-by-step how to create a traversal-based ZODB application with
  authentication.

Deprecations
------------

- Added deprecations for imports of ``ACLSecurityPolicy``,
  ``InheritingACLSecurityPolicy``, ``RemoteUserACLSecurityPolicy``,
  ``RemoteUserInheritingACLSecurityPolicy``, ``WhoACLSecurityPolicy``,
  and ``WhoInheritingACLSecurityPolicy`` from the
  ``repoze.bfg.security`` module; for the meantime (for backwards
  compatibility purposes) these live in the ``repoze.bfg.secpols``
  module.  Note however, that the entire concept of a "security
  policy" is deprecated in BFG in favor of separate authentication and
  authorization policies, so any use of a security policy will
  generate additional deprecation warnings even if you do start using
  ``repoze.bfg.secpols``.  ``repoze.bfg.secpols`` will disappear in a
  future release of ``repoze.bfg``.

Deprecated Import Alias Removals
--------------------------------

- Remove ``repoze.bfg.template`` module.  All imports from this
  package have been deprecated since 0.3.8.  Instead, import
  ``get_template``, ``render_template``, and
  ``render_template_to_response`` from the
  ``repoze.bfg.chameleon_zpt`` module. 

- Remove backwards compatibility import alias for
  ``repoze.bfg.traversal.split_path`` (deprecated since 0.6.5).  This
  must now be imported as ``repoze.bfg.traversal.traversal_path``).

- Remove backwards compatibility import alias for
  ``repoze.bfg.urldispatch.RoutesContext`` (deprecated since 0.6.5).
  This must now be imported as
  ``repoze.bfg.urldispatch.DefaultRoutesContext``.

- Removed backwards compatibility import aliases for
  ``repoze.bfg.router.get_options`` and ``repoze.bfg.router.Settings``
  (deprecated since 0.6.2).  These both must now be imported from
  ``repoze.bfg.settings``.

- Removed backwards compatibility import alias for
  ``repoze.bfg.interfaces.IRootPolicy`` (deprecated since 0.6.2).  It
  must be imported as ``repoze.bfg.interfaces.IRootFactory`` now.

- Removed backwards compatibility import alias for
  ``repoze.bfg.interfaces.ITemplate`` (deprecated since 0.4.4).  It
  must be imported as ``repoze.bfg.interfaces.ITemplateRenderer`` now.

- Removed backwards compatibility import alias for
  ``repoze.bfg.interfaces.ITemplateFactory`` (deprecated since 0.4.4).
  It must be imported as
  ``repoze.bfg.interfaces.ITemplateRendererFactory`` now.

- Removed backwards compatibility import alias for
  ``repoze.bfg.chameleon_zpt.ZPTTemplateFactory`` (deprecated since
  0.4.4).  This must be imported as ``repoze.bfg.ZPTTemplateRenderer``
  now.

0.9a2 (2009-05-27)
==================

Features
--------

- A paster command has been added named "bfgshell".  This command can
  be used to get an interactive prompt with your BFG root object in
  the global namespace.  E.g.::

    bin/paster bfgshell /path/to/myapp.ini myapp

  See the ``Project`` chapter in the BFG documentation for more
  information.

Deprecations
------------

- The name ``repoze.bfg.registry.registry_manager`` was never an API,
  but scripts in the wild were using it to set up an environment for
  use under a debug shell.  A backwards compatibility shim has been
  added for this purpose, but the feature is deprecated.

0.9a1 (2009-5-27)
=================

Features
--------

- New API functions named ``forget`` and ``remember`` are available in
  the ``security`` module.  The ``forget`` function returns headers
  which will cause the currently authenticated user to be logged out
  when set in a response.  The ``remember`` function (when passed the
  proper arguments) will return headers which will cause a principal
  to be "logged in" when set in a response.  See the Security API
  chapter of the docs for more info.

- New keyword arguments to the ``repoze.bfg.router.make_app`` call
  have been added: ``authentication_policy`` and
  ``authorization_policy``.  These should, respectively, be an
  implementation of an authentication policy (an object implementing
  the ``repoze.bfg.interfaces.IAuthenticationPolicy`` interface) and
  an implementation of an authorization policy (an object implementing
  ``repoze.bfg.interfaces.IAuthorizationPolicy)``.  Concrete
  implementations of authentication policies exist in
  ``repoze.bfg.authentication``.  Concrete implementations of
  authorization policies exist in ``repoze.bfg.authorization``.

  Both ``authentication_policy`` and ``authorization_policy`` default
  to ``None``.

  If ``authentication_policy`` is ``None``, but
  ``authorization_policy`` is *not* ``None``, then
  ``authorization_policy`` is ignored (the ability to do authorization
  depends on authentication).

  If the ``authentication_policy`` argument is *not* ``None``, and the
  ``authorization_policy`` argument *is* ``None``, the authorization
  policy defaults to an authorization implementation that uses ACLs
  (``repoze.bfg.authorization.ACLAuthorizationPolicy``).

  We no longer encourage configuration of "security policies" using
  ZCML, as previously we did for ``ISecurityPolicy``.  This is because
  it's not uncommon to need to configure settings for concrete
  authorization or authentication policies using paste .ini
  parameters; the app entry point for your application is the natural
  place to do this.

- Two new abstractions have been added in the way of adapters used by
  the system: an ``IAuthorizationPolicy`` and an
  ``IAuthenticationPolicy``.  A combination of these (as registered by
  the ``securitypolicy`` ZCML directive) take the place of the
  ``ISecurityPolicy`` abstraction in previous releases of repoze.who.
  The API functions in ``repoze.who.security`` (such as
  ``authentication_userid``, ``effective_principals``,
  ``has_permission``, and so on) have been changed to try to make use
  of these new adapters.  If you're using an older ``ISecurityPolicy``
  adapter, the system will still work, but it will print deprecation
  warnings when such a policy is used.

- The way the (internal) IViewPermission utilities registered via ZCML
  are invoked has changed.  They are purely adapters now, returning a
  boolean result, rather than returning a callable. You shouldn't have
  been using these anyway. ;-)

- New concrete implementations of IAuthenticationPolicy have been
  added to the ``repoze.bfg.authentication`` module:
  ``RepozeWho1AuthenticationPolicy`` which uses ``repoze.who``
  identity to retrieve authentication data from and
  ``RemoteUserAuthenticationPolicy``, which uses the ``REMOTE_USER``
  value in the WSGI environment to retrieve authentication data.

- A new concrete implementation of IAuthorizationPolicy has been added
  to the ``repoze.bfg.authorization`` module:
  ``ACLAuthorizationPolicy`` which uses ACL inheritance to do
  authorization.

- It is now possible to register a custom
  ``repoze.bfg.interfaces.IForbiddenResponseFactory`` for a given
  application.  This feature replaces the
  ``repoze.bfg.interfaces.IUnauthorizedAppFactory`` feature previously
  described in the Hooks chapter.  The IForbiddenResponseFactory will
  be called when the framework detects an authorization failure; it
  should accept a context object and a request object; it should
  return an IResponse object (a webob response, basically).  Read the
  below point for more info and see the Hooks narrative chapter of the
  BFG docs for more info.

Backwards Incompatibilities
---------------------------

- Custom NotFound and Forbidden (nee' Unauthorized) WSGI applications
  (registered as a utility for INotFoundAppFactory and
  IUnauthorizedAppFactory) could rely on an environment key named
  ``message`` describing the circumstance of the response.  This key
  has been renamed to ``repoze.bfg.message`` (as per the WSGI spec,
  which requires environment extensions to contain dots).

Deprecations
------------

- The ``repoze.bfg.interfaces.IUnauthorizedAppFactory`` interface has
  been deprecated in favor of using the new
  ``repoze.bfg.interfaces.IForbiddenResponseFactory`` mechanism.

- The ``view_execution_permitted`` API should now be imported from the
  ``repoze.bfg.security`` module instead of the ``repoze.bfg.view``
  module.

- The ``authenticated_userid`` and ``effective_principals`` APIs in
  ``repoze.bfg.security`` used to only take a single argument
  (request).  They now accept two arguments (``context`` and
  ``request``).  Calling them with a single argument is still
  supported but issues a deprecation warning.  (NOTE: this change was
  reverted in 0.9a7; meaning the 0.9 versions of these functions
  again accept ``request`` only, just like 0.8 and before).

- Use of "old-style" security policies (those base on ISecurityPolicy)
  is now deprecated.  See the "Security" chapter of the docs for info
  about activating an authorization policy and an authentication poicy.

0.8.1 (2009-05-21)
==================

Features
--------

- Class objects may now be used as view callables (both via ZCML and
  via use of the ``bfg_view`` decorator in Python 2.6 as a class
  decorator).  The calling semantics when using a class as a view
  callable is similar to that of using a class as a Zope "browser
  view": the class' ``__init__`` must accept two positional parameters
  (conventionally named ``context``, and ``request``).  The resulting
  instance must be callable (it must have a ``__call__`` method).
  When called, the instance should return a response.  For example::

    from webob import Response

    class MyView(object):
        def __init__(self, context, request):
            self.context = context
            self.request = request

        def __call__(self):
            return Response('hello from %s!' % self.context)

   See the "Views" chapter in the documentation and the
   ``repoze.bfg.view`` API documentation for more information.

- Removed the pickling of ZCML actions (the code that wrote
  ``configure.zcml.cache`` next to ``configure.zcml`` files in
  projects).  The code which managed writing and reading of the cache
  file was a source of subtle bugs when users switched between
  imperative (e.g. ``@bfg_view``) registrations and declarative
  registrations (e.g. the ``view`` directive in ZCML) on the same
  project. On a moderately-sized project (535 ZCML actions and 15 ZCML
  files), executing actions read from the pickle was saving us only
  about 200ms (2.5 sec vs 2.7 sec average). On very small projects (1
  ZCML file and 4 actions), startup time was comparable, and sometimes
  even slower when reading from the pickle, and both ways were so fast
  that it really just didn't matter anyway.

0.8 (2009-05-18)
================

Features
--------

- Added a ``traverse`` function to the ``repoze.bfg.traversal``
  module.  This function may be used to retrieve certain values
  computed during path resolution.  See the Traversal API chapter of
  the documentation for more information about this function.

Deprecations
------------

- Internal: ``ITraverser`` callables should now return a dictionary
  rather than a tuple.  Up until 0.7.0, all ITraversers were assumed
  to return a 3-tuple.  In 0.7.1, ITraversers were assumed to return a
  6-tuple.  As (by evidence) it's likely we'll need to add further
  information to the return value of an ITraverser callable, 0.8
  assumes that an ITraverser return a dictionary with certain elements
  in it.  See the ``repoze.bfg.interfaces.ITraverser`` interface for
  the list of keys that should be present in the dictionary.
  ``ITraversers`` which return tuples will still work, although a
  deprecation warning will be issued.

Backwards Incompatibilities
---------------------------

- If your code used the ITraverser interface directly (not via an API
  function such as ``find_model``) via an adapter lookup, you'll need
  to change your code to expect a dictionary rather than a 3- or
  6-tuple if your code ever gets return values from the default
  ModelGraphTraverser or RoutesModelTraverser adapters.

0.8a7 (2009-05-16)
==================

Backwards Incompatibilities
---------------------------

- The ``RoutesMapper`` class in ``repoze.bfg.urldispatch`` has been
  removed, as well as its documentation.  It had been deprecated since
  0.6.3.  Code in ``repoze.bfg.urldispatch.RoutesModelTraverser``
  which catered to it has also been removed.

- The semantics of the ``route`` ZCML directive have been simplified.
  Previously, it was assumed that to use a route, you wanted to map a
  route to an externally registered view.  The new ``route`` directive
  instead has a ``view`` attribute which is required, specifying the
  dotted path to a view callable.  When a route directive is
  processed, a view is *registered* using the name attribute of the
  route directive as its name and the callable as its value.  The
  ``view_name`` and ``provides`` attributes of the ``route`` directive
  are therefore no longer used.  Effectively, if you were previously
  using the ``route`` directive, it means you must change a pair of
  ZCML directives that look like this::

    <route
       name="home"
       path=""
       view_name="login"
       factory=".models.root.Root"
     />

    <view
       for=".models.root.Root"
       name="login"
       view=".views.login_view"
     />
    
  To a ZCML directive that looks like this::

    <route
       name="home"
       path=""
       view=".views.login_view"
       factory=".models.root.Root"
     />

  In other words, to make old code work, remove the ``view``
  directives that were only there to serve the purpose of backing
  ``route`` directives, and move their ``view=`` attribute into the
  ``route`` directive itself.

  This change also necessitated that the ``name`` attribute of the
  ``route`` directive is now required.  If you were previously using
  ``route`` directives without a ``name`` attribute, you'll need to
  add one (the name is arbitrary, but must be unique among all
  ``route`` and ``view`` statements).

  The ``provides`` attribute of the ``route`` directive has also been
  removed.  This directive specified a sequence of interface types
  that the generated context would be decorated with.  Since route
  views are always generated now for a single interface
  (``repoze.bfg.IRoutesContext``) as opposed to being looked up
  arbitrarily, there is no need to decorate any context to ensure a
  view is found.

Documentation
-------------

- Added API docs for the ``repoze.bfg.testing`` methods
  ``registerAdapter``, ``registerUtiity``, ``registerSubscriber``, and
  ``cleanUp``.

- Added glossary entry for "root factory".

- Noted existence of ``repoze.bfg.pagetemplate`` template bindings in
  "Available Add On Template System Bindings" in Templates chapter in
  narrative docs.

- Update "Templates" narrative chapter in docs (expand to show a
  sample template and correct macro example).

Features
--------

- Courtesty Carlos de la Guardia, added an ``alchemy`` Paster
  template.  This paster template sets up a BFG project that uses
  SQAlchemy (with SQLite) and uses traversal to resolve URLs.  (no
  Routes areused).  This template can be used via ``paster create -t
  bfg_alchemy``.

- The Routes ``Route`` object used to resolve the match is now put
  into the environment as ``bfg.route`` when URL dispatch is used.

- You can now change the default Routes "context factory" globally.
  See the "ZCML Hooks" chapter of the documentation (in the "Changing
  the Default Routes Context Factory" section).

0.8a6 (2009-05-11)
==================

Features
--------

- Added a ``routesalchemy`` Paster template.  This paster template
  sets up a BFG project that uses SQAlchemy (with SQLite) and uses
  Routes exclusively to resolve URLs (no traversal root factory is
  used).  This template can be used via ``paster create -t
  bfg_routesalchemy``.

Documentation
-------------

- Added documentation to the URL Dispatch chapter about how to catch
  the root URL using a ZCML ``route`` directive.

- Added documentation to the URL Dispatch chapter about how to perform
  a cleanup function at the end of a request (e.g. close the SQL
  connection).

Bug Fixes
---------

- In version 0.6.3, passing a ``get_root`` callback (a "root factory")
  to ``repoze.bfg.router.make_app`` became optional if any ``route``
  declaration was made in ZCML.  The intent was to make it possible to
  disuse traversal entirely, instead relying entirely on URL dispatch
  (Routes) to resolve all contexts.  However a compound set of bugs
  prevented usage of a Routes-based root view (a view which responds
  to "/").  One bug existed in `repoze.bfg.urldispatch``, another
  existed in Routes itself.

  To resolve this issue, the urldispatch module was fixed, and a fork
  of the Routes trunk was put into the "dev" index named
  ``Routes-1.11dev-chrism-home``.  The source for the fork exists at
  ``http://bitbucket.org/chrism/routes-home/`` (broken link);
  its contents have been merged into the Routes trunk
  (what will be Routes 1.11).

0.8a5 (2009-05-08)
==================

Features
--------

- Two new security policies were added:
  RemoteUserInheritingACLSecurityPolicy and
  WhoInheritingACLSecurityPolicy.  These are security policies which
  take into account *all* ACLs defined in the lineage of a context
  rather than stopping at the first ACL found in a lineage.  See the
  "Security" chapter of the API documentation for more information.

- The API and narrative documentation dealing with security was
  changed to introduce the new "inheriting" security policy variants.

- Added glossary entry for "lineage".

Deprecations
------------

- The security policy previously named
  ``RepozeWhoIdentityACLSecurityPolicy`` now has the slightly saner
  name of ``WhoACLSecurityPolicy``.  A deprecation warning is emitted
  when this policy is imported under the "old" name; usually this is
  due to its use in ZCML within your application.  If you're getting
  this deprecation warning, change your ZCML to use the new name,
  e.g. change::

   <utility
     provides="repoze.bfg.interfaces.ISecurityPolicy"
     factory="repoze.bfg.security.RepozeWhoIdentityACLSecurityPolicy"
     />

  To::

   <utility
     provides="repoze.bfg.interfaces.ISecurityPolicy"
     factory="repoze.bfg.security.WhoACLSecurityPolicy"
     />

0.8a4 (2009-05-04)
==================

Features
--------

- ``zope.testing`` is no longer a direct dependency, although our
  dependencies (such as ``zope.interface``, ``repoze.zcml``, etc)
  still depend on it.

- Tested on Google App Engine.  Added a tutorial to the documentation
  explaining how to deploy a BFG app to GAE.

Backwards Incompatibilities
---------------------------

- Applications which rely on ``zope.testing.cleanup.cleanUp`` in unit
  tests can still use that function indefinitely.  However, for
  maximum forward compatibility, they should import ``cleanUp`` from
  ``repoze.bfg.testing`` instead of from ``zope.testing.cleanup``.
  The BFG paster templates and docs have been changed to use this
  function instead of the ``zope.testing.cleanup`` version.

0.8a3 (2009-05-03)
===================

Features
--------

- Don't require a successful import of ``zope.testing`` at BFG
  application runtime.  This allows us to get rid of ``zope.testing``
  on platforms like GAE which have file limits.

0.8a2 (2009-05-02)
==================

Features
--------

- We no longer include the ``configure.zcml`` of the ``chameleon.zpt``
  package within the ``configure.zcml`` of the "repoze.bfg.includes"
  package.  This has been a no-op for some time now.

- The ``repoze.bfg.chameleon_zpt`` package no longer imports from
  ``chameleon.zpt`` at module scope, deferring the import until later
  within a method call.  The ``chameleon.zpt`` package can't be
  imported on platforms like GAE.

0.8a1 (2009-05-02)
==================

Deprecation Warning and Import Alias Removals
---------------------------------------------

- Since version 0.6.1, a deprecation warning has been emitted when the
  name ``model_url`` is imported from the ``repoze.bfg.traversal``
  module.  This import alias (and the deprecation warning) has been
  removed.  Any import of the ``model_url`` function will now need to
  be done from ``repoze.bfg.url``; any import of the name
  ``model_url`` from ``repoze.bfg.traversal`` will now fail.  This was
  done to remove a dependency on zope.deferredimport.

- Since version 0.6.5, a deprecation warning has been emitted when the
  name ``RoutesModelTraverser`` is imported from the
  ``repoze.bfg.traversal`` module.  This import alias (and the
  deprecation warning) has been removed.  Any import of the
  ``RoutesModelTraverser`` class will now need to be done from
  ``repoze.bfg.urldispatch``; any import of the name
  ``RoutesModelTraverser`` from ``repoze.bfg.traversal`` will now
  fail.  This was done to remove a dependency on zope.deferredimport.

Features
--------

- This release of ``repoze.bfg`` is "C-free".  This means it has no
  hard dependencies on any software that must be compiled from C
  source at installation time.  In particular, ``repoze.bfg`` no
  longer depends on the ``lxml`` package.

  This change has introduced some backwards incompatibilities,
  described in the "Backwards Incompatibilities" section below.

- This release was tested on Windows XP.  It appears to work fine and
  all the tests pass.

Backwards Incompatibilities
---------------------------

Incompatibilities related to making ``repoze.bfg`` "C-free":

- Removed the ``repoze.bfg.chameleon_genshi`` module, and thus support
  for Genshi-style chameleon templates.  Genshi-style Chameleon
  templates depend upon ``lxml``, which is implemented in C (as
  opposed to pure Python) and the ``repoze.bfg`` core is "C-free" as
  of this release. You may get Genshi-style Chameleon support back by
  installing the ``repoze.bfg.chameleon_genshi`` package availalable
  from https://pypi.org/project/repoze.bfg.chameleon_genshi/.
  All existing code that depended on the ``chameleon_genshi`` module
  prior to this release of ``repoze.bfg`` should work without change
  after this addon is installed.

- Removed the ``repoze.bfg.xslt`` module and thus support for XSL
  templates.  The ``repoze.bfg.xslt`` module depended upon ``lxml``,
  which is implemented in C, and the ``repoze.bfg`` core is "C-free"
  as of this release.  You bay get XSL templating back by installing
  the ``repoze.bfg.xslt`` package available from
  ``http://svn.repoze.org/repoze.bfg.xslt/`` (broken link)
  (also available in the index
  at ``http://dist.repoze.org/bfg/0.8/simple)`` (broken link).
  All existing code that
  depended upon the ``xslt`` module prior to this release of
  ``repoze.bfg`` should work without modification after this addon is
  installed.

- Removed the ``repoze.bfg.interfaces.INodeTemplateRenderer``
  interface and the an old b/w compat aliases from that interface to
  ``repoze.bfg.interfaces.INodeTemplate``.  This interface must now be
  imported from the ``repoze.bfg.xslt.interfaces`` package after
  installation of the ``repoze.bfg.xslt`` addon package described
  above as ``repoze.bfg.interfaces.INodeTemplateRenderer``.  This
  interface was never part of any public API.

Other backwards incompatibilities:

- The ``render_template`` function in ``repoze.bfg.chameleon_zpt``
  returns Unicode instead of a string.  Likewise, the individual
  values returned by the iterable created by the
  ``render_template_to_iterable`` function are also each Unicode.
  This is actually a backwards incompatibility inherited from our new
  use of the combination of ``chameleon.core`` 1.0b32 (the
  non-lxml-depending version) and ``chameleon.zpt`` 1.0b16+ ; the
  ``chameleon.zpt`` PageTemplateFile implementation used to return a
  string, but now returns Unicode.

0.7.1 (2009-05-01)
==================

Index-Related
-------------

- The canonical package index location for ``repoze.bfg`` has changed.
  The "old" index (``http://dist.repoze.org/lemonade/dev/simple``) (broken link)
  has been superseded by a new index location
  ``http://dist.repoze.org/bfg/current/simple`` (broken link).
  The installation
  documentation has been updated as well as the ``setup.cfg`` file in
  this package.  The "lemonade" index still exists, but it is not
  guaranteed to have the latest BFG software in it, nor will it be
  maintained in the future.

Features
--------

- The "paster create" templates have been modified to use links to the
  new "bfg.repoze.org" and "docs.repoze.org" websites.

- Added better documentation for virtual hosting at a URL prefix
  within the virtual hosting docs chapter.

- The interface for ``repoze.bfg.interfaces.ITraverser`` and the
  built-in implementations that implement the interface
  (``repoze.bfg.traversal.ModelGraphTraverser``, and
  ``repoze.bfg.urldispatch.RoutesModelTraverser``) now expect the
  ``__call__`` method of an ITraverser to return 3 additional
  arguments: ``traversed``, ``virtual_root``, and
  ``virtual_root_path`` (the old contract was that the ``__call__``
  method of an ITraverser returned; three arguments, the contract new
  is that it returns six).  ``traversed`` will be a sequence of
  Unicode names that were traversed (including the virtual root path,
  if any) or ``None`` if no traversal was performed, ``virtual_root``
  will be a model object representing the virtual root (or the
  physical root if traversal was not performed), and
  ``virtual_root_path`` will be a sequence representing the virtual
  root path (a sequence of Unicode names) or ``None`` if traversal was
  not performed.

  Six arguments are now returned from BFG ITraversers.  They are
  returned in this order: ``context``, ``view_name``, ``subpath``,
  ``traversed``, ``virtual_root``, and ``virtual_root_path``.

  Places in the BFG code which called an ITraverser continue to accept
  a 3-argument return value, although BFG will generate and log a
  warning when one is encountered.

- The request object now has the following attributes: ``traversed``
  (the sequence of names traversed or ``None`` if traversal was not
  performed), ``virtual_root`` (the model object representing the
  virtual root, including the virtual root path if any), and
  ``virtual_root_path`` (the seuquence of names representing the
  virtual root path or ``None`` if traversal was not performed).

- A new decorator named ``wsgiapp2`` was added to the
  ``repoze.bfg.wsgi`` module.  This decorator performs the same
  function as ``repoze.bfg.wsgi.wsgiapp`` except it fixes up the
  ``SCRIPT_NAME``, and ``PATH_INFO`` environment values before
  invoking the WSGI subapplication.

- The ``repoze.bfg.testing.DummyRequest`` object now has default
  attributes for ``traversed``, ``virtual_root``, and
  ``virtual_root_path``.

- The RoutesModelTraverser now behaves more like the Routes
  "RoutesMiddleware" object when an element in the match dict is named
  ``path_info`` (usually when there's a pattern like
  ``http://foo/*path_info``).  When this is the case, the
  ``PATH_INFO`` environment variable is set to the value in the match
  dict, and the ``SCRIPT_NAME`` is appended to with the prefix of the
  original ``PATH_INFO`` not including the value of the new variable.

- The notfound debug now shows the traversed path, the virtual root,
  and the virtual root path too.

- Speed up / clarify 'traversal' module's 'model_path', 'model_path_tuple',
  and '_model_path_list' functions.

Backwards Incompatibilities
---------------------------

- In previous releases, the ``repoze.bfg.url.model_url``,
  ``repoze.bfg.traversal.model_path`` and
  ``repoze.bfg.traversal.model_path_tuple`` functions always ignored
  the ``__name__`` argument of the root object in a model graph (
  effectively replacing it with a leading ``/`` in the returned value)
  when a path or URL was generated.  The code required to perform this
  operation was not efficient.  As of this release, the root object in
  a model graph *must* have a ``__name__`` attribute that is either
  ``None`` or the empty string (``''``) for URLs and paths to be
  generated properly from these APIs.  If your root model object has a
  ``__name__`` argument that is not one of these values, you will need
  to change your code for URLs and paths to be generated properly.  If
  your model graph has a root node with a string ``__name__`` that is
  not null, the value of ``__name__`` will be prepended to every path
  and URL generated.

- The ``repoze.bfg.location.LocationProxy`` class and the
  ``repoze.bfg.location.ClassAndInstanceDescr`` class have both been
  removed in order to be able to eventually shed a dependency on
  ``zope.proxy``.  Neither of these classes was ever an API.

- In all previous releases, the ``repoze.bfg.location.locate``
  function worked like so: if a model did not explicitly provide the
  ``repoze.bfg.interfaces.ILocation`` interface, ``locate`` returned a
  ``LocationProxy`` object representing ``model`` with its
  ``__parent__`` attribute assigned to ``parent`` and a ``__name__``
  attribute assigned to ``__name__``.  In this release, the
  ``repoze.bfg.location.locate`` function simply jams the ``__name__``
  and ``__parent__`` attributes on to the supplied model
  unconditionally, no matter if the object implements ILocation or
  not, and it never returns a proxy.  This was done because the
  LocationProxy behavior has now moved into an add-on package
  (``repoze.bfg.traversalwrapper``), in order to eventually be able to
  shed a dependency on ``zope.proxy``.

- In all previous releases, by default, if traversal was used (as
  opposed to URL-dispatch), and the root object supplied
  the``repoze.bfg.interfaces.ILocation`` interface, but the children
  returned via its ``__getitem__`` returned an object that did not
  implement the same interface, ``repoze.bfg`` provided some
  implicit help during traversal.  This traversal feature wrapped
  subobjects from the root (and thereafter) that did not implement
  ``ILocation`` in proxies which automatically provided them with a
  ``__name__`` and ``__parent__`` attribute based on the name being
  traversed and the previous object traversed.  This feature has now
  been removed from the base ``repoze.bfg`` package for purposes of
  eventually shedding a dependency on ``zope.proxy``.

  In order to re-enable the wrapper behavior for older applications
  which cannot be changed, register the "traversalwrapper"
  ``ModelGraphTraverser`` as the traversal policy, rather than the
  default ``ModelGraphTraverser``. To use this feature, you will need
  to install the ``repoze.bfg.traversalwrapper`` package (an add-on
  package, available at
  https://pypi.org/project/repoze.bfg.traversalwrapper/) Then change your
  application's ``configure.zcml`` to include the following stanza:

    <adapter
        factory="repoze.bfg.traversalwrapper.ModelGraphTraverser"
        provides="repoze.bfg.interfaces.ITraverserFactory"
        for="*"
        />

   When this ITraverserFactory is used instead of the default, no
   object in the graph (even the root object) must supply a
   ``__name__`` or ``__parent__`` attribute.  Even if subobjects
   returned from the root *do* implement the ILocation interface,
   these will still be wrapped in proxies that override the object's
   "real" ``__parent__`` and ``__name__`` attributes.

   See also changes to the "Models" chapter of the documentation (in
   the "Location-Aware Model Instances") section.

0.7.0 (2009-04-11)
==================

Bug Fixes
---------

- Fix a bug in ``repoze.bfg.wsgi.HTTPException``: the content length
  was returned as an int rather than as a string.
 
- Add explicit dependencies on ``zope.deferredimport``,
  ``zope.deprecation``, and ``zope.proxy`` for forward compatibility
  reasons (``zope.component`` will stop relying on
  ``zope.deferredimport`` soon and although we use it directly, it's
  only a transitive dependency, and ''zope.deprecation`` and
  ``zope.proxy`` are used directly even though they're only transitive
  dependencies as well).

- Using ``model_url`` or ``model_path`` against a broken model graph
  (one with models that had a non-root model with a ``__name__`` of
  ``None``) caused an inscrutable error to be thrown: ( if not
  ``_must_quote[cachekey].search(s): TypeError: expected string or
  buffer``).  Now URLs and paths generated against graphs that have
  None names in intermediate nodes will replace the None with the
  empty string, and, as a result, the error won't be raised.  Of
  course the URL or path will still be bogus.

Features
--------

- Make it possible to have ``testing.DummyTemplateRenderer`` return
  some nondefault string representation.

- Added a new ``anchor`` keyword argument to ``model_url``.  If 
  ``anchor`` is present, its string representation will be used 
  as a named anchor in the generated URL (e.g. if ``anchor`` is 
  passed as ``foo`` and the model URL is 
  ``http://example.com/model/url``, the generated URL will be 
  ``http://example.com/model/url#foo``).

Backwards Incompatibilities
---------------------------

- The default request charset encoding is now ``utf-8``.  As a result,
  the request machinery will attempt to decode values from the utf-8
  encoding to Unicode automatically when they are obtained via
  ``request.params``, ``request.GET``, and ``request.POST``.  The
  previous behavior of BFG was to return a bytestring when a value was
  accessed in this manner.  This change will break form handling code
  in apps that rely on values from those APIs being considered
  bytestrings.  If you are manually decoding values from form
  submissions in your application, you'll either need to change the
  code that does that to expect Unicode values from
  ``request.params``, ``request.GET`` and ``request.POST``, or you'll
  need to explicitly reenable the previous behavior.  To reenable the
  previous behavior, add the following to your application's
  ``configure.zcml``::

    <subscriber for="repoze.bfg.interfaces.INewRequest"
                handler="repoze.bfg.request.make_request_ascii"/>

  See also the documentation in the "Views" chapter of the BFG docs
  entitled "Using Views to Handle Form Submissions (Unicode and
  Character Set Issues)".

Documentation
-------------

- Add a section to the narrative Views chapter entitled "Using Views
  to Handle Form Submissions (Unicode and Character Set Issues)"
  explaining implicit decoding of form data values.

0.6.9 (2009-02-16)
==================

Bug Fixes
---------

- lru cache was unstable under concurrency (big surprise!) when it
  tried to redelete a key in the cache that had already been deleted.
  Symptom: line 64 in put:del data[oldkey]:KeyError: '/some/path'.
  Now we just ignore the key error if we can't delete the key (it has
  already been deleted).

- Empty location names in model paths when generating a URL using
  ``repoze.bfg.model_url`` based on a model obtained via traversal are
  no longer ignored in the generated URL.  This means that if a
  non-root model object has a ``__name__`` of ``''``, the URL will
  reflect it (e.g. ``model_url`` will generate ``http://foo/bar//baz``
  if an object with the ``__name__`` of ``''`` is a child of bar and
  the parent of baz).  URLs generated with empty path segments are,
  however, still irresolveable by the model graph traverser on request
  ingress (the traverser strips empty path segment names).

Features
--------

- Microspeedups of ``repoze.bfg.traversal.model_path``,
  ``repoze.bfg.traversal.model_path_tuple``,
  ``repoze.bfg.traversal.quote_path_segment``, and
  ``repoze.bfg.url.urlencode``.

- add zip_safe = false to setup.cfg.

Documentation
-------------

- Add a note to the ``repoze.bfg.traversal.quote_path_segment`` API
  docs about caching of computed values.

Implementation Changes
----------------------

- Simplification of
  ``repoze.bfg.traversal.TraversalContextURL.__call__`` (it now uses
  ``repoze.bfg.traversal.model_path`` instead of rolling its own
  path-generation).

0.6.8 (2009-02-05)
==================

Backwards Incompatibilities
---------------------------

- The ``repoze.bfg.traversal.model_path`` API now returns a *quoted*
  string rather than a string represented by series of unquoted
  elements joined via ``/`` characters.  Previously it returned a
  string or unicode object representing the model path, with each
  segment name in the path joined together via ``/`` characters,
  e.g. ``/foo /bar``.  Now it returns a string, where each segment is
  a UTF-8 encoded and URL-quoted element e.g. ``/foo%20/bar``.  This
  change was (as discussed briefly on the repoze-dev maillist)
  necessary to accommodate model objects which themselves have
  ``__name__`` attributes that contain the ``/`` character.

  For people that have no models that have high-order Unicode
  ``__name__`` attributes or ``__name__`` attributes with values that
  require URL-quoting with in their model graphs, this won't cause any
  issue.  However, if you have code that currently expects
  ``model_path`` to return an unquoted string, or you have an existing
  application with data generated via the old method, and you're too
  lazy to change anything, you may wish replace the BFG-imported
  ``model_path`` in your code with this function (this is the code of
  the "old" ``model_path`` implementation)::

        from repoze.bfg.location import lineage

        def i_am_too_lazy_to_move_to_the_new_model_path(model, *elements):
            rpath = []
            for location in lineage(model):
                if location.__name__:
                    rpath.append(location.__name__)
            path = '/' + '/'.join(reversed(rpath))
            if elements:
                suffix = '/'.join(elements)
                path = '/'.join([path, suffix])
            return path

- The ``repoze.bfg.traversal.find_model`` API no longer implicitly
  converts unicode representations of a full path passed to it as a
  Unicode object into a UTF-8 string.  Callers should either use
  prequoted path strings returned by
  ``repoze.bfg.traversal.model_path``, or tuple values returned by the
  result of ``repoze.bfg.traversal.model_path_tuple`` or they should
  use the guidelines about passing a string ``path`` argument
  described in the ``find_model`` API documentation.

Bugfixes
--------

- Each argument contained in ``elements`` passed to
  ``repoze.bfg.traversal.model_path`` will now have any ``/``
  characters contained within quoted to ``%2F`` in the returned
  string.  Previously, ``/`` characters in elements were left unquoted
  (a bug).

Features
--------

- A ``repoze.bfg.traversal.model_path_tuple`` API was added.  This API
  is an alternative to ``model_path`` (which returns a string);
  ``model_path_tuple`` returns a model path as a tuple (much like
  Zope's ``getPhysicalPath``).

- A ``repoze.bfg.traversal.quote_path_segment`` API was added.  This
  API will quote an individual path segment (string or unicode
  object).  See the ``repoze.bfg.traversal`` API documentation for
  more information.

- The ``repoze.bfg.traversal.find_model`` API now accepts "path
  tuples" (see the above note regarding ``model_path_tuple``) as well
  as string path representations (from
  ``repoze.bfg.traversal.model_path``) as a ``path`` argument.

- Add ` `renderer`` argument (defaulting to None) to
  ``repoze.bfg.testing.registerDummyRenderer``.  This makes it
  possible, for instance, to register a custom renderer that raises an
  exception in a unit test.

Implementation Changes
----------------------

- Moved _url_quote function back to ``repoze.bfg.traversal`` from
  ``repoze.bfg.url``.  This is not an API.

0.6.7 (2009-01-27)
==================

Features
--------

- The ``repoze.bfg.url.model_url`` API now works against contexts
  derived from Routes URL dispatch (``Routes.util.url_for`` is called
  under the hood).

- "Virtual root" support for traversal-based applications has been
  added.  Virtual root support is useful when you'd like to host some
  model in a ``repoze.bfg`` model graph as an application under a
  URL pathname that does not include the model path itself.  For more
  information, see the (new) "Virtual Hosting" chapter in the
  documentation.

- A ``repoze.bfg.traversal.virtual_root`` API has been added.  When
  called, it returns the virtual root object (or the physical root
  object if no virtual root has been specified).

Implementation Changes
----------------------

- ``repoze.bfg.traversal.RoutesModelTraverser`` has been moved to
  ``repoze.bfg.urldispatch``.

- ``model_url`` URL generation is now performed via an adapter lookup
  based on the context and the request.

- ZCML which registers two adapters for the ``IContextURL`` interface
  has been added to the configure.zcml in ``repoze.bfg.includes``.

0.6.6 (2009-01-26)
==================

Implementation Changes
----------------------

- There is an indirection in ``repoze.bfg.url.model_url`` now that
  consults a utility to generate the base model url (without extra
  elements or a query string).  Eventually this will service virtual
  hosting; for now it's undocumented and should not be hooked.

0.6.5 (2009-01-26)
==================

Features
--------

- You can now override the NotFound and Unauthorized responses that
  ``repoze.bfg`` generates when a view cannot be found or cannot be
  invoked due to lack of permission.  See the "ZCML Hooks" chapter in
  the docs for more information.

- Added Routes ZCML directive attribute explanations in documentation.

- Added a ``traversal_path`` API to the traversal module; see the
  "traversal" API chapter in the docs.  This was a function previously
  known as ``split_path`` that was not an API but people were using it
  anyway.  Unlike ``split_path``, it now returns a tuple instead of a
  list (as its values are cached).

Behavior Changes
----------------

- The ``repoze.bfg.view.render_view_to_response`` API will no longer
  raise a ValueError if an object returned by a view function it calls
  does not possess certain attributes (``headerlist``, ``app_iter``,
  ``status``).  This API used to attempt to perform a check using the
  ``is_response`` function in ``repoze.bfg.view``, and raised a
  ``ValueError`` if the ``is_response`` check failed.  The
  responsibility is now the caller's to ensure that the return value
  from a view function is a "real" response.

- WSGI environ dicts passed to ``repoze.bfg`` 's Router must now
  contain a REQUEST_METHOD key/value; if they do not, a KeyError will
  be raised (speed).  

- It is no longer permissible to pass a "nested" list of principals to
  ``repoze.bfg.ACLAuthorizer.permits`` (e.g. ``['fred', ['larry',
  'bob']]``).  The principals list must be fully expanded.  This
  feature was never documented, and was never an API, so it's not a
  backwards incompatibility.

- It is no longer permissible for a security ACE to contain a "nested"
  list of permissions (e.g. ``(Allow, Everyone, ['read', ['view',
  ['write', 'manage']]])`)`.  The list must instead be fully expanded
  (e.g. ``(Allow, Everyone, ['read', 'view', 'write', 'manage])``).  This
  feature was never documented, and was never an API, so it's not a
  backwards incompatibility.

- The ``repoze.bfg.urldispatch.RoutesRootFactory`` now injects the
  ``wsgiorg.routing_args`` environment variable into the environ when
  a route matches.  This is a tuple of ((), routing_args) where
  routing_args is the value that comes back from the routes mapper
  match (the "match dict").

- The ``repoze.bfg.traversal.RoutesModelTraverser`` class now wants to
  obtain the ``view_name`` and ``subpath`` from the
  ``wsgiorgs.routing_args`` environment variable.  It falls back to
  obtaining these from the context for backwards compatibility.

Implementation Changes
----------------------

- Get rid of ``repoze.bfg.security.ACLAuthorizer``: the
  ``ACLSecurityPolicy`` now does what it did inline.

- Get rid of ``repoze.bfg.interfaces.NoAuthorizationInformation``
  exception: it was used only by ``ACLAuthorizer``.

- Use a homegrown NotFound error instead of ``webob.exc.HTTPNotFound``
  (the latter is slow).

- Use a homegrown Unauthorized error instead of
  ``webob.exc.Unauthorized`` (the latter is slow).

- the ``repoze.bfg.lru.lru_cached`` decorator now uses functools.wraps
  in order to make documentation of LRU-cached functions possible.

- Various speed micro-tweaks.

Bug Fixes
---------

- ``repoze.bfg.testing.DummyModel`` did not have a ``get`` method;
  it now does.

0.6.4 (2009-01-23)
==================

Backwards Incompatibilities
---------------------------

- The ``unicode_path_segments`` configuration variable and the
  ``BFG_UNICODE_PATH_SEGMENTS`` configuration variable have been
  removed.  Path segments are now always passed to model
  ``__getitem__`` methods as unicode.  "True" has been the default for
  this setting since 0.5.4, but changing this configuration setting to
  false allowed you to go back to passing raw path element strings to
  model ``__getitem__`` methods.  Removal of this knob services a
  speed goal (we get about +80 req/s by removing the check), and it's
  clearer just to always expect unicode path segments in model
  ``__getitem__`` methods.

Implementation Changes
----------------------

- ``repoze.bfg.traversal.split_path`` now also handles decoding
  path segments to unicode (for speed, because its results are
  cached).

- ``repoze.bfg.traversal.step`` was made a method of the
   ModelGraphTraverser.

- Use "precooked" Request subclasses
  (e.g. ``repoze.bfg.request.GETRequest``) that correspond to HTTP
  request methods within ``router.py`` when constructing a request
  object rather than using ``alsoProvides`` to attach the proper
  interface to an unsubclassed ``webob.Request``.  This pattern is
  purely an optimization (e.g. preventing calls to ``alsoProvides``
  means the difference between 590 r/s and 690 r/s on a MacBook 2GHz).

- Tease out an extra 4% performance boost by changing the Router;
  instead of using imported ZCA APIs, use the same APIs directly
  against the registry that is an attribute of the Router.

- The registry used by BFG is now a subclass of
  ``zope.component.registry.Components`` (defined as
  ``repoze.bfg.registry.Registry``); it has a ``notify`` method, a
  ``registerSubscriptionAdapter`` and a ``registerHandler`` method.
  If no subscribers are registered via ``registerHandler`` or
  ``registerSubscriptionAdapter``, ``notify`` is a noop for speed.

- The Allowed and Denied classes in ``repoze.bfg.security`` now are
  lazier about constructing the representation of a reason message for
  speed; ``repoze.bfg.view_execution_permitted`` takes advantage of
  this.

- The ``is_response`` check was sped up by about half at the expense
  of making its code slightly uglier.

New Modules
-----------

- ``repoze.bfg.lru`` implements an LRU cache class and a decorator for
  internal use.

0.6.3 (2009-01-19)
==================

Bug Fixes
---------

- Readd ``root_policy`` attribute on Router object (as a property
  which returns the IRootFactory utility).  It was inadvertently
  removed in 0.6.2.  Code in the wild depended upon its presence
  (esp. scripts and "debug" helpers).

Features
--------

- URL-dispatch has been overhauled: it is no longer necessary to
  manually create a RoutesMapper in your application's entry point
  callable in order to use URL-dispatch (aka `Routes
  <https://routes.readthedocs.io/en/latest/>`_).  A new ``route`` directive has been
  added to the available list of ZCML directives.  Each ``route``
  directive inserted into your application's ``configure.zcml``
  establishes a Routes mapper connection.  If any ``route``
  declarations are made via ZCML within a particular application, the
  ``get_root`` callable passed in to ``repoze.bfg.router.make_app``
  will automatically be wrapped in the equivalent of a RoutesMapper.
  Additionally, the new ``route`` directive allows the specification
  of a ``context_interfaces`` attribute for a route, this will be used
  to tag the manufactured routes context with specific interfaces when
  a route specifying a ``context_interfaces`` attribute is matched.

- A new interface ``repoze.bfg.interfaces.IContextNotFound`` was
  added.  This interface is attached to a "dummy" context generated
  when Routes cannot find a match and there is no "fallback" get_root
  callable that uses traversal.

- The ``bfg_starter`` and ``bfg_zodb`` "paster create" templates now
  contain images and CSS which are displayed when the default page is
  displayed after initial project generation.

- Allow the ``repoze.bfg.view.static`` helper to be passed a relative
  ``root_path`` name; it will be considered relative to the file in
  which it was called.

- The functionality of ``repoze.bfg.convention`` has been merged into
  the core.  Applications which make use of ``repoze.bfg.convention``
  will continue to work indefinitely, but it is recommended that apps
  stop depending upon it.  To do so, substitute imports of
  ``repoze.bfg.convention.bfg_view`` with imports of
  ``repoze.bfg.view.bfg_view``, and change the stanza in ZCML from
  ``<convention package=".">`` to ``<scan package=".">``.  As a result
  of the merge, bfg has grown a new dependency: ``martian``.

- View functions which use the pushpage decorator are now pickleable
  (meaning their use won't prevent a ``configure.zcml.cache`` file
  from being written to disk).

- Instead of invariably using ``webob.Request`` as the "request
  factory" (e.g. in the ``Router`` class) and ``webob.Response`` and
  the "response factory" (e.g. in ``render_template_to_response``),
  allow both to be overridden via a ZCML utility hook.  See the "Using
  ZCML Hooks" chapter of the documentation for more information.

Deprecations
------------

- The class ``repoze.bfg.urldispatch.RoutesContext`` has been renamed
  to ``repoze.bfg.urldispatch.DefaultRoutesContext``.  The class
  should be imported by the new name as necessary (although in reality
  it probably shouldn't be imported from anywhere except internally
  within BFG, as it's not part of the API).

Implementation Changes
----------------------

- The ``repoze.bfg.wsgi.wsgiapp`` decorator now uses
  ``webob.Request.get_response`` to do its work rather than relying on
  homegrown WSGI code.

- The ``repoze.bfg.view.static`` helper now uses
  ``webob.Request.get_response`` to do its work rather than relying on
  homegrown WSGI code.

- The ``repoze.bfg.urldispatch.RoutesModelTraverser`` class has been
  moved to ``repoze.bfg.traversal.RoutesModelTraverser``.

- The ``repoze.bfg.registry.makeRegistry`` function was renamed to
  ``repoze.bfg.registry.populateRegistry`` and now accepts a
  ``registry`` argument (which should be an instance of
  ``zope.component.registry.Components``).

Documentation Additions
-----------------------

- Updated narrative urldispatch chapter with changes required by
  ``<route..>`` ZCML directive.

- Add a section on "Using BFG Security With URL Dispatch" into the
  urldispatch chapter of the documentation.

- Better documentation of security policy implementations that ship
  with repoze.bfg.

- Added a "Using ZPT Macros in repoze.bfg" section to the narrative
  templating chapter.

0.6.2 (2009-01-13)
==================

Features
--------

- Tests can be run with coverage output if you've got ``nose``
  installed in the interpreter which you use to run tests.  Using an
  interpreter with ``nose`` installed, do ``python setup.py
  nosetests`` within a checkout of the ``repoze.bfg`` package to see
  test coverage output.

- Added a ``post`` argument to the ``repoze.bfg.testing:DummyRequest``
  constructor.
  
- Added ``__len__`` and ``__nonzero__`` to ``repoze.bfg.testing:DummyModel``.

- The ``repoze.bfg.registry.get_options`` callable (now renamed to
  ``repoze.bfg.setings.get_options``) used to return only
  framework-specific keys and values in the dictionary it returned.
  It now returns all the keys and values in the dictionary it is
  passed *plus* any framework-specific settings culled from the
  environment.  As a side effect, all PasteDeploy application-specific
  config file settings are made available as attributes of the
  ``ISettings`` utility from within BFG.

- Renamed the existing BFG paster template to ``bfg_starter``.  Added
  another template (``bfg_zodb``) showing default ZODB setup using
  ``repoze.zodbconn``.

- Add a method named ``assert_`` to the DummyTemplateRenderer.  This
  method accepts keyword arguments.  Each key/value pair in the
  keyword arguments causes an assertion to be made that the renderer
  received this key with a value equal to the asserted value.

- Projects generated by the paster templates now use the
  ``DummyTemplateRenderer.assert_`` method in their view tests.

- Make the (internal) thread local registry manager maintain a stack
  of registries in order to make it possible to call one BFG
  application from inside another.

- An interface specific to the HTTP verb (GET/PUT/POST/DELETE/HEAD) is
  attached to each request object on ingress.  The HTTP-verb-related
  interfaces are defined in ``repoze.bfg.interfaces`` and are
  ``IGETRequest``, ``IPOSTRequest``, ``IPUTRequest``,
  ``IDELETERequest`` and ``IHEADRequest``.  These interfaces can be
  specified as the ``request_type`` attribute of a bfg view
  declaration.  A view naming a specific HTTP-verb-matching interface
  will be found only if the view is defined with a request_type that
  matches the HTTP verb in the incoming request.  The more general
  ``IRequest`` interface can be used as the request_type to catch all
  requests (and this is indeed the default).  All requests implement
  ``IRequest``. The HTTP-verb-matching idea was pioneered by
  `repoze.bfg.restrequest
  <https://pypi.org/project/repoze.bfg.restrequest/1.0.1/>`_ . That
  package is no longer required, but still functions fine.

Bug Fixes
---------

- Fix a bug where the Paste configuration's ``unicode_path_segments``
  (and os.environ's ``BFG_UNICODE_PATH_SEGMENTS``) may have been
  defaulting to false in some circumstances.  It now always defaults
  to true, matching the documentation and intent.

- The ``repoze.bfg.traversal.find_model`` API did not work properly
  when passed a ``path`` argument which was unicode and contained
  high-order bytes when the ``unicode_path_segments`` or
  ``BFG_UNICODE_PATH_SEGMENTS`` configuration variables were "true".

- A new module was added: ``repoze.bfg.settings``.  This contains
  deployment-settings-related code.

Implementation Changes
----------------------

- The ``make_app`` callable within ``repoze.bfg.router`` now registers
  the ``root_policy`` argument as a utility (unnamed, using the new
  ``repoze.bfg.interfaces.IRootFactory`` as a provides interface)
  rather than passing it as the first argument to the
  ``repoze.bfg.router.Router`` class.  As a result, the
  ``repoze.bfg.router.Router`` router class only accepts a single
  argument: ``registry``.  The ``repoze.bfg.router.Router`` class
  retrieves the root policy via a utility lookup now.  The
  ``repoze.bfg.router.make_app`` API also now performs some important
  application registrations that were previously handled inside
  ``repoze.bfg.registry.makeRegistry``.

New Modules
-----------

- A ``repoze.bfg.settings`` module was added.  It contains code
  related to deployment settings.  Most of the code it contains was
  moved to it from the ``repoze.bfg.registry`` module.

Behavior Changes
----------------

- The ``repoze.bfg.settings.Settings`` class (an instance of which is
  registered as a utility providing
  ``repoze.bfg.interfaces.ISettings`` when any application is started)
  now automatically calls ``repoze.bfg.settings.get_options`` on the
  options passed to its constructor.  This means that usage of
  ``get_options`` within an application's ``make_app`` function is no
  longer required (the "raw" ``options`` dict or None may be passed).

- Remove old cold which attempts to recover from trying to unpickle a
  ``z3c.pt`` template; Chameleon has been the templating engine for a
  good long time now.  Running repoze.bfg against a sandbox that has
  pickled ``z3c.pt`` templates it will now just fail with an
  unpickling error, but can be fixed by deleting the template cache
  files.

Deprecations
------------

- Moved the ``repoze.bfg.registry.Settings`` class.  This has been
  moved to ``repoze.bfg.settings.Settings``. A deprecation warning is
  issued when it is imported from the older location.

- Moved the ``repoze.bfg.registry.get_options`` function This has been
  moved to ``repoze.bfg.settings.get_options``.  A deprecation warning
  is issued when it is imported from the older location.

- The ``repoze.bfg.interfaces.IRootPolicy`` interface was renamed
  within the interfaces package.  It has been renamed to
  ``IRootFactory``.  A deprecation warning is issued when it is
  imported from the older location.

0.6.1 (2009-01-06)
==================

New Modules
-----------

- A new module ``repoze.bfg.url`` has been added.  It contains the
  ``model_url`` API (moved from ``repoze.bfg.traversal``) and an
  implementation of ``urlencode`` (like Python's
  ``urllib.urlencode``) which can handle Unicode keys and values in
  parameters to the ``query`` argument.

Deprecations
------------

- The ``model_url`` function has been moved from
  ``repoze.bfg.traversal`` into ``repoze.bfg.url``.  It can still
  be imported from ``repoze.bfg.traversal`` but an import from
  ``repoze.bfg.traversal`` will emit a DeprecationWarning.

Features
--------

- A ``static`` helper class was added to the ``repoze.bfg.views``
  module.  Instances of this class are willing to act as BFG views
  which return static resources using files on disk.  See the
  ``repoze.bfg.view`` docs for more info.

- The ``repoze.bfg.url.model_url`` API (nee'
  ``repoze.bfg.traversal.model_url``) now accepts and honors a
  keyword argument named ``query``.  The value of this argument
  will be used to compose a query string, which will be attached to
  the generated URL before it is returned.  See the API docs (in
  the docs directory or on the web
  ``http://static.repoze.org/bfgdocs``) (broken URL) for more information.

0.6 (2008-12-26)
================

Backwards Incompatibilities
---------------------------

- Rather than prepare the "stock" implementations of the ZCML directives
  from the ``zope.configuration`` package for use under ``repoze.bfg``,
  ``repoze.bfg`` now makes available the implementations of directives
  from the ``repoze.zcml`` package (see https://pypi.org/project/repoze.zcml/).
  As a result, the ``repoze.bfg`` package now depends on the
  ``repoze.zcml`` package, and no longer depends directly on the
  ``zope.component``, ``zope.configuration``, ``zope.interface``, or
  ``zope.proxy`` packages.

  The primary reason for this change is to enable us to eventually reduce
  the number of inappropriate ``repoze.bfg`` Zope package dependencies,
  as well as to shed features of dependent package directives that don't
  make sense for ``repoze.bfg``.

  Note that currently the set of requirements necessary to use bfg has not
  changed.  This is due to inappropriate Zope package requirements in
  ``chameleon.zpt``, which will hopefully be remedied soon. NOTE: in
  lemonade index a 1.0b8-repozezcml0 package exists which does away with
  these requirements.

- BFG applications written prior to this release which expect the "stock"
  ``zope.component`` ZCML directive implementations (e.g. ``adapter``,
  ``subscriber``, or ``utility``) to function now must either 1) include
  the ``meta.zcml`` file from ``zope.component`` manually (e.g. ``<include
  package="zope.component" file="meta.zcml">``) and include the
  ``zope.security`` package as an ``install_requires`` dependency or 2)
  change the ZCML in their applications to use the declarations from
  `repoze.zcml <https://pypi.org/project/repoze.zcml/>`_ instead of the stock
  declarations.  ``repoze.zcml`` only makes available the ``adapter``,
  ``subscriber`` and ``utility`` directives.

  In short, if you've got an existing BFG application, after this
  update, if your application won't start due to an import error for
  "zope.security", the fastest way to get it working again is to add
  ``zope.security`` to the "install_requires" of your BFG
  application's ``setup.py``, then add the following ZCML anywhere
  in your application's ``configure.zcml``::

   <include package="zope.component" file="meta.zcml">

  Then re-``setup.py develop`` or reinstall your application.

- The ``http://namespaces.repoze.org/bfg`` XML namespace is now the default
  XML namespace in ZCML for paster-generated applications.  The docs have
  been updated to reflect this.

- The copies of BFG's ``meta.zcml`` and ``configure.zcml`` were removed
  from the root of the ``repoze.bfg`` package.  In 0.3.6, a new package
  named ``repoze.bfg.includes`` was added, which contains the "correct"
  copies of these ZCML files; the ones that were removed were for backwards
  compatibility purposes.

- The BFG ``view`` ZCML directive no longer calls
  ``zope.component.interface.provideInterface`` for the ``for`` interface.
  We don't support ``provideInterface`` in BFG because it mutates the
  global registry.

Other
-----

- The minimum requirement for ``chameleon.core`` is now 1.0b13.  The
  minimum requirement for ``chameleon.zpt`` is now 1.0b8.  The minimum
  requirement for ``chameleon.genshi`` is now 1.0b2.

- Updated paster template "ez_setup.py" to one that requires setuptools
  0.6c9.

- Turn ``view_execution_permitted`` from the ``repoze.bfg.view`` module
  into a documented API.

- Doc cleanups.

- Documented how to create a view capable of serving static resources.

0.5.6 (2008-12-18)
==================

- Speed up ``traversal.model_url`` execution by using a custom url quoting
  function instead of Python's ``urllib.quote``, by caching URL path
  segment quoting and encoding results, by disusing Python's
  ``urlparse.urljoin`` in favor of a simple string concatenation, and by
  using ``ob.__class__ is unicode`` rather than ``isinstance(ob, unicode)``
  in one strategic place.

0.5.5 (2008-12-17)
==================

Backwards Incompatibilities
---------------------------

- In the past, during traversal, the ModelGraphTraverser (the default
  traverser) always passed each URL path segment to any ``__getitem__``
  method of a model object as a byte string (a ``str`` object).  Now, by
  default the ModelGraphTraverser attempts to decode the path segment to
  Unicode (a ``unicode`` object) using the UTF-8 encoding before passing it
  to the ``__getitem__`` method of a model object.  This makes it possible
  for model objects to be dumber in ``__getitem__`` when trying to resolve
  a subobject, as model objects themselves no longer need to try to divine
  whether or not to try to decode the path segment passed by the
  traverser.

  Note that since 0.5.4, URLs generated by repoze.bfg's ``model_url`` API
  will contain UTF-8 encoded path segments as necessary, so any URL
  generated by BFG itself will be decodeable by the traverser.  If another
  application generates URLs to a BFG application, to be resolved
  successfully, it should generate the URL with UTF-8 encoded path segments
  to be successfully resolved.  The decoder is not at all magical: if a
  non-UTF-8-decodeable path segment (e.g. one encoded using UTF-16 or some
  other insanity) is passed in the URL, BFG will raise a ``TypeError`` with
  a message indicating it could not decode the path segment.

  To turn on the older behavior, where path segments were not decoded to
  Unicode before being passed to model object ``__getitem__`` by the
  traverser, and were passed as a raw byte string, set the
  ``unicode_path_segments`` configuration setting to a false value in your
  BFG application's section of the paste .ini file, for example::

    unicode_path_segments = False

  Or start the application using the ``BFG_UNICODE_PATH_SEGMENT`` envvar
  set to a false value::

    BFG_UNICODE_PATH_SEGMENTS=0

0.5.4 (2008-12-13)
==================

Backwards Incompatibilities
---------------------------

- URL-quote "extra" element names passed in as ``**elements`` to the
  ``traversal.model_url`` API.  If any of these names is a Unicode string,
  encode it to UTF-8 before URL-quoting.  This is a slight backwards
  incompatibility that will impact you if you were already UTF-8 encoding
  or URL-quoting the values you passed in as ``elements`` to this API.

Bugfixes
--------

- UTF-8 encode each segment in the model path used to generate a URL before
  url-quoting it within the ``traversal.model_url`` API.  This is a bugfix,
  as Unicode cannot always be successfully URL-quoted.

Features
--------

- Make it possible to run unit tests using a buildout-generated Python
  "interpreter".  

- Add ``request.root`` to ``router.Router`` in order to have easy access to
  the application root.

0.5.3 (2008-12-07)
==================

- Remove the ``ITestingTemplateRenderer`` interface.  When
  ``testing.registerDummyRenderer`` is used, it instead registers a dummy
  implementation using ``ITemplateRenderer`` interface, which is checked
  for when the built-in templating facilities do rendering.  This change
  also allows developers to make explicit named utility registrations in
  the ZCML registry against ``ITemplateRenderer``; these will be found
  before any on-disk template is looked up.

0.5.2 (2008-12-05)
==================

- The component registration handler for views (functions or class
  instances) now observes component adaptation annotations (see
  ``zope.component.adaptedBy``) and uses them before the fallback values
  for ``for_`` and ``request_type``. This change does not affect existing
  code insomuch as the code does not rely on these defaults when an
  annotation is set on the view (unlikely).  This means that for a
  new-style class you can do ``zope.component.adapts(ISomeContext,
  ISomeRequest)`` at class scope or at module scope as a decorator to a
  bfg view function you can do ``@zope.component.adapter(ISomeContext,
  ISomeRequest)``.  This differs from r.bfg.convention inasmuch as you
  still need to put something in ZCML for the registrations to get done;
  it's only the defaults that will change if these declarations exist.

- Strip all slashes from end and beginning of path in clean_path within
  traversal machinery.

0.5.1 (2008-11-25)
==================

- Add ``keys``, ``items``, and ``values`` methods to
  ``testing.DummyModel``.

- Add __delitem__ method to ``testing.DummyModel``.

0.5.0 (2008-11-18)
==================

- Fix ModelGraphTraverser; don't try to change the ``__name__`` or
  ``__parent__`` of an object that claims it implements ILocation during
  traversal even if the ``__name__`` or ``__parent__`` of the object
  traversed does not match the name used in the traversal step or the or
  the traversal parent .  Rationale: it was insane to do so. This bug was
  only found due to a misconfiguration in an application that mistakenly
  had intermediate persistent non-ILocation objects; traversal was causing
  a persistent write on every request under this setup.

- ``repoze.bfg.location.locate`` now unconditionally sets ``__name__`` and
  ``__parent__`` on objects which provide ILocation (it previously only set
  them conditionally if they didn't match attributes already present on the
  object via equality).

0.4.9 (2008-11-17)
==================

- Add chameleon text template API (chameleon ${name} renderings where the
  template does not need to be wrapped in any containing XML).

- Change docs to explain install in terms of a virtualenv
  (unconditionally).

- Make pushpage decorator compatible with repoze.bfg.convention's
  ``bfg_view`` decorator when they're stacked.

- Add content_length attribute to testing.DummyRequest.

- Change paster template ``tests.py`` to include a true unit test.  Retain
  old test as an integration test.  Update documentation.

- Document view registrations against classes and ``repoze.bfg.convention``
  in context.

- Change the default paster template to register its single view against a
  class rather than an interface.

- Document adding a request type interface to the request via a subscriber
  function in the events narrative documentation.

0.4.8 (2008-11-12)
==================

Backwards Incompatibilities
---------------------------

- ``repoze.bfg.traversal.model_url`` now always appends a slash to all
  generated URLs unless further elements are passed in as the third and
  following arguments.  Rationale: views often use ``model_url`` without
  the third-and-following arguments in order to generate a URL for a model
  in order to point at the default view of a model.  The URL that points to
  the default view of the *root* model is technically ``http://mysite/`` as
  opposed to ``http://mysite`` (browsers happen to ask for '/' implicitly
  in the GET request).  Because URLs are never automatically generated for
  anything *except* models by ``model_url``, and because the root model is
  not really special, we continue this pattern.  The impact of this change
  is minimal (at most you will have too many slashes in your URL, which BFG
  deals with gracefully anyway).

0.4.7 (2008-11-11)
==================

Features
--------

- Allow ``testing.registerEventListener`` to be used with Zope 3 style
  "object events" (subscribers accept more than a single event argument).
  We extend the list with the arguments, rather than append.

0.4.6 (2008-11-10)
==================

Bug Fixes
---------

- The ``model_path`` and ``model_url`` traversal APIs returned the wrong
  value for the root object (e.g. ``model_path`` returned ``''`` for the
  root object, while it should have been returning ``'/'``).

0.4.5 (2008-11-09)
==================

Features
--------

- Added a ``clone`` method and a ``__contains__`` method to the DummyModel
  testing object.

- Allow DummyModel objects to receive extra keyword arguments, which will
  be attached as attributes.

- The DummyTemplateRenderer now returns ``self`` as its implementation.

0.4.4 (2008-11-08)
==================

Features
--------

- Added a ``repoze.bfg.testing`` module to attempt to make it slightly
  easier to write unittest-based automated tests of BFG applications.
  Information about this module is in the documentation.

- The default template renderer now supports testing better by looking for
  ``ITestingTemplateRenderer`` using a relative pathname.  This is exposed
  indirectly through the API named ``registerTemplateRenderer`` in
  ``repoze.bfg.testing``.

Deprecations
------------

- The names ``repoze.bfg.interfaces.ITemplate`` ,
  ``repoze.bfg.interfaces.ITemplateFactory`` and
  ``repoze.bfg.interfaces.INodeTemplate`` have been deprecated.  These
  should now be imported as ``repoze.bfg.interfaces.ITemplateRenderer`` and
  ``repoze.bfg.interfaces.ITemplateRendererFactory``, and
  ``INodeTemplateRenderer`` respectively.

- The name ``repoze.bfg.chameleon_zpt.ZPTTemplateFactory`` is deprecated.
  Use ``repoze.bfg.chameleon_zpt.ZPTTemplateRenderer``.

- The name ``repoze.bfg.chameleon_genshi.GenshiTemplateFactory`` is
  deprecated.  Use ``repoze.bfg.chameleon_genshi.GenshiTemplateRenderer``.

- The name ``repoze.bfg.xslt.XSLTemplateFactory`` is deprecated.  Use
  ``repoze.bfg.xslt.XSLTemplateRenderer``.

0.4.3 (2008-11-02)
==================

Bug Fixes
---------

- Not passing the result of "get_options" as the second argument of
  make_app could cause attribute errors when attempting to look up settings
  against the ISettings object (internal).  Fixed by giving the Settings
  objects defaults for ``debug_authorization`` and ``debug_notfound``.

- Return an instance of ``Allowed`` (rather than ``True``) from
  ``has_permission`` when no security policy is in use.

- Fix bug where default deny in authorization check would throw a TypeError
  (use ``ACLDenied`` instead of ``Denied``).

0.4.2 (2008-11-02)
==================

Features
--------

- Expose a single ILogger named "repoze.bfg.debug" as a utility; this
  logger is registered unconditionally and is used by the authorization
  debug machinery.  Applications may also make use of it as necessary
  rather than inventing their own logger, for convenience.

- The ``BFG_DEBUG_AUTHORIZATION`` envvar and the ``debug_authorization``
  config file value now only imply debugging of view-invoked security
  checks.  Previously, information was printed for every call to
  ``has_permission`` as well, which made output confusing.  To debug
  ``has_permission`` checks and other manual permission checks, use the
  debugger and print statements in your own code.

- Authorization debugging info is now only present in the HTTP response
  body oif ``debug_authorization`` is true.

- The format of authorization debug messages was improved.

- A new ``BFG_DEBUG_NOTFOUND`` envvar was added and a symmetric
  ``debug_notfound`` config file value was added.  When either is true, and
  a NotFound response is returned by the BFG router (because a view could
  not be found), debugging information is printed to stderr.  When this
  value is set true, the body of HTTPNotFound responses will also contain
  the same debugging information.

- ``Allowed`` and ``Denied`` responses from the security machinery are now
  specialized into two types: ACL types, and non-ACL types.  The
  ACL-related responses are instances of ``repoze.bfg.security.ACLAllowed``
  and ``repoze.bfg.security.ACLDenied``.  The non-ACL-related responses are
  ``repoze.bfg.security.Allowed`` and ``repoze.bfg.security.Denied``.  The
  allowed-type responses continue to evaluate equal to things that
  themselves evaluate equal to the ``True`` boolean, while the denied-type
  responses continue to evaluate equal to things that themselves evaluate
  equal to the ``False`` boolean.  The only difference between the two
  types is the information attached to them for debugging purposes.

- Added a new ``BFG_DEBUG_ALL`` envvar and a symmetric ``debug_all`` config
  file value.  When either is true, all other debug-related flags are set
  true unconditionally (e.g. ``debug_notfound`` and
  ``debug_authorization``).

Documentation
-------------

- Added info about debug flag changes.

- Added a section to the security chapter named "Debugging Imperative
  Authorization Failures" (for e.g. ``has_permssion``).

Bug Fixes
---------

- Change default paster template generator to use ``Paste#http`` server
  rather than ``PasteScript#cherrpy`` server.  The cherrypy server has a
  security risk in it when ``REMOTE_USER`` is trusted by the downstream
  application.

0.4.1 (2008-10-28)
==================

Bug Fixes
---------

- If the ``render_view_to_response`` function was called, if the view was
  found and called, but it returned something that did not implement
  IResponse, the error would pass by unflagged.  This was noticed when I
  created a view function that essentially returned None, but received a
  NotFound error rather than a ValueError when the view was rendered.  This
  was fixed.

0.4.0 (2008-10-03)
==================

Docs 
----

- An "Environment and Configuration" chapter was added to the narrative 
  portion of the documentation.

Features
--------

- Ensure bfg doesn't generate warnings when running under Python
  2.6.

- The environment variable ``BFG_RELOAD_TEMPLATES`` is now available
  (serves the same purpose as ``reload_templates`` in the config file).

- A new configuration file option ``debug_authorization`` was added.
  This turns on printing of security authorization debug statements
  to ``sys.stderr``.  The ``BFG_DEBUG_AUTHORIZATION`` environment
  variable was also added; this performs the same duty.

Bug Fixes
---------

- The environment variable ``BFG_SECURITY_DEBUG`` did not always work.
  It has been renamed to ``BFG_DEBUG_AUTHORIZATION`` and fixed.

Deprecations
------------

- A deprecation warning is now issued when old API names from the
  ``repoze.bfg.templates`` module are imported.

Backwards incompatibilities
---------------------------

- The ``BFG_SECURITY_DEBUG`` environment variable was renamed to
  ``BFG_DEBUG_AUTHORIZATION``.

0.3.9 (2008-08-27)
==================

Features
--------

- A ``repoze.bfg.location`` API module was added.

Backwards incompatibilities
---------------------------

- Applications must now use the ``repoze.bfg.interfaces.ILocation``
  interface rather than ``zope.location.interfaces.ILocation`` to
  represent that a model object is "location-aware".  We've removed
  a dependency on ``zope.location`` for cleanliness purposes: as
  new versions of zope libraries are released which have improved
  dependency information, getting rid of our dependence on
  ``zope.location`` will prevent a newly installed repoze.bfg
  application from requiring the ``zope.security``, egg, which not
  truly used at all in a "stock" repoze.bfg setup.  These
  dependencies are still required by the stack at this time; this
  is purely a futureproofing move.

  The security and model documentation for previous versions of
  ``repoze.bfg`` recommended using the
  ``zope.location.interfaces.ILocation`` interface to represent
  that a model object is "location-aware".  This documentation has
  been changed to reflect that this interface should now be
  imported from ``repoze.bfg.interfaces.ILocation`` instead.

0.3.8 (2008-08-26)
==================

Docs
----

- Documented URL dispatch better in narrative form.

Bug fixes
---------

- Routes URL dispatch did not have access to the WSGI environment,
  so conditions such as method=GET did not work.

Features
--------

- Add ``principals_allowed_by_permission`` API to security module.

- Replace ``z3c.pt`` support with support for ``chameleon.zpt``.
  Chameleon is the new name for the package that used to be named
  ``z3c.pt``.  NOTE: If you update a ``repoze.bfg`` SVN checkout
  that you're using for development, you will need to run "setup.py
  install" or "setup.py develop" again in order to obtain the
  proper Chameleon packages.  ``z3c.pt`` is no longer supported by
  ``repoze.bfg``.  All API functions that used to render ``z3c.pt``
  templates will work fine with the new packages, and your
  templates should render almost identically.

- Add a ``repoze.bfg.chameleon_zpt`` module.  This module provides
  Chameleon ZPT support.

- Add a ``repoze.bfg.xslt`` module.  This module provides XSLT
  support.

- Add a ``repoze.bfg.chameleon_genshi`` module.  This provides
  direct Genshi support, which did not exist previously.

Deprecations
------------

- Importing API functions directly from ``repoze.bfg.template`` is
  now deprecated.  The ``get_template``, ``render_template``,
  ``render_template_to_response`` functions should now be imported
  from ``repoze.chameleon_zpt``.  The ``render_transform``, and
  ``render_transform_to_response`` functions should now be imported
  from ``repoze.bfg.xslt``.  The ``repoze.bfg.template`` module
  will remain around "forever" to support backwards compatibility.

0.3.7 (2008-09-09)
==================

Features
--------

- Add compatibility with z3c.pt 1.0a7+ (z3c.pt became a namespace package).

Bug fixes
---------

- ``repoze.bfg.traversal.find_model`` function did not function properly.

0.3.6 (2008-09-04)
==================

Features
--------

- Add startup process docs.

- Allow configuration cache to be bypassed by actions which include special
  "uncacheable" discriminators (for actions that have variable results).

Bug Fixes
---------

- Move core repoze.bfg ZCML into a ``repoze.bfg.includes`` package so we
  can use repoze.bfg better as a namespace package.  Adjust the code
  generator to use it.  We've left around the ``configure.zcml`` in the
  repoze.bfg package directly so as not to break older apps.

- When a zcml application registry cache was unpickled, and it contained a
  reference to an object that no longer existed (such as a view), bfg would
  not start properly.

0.3.5 (2008-09-01)
==================

Features
--------

- Event notification is issued after application is created and configured
  (``IWSGIApplicationCreatedEvent``).

- New API module: ``repoze.bfg.view``.  This module contains the functions
  named ``render_view_to_response``, ``render_view_to_iterable``,
  ``render_view`` and ``is_response``, which are documented in the API
  docs.  These features aid programmatic (non-server-driven) view
  execution.

0.3.4 (2008-08-28)
==================

Backwards incompatibilities
---------------------------

- Make ``repoze.bfg`` a namespace package so we can allow folks to create
  subpackages (e.g. ``repoze.bfg.otherthing``) within separate eggs.  This
  is a backwards incompatible change which makes it impossible to import
  "make_app" and "get_options" from the ``repoze.bfg`` module directly.
  This change will break all existing apps generated by the paster code
  generator.  Instead, you need to import these functions as
  ``repoze.bfg.router:make_app`` and ``repoze.bfg.registry:get_options``,
  respectively.  Sorry folks, it has to be done now or never, and
  definitely better now.

Features
--------

- Add ``model_path`` API function to traversal module.

Bugfixes

- Normalize path returned by repoze.bfg.caller_path.

0.3.3 (2008-08-23)
==================

- Fix generated test.py module to use project name rather than package
  name.

0.3.2 (2008-08-23)
==================

- Remove ``sampleapp`` sample application from bfg package itself.

- Remove dependency on FormEncode (only needed by sampleapp).

- Fix paster template generation so that case-sensitivity is preserved for
  project vs. package name.

- Depend on ``z3c.pt`` version 1.0a1 (which requires the ``[lxml]`` extra
  currently).

- Read and write a pickled ZCML actions list, stored as
  ``configure.zcml.cache`` next to the applications's "normal"
  configuration file.  A given bfg app will usually start faster if it's
  able to read the pickle data.  It fails gracefully to reading the real
  ZCML file if it cannot read the pickle.

0.3.1 (2008-08-20)
==================

- Generated application differences: ``make_app`` entry point renamed to
  ``app`` in order to have a different name than the bfg function of the
  same name, to prevent confusion.

- Add "options" processing to bfg's ``make_app`` to support runtime
  options.  A new API function named ``get_options`` was added to the
  registry module.  This function is typically used in an application's
  ``app`` entry point.  The Paste config file section for the app can now
  supply the ``reload_templates`` option, which, if true, will prevent the
  need to restart the appserver in order for ``z3c.pt`` or XSLT template
  changes to be detected.

- Use only the module name in generated project's "test_suite" (run all
  tests found in the package).

- Default port for generated apps changed from 5432 to 6543 (Postgres
  default port is 6543).

0.3.0 (2008-08-16)
==================

- Add ``get_template`` API to template module.

0.2.9 (2008-08-11)
==================

- 0.2.8 was "brown bag" release.  It didn't work at all.  Symptom:
  ComponentLookupError when trying to render a page.

0.2.8 (2008-08-11)
==================

- Add ``find_model`` and ``find_root`` traversal APIs.  In the process,
  make ITraverser a uni-adapter (on context) rather than a multiadapter (on
  context and request).

0.2.7 (2008-08-05)
==================

- Add a ``request_type`` attribute to the available attributes of a
  ``bfg:view`` configure.zcml element.  This attribute will have a value
  which is a dotted Python path, pointing at an interface.  If the request
  object implements this interface when the view lookup is performed, the
  appropriate view will be called.  This is meant to allow for simple
  "skinning" of sites based on request type.  An event subscriber should
  attach the interface to the request on ingress to support skins.

- Remove "template only" views.  These were just confusing and were never
  documented.

- Small url dispatch overhaul: the ``connect`` method of the
  ``urldispatch.RoutesMapper`` object now accepts a keyword parameter named
  ``context_factory``.  If this parameter is supplied, it must be a
  callable which returns an instance.  This instance is used as the context
  for the request when a route is matched.

- The registration of a RoutesModelTraverser no longer needs to be
  performed by the application; it's in the bfg ZCML now.

0.2.6 (2008-07-31)
==================

- Add event sends for INewRequest and INewResponse.  See the events.rst
  chapter in the documentation's ``api`` directory.

0.2.5 (2008-07-28)
==================

- Add ``model_url`` API.

0.2.4 (2008-07-27)
==================

- Added url-based dispatch.

0.2.3 (2008-07-20)
==================

- Add API functions for authenticated_userid and effective_principals.

0.2.2 (2008-07-20)
==================

- Add authenticated_userid and effective_principals API to security
  policy.

0.2.1 (2008-07-20)
==================

- Add find_interface API.

0.2 (2008-07-19)
================

- Add wsgiapp decorator.

- The concept of "view factories" was removed in favor of always calling a
  view, which is a callable that returns a response directly (as opposed to
  returning a view).  As a result, the ``factory`` attribute in the
  bfg:view ZCML statement has been renamed to ``view``.  Various interface
  names were changed also.

- ``render_template`` and ``render_transform`` no longer return a Response
  object.  Instead, these return strings.  The old behavior can be obtained
  by using ``render_template_to_response`` and
  ``render_transform_to_response``.

- Added 'repoze.bfg.push:pushpage' decorator, which creates BFG views from
  callables which take (context, request) and return a mapping of top-level
  names.

- Added ACL-based security.

- Support for XSLT templates via a render_transform method

0.1 (2008-07-08)
================

- Initial release.

