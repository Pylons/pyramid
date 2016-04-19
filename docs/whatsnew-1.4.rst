What's New in Pyramid 1.4
=========================

This article explains the new features in :app:`Pyramid` version 1.4 as
compared to its predecessor, :app:`Pyramid` 1.3.  It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 1.4, as well as software dependency changes and notable
documentation additions.

Major Feature Additions
-----------------------

The major feature additions in Pyramid 1.4 follow.

Third-Party Predicates
~~~~~~~~~~~~~~~~~~~~~~~

- Third-party custom view, route, and subscriber predicates can now be added
  for use by view authors via
  :meth:`pyramid.config.Configurator.add_view_predicate`,
  :meth:`pyramid.config.Configurator.add_route_predicate` and
  :meth:`pyramid.config.Configurator.add_subscriber_predicate`.  So, for
  example, doing this::

     config.add_view_predicate('abc', my.package.ABCPredicate)

  Might allow a view author to do this in an application that configured that
  predicate::

     @view_config(abc=1)

  Similar features exist for :meth:`pyramid.config.Configurator.add_route`,
  and :meth:`pyramid.config.Configurator.add_subscriber`.  See
  :ref:`registering_thirdparty_predicates` for more information.

Easy Custom JSON Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Views can now return custom objects which will be serialized to JSON by a
  JSON renderer by defining a ``__json__`` method on the object's class. This
  method should return values natively serializable by ``json.dumps`` (such
  as ints, lists, dictionaries, strings, and so forth).  See
  :ref:`json_serializing_custom_objects` for more information.  The JSON
  renderer now also allows for the definition of custom type adapters to
  convert unknown objects to JSON serializations, in case you can't add a
  ``__json__`` method to returned objects.

Partial Mako and Chameleon Template Renderings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The Mako renderer now supports using a def name in an asset spec.  When the
  def name is present in the asset spec, the system will render the template
  named def within the template instead of rendering the entire template. An
  example asset spec which names a def is
  ``package:path/to/template#defname.mako``. This will render the def named
  ``defname`` inside the ``template.mako`` template instead of rendering the
  entire template.  The old way of returning a tuple in the form
  ``('defname', {})`` from the view is supported for backward compatibility.

- The Chameleon ZPT renderer now supports using a macro name in an asset
  spec.  When the macro name is present in the asset spec, the system will
  render the macro listed as a ``define-macro`` and return the result instead
  of rendering the entire template.  An example asset spec:
  ``package:path/to/template#macroname.pt``.  This will render the macro
  defined as ``macroname`` within the ``template.pt`` template instead of the
  entire template.

Subrequest Support
~~~~~~~~~~~~~~~~~~

- Developers may invoke a subrequest by using the
  :meth:`pyramid.request.Request.invoke_subrequest` API.  This allows a
  developer to obtain a response from one view callable by issuing a subrequest
  from within a different view callable.  See :ref:`subrequest_chapter` for
  more information.

Minor Feature Additions
-----------------------

- :class:`pyramid.authentication.AuthTktAuthenticationPolicy` has been updated
  to support newer hashing algorithms such as ``sha512``. Existing applications
  should consider updating if possible for improved security over the default
  md5 hashing.

- :meth:`pyramid.config.Configurator.add_directive` now accepts arbitrary
  callables like partials or objects implementing ``__call__`` which don't
  have ``__name__`` and ``__doc__`` attributes.  See
  https://github.com/Pylons/pyramid/issues/621 and
  https://github.com/Pylons/pyramid/pull/647.

- As of this release, the ``request_method`` view/route predicate, when used,
  will also imply that ``HEAD`` is implied when you use ``GET``.  For
  example, using ``@view_config(request_method='GET')`` is equivalent to
  using ``@view_config(request_method=('GET', 'HEAD'))``.  Using
  ``@view_config(request_method=('GET', 'POST')`` is equivalent to using
  ``@view_config(request_method=('GET', 'HEAD', 'POST')``.  This is because
  HEAD is a variant of GET that omits the body, and WebOb has special support
  to return an empty body when a HEAD is used.

- :meth:`pyramid.config.Configurator.add_request_method` has been introduced
  to support extending request objects with arbitrary callables. This method
  expands on the now documentation-deprecated
  :meth:`pyramid.config.Configurator.set_request_property` by supporting
  methods as well as properties. This method also causes less code to be
  executed at request construction time than
  :meth:`~pyramid.config.Configurator.set_request_property`.

- The static view machinery now raises rather than returns
  :class:`pyramid.httpexceptions.HTTPNotFound` and
  :class:`pyramid.httpexceptions.HTTPMovedPermanently` exceptions, so these can
  be caught by the Not Found View (and other exception views).

- When there is a predicate mismatch exception (seen when no view matches for
  a given request due to predicates not working), the exception now contains
  a textual description of the predicate which didn't match.

- An :meth:`pyramid.config.Configurator.add_permission` directive method was
  added to the Configurator.  This directive registers a free-standing
  permission introspectable into the Pyramid introspection system.
  Frameworks built atop Pyramid can thus use the ``permissions``
  introspectable category data to build a comprehensive list of permissions
  supported by a running system.  Before this method was added, permissions
  were already registered in this introspectable category as a side effect of
  naming them in an :meth:`pyramid.config.Configurator.add_view` call, this
  method just makes it possible to arrange for a permission to be put into
  the ``permissions`` introspectable category without naming it along with an
  associated view.  Here's an example of usage of ``add_permission``::

      config = Configurator()
      config.add_permission('view')

- The :func:`pyramid.session.UnencryptedCookieSessionFactoryConfig` function
  now accepts ``signed_serialize`` and ``signed_deserialize`` hooks which may
  be used to influence how the sessions are marshalled (by default this is
  done with HMAC+pickle).

- :class:`pyramid.testing.DummyRequest` now supports methods supplied by the
  ``pyramid.util.InstancePropertyMixin`` class such as ``set_property``.

- Request properties and methods added via
  :meth:`pyramid.config.Configurator.add_request_method` or
  :meth:`pyramid.config.Configurator.set_request_property` are now available to
  tweens.

- Request properties and methods added via
  :meth:`pyramid.config.Configurator.add_request_method` or
  :meth:`pyramid.config.Configurator.set_request_property` are now available
  in the request object returned from :func:`pyramid.paster.bootstrap`.

- ``request.context`` of environment request during
  :func:`pyramid.paster.bootstrap` is now the root object if a context isn't
  already set on a provided request.

- :class:`pyramid.decorator.reify`  is now an API, and was added to
  the API documentation.

- Added the :func:`pyramid.testing.testConfig` context manager, which can be
  used to generate a configurator in a test, e.g. ``with
  testing.testConfig(...):``.

- A new :func:`pyramid.session.check_csrf_token` convenience API function was
  added.

- A ``check_csrf`` view predicate was added.  For example, you can now do
  ``config.add_view(someview, check_csrf=True)``.  When the predicate is
  checked, if the ``csrf_token`` value in ``request.params`` matches the csrf
  token in the request's session, the view will be permitted to execute.
  Otherwise, it will not be permitted to execute.

- Add ``Base.metadata.bind = engine`` to ``alchemy`` scaffold, so that tables
  defined imperatively will work.

- Comments with references to documentation sections placed in scaffold
  ``.ini`` files.

- Allow multiple values to be specified to the ``request_param`` view/route
  predicate as a sequence.  Previously only a single string value was allowed.
  See https://github.com/Pylons/pyramid/pull/705

- Added an HTTP Basic authentication policy
  at :class:`pyramid.authentication.BasicAuthAuthenticationPolicy`.

- The :meth:`pyramid.config.Configurator.testing_securitypolicy` method now
  returns the policy object it creates.

- The DummySecurityPolicy created by
  :meth:`pyramid.config.Configurator.testing_securitypolicy` now sets a
  ``forgotten`` value  on the policy (the value ``True``) when its ``forget``
  method is called.

- The DummySecurityPolicy created by
  :meth:`pyramid.config.Configurator.testing_securitypolicy` now sets a
  ``remembered`` value on the policy, which is the value of the ``principal``
  argument it's called with when its ``remember`` method is called.

- New ``physical_path`` view predicate.  If specified, this value should be a
  string or a tuple representing the physical traversal path of the context
  found via traversal for this predicate to match as true.  For example:
  ``physical_path='/'`` or ``physical_path='/a/b/c'`` or ``physical_path=('',
  'a', 'b', 'c')``.  It's useful when you want to always potentially show a
  view when some object is traversed to, but you can't be sure about what kind
  of object it will be, so you can't use the ``context`` predicate.  

- Added an ``effective_principals`` route and view predicate.

- Do not allow the userid returned from the
  :func:`pyramid.security.authenticated_userid` or the userid that is one of the
  list of principals returned by :func:`pyramid.security.effective_principals`
  to be either of the strings ``system.Everyone`` or ``system.Authenticated``
  when any of the built-in authorization policies that live in
  :mod:`pyramid.authentication` are in use.  These two strings are reserved for
  internal usage by Pyramid and they will no longer be accepted as valid
  userids.

- Allow a ``_depth`` argument to :class:`pyramid.view.view_config`, which will
  permit limited composition reuse of the decorator by other software that
  wants to provide custom decorators that are much like view_config.

- Allow an iterable of decorators to be passed to
  :meth:`pyramid.config.Configurator.add_view`. This allows views to be wrapped
  by more than one decorator without requiring combining the decorators 
  yourself.

- :func:`pyramid.security.view_execution_permitted` used to return `True` if no
  view could be found. It now raises a :exc:`TypeError` exception in that case,
  as it doesn't make sense to assert that a nonexistent view is
  execution-permitted. See https://github.com/Pylons/pyramid/issues/299.

- Small microspeed enhancement which anticipates that a
  :class:`pyramid.response.Response` object is likely to be returned from a 
  view.  Some code is shortcut if the class of the object returned by a view is 
  this class.  A similar microoptimization was done to
  :func:`pyramid.request.Request.is_response`.

- Make it possible to use variable arguments on all ``p*`` commands
  (``pserve``, ``pshell``, ``pviews``, etc) in the form ``a=1 b=2`` so you can
  fill in values in parameterized ``.ini`` file, e.g. ``pshell
  etc/development.ini http_port=8080``.

- In order to allow people to ignore unused arguments to subscriber callables
  and to normalize the relationship between event subscribers and subscriber
  predicates, we now allow both subscribers and subscriber predicates to accept
  only a single ``event`` argument even if they've been subscribed for
  notifications that involve multiple interfaces.

Backwards Incompatibilities
---------------------------

- The Pyramid router no longer adds the values ``bfg.routes.route`` or
  ``bfg.routes.matchdict`` to the request's WSGI environment dictionary.
  These values were docs-deprecated in ``repoze.bfg`` 1.0 (effectively seven
  minor releases ago).  If your code depended on these values, use
  ``request.matched_route`` and ``request.matchdict`` instead.

- It is no longer possible to pass an environ dictionary directly to
  ``pyramid.traversal.ResourceTreeTraverser.__call__`` (aka
  ``ModelGraphTraverser.__call__``).  Instead, you must pass a request
  object.  Passing an environment instead of a request has generated a
  deprecation warning since Pyramid 1.1.

- Pyramid will no longer work properly if you use the
  ``webob.request.LegacyRequest`` as a request factory.  Instances of the
  LegacyRequest class have a ``request.path_info`` which return a string.
  This Pyramid release assumes that ``request.path_info`` will
  unconditionally be Unicode.

- The functions from ``pyramid.chameleon_zpt`` and ``pyramid.chameleon_text``
  named ``get_renderer``, ``get_template``, ``render_template``, and
  ``render_template_to_response`` have been removed.  These have issued a
  deprecation warning upon import since Pyramid 1.0.  Use
  :func:`pyramid.renderers.get_renderer`,
  ``pyramid.renderers.get_renderer().implementation()``,
  :func:`pyramid.renderers.render` or
  :func:`pyramid.renderers.render_to_response` respectively instead of these
  functions.

- The ``pyramid.configuration`` module was removed.  It had been deprecated
  since Pyramid 1.0 and printed a deprecation warning upon its use.  Use
  :mod:`pyramid.config` instead.

- The ``pyramid.paster.PyramidTemplate`` API was removed.  It had been
  deprecated since Pyramid 1.1 and issued a warning on import.  If your code
  depended on this, adjust your code to import
  :class:`pyramid.scaffolds.PyramidTemplate` instead.

- The ``pyramid.settings.get_settings()`` API was removed.  It had been
  printing a deprecation warning since Pyramid 1.0.  If your code depended on
  this API, use ``pyramid.threadlocal.get_current_registry().settings``
  instead or use the ``settings`` attribute of the registry available from
  the request (``request.registry.settings``).

- These APIs from the ``pyramid.testing`` module were removed.  They have
  been printing deprecation warnings since Pyramid 1.0:

  * ``registerDummySecurityPolicy``, use
    :meth:`pyramid.config.Configurator.testing_securitypolicy` instead.

  * ``registerResources`` (aka ``registerModels``), use
    :meth:`pyramid.config.Configurator.testing_resources` instead.

  * ``registerEventListener``, use
    :meth:`pyramid.config.Configurator.testing_add_subscriber` instead.

  * ``registerTemplateRenderer`` (aka ``registerDummyRenderer``), use
    :meth:`pyramid.config.Configurator.testing_add_renderer` instead.

  * ``registerView``, use :meth:`pyramid.config.Configurator.add_view` instead.

  * ``registerUtility``, use
    :meth:`pyramid.config.Configurator.registry.registerUtility` instead.

  * ``registerAdapter``, use
    :meth:`pyramid.config.Configurator.registry.registerAdapter` instead.

  * ``registerSubscriber``, use 
    :meth:`pyramid.config.Configurator.add_subscriber` instead.

  * ``registerRoute``, use 
    :meth:`pyramid.config.Configurator.add_route` instead.

  * ``registerSettings``, use 
    :meth:`pyramid.config.Configurator.add_settings` instead.

- In Pyramid 1.3 and previous, the ``__call__`` method of a Response object
  returned by a view was invoked before any finished callbacks were executed.
  As of this release, the ``__call__`` method of a Response object is invoked
  *after* finished callbacks are executed.  This is in support of the
  :meth:`pyramid.request.Request.invoke_subrequest` feature.

Deprecations
------------

- The :meth:`pyramid.config.Configurator.set_request_property` directive has
  been documentation-deprecated.  The method remains usable but the more
  featureful :meth:`pyramid.config.Configurator.add_request_method` should be
  used in its place (it has all of the same capabilities but can also extend
  the request object with methods).

- :class:`pyramid.authentication.AuthTktAuthenticationPolicy` will emit a
  deprecation warning if an application is using the policy without explicitly
  passing a ``hashalg`` argument. This is because the default is "md5" which is
  considered theoretically subject to collision attacks. If you really want
  "md5" then you must specify it explicitly to get rid of the warning.

Documentation Enhancements
--------------------------

- Added an :ref:`upgrading_chapter` chapter to the narrative documentation.
  It describes how to cope with deprecations and removals of Pyramid APIs and
  how to show Pyramid-generated deprecation warnings while running tests and
  while running a server.

- Added a :ref:`subrequest_chapter` chapter to the narrative documentation.

- All of the tutorials that use
  :class:`pyramid.authentication.AuthTktAuthenticationPolicy` now explicitly 
  pass ``sha512`` as a ``hashalg`` argument.

- Many cleanups and improvements to narrative and API docs.

Dependency Changes
------------------

- Pyramid now requires WebOb 1.2b3+ (the prior Pyramid release only relied on
  1.2dev+).  This is to ensure that we obtain a version of WebOb that returns
  ``request.path_info`` as text.

