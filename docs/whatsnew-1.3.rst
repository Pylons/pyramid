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

Pyramid is now Python 3 compatible.  Python 3.2 or better is required.  A new
:mod:`pyramid.compat` module was added which provides Python 2/3 straddling
support for Pyramid add-ons and development environments.

Python 3 compatibility required dropping some package dependencies and
support for older Python versions and platforms.  See the "Backwards
Incompatibilities" section below for more information.

Introspection
~~~~~~~~~~~~~

A configuration introspection system was added; see
:ref:`using_introspection` and :ref:`introspection` for more information on
using the introspection system as a developer.

A new release of the pyramid debug toolbar will provide an "Introspection"
panel that presents introspection information to a developer.

New APIs were added to support introspection
:attr:`pyramid.registry.Introspectable`,
:attr:`pyramid.registry.noop_introspector`, 
:attr:`pyramid.config.Configurator.introspector`,
:attr:`pyramid.config.Configurator.introspectable`,
:attr:`pyramid.registry.Registry.introspector`.

Minor Feature Additions
-----------------------

- A ``mako.directories`` setting is no longer required to use Mako templates
  Rationale: Mako template renderers can be specified using an absolute asset
  spec.  An entire application can be written with such asset specs,
  requiring no ordered lookup path.

- ``bpython`` interpreter compatibility in ``pshell``.  See
  :ref:`ipython_or_bpython` for more information.

- Added :func:`pyramid.paster.get_appsettings`` API function.  This function
  returns the settings defined within an ``[app:...]`` section in a
  PasteDeploy ``ini`` file.

- Added :func:`pyramid.paster.setup_logging` API function.  This function
  sets up Python logging according to the logging configuration in a
  PasteDeploy ``ini`` file.

- Configuration conflict reporting is reported in a more understandable way
  ("Line 11 in file..." vs. a repr of a tuple of similar info).

- Allow extra keyword arguments to be passed to the
  :meth:`pyramid.config.Configurator.action` method.

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
  scaffolding is now the ``wsgiref`` WSGI server instead of the
  ``paste.httpserver`` server.  ``wsgiref``, unlike the server it replaced
  (``paste.httpserver``) is not a production quality server.  See
  :ref:`alternate_wsgi_server` for information about how to use another WSGI
  server in production. Rationale: Rationale: the Paste and PasteScript
  packages do not run under Python 3.

- The ``pshell`` command (see "paster pshell") no longer accepts a
  ``--disable-ipython`` command-line argument.  Instead, it accepts a ``-p``
  or ``--python-shell`` argument, which can be any of the values ``python``,
  ``ipython`` or ``bpython``.

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

Scaffolding Changes
-------------------

- Rendered scaffolds have now been changed to be more relocatable (fewer
  mentions of the package name within files in the package).

- The ``routesalchemy`` scaffold has been renamed ``alchemy``, replacing the
  older (traversal-based) ``alchemy`` scaffold (which has been retired).

- The ``starter`` scaffold now uses URL dispatch by default.


