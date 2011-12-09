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

Pyramid is now Python 3 compatible.  Python 3.2 or better is required.

This feature required us to make some compromises.

Pyramid no longer runs on Python 2.5.  This includes the most recent release
of Jython and the Python 2.5 version of Google App Engine.  We could not
easily "straddle" Python 2 and 3 versions and support Python 2 versions older
than Python 2.6.  You will need Python 2.6 or better to run this version of
Pyramid.  If you need to use Pyramid on Python 2.5, you should use the most
recent 1.2.X release of Pyramid there.

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

- We've made the default WSGI server the ``wsgiref`` server.

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
``paster serve`` and ``paster create`` instead if they like.  However, using
``pserve`` and ``pcreate`` will work under both Python 2 and Python 3.

Analogues of ``paster pshell``, ``paster pviews`` and ``paster ptweens`` also
exist under the respective console script names ``pshell``, ``pviews``, and
``ptweens``.

We've replaced use of the Paste ``httpserver`` with the ``wsgiref`` server in
the scaffolds, so once you create a project from a scaffold, its
``development.ini`` and ``production.ini`` will have the following line::

    use = egg:pyramid#wsgiref

Instead of this (which was the default in older versions)::

    use = egg:Paste#http

Using ``wsgiref`` as the default WSGI server is purely a default to make it
possible to use the same scaffolding under Python 2 and Python 3; people
running Pyramid under Python 2 can still manually install ``Paste`` and use
the Paste ``httpserver`` by replacing the former line with the latter.  This is
actually recommended if you rely on proxying from Apache or Nginx to a
``pserve`` -invoked application.  **The wsgiref server is not a production
quality server.** See :ref:`alternate_wsgi_server` for more information.

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

The latest release of the pyramid debug toolbar (0.9.6) provides an
"Introspection" panel that exposes introspection information to a Pyramid
application developer.

New APIs were added to support introspection
:attr:`pyramid.registry.Introspectable`,
:attr:`pyramid.registry.noop_introspector`, 
:attr:`pyramid.config.Configurator.introspector`,
:attr:`pyramid.config.Configurator.introspectable`,
:attr:`pyramid.registry.Registry.introspector`.

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

- Removed the ``pyramid.renderers.renderer_from_name`` function.  It has been
  deprecated since Pyramid 1.0, and was never an API.

- To use ZCML with versions of Pyramid >= 1.3, you will need ``pyramid_zcml``
  version >= 0.8 and ``zope.configuration`` version >= 3.8.0.  The
  ``pyramid_zcml`` package version 0.8 is backwards compatible all the way to
  Pyramid 1.0, so you won't be warned if you have older versions installed
  and upgrade Pyramid itself "in-place"; it may simply break instead
  (particularly if you use ZCML's ``includeOverrides`` directive).

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

- The ``alchemy`` and ``starter`` scaffolds are Python 3 compatible.

- The ``starter`` scaffold now uses URL dispatch by default.
