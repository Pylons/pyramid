What's New In :mod:`repoze.bfg` 1.2
===================================

This article explains the new features in :mod:`repoze.bfg` version
1.2 as compared to the previous 1.1 release.  It also documents
backwards incompatibilities between the two versions and deprecations
added to 1.2, as well as software dependency changes and notable
documentation additions.

Major Feature Additions
-----------------------

The major feature addition in 1.2 is an :term:`imperative
configuration` mode.

A :mod:`repoze.bfg` application can now begin its life as a single
Python file.  Later, the application might evolve into a set of Python
files in a package.  Even later, it might start making use of other
configuration features, such as :term:`ZCML` and perhaps a
:term:`scan`.  But neither the use of a package nor the use of
non-imperative configuration is required to create a simple
:mod:`repoze.bfg` application any longer.

:term:`Imperative configuration` makes :mod:`repoze.bfg` competitive
with "microframeworks" such as `Bottle <http://bottle.paws.de/>`_ and
`Tornado <http://www.tornadoweb.org/>`_.  :mod:`repoze.bfg` has a good
deal of functionality that most microframeworks lack, so this is
hopefully a "best of both worlds" feature.

The simplest possible :mod:`repoze.bfg` application is now:

  .. code-block:: python
     :linenos:

     from webob import Response
     from paste.httpserver import serve
     from repoze.bfg.configuration import Configurator

     def hello_world(request):
         return Response('Hello world!')

     if __name__ == '__main__':
         config = Configurator()
         config.begin()
         config.add_view(hello_world)
         config.end()
         app = config.make_wsgi_app()
         serve(app)

For an introduction to imperative-mode configuration, see
:ref:`configuration_narr`.

Minor Miscellaneous Feature Additions
-------------------------------------

- The :func:`repoze.bfg.testing.setUp` function now accepts three
  extra optional keyword arguments: ``registry``, ``request`` and
  ``hook_zca``.

  If the ``registry`` argument is not ``None``, the argument will be
  treated as the registry that is set as the "current registry" (it
  will be returned by
  :func:`repoze.bfg.threadlocal.get_current_registry`) for the
  duration of the test.  If the ``registry`` argument is ``None`` (the
  default), a new registry is created and used for the duration of the
  test.

  The value of the ``request`` argument is used as the "current
  request" (it will be returned by
  :func:`repoze.bfg.threadlocal.get_current_request`) for the duration
  of the test; it defaults to ``None``.

  If ``hook_zca`` is ``True`` (the default), the
  :func:`zope.component.getSiteManager` function will be hooked with a
  function that returns the value of ``registry`` (or the
  default-created registry if ``registry`` is ``None``) instead of the
  registry returned by :func:`zope.component.getGlobalSiteManager`,
  causing the Zope Component Architecture API (``getSiteManager``,
  ``getAdapter``, ``getUtility``, and so on) to use the testing
  registry instead of the global ZCA registry.

- The :func:`repoze.bfg.testing.tearDown` function now accepts an
  ``unhook_zca`` argument.  If this argument is ``True`` (the
  default), :func:`zope.component.getSiteManager.reset` will be
  called.  This will cause the result of the
  :func:`zope.component.getSiteManager` function to be the global ZCA
  registry (the result of :func:`zope.component.getGlobalSiteManager`)
  once again.

- :class:`repoze.bfg.testing.DummyModel` now accepts a new constructor
  keyword argument: ``__provides__``.  If this constructor argument is
  provided, it should be an interface or a tuple of interfaces.  The
  resulting model will then provide these interfaces (they will be
  attached to the constructed model via
  :func:`zope.interface.alsoProvides`).

- When the :exc:`repoze.bfg.exceptions.NotFound` or
  :exc:`repoze.bfg.exceptions.Forbidden` error is raised from within a
  custom :term:`root factory` or the factory of a :term:`route`, the
  appropriate response is sent to the requesting user agent (the
  result of the notfound view or the forbidden view, respectively).
  When these errors are raised from within a root factory, the
  :term:`context` passed to the notfound or forbidden view will be
  ``None``.  Also, the request will not be decorated with
  ``view_name``, ``subpath``, ``context``, etc. as would normally be
  the case if traversal had been allowed to take place.

Backwards Incompatibilites
--------------------------

- Unit tests which use :func:`zope.testing.cleanup.cleanUp` for the
  purpose of isolating tests from one another may now begin to fail
  due to lack of isolation between tests.

  Here's why: In repoze.bfg 1.1 and prior, the registry returned by
  :func:`repoze.bfg.threadlocal.get_current_registry` when no other
  registry had been pushed on to the threadlocal stack was the
  :data:`zope.component.globalregistry.base` global registry (aka the
  result of :func:`zope.component.getGlobalSiteManager()`).  In
  :mod:`repoze.bfg` 1.2+, however, the registry returned in this
  situation is the new module-scope
  :data:`repoze.bfg.registry.global_registry` object.  The
  :func:`zope.testing.cleanup.cleanUp` function clears the
  :data:`zope.component.globalregistry.base` global registry
  unconditionally.  However, it does not know about the
  :data:`repoze.bfg.registry.global_registry` object, so it does not
  clear it.

  If you use the :func:`zope.testing.cleanup.cleanUp` function in the
  ``setUp`` of test cases in your unit test suite instead of using the
  (more correct as of 1.1) :func:`repoze.bfg.testing.setUp`, you will
  need to replace all calls to :func:`zope.testing.cleanup.cleanUp`
  with a call to :func:`repoze.bfg.testing.setUp`.

  If replacing all calls to :func:`zope.testing.cleanup.cleanUp` with
  a call to :func:`repoze.bfg.testing.setUp` is infeasible, you can
  put the below-mentioned bit of code somewhere that is executed
  exactly **once** (*not* for each test in a test suite).  Placing
  this in the ``__init__.py`` of your package or the ``__init__.py``
  of a ``tests`` subpackage would be a reasonable place)::

    import zope.testing.cleanup
    from repoze.bfg.testing import setUp
    zope.testing.cleanup.addCleanUp(setUp)

- When there is no "current registry" in the
  :data:`repoze.bfg.threadlocal.manager` threadlocal data structure
  (this is the case when there is no "current request" or we're not in
  the midst of a :func:`repoze.bfg.testing.setUp` or
  :meth:`repoze.bfg.configuration.Configurator.begin` bounded unit
  test), the ``.get`` method of the manager returns a data structure
  containing a *global* registry.  In previous releases, this function
  returned the global Zope "base" registry: the result of
  :func:`zope.component.getGlobalSiteManager`, which is an instance of
  the :class:`zope.component.registry.Component` class.  In this
  release, however, the global registry returns a globally importable
  instance of the :class:`repoze.bfg.registry.Registry` class.  This
  registry instance can always be imported as
  :data:`repoze.bfg.registry.global_registry`.

  Effectively, this means that when you call
  :func:`repoze.bfg.threadlocal.get_current_registry` when no "real"
  request or bounded unit test is in effect, you will always get back
  the global registry that lives in
  :data:`repoze.bfg.registry.global_registry`.  It also means that
  :mod:`repoze.bfg` APIs that *call*
  :func:`repoze.bfg.threadlocal.get_current_registry` will use this
  registry.

  This change was made because :mod:`repoze.bfg` now expects the
  registry it uses to have a slightly different API than a bare
  instance of :class:`zope.component.registry.Components`.

- View registration no longer registers a
  :class:`repoze.bfg.interfaces.IViewPermission` adapter (it is no
  longer checked by the framework; since 1.1, views have been
  responsible for providing their own security).

- The :func:`repoze.bfg.router.make_app` callable no longer accepts an
  ``authentication_policy`` nor an ``authorization_policy`` argument.
  These features were deprecated in version 1.0 and have been removed.

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
  the responsibility of the :mod:`repoze.bfg.includes` ZCML to include
  this file in the past; it now just doesn't.

- The :func:`repoze.bfg.testing.zcml_configure` API was removed.  Use
  the :meth:`repoze.bfg.configuration.Configurator.load_zcml` API
  instead.

- The :mod:`repoze.bfg.templating` module has been removed; it had
  been deprecated in 1.1 and hasn't possessed any APIs since before
  1.0.

Deprecations and Behavior Differences
-------------------------------------

- If you disuse the legacy :func:`repoze.bfg.router.make_app` function
  in favor of
  :meth:`repoze.bfg.configuration.Configurator.make_wsgi_app`, and you
  also want to use the "global" ZCA API (``getUtility``,
  ``getAdapter``, ``getSiteManager``, etc), you will need to "hook"
  the ZCA before calling methods of the configurator using the
  ``sethook`` method of the ``getSiteManager`` API, e.g.::

    from zope.component import getSiteManager
    from repoze.bfg.configuration import Configurator
    from repoze.bfg.threadlocal import get_current_registry
    from mypackage.models import get_root

    def app(global_config, **settings):
        config = Configurator(root_factory=get_root, settings=settings)
        getSiteManager.sethook(get_current_registry)
        zcml_file = settings.get('configure_zcml', 'configure.zcml')
        config.load_zcml(zcml_file)
        return config.make_wsgi_app()

  The :func:`repoze.bfg.router.make_app` function does this on your
  behalf for backward compatibility purposes.

- The :func:`repoze.bfg.router.make_app` function is now nominally
  deprecated.  Its import and usage does not throw a warning, nor will
  it probably ever disappear.  However, using a
  :class:`repoze.bfg.configuration.Configurator` class is now the
  preferred way to generate a WSGI application.

  Note that :func:`repoze.bfg.router.make_app` calls
  ``zope.component.getSiteManager.sethook(
  repoze.bfg.threadlocal.get_current_registry)`` on the caller's
  behalf, hooking ZCA global API lookups, for backwards compatibility
  purposes.  If you disuse ``make_app``, your calling code will need
  to perform this call itself, at least if your application uses the
  ZCA global API (``getSiteManager``, ``getAdapter``, etc).

Dependency Changes
------------------

- A dependency on the ``martian`` package has been removed (its
  functionality is replaced internally).

- A dependency on the ``repoze.zcml`` package has been removed (its
  functionality is replaced internally).

Documentation Enhancements
--------------------------

- The documentation now uses the "request-only" view calling
  convention in most examples (as opposed to the ``context, request``
  convention).  This is a documentation-only change; the ``context,
  request`` convention is also supported and documented, and will be
  "forever".

- :mod:`repoze.bfg.configuration` API documentation has been added.

- A narrative documentation chapter entitled "Creating Your First
  ``repoze.bfg`` Application" has been added.  This chapter details
  usage of the new :class:`repoze.bfg.configuration.Configurator`
  class, and demonstrates a simplified "imperative-mode"
  configuration; doing :mod:`repoze.bfg` application configuration
  imperatively was previously much more difficult.

- A narrative documentation chapter entitled "Configuration,
  Decorations and Code Scanning" (:ref:`scanning_chapter`) explaining
  ZCML- vs. imperative- vs. decorator-based configuration equivalence.

- The "ZCML Hooks" chapter has been renamed to "Hooks"
  (:ref:`hooks_chapter`); it documents how to override hooks now via
  imperative configuration and ZCML.

- The explanation about how to supply an alternate "response factory"
  has been removed from the "Hooks" chapter.  This feature may be
  removed in a later release (it still works now, it's just not
  documented).

- Add a section entitled "Test Set Up and Tear Down" to the
  unittesting chapter (:ref:`unittesting_chapter`).

- Remove explanation of changing the request type in a new request
  event subscriber in the "Events" narrative documentation chapter, as
  other predicates are now usually an easier way to get this done.

- Added "Thread Locals" narrative chapter to documentation, and added
  a API chapter documenting the :mod:`repoze.bfg.threadlocals` module.

- Added a "Special Exceptions" section to the "Views" narrative
  documentation chapter explaining the effect of raising
  :exc:`repoze.bfg.exceptions.NotFound` and
  :exc:`repoze.bfg.exceptions.Forbidden` from within view code.
