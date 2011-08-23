What's New In Pyramid 1.2
=========================

This article explains the new features in :app:`Pyramid` version 1.2 as
compared to its predecessor, :app:`Pyramid` 1.1.  It also documents backwards
incompatibilities between the two versions and deprecations added to Pyramid
1.2, as well as software dependency changes and notable documentation
additions.

Major Feature Additions
-----------------------

The major feature additions in Pyramid 1.2 follow.

``route_prefix`` Argument to include
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`pyramid.config.Configurator.include` method now accepts a
``route_prefix`` argument.  This argument allows you to compose URL dispatch
applications together from disparate packages.  See :ref:`route_prefix` for
more information.

Tweens
~~~~~~

A :term:`tween` is used to wrap the Pyramid router's primary request handling
function.  This is a feature that can be used by Pyramid framework
extensions, to provide, for example, view timing support and can provide a
convenient place to hang bookkeeping code.  Tweens are is a little like
:term:`WSGI` middleware, but have access to Pyramid functionality such as
renderers and a full-featured request object.

To support this feature, a new configurator directive exists named
:meth:`pyramid.config.Configurator.add_tween`.  This directive adds a
"tween".

Tweens are further described in :ref:`registering_tweens`.

A new paster command now exists: ``paster ptweens``.  This command prints the
current tween configuration for an application.  See the section entitled
:ref:`displaying_tweens` for more info.

Scaffolding Changes
~~~~~~~~~~~~~~~~~~~

- All scaffolds now use the ``pyramid_tm`` package rather than the
  ``repoze.tm2`` middleware to manage transaction management.

- The ZODB scaffold now uses the ``pyramid_zodbconn`` package rather than the
  ``repoze.zodbconn`` package to provide ZODB integration.

- All scaffolds now use the ``pyramid_debugtoolbar`` package rather than the
  ``WebError`` package to provide interactive debugging features.

- Projects created via a scaffold no longer depend on the ``WebError``
  package at all; configuration in the ``production.ini`` file which used to
  require its ``error_catcher`` middleware has been removed.  Configuring
  error catching / email sending is now the domain of the ``pyramid_exclog``
  package (see https://docs.pylonsproject.org/projects/pyramid_exclog/dev/).

Minor Feature Additions
-----------------------

- The ``[pshell]`` section in an ini configuration file now treats a
  ``setup`` key as a dotted name that points to a callable that is passed the
  bootstrap environment.  It can mutate the environment as necessary during a
  ``paster pshell`` session.  This feature is described in
  :ref:`writing_a_script`.

- A new configuration setting named ``pyramid.includes`` is now available.
  It is described in :ref:`including_packages`.

- Added a :data:`pyramid.security.NO_PERMISSION_REQUIRED` constant for use in
  ``permission=`` statements to view configuration.  This constant has a
  value of the string ``__no_permission_required__``.  This string value was
  previously referred to in documentation; now the documentation uses the
  constant.

- Added a decorator-based way to configure a response adapter:
  :class:`pyramid.response.response_adapter`.  This decorator has the same
  use as :meth:`pyramid.config.Configurator.add_response_adapter` but it's
  declarative.

- The :class:`pyramid.events.BeforeRender` event now has an attribute named
  ``rendering_val``.  This can be used to introspect the value returned by a
  view in a BeforeRender subscriber.

- The Pyramid debug logger now uses the standard logging configuration
  (usually set up by Paste as part of startup).  This means that output from
  e.g. ``debug_notfound``, ``debug_authorization``, etc. will go to the
  normal logging channels.  The logger name of the debug logger will be the
  package name of the *caller* of the Configurator's constructor.

- A new attribute is available on request objects: ``exc_info``.  Its value
  will be ``None`` until an exception is caught by the Pyramid router, after
  which it will be the result of ``sys.exc_info()``.

- :class:`pyramid.testing.DummyRequest` now implements the
  ``add_finished_callback`` and ``add_response_callback`` methods implemented
  by :class:`pyramid.request.Request`.

- New methods of the :class:`pyramid.config.Configurator` class:
  :meth:`~pyramid.config.Configurator.set_authentication_policy` and
  :meth:`~pyramid.config.Configurator.set_authorization_policy`.  These are
  meant to be consumed mostly by add-on authors who wish to offer packages
  which register security policies.

- New Configurator method:
  :meth:`pyramid.config.Configurator.set_root_factory`, which can set the
  root factory after the Configurator has been constructed.

- Pyramid no longer eagerly commits some default configuration statements at
  :term:`Configurator` construction time, which permits values passed in as
  constructor arguments (e.g. ``authentication_policy`` and
  ``authorization_policy``) to override the same settings obtained via the
  :meth:`pyramid.config.Configurator.include` method.

- Better Mako rendering exceptions; the template line which caused the error
  is now shown when a Mako rendering raises an exception.

- New request methods: :meth:`~pyramid.request.Request.current_route_url`,
  :meth:`~pyramid.request.Request.current_route_path`, and
  :meth:`~pyramid.request.Request.static_path`.

- New functions in the :mod:`pyramid.url` module:
  :func:`~pyramid.url.current_route_path` and
  :func:`~pyramid.url.static_path`.

- The :meth:`pyramid.request.Request.static_url` API (and its brethren
  :meth:`pyramid.request.Request.static_path`,
  :func:`pyramid.url.static_url`, and :func:`pyramid.url.static_path`) now
  accept an asbolute filename as a "path" argument.  This will generate a URL
  to an asset as long as the filename is in a directory which was previously
  registered as a static view.  Previously, trying to generate a URL to an
  asset using an absolute file path would raise a ValueError.

- The :class:`~pyramid.authentication.RemoteUserAuthenticationPolicy`,
  :class:`~pyramid.authentication.AuthTktAuthenticationPolicy`, and
  :class:`~pyramid.authentication.SessionAuthenticationPolicy` constructors
  now accept an additional keyword argument named ``debug``.  By default,
  this keyword argument is ``False``.  When it is ``True``, debug information
  will be sent to the Pyramid debug logger (usually on stderr) when the
  ``authenticated_userid`` or ``effective_principals`` method is called on
  any of these policies.  The output produced can be useful when trying to
  diagnose authentication-related problems.

- New view predicate: ``match_param``.  Example: a view added via
  ``config.add_view(aview, match_param='action=edit')`` will be called only
  when the ``request.matchdict`` has a value inside it named ``action`` with
  a value of ``edit``.

Deprecations
------------

- All Pyramid-related :term:`deployment settings` (e.g. ``debug_all``,
  ``debug_notfound``) are now meant to be prefixed with the prefix
  ``pyramid.``.  For example: ``debug_all`` -> ``pyramid.debug_all``.  The
  old non-prefixed settings will continue to work indefinitely but supplying
  them may print a deprecation warning.  All scaffolds and tutorials have
  been changed to use prefixed settings.

- The :term:`deployment settings` dictionary now raises a deprecation warning
  when you attempt to access its values via ``__getattr__`` instead of via
  ``__getitem__``.

Backwards Incompatibilities
---------------------------

- If a string is passed as the ``debug_logger`` parameter to a
  :term:`Configurator`, that string is considered to be the name of a global
  Python logger rather than a dotted name to an instance of a logger.

- The :meth:`pyramid.config.Configurator.include` method now accepts only a
  single ``callable`` argument.  A *sequence* of callables used to be
  permitted.  If you are passing more than one ``callable`` to
  :meth:`pyramid.config.Configurator.include`, it will break.  You now must
  now instead make a separate call to the method for each callable.

Documentation Enhancements
--------------------------

- Narrative and API documentation which used the ``route_url``,
  ``route_path``, ``resource_url``, ``static_url``, and ``current_route_url``
  functions in the :mod:`pyramid.url` package have now been changed to use
  eponymous methods of the request instead.

- Added a section entitled :ref:`route_prefix` to the "URL Dispatch"
  narrative documentation chapter.

- Added a new module to the API docs: :mod:`pyramid.tweens`.

- Added a :ref:`registering_tweens` section to the "Hooks" narrative chapter.

- Added a :ref:`displaying_tweens` section to the "Command-Line Pyramid"
  narrative chapter.

- Added documentation for :ref:`explicit_tween_config` and
  :ref:`including_packages` to the "Environment Variables and ``.ini`` Files
  Settings" chapter.

- Added a :ref:`logging_chapter` chapter to the narrative docs.

- All tutorials now use - The ``route_url``, ``route_path``,
  ``resource_url``, ``static_url``, and ``current_route_url`` methods of the
  :class:`pyramid.request.Request` rather than the function variants imported
  from ``pyramid.url``.

- The ZODB wiki tutorial now uses the ``pyramid_zodbconn`` package rather
  than the ``repoze.zodbconn`` package to provide ZODB integration.

Dependency Changes
------------------

- Pyramid now relies on PasteScript >= 1.7.4.  This version contains a
  feature important for allowing flexible logging configuration.

