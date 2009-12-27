.. index::
   single: environment variables
   single: settings
   single: reload
   single: configure.zcml
   single: configure_zcml
   single: debug_authorization
   single: reload_resources
   single: debug_notfound
   single: debug_all
   single: reload_all
   pair: debug; settings
   pair: reload; settings
   pair: environment; variables
   pair: ini file; settings
   pair: PasteDeploy; settings
  
.. _environment_chapter:

Environment Variables and ``.ini`` File Settings
================================================

:mod:`repoze.bfg` behavior can be configured through a combination of
operating system environment variables and ``.ini`` configuration file
application section settings.  The meaning of the environment
variables and the configuration file settings overlap.

.. note:: Where a configuration file setting exists with the same
          meaning as an environment variable, and both are present at
          application startup time, the environment variable setting
          takes precedence.

The term "configuration file setting name" refers to a key in the
``.ini`` configuration for your application.  The configuration file
setting names documented in this chapter are reserved for
:mod:`repoze.bfg` use.  You should not use them to indicate
application-specific configuration settings.

+---------------------------------+-----------------------------+----------------------------------------+
| Environment Variable Name       | Config File Setting Name    |       Further Information              |
+=================================+=============================+========================================+
| ``BFG_RELOAD_TEMPLATES``        |  ``reload_templates``       |  Reload templates without restart      |
|                                 |                             |  when true                             |
|                                 |                             |  See also:                             |
|                                 |                             |  :ref:`reload_templates_section`       |
+---------------------------------+-----------------------------+----------------------------------------+
| ``BFG_RELOAD_RESOURCES``        |  ``reload_resources``       |  Don't cache any resource file data    |
|                                 |                             |  when true                             |
|                                 |                             |  See also:                             |
|                                 |                             |  :ref:`overriding_resources_section`   |
+---------------------------------+-----------------------------+----------------------------------------+
| ``BFG_DEBUG_AUTHORIZATION``     |  ``debug_authorization``    |  Print view authorization failure &    |
|                                 |                             |  success info to stderr when true      |
|                                 |                             |  See also:                             |
|                                 |                             |  :ref:`debug_authorization_section`    | 
+---------------------------------+-----------------------------+----------------------------------------+
| ``BFG_DEBUG_NOTFOUND``          |  ``debug_notfound``         |  Print view-related NotFound debug     |
|                                 |                             |  messages to stderr when true          |
|                                 |                             |  See also:                             |
|                                 |                             |  :ref:`debug_notfound_section`         |
+---------------------------------+-----------------------------+----------------------------------------+
| ``BFG_DEBUG_ALL``               |  ``debug_all``              |  Turns all debug_* settings on.        |
+---------------------------------+-----------------------------+----------------------------------------+
| ``BFG_RELOAD_ALL``              |  ``reload_all``             |  Turns all reload_* settings on.       |
+---------------------------------+-----------------------------+----------------------------------------+
| ``BFG_CONFIGURE_ZCML``          |  ``configure_zcml``         |  Use the specified filename to load    |
|                                 |                             |  the default app :term:`ZCML` file     |
|                                 |                             |  instead of the filename implied by    |
|                                 |                             |  ``filename`` value passed to          |
|                                 |                             |  ``repoze.bfg.router.make_app``.  If   |
|                                 |                             |  this is a relative filename, it will  |
|                                 |                             |  be considered relative to the         |
|                                 |                             |  ``package`` passed to ``make_app``    |
|                                 |                             |  by the application.  It may also      |
|                                 |                             |  take the form of a :term:`resource    |
|                                 |                             |  specification` which names both the   |
|                                 |                             |  package name and a package-relative   |
|                                 |                             |  filename, e.g.                        |
|                                 |                             |  ``dotted.package.name:path/to.zcml``. |
|                                 |                             |  If it is a resource specification,    |
|                                 |                             |  both the  *package* and the           |
|                                 |                             |  *filename* passed  to ``make_app``    |
|                                 |                             |  are overridden with the implied       |
|                                 |                             |  values.                               |
+---------------------------------+-----------------------------+----------------------------------------+

Examples
--------

Let's presume your configuration file is named ``MyProject.ini``, and
there is a section representing your application named ``[app:main]``
within the file that represents your :mod:`repoze.bfg` application.
The configuration file settings documented in the above "Config File
Setting Name" column would go in the ``[app:main]`` section.  Here's
an example of such a section::

  [app:main]
  use = egg:MyProject#app
  reload_templates = true
  debug_authorization = true

You can also use environment variables to accomplish the same purpose
for settings documented as such.  For example, you might start your
:mod:`repoze.bfg` application using the following command line::

  BFG_DEBUG_AUTHORIZATION=1 BFG_RELOAD_TEMPLATES=1 bin/paster serve MyProject.ini

If you started your application this way, your :mod:`repoze.bfg`
application would behave in the same manner as if you had placed the
respective settings in the ``[app:main]`` section of your
application's ``.ini`` file.

If you want to turn all ``debug`` settings (every setting that starts
with ``debug_``). on in one fell swoop, you can use
``BFG_DEBUG_ALL=1`` as an environment variable setting or you may use
``debug_all=true`` in the config file.  Note that this does not effect
settings that do not start with ``debug_*`` such as
``reload_templates``.

If you want to turn all ``reload`` settings (every setting that starts
with ``reload_``). on in one fell swoop, you can use
``BFG_RELOAD_ALL=1`` as an environment variable setting or you may use
``reload_all=true`` in the config file.  Note that this does not
effect settings that do not start with ``reload_*`` such as
``debug_notfound``.

.. index:: 
   pair: reload_templates; reload_resources

Understanding the Distinction Between ``reload_templates`` and ``reload_resources``
-----------------------------------------------------------------------------------

The difference between ``reload_resources`` and ``reload_templates``
is a bit subtle.  Templates are themselves also treated by
:mod:`repoze.bfg` as :term:`pkg_resources` resource files (along with
static files and other resources), so the distinction can be
confusing.  It's helpful to read :ref:`overriding_resources_section`
for some context about resources in general.

When ``reload_templates`` is true, :mod:`repoze.bfg`` takes advantage
of the underlying templating systems' ability to check for file
modifications to an individual template file.  When
``reload_templates`` is true but ``reload_resources`` is *not* true,
the template filename returned by pkg_resources is cached by
:mod:`repoze.bfg` on the first request.  Subsequent requests for the
same template file will return a cached template filename.  The
underlying templating system checks for modifications to this
particular file for every request.  Setting ``reload_templates`` to
``True`` doesn't effect performance dramatically (although it should
still not be used in production because it has some effect).

However, when ``reload_resources`` is true, :mod:`repoze.bfg` will not
cache the template filename, meaning you can see the effect of
changing the content of an overridden resource directory for templates
without restarting the server after every change.  Subsequent requests
for the same template file may return different filenames based on the
current state of overridden resource directories. Setting
``reload_resources`` to ``True`` effects performance *dramatically*
(slowing things down by an order of magnitude for each template
rendering) but it's convenient when moving files around in overridden
resource directories. ``reload_resources`` makes the system *very
slow* when templates are in use.  Never set ``reload_resources`` to
``True`` on a production system.

