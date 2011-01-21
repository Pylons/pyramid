What's New In Pyramid 1.0
=========================

This article explains the new features in Pyramid version 1.0 as compared to
its predecessor, :mod:`repoze.bfg` 1.3.  It also documents backwards
incompatibilities between the two versions and deprecations added to Pyramid
1.0, as well as software dependency changes and notable documentation
additions.

Major Feature Additions
-----------------------

The major feature additions in Pyramid 1.0 are:

- New name and branding association with the Pylons Project.

- Paster template improvements

- Terminology changes

- Better platform compatibility and support

- Direct built-in support for the Mako templating language.

- Built-in support for sessions.

- Updated URL dispatch features

- Better imperative extensibility

- ZCML externalized

- Better support for global template variables during rendering

- View mappers

- Testing system improvements

- Authentication support improvements

- Documentation improvements

New Name and Branding
~~~~~~~~~~~~~~~~~~~~~

The name of ``repoze.bfg`` has been changed to Pyramid.  The project
is now branded under a new entity, "The Pylons Project".  The Pylons Project
is the project name for a collection of web-framework-related technologies.
Pyramid was the first package in the Pylons Project. Other packages to the
collection have been added over time, such as support packages useful for
Pylons 1 users as well as ex-Zope users.  Pyramid is the successor to both
:mod:`repoze.bfg` and :term:`Pylons` version 1.

The Pyramid codebase is derived almost entirely from :mod:`repoze.bfg`
with some changes made for the sake of Pylons 1 compatibility.

Pyramid is technically backwards incompatible with :mod:`repoze.bfg`, as it
has a new package name, so older imports from the ``repoze.bfg`` module will
fail if you do nothing to your existing :mod:`repoze.bfg` application.
However, you won't have to do much to use your existing BFG applications on
Pyramid. There's automation which will change most of your import statements
and ZCML declarations. See
http://docs.pylonshq.com/pyramid/dev/tutorials/bfg/index.html for upgrade
instructions.

Pylons 1 users will need to do more work to use Pyramid, as Pyramid shares no
"DNA" with Pylons.  It is hoped that over time documentation and upgrade code
will be developed to help Pylons 1 users transition to Pyramid more easily.

:mod:`repoze.bfg` version 1.3 will be its last major release. Minor updates
will be made for critical bug fixes.  Pylons version 1 will continue to see
maintenance releases, as well.

The Repoze project will continue to exist. Repoze will be able to regain its
original focus: bringing Zope technologies to WSGI. The popularity of
:mod:`repoze.bfg` as its own web framework hindered this goal.

We hope that people are attracted at first by the spirit of cooperation
demonstrated by the Pylons Project and the merging of development
communities. It takes humility to sacrifice a little sovereignty and work
together. The opposite, forking or splintering of projects, is much more
common in the open source world. We feel there is a limited amount of oxygen
in the space of "top-tier" Python web frameworks and we don’t do the Python
community a service by over-crowding.  By merging the :mod:`repoze.bfg` and
the philosophically-similar Pylons communities, both gain an expanded
audience and a stronger chance of future success.

Paster Template Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Normalized all paster templates: each now uses the name ``main`` to
  represent the function that returns a WSGI application, each now uses
  WebError, each now has roughly the same shape of development.ini style.

- All preexisting paster templates now use "imperative" configuration
  (``starter``, ``routesalchemy``, ``alchemy``, ``zodb``).

- The ``pyramid_zodb``, ``pyramid_routesalchemy`` and ``pyramid_alchemy``
  paster templates now use a default "commit veto" hook when configuring the
  ``repoze.tm2`` transaction manager in ``development.ini``.  This prevents a
  transaction from being committed when the response status code is within
  the 400 or 500 ranges.  See also
  http://docs.repoze.org/tm2/#using-a-commit-veto.

- The paster templates now have much nicer CSS and graphics.

Terminology Changes
~~~~~~~~~~~~~~~~~~~

- The Pyramid concept previously known as "model" is now known as "resource".
  As a result:

  - The following API changes have been made::

      pyramid.url.model_url -> 
                        pyramid.url.resource_url

      pyramid.traversal.find_model -> 
                        pyramid.url.find_resource

      pyramid.traversal.model_path ->
                        pyramid.traversal.resource_path

      pyramid.traversal.model_path_tuple ->
                        pyramid.traversal.resource_path_tuple

      pyramid.traversal.ModelGraphTraverser -> 
                        pyramid.traversal.ResourceTreeTraverser

      pyramid.config.Configurator.testing_models ->
                        pyramid.config.Configurator.testing_resources

      pyramid.testing.registerModels ->
                        pyramid.testing.registerResources

      pyramid.testing.DummyModel ->
                        pyramid.testing.DummyResource

   - All documentation which previously referred to "model" now refers to
     "resource".

   - The ``starter`` and ``starter_zcml`` paster templates now have a
     ``resources.py`` module instead of a ``models.py`` module.

  - Positional argument names of various APIs have been changed from
    ``model`` to ``resource``.

  Backwards compatibility shims have been left in place in all cases.

- The Pyramid concept previously known as "resource" is now known as "asset".
  As a result:

  - The (non-API) module previously known as ``pyramid.resource`` is now
    known as ``pyramid.asset``.

  - All docs that previously referred to "resource specification" now refer
    to "asset specification".

  - The following API changes were made::

      pyramid.config.Configurator.absolute_resource_spec ->
                        pyramid.config.Configurator.absolute_asset_spec

      pyramid.config.Configurator.override_resource ->
                        pyramid.config.Configurator.override_asset

  - The ZCML directive previously known as ``resource`` is now known as
    ``asset``.

  - The setting previously known as ``BFG_RELOAD_RESOURCES`` (envvar) or
    ``reload_resources`` (config file) is now known, respectively, as
    ``PYRAMID_RELOAD_ASSETS`` and ``reload_assets``.

  Backwards compatibility shims have been left in place in all cases.

Better Platform Compatibility and Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Make test suite pass on Jython (requires PasteScript trunk, presumably to
  be 1.7.4).

- Make test suite pass on PyPy (Chameleon doesn't work).

Sessions
~~~~~~~~

- Using ``request.session`` now returns a (dictionary-like) session
  object if a session factory has been configured.

- New argument to configurator: ``session_factory``.

- New method on configurator: ``set_session_factory``

- New API methods in ``pyramid.session``: ``signed_serialize`` and
  ``signed_deserialize``.

- Added flash messaging, as described in the "Flash Messaging" narrative
  documentation chapter.

- Added CSRF token generation, as described in the narrative chapter entitled
  "Preventing Cross-Site Request Forgery Attacks".

Mako
~~~~

- Added Mako TemplateLookup settings for ``mako.error_handler``,
  ``mako.default_filters``, and ``mako.imports``.

- New boolean Mako settings variable ``mako.strict_undefined``.  See `Mako
  Context Variables
  <http://www.makotemplates.org/docs/runtime.html#context-variables>`_ for
  its meaning.

URL Dispatch
~~~~~~~~~~~~

- URL Dispatch now allows for replacement markers to be located anywhere
  in the pattern, instead of immediately following a ``/``.

- URL Dispatch now uses the form ``{marker}`` to denote a replace marker in
  the route pattern instead of ``:marker``. The old colon-style marker syntax
  is still accepted for backwards compatibility. The new format allows a
  regular expression for that marker location to be used instead of the
  default ``[^/]+``, for example ``{marker:\d+}`` is now valid to require the
  marker to be digits.

- Add a new API ``pyramid.url.current_route_url``, which computes a URL based
  on the "current" route (if any) and its matchdict values.

- Add ``paster proute`` command which displays a summary of the routing
  table.  See the narrative documentation section within the "URL Dispatch"
  chapter entitled "Displaying All Application Routes".

- Added ``debug_routematch`` configuration setting that logs matched routes
  (including the matchdict and predicates).

- Add a ``pyramid.url.route_path`` API, allowing folks to generate relative
  URLs.  Calling ``route_path`` is the same as calling
  ``pyramid.url.route_url`` with the argument ``_app_url`` equal to the empty
  string.

- Add a ``pyramid.request.Request.route_path`` API.  This is a convenience
  method of the request which calls ``pyramid.url.route_url``.

- Added class vars ``matchdict`` and ``matched_route`` to
  ``pyramid.request.Request``.  Each is set to ``None``.

ZCML Externalized
~~~~~~~~~~~~~~~~~

- The ``load_zcml`` method of a Configurator has been removed from the
  Pyramid core.  Loading ZCML is now a feature of the ``pyramid_zcml``
  package, which can be downloaded from PyPI.  Documentation for the package
  should be available via
  http://pylonsproject.org/projects/pyramid_zcml/dev/, which describes how
  to add a configuration statement to your ``main`` block to reobtain this
  method.  You will also need to add an ``install_requires`` dependency upon
  ``pyramid_zcml`` to your ``setup.py`` file.

- The ``bfg2pyramid`` script now converts ZCML include tags that have
  ``repoze.bfg.includes`` as a package attribute to the value
  ``pyramid_zcml``.  For example, ``<include package="repoze.bfg.includes">``
  will be converted to ``<include package="pyramid_zcml">``.

- The ``pyramid.includes`` subpackage has been removed.  ZCML files which use
  include the package ``pyramid.includes`` (e.g. ``<include
  package="pyramid.includes"/>``) now must include the ``pyramid_zcml``
  package instead (e.g. ``<include package="pyramid_zcml"/>``).

- The "Declarative Configuration" narrative chapter has been removed (it was
  moved to the ``pyramid_zcml`` package).

- Most references to ZCML in narrative chapters have been removed or
  redirected to ``pyramid_zcml`` locations.

- The ``starter_zcml`` paster template has been moved to the ``pyramid_zcml``
  package.

- The ``make_app`` function has been removed from the ``pyramid.router``
  module.  It continues life within the ``pyramid_zcml`` package.  This
  leaves the ``pyramid.router`` module without any API functions.

Imperative Two-Phase Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Imperative two-phase configuration with conflict detection.

- Add ``add_directive`` method to configurator, which allows framework
  extenders to add methods to the configurator (ala ZCML directives).

- When ``Configurator.include`` is passed a *module* as an argument, it
  defaults to attempting to find and use a callable named ``includeme``
  within that module.  This makes it possible to use
  ``config.include('some.module')`` rather than
  ``config.include('some.module.somefunc')`` as long as the include function
  within ``some.module`` is named ``includeme``.

- The new ``pyramid.config.Configurator` class has API methods that the older
  ``pyramid.configuration.Configurator`` class did not: ``with_context`` (a
  classmethod), ``include``, ``action``, and ``commit``.  These methods exist
  for imperative application extensibility purposes.

- Surrounding application configuration with ``config.begin()`` and
  ``config.end()`` is no longer necessary.  All paster templates have been
  changed to no longer call these functions.

Better Support for Global Template Variables During Rendering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- New event type: ``pyramid.interfaces.IBeforeRender``.  An object of this type
  is sent as an event before a renderer is invoked (but after the
  application-level renderer globals factory added via
  ``pyramid.configurator.configuration.set_renderer_globals_factory``, if any,
  has injected its own keys).  Applications may now subscribe to the
  ``IBeforeRender`` event type in order to introspect the and modify the set of
  renderer globals before they are passed to a renderer.  The event object
  iself has a dictionary-like interface that can be used for this purpose.  For
  example::

    from repoze.events import subscriber
    from pyramid.interfaces import IRendererGlobalsEvent

    @subscriber(IRendererGlobalsEvent)
    def add_global(event):
        event['mykey'] = 'foo'

  If a subscriber attempts to add a key that already exist in the renderer
  globals dictionary, a ``KeyError`` is raised.  This limitation is due to the
  fact that subscribers cannot be ordered relative to each other.  The set of
  keys added to the renderer globals dictionary by all subscribers and
  app-level globals factories must be unique.

View Mappers
~~~~~~~~~~~~

- New constructor argument to Configurator: ``default_view_mapper``.  Useful
  to create systems that have alternate view calling conventions.  A view
  mapper allows objects that are meant to be used as view callables to have
  an arbitrary argument list and an arbitrary result.  The object passed as
  ``default_view_mapper`` should implement the
  ``pyramid.interfaces.IViewMapperFactory`` interface.

- add a ``set_view_mapper`` API to Configurator.  Has
  the same result as passing ``default_view_mapper`` to the Configurator
  constructor.

- ``config.add_view`` now accepts a ``mapper`` keyword argument, which should
  either be ``None``, a string representing a Python dotted name, or an
  object which is an ``IViewMapperFactory``.  This feature is not useful for
  "civilians", only for extension writers.

Testing Support Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``pyramid.testing.setUp`` and ``pyramid.testing.tearDown`` have been
  undeprecated.  They are now the canonical setup and teardown APIs for test
  configuration, replacing "direct" creation of a Configurator.  This is a
  change designed to provide a facade that will protect against any future
  Configurator deprecations.

- Add ``charset`` attribute to ``pyramid.testing.DummyRequest``
  (unconditionally ``UTF-8``).

- Instances of ``pyramid.testing.DummyRequest`` now have a ``session``
  object, which is mostly a dictionary, but also implements the other session
  API methods for flash and CSRF.

- ``pyramid.testing.DummyRequest`` now has a class variable,
  ``query_string``, which defaults to the empty string.

- The ``pyramid.testing.setUp`` function now accepts an ``autocommit``
  keyword argument, which defaults to ``True``.  If it is passed ``False``,
  the Config object returned by ``setUp`` will be a non-autocommiting Config
  object.

Authentication Support Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The ``pyramid.interfaces.IAuthenticationPolicy`` interface now specifies an
  ``unauthenticated_userid`` method.  This method supports an important
  optimization required by people who are using persistent storages which do
  not support object caching and whom want to create a "user object" as a
  request attribute.

- A new API has been added to the ``pyramid.security`` module named
  ``unauthenticated_userid``.  This API function calls the
  ``unauthenticated_userid`` method of the effective security policy.

- An ``unauthenticated_userid`` method has been added to the dummy
  authentication policy returned by
  ``pyramid.config.Configurator.testing_securitypolicy``.  It returns the
  same thing as that the dummy authentication policy's
  ``authenticated_userid`` method.

- The class ``pyramid.authentication.AuthTktCookieHelper`` is now an API.
  This class can be used by third-party authentication policy developers to
  help in the mechanics of authentication cookie-setting.

- The AuthTktAuthenticationPolicy now accepts a ``tokens`` parameter via
  ``pyramid.security.remember``.  The value must be a sequence of strings.
  Tokens are placed into the auth_tkt "tokens" field and returned in the
  auth_tkt cookie.

Documentation Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Casey Duncan, a good friend, and an excellent technical writer has given us
  the gift of professionally editing the entire Pyramid documentation set.
  Any faults in the documentation are the development team's, and all
  improvements are his.

- The "Resource Location and View Lookup" chapter has been replaced with a
  variant of Rob Miller's "Much Ado About Traversal" (originally published at
  http://blog.nonsequitarian.org/2010/much-ado-about-traversal/).

- Many users have contributed documentation fixes and improvements including
  Ben Bangert, Blaise Laflamme, Rob Miller, Mike Orr, Carlos de la Guardia,
  Paul Everitt, Tres Seaver, John Shipman, Marius Gedminas, Chris Rossi,
  Joachim Krebs, Xavier Spriet, Reed O'Brien, William Chambers, Charlie
  Choiniere, and Jamaludin Ahmad.

Minor Feature Additions
-----------------------

- The ``settings`` object which used to be available only when
  ``request.settings.get_settings`` was called is now available as
  ``registry.settings`` (e.g. ``request.registry.settings`` in view code).

- ``config.add_view`` now accepts a ``decorator`` keyword argument, a callable
  which will decorate the view callable before it is added to the registry.

- Allow static renderer provided during view registration to be overridden at
  request time via a request attribute named ``override_renderer``, which
  should be the name of a previously registered renderer.  Useful to provide
  "omnipresent" RPC using existing rendered views.

- If a resource implements a ``__resource_url__`` method, it will be called
  as the result of invoking the ``pyramid.url.resource_url`` function to
  generate a URL, overriding the default logic.  See the new "Generating The
  URL Of A Resource" section within the Resources narrative chapter.

- The name ``registry`` is now available in a ``pshell`` environment by
  default.  It is the application registry object.

- Add support for json on GAE by catching ``NotImplementedError`` and
  importing simplejson from django.utils.

- Add ``pyramid.httpexceptions`` module, which is a facade for the
  ``webob.exc`` module.

- New class: ``pyramid.response.Response``.  This is a pure facade for
  ``webob.Response`` (old code need not change to use this facade, it's
  existence is mostly for vanity and documentation-generation purposes).

- The request now has a new attribute: ``tmpl_context`` for benefit of
  Pylons users.

- New interface: ``pyramid.interfaces.IRendererInfo``.  An object of this type
  is passed to renderer factory constructors (see "Backwards
  Incompatibilities").

- New API method: ``pyramid.settings.asbool``.

- New API methods for ``pyramid.request.Request``: ``model_url``,
  ``route_url``, and ``static_url``.  These are simple passthroughs for their
  respective functions in ``pyramid.url``.

Backwards Incompatibilities
---------------------------

- When a ``pyramid.exceptions.Forbidden`` error is raised, its status code
  now ``403 Forbidden``.  It was previously ``401 Unauthorized``, for
  backwards compatibility purposes with ``repoze.bfg``.  This change will
  cause problems for users of Pyramid with ``repoze.who``, which intercepts
  ``401 Unauthorized`` by default, but allows ``403 Forbidden`` to pass
  through.  Those deployments will need to configure ``repoze.who`` to also
  react to ``403 Forbidden``.

- ``paster bfgshell`` is now known as ``paster pshell``.

- There is no longer an ``IDebugLogger`` registered as a named utility
  with the name ``repoze.bfg.debug``.

- The logger which used to have the name of ``repoze.bfg.debug`` now
  has the name ``pyramid.debug``.

- The deprecated API ``pyramid.testing.registerViewPermission``
  has been removed.

- The deprecated API named ``pyramid.testing.registerRoutesMapper``
  has been removed.

- The deprecated API named ``pyramid.request.get_request`` was removed.

- The deprecated API named ``pyramid.security.Unauthorized`` was
  removed.

- The deprecated API named ``pyramid.view.view_execution_permitted``
  was removed.

- The deprecated API named ``pyramid.view.NotFound`` was removed.

- The ``bfgshell`` paster command is now named ``pshell``.

- The Venusian "category" for all built-in Venusian decorators
  (e.g. ``subscriber`` and ``view_config``/``bfg_view``) is now
  ``pyramid`` instead of ``bfg``.

- ``pyramid.renderers.rendered_response`` function removed; use
  ``render_pyramid.renderers.render_to_response`` instead.

- Renderer factories now accept a *renderer info object* rather than an
  absolute resource specification or an absolute path.  The object has the
  following attributes: ``name`` (the ``renderer=`` value), ``package`` (the
  'current package' when the renderer configuration statement was found),
  ``type``: the renderer type, ``registry``: the current registry, and
  ``settings``: the deployment settings dictionary.

  Third-party ``repoze.bfg`` renderer implementations that must be ported to
  Pyramid will need to account for this.

  This change was made primarily to support more flexible Mako template
  rendering.

- The presence of the key ``repoze.bfg.message`` in the WSGI environment when
  an exception occurs is now deprecated.  Instead, code which relies on this
  environ value should use the ``exception`` attribute of the request
  (e.g. ``request.exception[0]``) to retrieve the message.

- The values ``bfg_localizer`` and ``bfg_locale_name`` kept on the request
  during internationalization for caching purposes were never APIs.  These
  however have changed to ``localizer`` and ``locale_name``, respectively.

- The default ``cookie_name`` value of the ``authtktauthenticationpolicy`` ZCML
  now defaults to ``auth_tkt`` (it used to default to ``repoze.bfg.auth_tkt``).

- The default ``cookie_name`` value of the
  ``pyramid.authentication.AuthTktAuthenticationPolicy`` constructor now
  defaults to ``auth_tkt`` (it used to default to ``repoze.bfg.auth_tkt``).

- The ``request_type`` argument to the ``view`` ZCML directive, the
  ``pyramid.configuration.Configurator.add_view`` method, or the
  ``pyramid.view.view_config`` decorator (nee ``bfg_view``) is no longer
  permitted to be one of the strings ``GET``, ``HEAD``, ``PUT``, ``POST`` or
  ``DELETE``, and now must always be an interface.  Accepting the
  method-strings as ``request_type`` was a backwards compatibility strategy
  servicing repoze.bfg 1.0 applications.  Use the ``request_method``
  parameter instead to specify that a view a string request-method predicate.

- The ``pyramid.testing.zcml_configure`` API has been removed.  It had been
  advertised as removed since repoze.bfg 1.2a1, but hadn't actually been.

- All environment variables which used to be prefixed with ``BFG_`` are now
  prefixed with ``PYRAMID_`` (e.g. ``BFG_DEBUG_NOTFOUND`` is now
  ``PYRAMID_DEBUG_NOTFOUND``)

- Since the ``pyramid.interfaces.IAuthenticationPolicy`` interface now
  specifies that a policy implementation must implement an
  ``unauthenticated_userid`` method, all third-party custom authentication
  policies now must implement this method.  It, however, will only be called
  when the global function named ``pyramid.security.unauthenticated_userid``
  is invoked, so if you're not invoking that, you will not notice any issues.

- The ``configure_zcml`` setting within the deployment settings (within
  ``**settings`` passed to a Pyramid ``main`` function) has ceased to have any
  meaning.

Deprecations and Behavior Differences
-------------------------------------

- The ``pyramid.settings.get_settings`` API is now deprecated.  Use
  ``pyramid.threadlocals.get_current_registry().settings`` instead or use the
  ``settings`` attribute of the registry available from the request
  (``request.registry.settings``).

- The decorator previously known as ``pyramid.view.bfg_view`` is now
  known most formally as ``pyramid.view.view_config`` in docs and
  paster templates.

- Obtaining the ``settings`` object via
  ``registry.{get|query}Utility(ISettings)`` is now deprecated.  Instead,
  obtain the ``settings`` object via the ``registry.settings`` attribute.  A
  backwards compatibility shim was added to the registry object to register
  the settings object as an ISettings utility when ``setattr(registry,
  'settings', foo)`` is called, but it will be removed in a later release.

- Obtaining the ``settings`` object via ``pyramid.settings.get_settings`` is
  now deprecated.  Obtain it as the ``settings`` attribute of the registry
  now (obtain the registry via ``pyramid.threadlocal.get_registry`` or as
  ``request.registry``).

- ``pyramid.configuration.Configurator`` is now deprecated.  Use
  ``pyramid.config.Configurator``, passing its constructor
  ``autocommit=True`` instead.  The ``pyramid.configuration.Configurator``
  alias will live for a long time, as every application uses it, but its
  import now issues a deprecation warning.  The
  ``pyramid.config.Configurator`` class has the same API as
  ``pyramid.configuration.Configurator`` class, which it means to replace,
  except by default it is a *non-autocommitting* configurator. The
  now-deprecated ``pyramid.configuration.Configurator`` will autocommit every
  time a configuration method is called.  The ``pyramid.configuration``
  module remains, but it is deprecated.  Use ``pyramid.config`` instead.

Dependency Changes
------------------

- Depend on Venusian >= 0.5 (for scanning conflict exception decoration).

Documentation Enhancements
--------------------------

- Added a ``pyramid.httpexceptions`` API documentation chapter.

- Added a ``pyramid.session`` API documentation chapter.

- Added a ``Session Objects`` narrative documentation chapter.

- Added an API chapter for the ``pyramid.personality`` module.

- Added an API chapter for the ``pyramid.response`` module.

- All documentation which previously referred to ``webob.Response`` now uses
  ``pyramid.response.Response`` instead.

- The documentation has been overhauled to use imperative configuration,
  moving declarative configuration (ZCML) explanations to a separate
  narrative chapter ``declarative.rst``.

- The ZODB Wiki tutorial was updated to take into account changes to the
  ``pyramid_zodb`` paster template.

- The SQL Wiki tutorial was updated to take into account changes to the
  ``pyramid_routesalchemy`` paster template.

- Removed ``zodbsessions`` tutorial chapter.  It's still useful, but we now
  have a SessionFactory abstraction which competes with it, and maintaining
  documentation on both ways to do it is a distraction.

- Merged many wording, readability, and correctness changes to narrative
  documentation chapters from https://github.com/caseman/pyramid (up to and
  including "Models" narrative chapter).

- "Sample Applications" section of docs changed to note existence of Cluegun,
  Shootout and Virginia sample applications, ported from their repoze.bfg
  origin packages.

- Add ``pyramid.interfaces.ITemplateRenderer`` interface to Interfaces API
  chapter (has ``implementation()`` method, required to be used when getting
  at Chameleon macros).

- Add a "Modifying Package Structure" section to the project narrative
  documentation chapter (explain turning a module into a package).

- Added "Debugging Route Matching" section to the urldispatch narrative
  documentation chapter.

- Added reference to ``PYRAMID_DEBUG_ROUTEMATCH`` envvar and
  ``debug_routematch`` config file setting to the Environment narrative docs
  chapter.

- Direct Jython users to Mako rather than Jinja2 in "Install" narrative
  chapter.

- Added an example of ``WebTest`` functional testing to the testing narrative
  chapter.

- Rearranged chapter ordering by popular demand (URL dispatch first, then
  traversal).  Put hybrid chapter after views chapter.

- Split off "Renderers" as its own chapter from "Views" chapter in narrative
  documentation.

- Added "Generating The URL Of A Resource" section to the Resources narrative
  chapter (includes information about overriding URL generation using
  ``__resource_url__``).

- Added "Generating the Path To a Resource" section to the Resources
  narrative chapter.

- Added "Finding a Resource by Path" section to the Resources narrative
  chapter.

- Added "Obtaining the Lineage of a Resource" to the Resources narrative
  chapter.

- Added "Determining if a Resource is In The Lineage of Another Resource" to
  Resources narrative chapter.

- Added "Finding the Root Resource" to Resources narrative chapter.

- Added "Finding a Resource With a Class or Interface in Lineage" to
  Resources narrative chapter.

- Added a "Flash Messaging" narrative documentation chapter.

- Added a narrative chapter entitled "Preventing Cross-Site Request Forgery
  Attacks".

- Changed the "ZODB + Traversal Wiki Tutorial" based on changes to
  ``pyramid_zodb`` Paster template.

- Added "Advanced Configuration" narrative chapter which documents how to
  deal with configuration conflicts, two-phase configuration, ``include`` and
  ``commit``.

- Add "Pyramid Provides More Than One Way to Do It" to Design Defense
  documentation.

- Added narrative documentation section within the "URL Dispatch" chapter
  entitled "Displaying All Application Routes" (for ``paster proutes``
  command).

- The (weak) "Converting a CMF Application to Pyramid" tutorial has been
  removed from the tutorials section.  It was moved to the
  ``pyramid_tutorials`` Github repository.

- Split views chapter into 2: View Callables and View Configuration.

- Reorder Renderers and Templates chapters after View Callables but before
  View Configuration.

