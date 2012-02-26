What's New In Pyramid 1.3
=========================

This article explains the new features in :app:`Pyramid` version 1.3 as
compared to its predecessor, :app:`Pyramid` 1.2.  It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 1.3, as well as software dependency changes and notable
documentation additions.

Major Feature Additions
-----------------------

The major feature additions in Pyramid 1.3 follow.

Python 3 Compatibility
~~~~~~~~~~~~~~~~~~~~~~

In addition to running on Python 2 (version 2.6 or 2.7 required), Pyramid is
now Python 3 compatible.  For Python 3 compatibility, Python 3.2 or better
is required.

.. warning::

   As of this writing (the release of Pyramid 1.3a1), if you attempt to
   install a Pyramid project that used ``alchemy`` scaffold via ``setup.py
   develop`` on Python 3.2, it may quit with an installation error while
   trying to install ``Pygments``.  If this happens, please rerun the
   ``setup.py develop`` command again and it will complete.  We're just as
   clueless as you are as to why this happens at this point, but hopefully
   we'll figure it out before Pyramid 1.3 leaves the alpha/beta phase.

This feature required us to make some compromises.

Pyramid no longer runs on Python 2.5.  This includes the most recent release
of Jython and the Python 2.5 version of Google App Engine.  We could not
easily "straddle" Python 2 and 3 versions and support Python 2 versions older
than Python 2.6.  You will need Python 2.6 or better to run this version of
Pyramid.  If you need to use Python 2.5, you should use the most recent 1.2.X
release of Pyramid.

Though many Pyramid add-ons have releases which are already Python 3
compatible (in particular ``pyramid_debugtoolbar``, ``pyramid_jinja2``,
``pyramid_exclog``, and ``pyramid_tm``), some are still known to work only
under Python 2.  Likewise, some scaffolding dependencies (particularly ZODB)
do not yet work under Python
3.  Please be patient as we gain full ecosystem support for Python 3.  You
can see more details about ongoing porting efforts at
https://github.com/Pylons/pyramid/wiki/Python-3-Porting .

The libraries named ``Paste`` and ``PasteScript`` which have been
dependencies of Pyramid since 1.0+ have not been ported to Python 3, and we
were unwilling to port and maintain them ourselves.  As a result, we've had
to make some changes:

- We've replaced the ``paster`` command with Pyramid-specific analogues.

- We've made the default WSGI server used by Pyramid scaffolding the
  :term:`waitress` server.

Previously (in Pyramid 1.0, 1.1 and 1.2), you created a Pyramid application
using ``paster create``, like so::

    $ myvenv/bin/paster create -t pyramid_starter foo

You're now instead required to create an application using ``pcreate`` like
so::

    $ myvenv/bin/pcreate -s starter foo

Note that the names of available scaffolds have changed and the flags
supported by ``pcreate`` are different than those that were supported by
``paster create``.

Instead of running a Pyramid project created via a scaffold using ``paster
serve``, as was done in Pyramid <= 1.2.X, you now must use the ``pserve``
command::

    $myvenv/bin/pserve development.ini

The ``ini`` configuration file format supported by Pyramid has not changed.
As a result, Python 2-only users can install PasteScript manually and use
``paster serve`` instead if they like.  However, using ``pserve`` will work
under both Python 2 and Python 3.  ``pcreate`` is required to be used for
internal Pyramid scaffolding; externally distributed scaffolding may allow
for both ``pcreate`` and/or ``paster create``.

Analogues of ``paster pshell``, ``paster pviews``, ``paster request`` and
``paster ptweens`` also exist under the respective console script names
``pshell``, ``pviews``, ``prequest`` and ``ptweens``.

We've replaced use of the Paste ``httpserver`` with the ``waitress`` server in
the scaffolds, so once you create a project from a scaffold, its
``development.ini`` and ``production.ini`` will have the following line::

    use = egg:waitress#main

Instead of this (which was the default in older versions)::

    use = egg:Paste#http

.. warning::

   Previously, paste.httpserver "helped" by converting header values that
   weren't strings to strings. The ``waitress`` server, on the other hand
   implements the spec more fully. This specifically may affect you if you
   are modifying headers on your response. The following error might be an
   indicator of this problem: **AssertionError: Header values must be
   strings, please check the type of the header being returned.** A common
   case would be returning unicode headers instead of string headers.

A new :mod:`pyramid.compat` module was added which provides Python 2/3
straddling support for Pyramid add-ons and development environments.

Python 3 compatibility required dropping some package dependencies and
support for older Python versions and platforms.  See the "Backwards
Incompatibilities" section below for more information.

Introspection
~~~~~~~~~~~~~

A configuration introspection system was added; see
:ref:`using_introspection` and :ref:`introspection` for more information on
using the introspection system as a developer.

The latest release of the pyramid debug toolbar (0.9.7+) provides an
"Introspection" panel that exposes introspection information to a Pyramid
application developer.

New APIs were added to support introspection
:attr:`pyramid.registry.Introspectable`,
:attr:`pyramid.config.Configurator.introspector`,
:attr:`pyramid.config.Configurator.introspectable`,
:attr:`pyramid.registry.Registry.introspector`.

``@view_defaults`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you use a class as a view, you can use the new
:class:`pyramid.view.view_defaults` class decorator on the class to provide
defaults to the view configuration information used by every ``@view_config``
decorator that decorates a method of that class.

For instance, if you've got a class that has methods that represent "REST
actions", all which are mapped to the same route, but different request
methods, instead of this:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   class RESTView(object):
       def __init__(self, request):
           self.request = request

       @view_config(route_name='rest', request_method='GET')
       def get(self):
           return Response('get')

       @view_config(route_name='rest', request_method='POST')
       def post(self):
           return Response('post')

       @view_config(route_name='rest', request_method='DELETE')
       def delete(self):
           return Response('delete')

You can do this:

.. code-block:: python
   :linenos:

   from pyramid.view import view_defaults
   from pyramid.view import view_config
   from pyramid.response import Response

   @view_defaults(route_name='rest')
   class RESTView(object):
       def __init__(self, request):
           self.request = request

       @view_config(request_method='GET')
       def get(self):
           return Response('get')

       @view_config(request_method='POST')
       def post(self):
           return Response('post')

       @view_config(request_method='DELETE')
       def delete(self):
           return Response('delete')

This also works for imperative view configurations that involve a class.

See :ref:`view_defaults` for more information.

Extending a Request without Subclassing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is now possible to extend a :class:`pyramid.request.Request` object
with property descriptors without having to create a custom request factory.
The new method :meth:`pyramid.config.Configurator.set_request_property`
provides an entry point for addons to register properties which will be
added to each request. New properties may be reified, effectively caching
the return value for the lifetime of the instance. Common use-cases for this
would be to get a database connection for the request or identify the current
user. The new method :meth:`pyramid.request.Request.set_property` has been
added, as well, but the configurator method should be preferred as it
provides conflict detection and consistency in the lifetime of the
properties.

Not Found and Forbidden View Helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not Found helpers:

- New API: :meth:`pyramid.config.Configurator.add_notfound_view`.  This is a
  wrapper for :meth:`pyramid.Config.configurator.add_view` which provides
  support for an "append_slash" feature as well as doing the right thing when
  it comes to permissions (a not found view should always be public).  It
  should be preferred over calling ``add_view`` directly with
  ``context=HTTPNotFound`` as was previously recommended.

- New API: :class:`pyramid.view.notfound_view_config``.  This is a decorator
  constructor like :class:`pyramid.view.view_config` that calls
  :meth:`pyramid.config.Configurator.add_notfound_view` when scanned.  It
  should be preferred over using ``pyramid.view.view_config`` with
  ``context=HTTPNotFound`` as was previously recommended.

Forbidden helpers:

- New API: :meth:`pyramid.config.Configurator.add_forbidden_view`.  This is a
  wrapper for :meth:`pyramid.Config.configurator.add_view` which does the
  right thing about permissions.  It should be preferred over calling
  ``add_view`` directly with ``context=HTTPForbidden`` as was previously
  recommended.

- New API: :class:`pyramid.view.forbidden_view_config`.  This is a decorator
  constructor like :class:`pyramid.view.view_config` that calls
  :meth:`pyramid.config.Configurator.add_forbidden_view` when scanned.  It
  should be preferred over using ``pyramid.view.view_config`` with
  ``context=HTTPForbidden`` as was previously recommended.

Minor Feature Additions
-----------------------

- New APIs: :class:`pyramid.path.AssetResolver` and
  :class:`pyramid.path.DottedNameResolver`.  The former can be used to
  resolve an :term:`asset specification` to an API that can be used to read
  the asset's data, the latter can be used to resolve a :term:`dotted Python
  name` to a module or a package.

- A ``mako.directories`` setting is no longer required to use Mako templates
  Rationale: Mako template renderers can be specified using an absolute asset
  spec.  An entire application can be written with such asset specs,
  requiring no ordered lookup path.

- ``bpython`` interpreter compatibility in ``pshell``.  See
  :ref:`ipython_or_bpython` for more information.

- Added :func:`pyramid.paster.get_appsettings` API function.  This function
  returns the settings defined within an ``[app:...]`` section in a
  PasteDeploy ``ini`` file.

- Added :func:`pyramid.paster.setup_logging` API function.  This function
  sets up Python logging according to the logging configuration in a
  PasteDeploy ``ini`` file.

- Configuration conflict reporting is reported in a more understandable way
  ("Line 11 in file..." vs. a repr of a tuple of similar info).

- We allow extra keyword arguments to be passed to the
  :meth:`pyramid.config.Configurator.action` method.

- Responses generated by Pyramid's :class:`pyramid.views.static_view` now use
  a ``wsgi.file_wrapper`` (see
  http://www.python.org/dev/peps/pep-0333/#optional-platform-specific-file-handling)
  when one is provided by the web server.

- The :meth:`pyramid.config.Configurator.scan` method can be passed an
  ``ignore`` argument, which can be a string, a callable, or a list
  consisting of strings and/or callables.  This feature allows submodules,
  subpackages, and global objects from being scanned.  See
  http://readthedocs.org/docs/venusian/en/latest/#ignore-scan-argument for
  more information about how to use the ``ignore`` argument to ``scan``.

- Add :meth:`pyramid.config.Configurator.add_traverser` API method.  See
  :ref:`changing_the_traverser` for more information.  This is not a new
  feature, it just provides an API for adding a traverser without needing to
  use the ZCA API.

- Add :meth:`pyramid.config.Configurator.add_resource_url_adapter` API
  method.  See :ref:`changing_resource_url` for more information.  This is
  not a new feature, it just provides an API for adding a resource url
  adapter without needing to use the ZCA API.

- The :meth:`pyramid.config.Configurator.scan` method can now be passed an
  ``ignore`` argument, which can be a string, a callable, or a list
  consisting of strings and/or callables.  This feature allows submodules,
  subpackages, and global objects from being scanned.  See
  http://readthedocs.org/docs/venusian/en/latest/#ignore-scan-argument for
  more information about how to use the ``ignore`` argument to ``scan``.

- Better error messages when a view callable returns a value that cannot be
  converted to a response (for example, when a view callable returns a
  dictionary without a renderer defined, or doesn't return any value at all).
  The error message now contains information about the view callable itself
  as well as the result of calling it.

- Better error message when a .pyc-only module is ``config.include`` -ed.
  This is not permitted due to error reporting requirements, and a better
  error message is shown when it is attempted.  Previously it would fail with
  something like "AttributeError: 'NoneType' object has no attribute
  'rfind'".

- The system value ``req`` is now supplied to renderers as an alias for
  ``request``.  This means that you can now, for example, in a template, do
  ``req.route_url(...)`` instead of ``request.route_url(...)``.  This is
  purely a change to reduce the amount of typing required to use request
  methods and attributes from within templates.  The value ``request`` is
  still available too, this is just an alternative.

- A new interface was added: :class:`pyramid.interfaces.IResourceURL`.  An
  adapter implementing its interface can be used to override resource URL
  generation when :meth:`pyramid.request.Request.resource_url` is called.
  This interface replaces the now-deprecated
  ``pyramid.interfaces.IContextURL`` interface.

- The dictionary passed to a resource's ``__resource_url__`` method (see
  :ref:`overriding_resource_url_generation`) now contains an ``app_url`` key,
  representing the application URL generated during
  :meth:`pyramid.request.Request.resource_url`.  It represents a potentially
  customized URL prefix, containing potentially custom scheme, host and port
  information passed by the user to ``request.resource_url``.  It should be
  used instead of ``request.application_url`` where necessary.

- The :meth:`pyramid.request.Request.resource_url` API now accepts these
  arguments: ``app_url``, ``scheme``, ``host``, and ``port``.  The app_url
  argument can be used to replace the URL prefix wholesale during url
  generation.  The ``scheme``, ``host``, and ``port`` arguments can be used
  to replace the respective default values of ``request.application_url``
  partially.

- A new API named :meth:`pyramid.request.Request.resource_path` now exists.
  It works like :meth:`pyramid.request.Request.resource_url` but produces a
  relative URL rather than an absolute one.

- The :meth:`pyramid.request.Request.route_url` API now accepts these
  arguments: ``_app_url``, ``_scheme``, ``_host``, and ``_port``.  The
  ``_app_url`` argument can be used to replace the URL prefix wholesale
  during url generation.  The ``_scheme``, ``_host``, and ``_port`` arguments
  can be used to replace the respective default values of
  ``request.application_url`` partially.

- New APIs: :class:`pyramid.response.FileResponse` and
  :class:`pyramid.response.FileIter`, for usage in views that must serve
  files "manually".

Backwards Incompatibilities
---------------------------

- Pyramid no longer runs on Python 2.5 (which includes the most recent
  release of Jython and the Python 2.5 version of GAE as of this writing).

- The ``paster`` command is no longer the documented way to create projects,
  start the server, or run debugging commands.  To create projects from
  scaffolds, ``paster create`` is replaced by the ``pcreate`` console script.
  To serve up a project, ``paster serve`` is replaced by the ``pserve``
  console script.  New console scripts named ``pshell``, ``pviews``,
  ``proutes``, and ``ptweens`` do what their ``paster <commandname>``
  equivalents used to do.  All relevant narrative documentation has been
  updated.  Rationale: the Paste and PasteScript packages do not run under
  Python 3.

- The default WSGI server run as the result of ``pserve`` from newly rendered
  scaffolding is now the ``waitress`` WSGI server instead of the
  ``paste.httpserver`` server.  Rationale: the Paste and PasteScript packages
  do not run under Python 3.

- The ``pshell`` command (see "paster pshell") no longer accepts a
  ``--disable-ipython`` command-line argument.  Instead, it accepts a ``-p``
  or ``--python-shell`` argument, which can be any of the values ``python``,
  ``ipython`` or ``bpython``.

- Removed the ``pyramid.renderers.renderer_from_name`` function.  It has been
  deprecated since Pyramid 1.0, and was never an API.

- To use ZCML with versions of Pyramid >= 1.3, you will need ``pyramid_zcml``
  version >= 0.8 and ``zope.configuration`` version >= 3.8.0.  The
  ``pyramid_zcml`` package version 0.8 is backwards compatible all the way to
  Pyramid 1.0, so you won't be warned if you have older versions installed
  and upgrade Pyramid itself "in-place"; it may simply break instead
  (particularly if you use ZCML's ``includeOverrides`` directive).

- String values passed to :meth:`Pyramid.request.Request.route_url` or
  :meth:`Pyramid.request.Request.route_path` that are meant to replace
  "remainder" matches will now be URL-quoted except for embedded slashes. For
  example::

     config.add_route('remain', '/foo*remainder')
     request.route_path('remain', remainder='abc / def')
     # -> '/foo/abc%20/%20def'

  Previously string values passed as remainder replacements were tacked on
  untouched, without any URL-quoting.  But this doesn't really work logically
  if the value passed is Unicode (raw unicode cannot be placed in a URL or in
  a path) and it is inconsistent with the rest of the URL generation
  machinery if the value is a string (it won't be quoted unless by the
  caller).

  Some folks will have been relying on the older behavior to tack on query
  string elements and anchor portions of the URL; sorry, you'll need to
  change your code to use the ``_query`` and/or ``_anchor`` arguments to
  ``route_path`` or ``route_url`` to do this now.

- If you pass a bytestring that contains non-ASCII characters to
  :meth:`pyramid.config.Configurator.add_route` as a pattern, it will now
  fail at startup time.  Use Unicode instead.

- The ``path_info`` route and view predicates now match against
  ``request.upath_info`` (Unicode) rather than ``request.path_info``
  (indeterminate value based on Python 3 vs. Python 2).  This has to be done
  to normalize matching on Python 2 and Python 3.

- The ``match_param`` view predicate no longer accepts a dict. This will have
  no negative affect because the implementation was broken for dict-based
  arguments.

- The ``pyramid.interfaces.IContextURL`` interface has been deprecated.
  People have been instructed to use this to register a resource url adapter
  in the "Hooks" chapter to use to influence
  :meth:`pyramid.request.Request.resource_url` URL generation for resources
  found via custom traversers since Pyramid 1.0.

  The interface still exists and registering an adapter using it as
  documented in older versions still works, but this interface will be
  removed from the software after a few major Pyramid releases.  You should
  replace it with an equivalent :class:`pyramid.interfaces.IResourceURL`
  adapter, registered using the new
  :meth:`pyramid.config.Configurator.add_resource_url_adapter` API.  A
  deprecation warning is now emitted when a
  ``pyramid.interfaces.IContextURL`` adapter is found when
  :meth:`pyramid.request.Request.resource_url` is called.

- Remove ``pyramid.config.Configurator.with_context`` class method.  It was
  never an API, it is only used by ``pyramid_zcml`` and its functionality has
  been moved to that package's latest release.  This means that you'll need
  to use the 0.9.2 or later release of ``pyramid_zcml`` with this release of
  Pyramid.

- The older deprecated ``set_notfound_view`` Configurator method is now an
  alias for the new ``add_notfound_view`` Configurator method.  Likewise, the
  older deprecated ``set_forbidden_view`` is now an alias for the new
  ``add_forbidden_view`` Configurator method. This has the following impact:
  the ``context`` sent to views with a ``(context, request)`` call signature
  registered via the ``set_notfound_view`` or ``set_forbidden_view`` will now
  be an exception object instead of the actual resource context found.  Use
  ``request.context`` to get the actual resource context.  It's also
  recommended to disuse ``set_notfound_view`` in favor of
  ``add_notfound_view``, and disuse ``set_forbidden_view`` in favor of
  ``add_forbidden_view`` despite the aliasing.

Deprecations
------------

- The API documentation for ``pyramid.view.append_slash_notfound_view`` and
  ``pyramid.view.AppendSlashNotFoundViewFactory`` was removed.  These names
  still exist and are still importable, but they are no longer APIs.  Use
  ``pyramid.config.Configurator.add_notfound_view(append_slash=True)`` or
  ``pyramid.view.notfound_view_config(append_slash=True)`` to get the same
  behavior.

- The ``set_forbidden_view`` and ``set_notfound_view`` methods of the
  Configurator were removed from the documentation.  They have been
  deprecated since Pyramid 1.1.

- All references to the ``tmpl_context`` request variable were removed from
  the docs.  Its existence in Pyramid is confusing for people who were never
  Pylons users.  It was added as a porting convenience for Pylons users in
  Pyramid 1.0, but it never caught on because the Pyramid rendering system is
  a lot different than Pylons' was, and alternate ways exist to do what it
  was designed to offer in Pylons.  It will continue to exist "forever" but
  it will not be recommended or mentioned in the docs.

Documentation Enhancements
--------------------------

- The :ref:`bfg_sql_wiki_tutorial` has been updated.  It now uses
  ``@view_config`` decorators and an explicit database population script.

- Minor updates to the :ref:`bfg_wiki_tutorial`.

- A narrative documentation chapter named :ref:`extconfig_narr` was added; it
  describes how to add a custom :term:`configuration directive`, and how use
  the :meth:`pyramid.config.Configurator.action` method within custom
  directives.  It also describes how to add :term:`introspectable` objects.

- A narrative documentation chapter named :ref:`using_introspection` was
  added.  It describes how to query the introspection system.

- Added an API docs chapter for :mod:`pyramid.scaffolds`.

- Added a narrative docs chapter named :ref:`scaffolding_chapter`.

- Added a description of the ``prequest`` command-line script at
  :ref:`invoking_a_request`.

- Added a section to the "Command-Line Pyramid" chapter named
  :ref:`making_a_console_script`.

- Removed the "Running Pyramid on Google App Engine" tutorial from the main
  docs.  It survives on in the Cookbook
  (http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/gae.html).
  Rationale: it provides the correct info for the Python 2.5 version of GAE
  only, and this version of Pyramid does not support Python 2.5.

- Updated the :ref:`changing_the_forbidden_view` section, replacing
  explanations of registering a view using ``add_view`` or ``view_config``
  with ones using ``add_forbidden_view`` or ``forbidden_view_config``.

- Updated the :ref:`changing_the_notfound_view` section, replacing
  explanations of registering a view using ``add_view`` or ``view_config``
  with ones using ``add_notfound_view`` or ``notfound_view_config``.

- Updated the :ref:`redirecting_to_slash_appended_routes` section, replacing
  explanations of registering a view using ``add_view`` or ``view_config``
  with ones using ``add_notfound_view`` or ``notfound_view_config``

- Updated all tutorials to use ``pyramid.view.forbidden_view_config`` rather
  than ``pyramid.view.view_config`` with an HTTPForbidden context.

Dependency Changes
------------------

- Pyramid no longer depends on the ``zope.component`` package, except as a
  testing dependency.

- Pyramid now depends on the following package versions:
  zope.interface>=3.8.0, WebOb>=1.2dev, repoze.lru>=0.4,
  zope.deprecation>=3.5.0, translationstring>=0.4 for Python 3 compatibility
  purposes.  It also, as a testing dependency, depends on WebTest>=1.3.1 for
  the same reason.

- Pyramid no longer depends on the ``Paste`` or ``PasteScript`` packages.
  These packages are not Python 3 compatible.

- Depend on ``venusian`` >= 1.0a3 to provide scan ``ignore`` support.

Scaffolding Changes
-------------------

- Rendered scaffolds have now been changed to be more relocatable (fewer
  mentions of the package name within files in the package).

- The ``routesalchemy`` scaffold has been renamed ``alchemy``, replacing the
  older (traversal-based) ``alchemy`` scaffold (which has been retired).

- The ``alchemy`` and ``starter`` scaffolds are Python 3 compatible.

- The ``starter`` scaffold now uses URL dispatch by default.
