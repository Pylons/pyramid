.. index::
   single: environment variables
   single: settings
   single: reload
   single: debug_authorization
   single: reload_assets
   single: debug_notfound
   single: debug_all
   single: reload_all
   single: debug settings
   single: reload settings
   single: default_locale_name
   single: environment variables
   single: ini file settings
   single: PasteDeploy settings
  
.. _environment_chapter:

Environment Variables and ``.ini`` File Settings
================================================

:app:`Pyramid` behavior can be configured through a combination of
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
:app:`Pyramid` use.  You should not use them to indicate
application-specific configuration settings.

Reloading Templates
-------------------

When this value is true, templates are automatically reloaded whenever
they are modified without restarting the application, so you can see
changes to templates take effect immediately during development.  This
flag is meaningful to Chameleon and Mako templates, as well as most
third-party template rendering extensions.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_RELOAD_TEMPLATES``    |  ``reload_templates``       |
|                                 |                             |
|                                 |                             |
|                                 |                             |
+---------------------------------+-----------------------------+

Reloading Assets
----------------

Don't cache any asset file data when this value is true.  See
also :ref:`overriding_assets_section`.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_RELOAD_ASSETS``       |  ``reload_assets``          |
|                                 |                             |
|                                 |                             |
|                                 |                             |
+---------------------------------+-----------------------------+

.. note:: For backwards compatibility purposes, aliases can be
   used for configurating asset reloading: ``PYRAMID_RELOAD_RESOURCES`` (envvar)
   and ``reload_resources`` (config file).

Debugging Authorization
-----------------------

Print view authorization failure and success information to stderr
when this value is true.  See also :ref:`debug_authorization_section`.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_DEBUG_AUTHORIZATION`` |  ``debug_authorization``    |
|                                 |                             |
|                                 |                             |
|                                 |                             | 
+---------------------------------+-----------------------------+

Debugging Not Found Errors
--------------------------

Print view-related ``NotFound`` debug messages to stderr
when this value is true.  See also :ref:`debug_notfound_section`.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_DEBUG_NOTFOUND``      |  ``debug_notfound``         |
|                                 |                             |
|                                 |                             |
|                                 |                             |
+---------------------------------+-----------------------------+

Debugging Route Matching
------------------------

Print debugging messages related to :term:`url dispatch` route matching when
this value is true.  See also :ref:`debug_routematch_section`.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_DEBUG_ROUTEMATCH``    |  ``debug_routematch``       |
|                                 |                             |
|                                 |                             |
|                                 |                             |
+---------------------------------+-----------------------------+

Debugging All
-------------

Turns on all ``debug*`` settings.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_DEBUG_ALL``           |  ``debug_all``              |
|                                 |                             |
|                                 |                             |
|                                 |                             |
+---------------------------------+-----------------------------+

Reloading All
-------------

Turns on all ``reload*`` settings.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_RELOAD_ALL``          |  ``reload_all``             |
|                                 |                             |
|                                 |                             |
|                                 |                             |
+---------------------------------+-----------------------------+

.. _default_locale_name_setting:

Default Locale Name
--------------------

The value supplied here is used as the default locale name when a
:term:`locale negotiator` is not registered.  See also
:ref:`localization_deployment_settings`.

+---------------------------------+-----------------------------+
| Environment Variable Name       | Config File Setting Name    |
+=================================+=============================+
| ``PYRAMID_DEFAULT_LOCALE_NAME`` |  ``default_locale_name``    |
|                                 |                             |
|                                 |                             |
|                                 |                             |
+---------------------------------+-----------------------------+

.. _mako_template_renderer_settings:

Mako Template Render Settings
-----------------------------

Mako derives additional settings to configure its template renderer that
should be set when using it. Many of these settings are optional and only need
to be set if they should be different from the default. The Mako Template
Renderer uses a subclass of Mako's `template lookup
<http://www.makotemplates.org/docs/usage.html#usage_lookup>`_ and accepts
several arguments to configure it.

Mako Directories
++++++++++++++++

The value(s) supplied here are passed in as the template directories. They
should be in :term:`asset specification` format, for example:
``my.package:templates``.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.directories``       |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Module Directory
+++++++++++++++++++++

The value supplied here tells Mako where to store compiled Mako templates. If
omitted, compiled templates will be stored in memory. This value should be an
absolute path, for example: ``%(here)s/data/templates`` would use a directory
called ``data/templates`` in the same parent directory as the INI file.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.module_directory``  |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Input Encoding
+++++++++++++++++++

The encoding that Mako templates are assumed to have. By default this is set
to ``utf-8``. If you wish to use a different template encoding, this value
should be changed accordingly.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.input_encoding``    |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Error Handler
++++++++++++++++++

Python callable which is called whenever Mako compile or runtime exceptions
occur. The callable is passed the current context as well as the exception. If
the callable returns True, the exception is considered to be handled, else it
is re-raised after the function completes. Is used to provide custom
error-rendering functions.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.error_handler``     |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Default Filters
++++++++++++++++++++

List of string filter names that will be applied to all Mako expressions.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.default_filters``   |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Import
+++++++++++

String list of Python statements, typically individual “import” lines, which
will be placed into the module level preamble of all generated Python modules.


+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.imports``           |
|                             |
|                             |
|                             |
+-----------------------------+


Mako Strict Undefined
+++++++++++++++++++++

``true`` or ``false``, representing the "strict undefined" behavior of Mako
(see `Mako Context Variables
<http://www.makotemplates.org/docs/runtime.html#context-variables>`_).  By
default, this is ``false``.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.strict_undefined``  |
|                             |
|                             |
|                             |
+-----------------------------+

Examples
--------

Let's presume your configuration file is named ``MyProject.ini``, and
there is a section representing your application named ``[app:main]``
within the file that represents your :app:`Pyramid` application.
The configuration file settings documented in the above "Config File
Setting Name" column would go in the ``[app:main]`` section.  Here's
an example of such a section:

.. code-block:: ini
  :linenos:

  [app:main]
  use = egg:MyProject#app
  reload_templates = true
  debug_authorization = true

You can also use environment variables to accomplish the same purpose
for settings documented as such.  For example, you might start your
:app:`Pyramid` application using the following command line:

.. code-block:: text

  $ PYRAMID_DEBUG_AUTHORIZATION=1 PYRAMID_RELOAD_TEMPLATES=1 \
         bin/paster serve MyProject.ini

If you started your application this way, your :app:`Pyramid`
application would behave in the same manner as if you had placed the
respective settings in the ``[app:main]`` section of your
application's ``.ini`` file.

If you want to turn all ``debug`` settings (every setting that starts
with ``debug_``). on in one fell swoop, you can use
``PYRAMID_DEBUG_ALL=1`` as an environment variable setting or you may use
``debug_all=true`` in the config file.  Note that this does not affect
settings that do not start with ``debug_*`` such as
``reload_templates``.

If you want to turn all ``reload`` settings (every setting that starts
with ``reload_``). on in one fell swoop, you can use
``PYRAMID_RELOAD_ALL=1`` as an environment variable setting or you may use
``reload_all=true`` in the config file.  Note that this does not
affect settings that do not start with ``reload_*`` such as
``debug_notfound``.

.. note::
   Specifying configuration settings via environment variables is generally
   most useful during development, where you may wish to augment or
   override the more permanent settings in the configuration file.
   This is useful because many of the reload and debug settings may
   have performance or security (i.e., disclosure) implications 
   that make them undesirable in a production environment.

.. index:: 
   single: reload_templates
   single: reload_assets

Understanding the Distinction Between ``reload_templates`` and ``reload_assets``
--------------------------------------------------------------------------------

The difference between ``reload_assets`` and ``reload_templates`` is a bit
subtle.  Templates are themselves also treated by :app:`Pyramid` as asset
files (along with other static files), so the distinction can be confusing.
It's helpful to read :ref:`overriding_assets_section` for some context
about assets in general.

When ``reload_templates`` is true, :app:`Pyramid` takes advantage of the
underlying templating systems' ability to check for file modifications to an
individual template file.  When ``reload_templates`` is true but
``reload_assets`` is *not* true, the template filename returned by the
``pkg_resources`` package (used under the hood by asset resolution) is cached
by :app:`Pyramid` on the first request.  Subsequent requests for the same
template file will return a cached template filename.  The underlying
templating system checks for modifications to this particular file for every
request.  Setting ``reload_templates`` to ``True`` doesn't affect performance
dramatically (although it should still not be used in production because it
has some effect).

However, when ``reload_assets`` is true, :app:`Pyramid` will not cache the
template filename, meaning you can see the effect of changing the content of
an overridden asset directory for templates without restarting the server
after every change.  Subsequent requests for the same template file may
return different filenames based on the current state of overridden asset
directories. Setting ``reload_assets`` to ``True`` affects performance
*dramatically*, slowing things down by an order of magnitude for each
template rendering.  However, it's convenient to enable when moving files
around in overridden asset directories. ``reload_assets`` makes the system
*very slow* when templates are in use.  Never set ``reload_assets`` to
``True`` on a production system.

