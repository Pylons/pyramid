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
   single: debug_routematch
   single: prevent_http_cache
   single: reload settings
   single: default_locale_name
   single: environment variables
   single: ini file settings
   single: PasteDeploy settings

.. _environment_chapter:

Environment Variables and ``.ini`` File Settings
================================================

:app:`Pyramid` behavior can be configured through a combination of operating
system environment variables and ``.ini`` configuration file application
section settings.  The meaning of the environment variables and the
configuration file settings overlap.

.. note::
  Where a configuration file setting exists with the same meaning as an
  environment variable, and both are present at application startup time, the
  environment variable setting takes precedence.

The term "configuration file setting name" refers to a key in the ``.ini``
configuration for your application.  The configuration file setting names
documented in this chapter are reserved for :app:`Pyramid` use.  You should not
use them to indicate application-specific configuration settings.

Reloading Templates
-------------------

When this value is true, templates are automatically reloaded whenever they are
modified without restarting the application, so you can see changes to
templates take effect immediately during development.  This flag is meaningful
to Chameleon and Mako templates, as well as most third-party template rendering
extensions.

+-------------------------------+--------------------------------+
| Environment Variable Name     | Config File Setting Name       |
+===============================+================================+
| ``PYRAMID_RELOAD_TEMPLATES``  |  ``pyramid.reload_templates``  |
|                               |   or ``reload_templates``      |
+-------------------------------+--------------------------------+

Reloading Assets
----------------

Don't cache any asset file data when this value is true.

.. seealso::

    See also :ref:`overriding_assets_section`.

+----------------------------+-----------------------------+
| Environment Variable Name  | Config File Setting Name    |
+============================+=============================+
| ``PYRAMID_RELOAD_ASSETS``  |  ``pyramid.reload_assets``  |
|                            |  or ``reload_assets``       |
+----------------------------+-----------------------------+

.. note:: For backwards compatibility purposes, aliases can be used for
   configuring asset reloading: ``PYRAMID_RELOAD_RESOURCES`` (envvar) and
   ``pyramid.reload_resources`` (config file).

Debugging Authorization
-----------------------

Print view authorization failure and success information to stderr when this
value is true.

.. seealso::

    See also :ref:`debug_authorization_section`.

+---------------------------------+-----------------------------------+
| Environment Variable Name       | Config File Setting Name          |
+=================================+===================================+
| ``PYRAMID_DEBUG_AUTHORIZATION`` |  ``pyramid.debug_authorization``  |
|                                 |  or ``debug_authorization``       |
+---------------------------------+-----------------------------------+

Debugging Not Found Errors
--------------------------

Print view-related ``NotFound`` debug messages to stderr when this value is
true.

.. seealso::

    See also :ref:`debug_notfound_section`.

+----------------------------+------------------------------+
| Environment Variable Name  | Config File Setting Name     |
+============================+==============================+
| ``PYRAMID_DEBUG_NOTFOUND`` |  ``pyramid.debug_notfound``  |
|                            |  or ``debug_notfound``       |
+----------------------------+------------------------------+

Debugging Route Matching
------------------------

Print debugging messages related to :term:`url dispatch` route matching when
this value is true.

.. seealso::

    See also :ref:`debug_routematch_section`.

+------------------------------+--------------------------------+
| Environment Variable Name    | Config File Setting Name       |
+==============================+================================+
| ``PYRAMID_DEBUG_ROUTEMATCH`` |  ``pyramid.debug_routematch``  |
|                              |  or ``debug_routematch``       |
+------------------------------+--------------------------------+

.. _preventing_http_caching:

Preventing HTTP Caching
-----------------------

Prevent the ``http_cache`` view configuration argument from having any effect
globally in this process when this value is true.  No HTTP caching-related
response headers will be set by the :app:`Pyramid` ``http_cache`` view
configuration feature when this is true.

.. seealso::

    See also :ref:`influencing_http_caching`.

+---------------------------------+----------------------------------+
| Environment Variable Name       | Config File Setting Name         |
+=================================+==================================+
| ``PYRAMID_PREVENT_HTTP_CACHE``  |  ``pyramid.prevent_http_cache``  |
|                                 |  or ``prevent_http_cache``       |
+---------------------------------+----------------------------------+

Preventing Cache Busting
------------------------

Prevent the ``cachebust`` static view configuration argument from having any
effect globally in this process when this value is true.  No cache buster will
be configured or used when this is true.

.. versionadded:: 1.6

.. seealso::

    See also :ref:`cache_busting`.

+---------------------------------+----------------------------------+
| Environment Variable Name       | Config File Setting Name         |
+=================================+==================================+
| ``PYRAMID_PREVENT_CACHEBUST``   |  ``pyramid.prevent_cachebust``   |
|                                 |  or ``prevent_cachebust``        |
+---------------------------------+----------------------------------+

Debugging All
-------------

Turns on all ``debug*`` settings.

+----------------------------+---------------------------+
| Environment Variable Name  | Config File Setting Name  |
+============================+===========================+
| ``PYRAMID_DEBUG_ALL``      |  ``pyramid.debug_all``    |
|                            |  or ``debug_all``         |
+----------------------------+---------------------------+

Reloading All
-------------

Turns on all ``reload*`` settings.

+---------------------------+----------------------------+
| Environment Variable Name | Config File Setting Name   |
+===========================+============================+
| ``PYRAMID_RELOAD_ALL``    |  ``pyramid.reload_all`` or |
|                           |  ``reload_all``            |
+---------------------------+----------------------------+

.. _default_locale_name_setting:

Default Locale Name
-------------------

The value supplied here is used as the default locale name when a :term:`locale
negotiator` is not registered.

.. seealso::

    See also :ref:`localization_deployment_settings`.

+---------------------------------+-----------------------------------+
| Environment Variable Name       | Config File Setting Name          |
+=================================+===================================+
| ``PYRAMID_DEFAULT_LOCALE_NAME`` |  ``pyramid.default_locale_name``  |
|                                 |  or ``default_locale_name``       |
+---------------------------------+-----------------------------------+

.. _including_packages:

Including Packages
------------------

``pyramid.includes`` instructs your application to include other packages.
Using the setting is equivalent to using the
:meth:`pyramid.config.Configurator.include` method.

+--------------------------+
| Config File Setting Name |
+==========================+
| ``pyramid.includes``     |
+--------------------------+

The value assigned to ``pyramid.includes`` should be a sequence.  The sequence
can take several different forms.

1) It can be a string.

   If it is a string, the package names can be separated by spaces::

      package1 package2 package3

   The package names can also be separated by carriage returns::

       package1
       package2
       package3

2) It can be a Python list, where the values are strings::

   ['package1', 'package2', 'package3']

Each value in the sequence should be a :term:`dotted Python name`.

``pyramid.includes`` vs. :meth:`pyramid.config.Configurator.include`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two methods exist for including packages: ``pyramid.includes`` and
:meth:`pyramid.config.Configurator.include`.  This section explains their
equivalence.

Using PasteDeploy
+++++++++++++++++

Using the following ``pyramid.includes`` setting in the PasteDeploy ``.ini``
file in your application:

.. code-block:: ini

   [app:main]
   pyramid.includes = pyramid_debugtoolbar
                      pyramid_tm

Is equivalent to using the following statements in your configuration code:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def main(global_config, **settings):
       config = Configurator(settings=settings)
       # ...
       config.include('pyramid_debugtoolbar')
       config.include('pyramid_tm')
       # ...

It is fine to use both or either form.

Plain Python
++++++++++++

Using the following ``pyramid.includes`` setting in your plain-Python Pyramid
application:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   if __name__ == '__main__':
       settings = {'pyramid.includes':'pyramid_debugtoolbar pyramid_tm'}
       config = Configurator(settings=settings)

Is equivalent to using the following statements in your configuration code:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   if __name__ == '__main__':
       settings = {}
       config = Configurator(settings=settings)
       config.include('pyramid_debugtoolbar')
       config.include('pyramid_tm')

It is fine to use both or either form.

.. _explicit_tween_config:

Explicit Tween Configuration
----------------------------

This value allows you to perform explicit :term:`tween` ordering in your
configuration.  Tweens are bits of code used by add-on authors to extend
Pyramid.  They form a chain, and require ordering.

Ideally you won't need to use the ``pyramid.tweens`` setting at all.  Tweens
are generally ordered and included "implicitly" when an add-on package which
registers a tween is "included".  Packages are included when you name a
``pyramid.includes`` setting in your configuration or when you call
:meth:`pyramid.config.Configurator.include`.

Authors of included add-ons provide "implicit" tween configuration ordering
hints to Pyramid when their packages are included.  However, the implicit tween
ordering is only best-effort.  Pyramid will attempt to provide an implicit
order of tweens as best it can using hints provided by add-on authors, but
because it's only best-effort, if very precise tween ordering is required, the
only surefire way to get it is to use an explicit tween order. You may be
required to inspect your tween ordering (see :ref:`displaying_tweens`) and add
a ``pyramid.tweens`` configuration value at the behest of an add-on author.

+---------------------------+
| Config File Setting Name  |
+===========================+
| ``pyramid.tweens``        |
+---------------------------+

The value assigned to ``pyramid.tweens`` should be a sequence.  The sequence
can take several different forms.

1) It can be a string.

   If it is a string, the tween names can be separated by spaces::

      pkg.tween_factory1 pkg.tween_factory2 pkg.tween_factory3

   The tween names can also be separated by carriage returns::

      pkg.tween_factory1
      pkg.tween_factory2
      pkg.tween_factory3

2) It can be a Python list, where the values are strings::

   ['pkg.tween_factory1', 'pkg.tween_factory2', 'pkg.tween_factory3']

Each value in the sequence should be a :term:`dotted Python name`.

PasteDeploy Configuration vs. Plain-Python Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the following ``pyramid.tweens`` setting in the PasteDeploy ``.ini`` file
in your application:

.. code-block:: ini

   [app:main]
   pyramid.tweens = pyramid_debugtoolbar.toolbar.tween_factory
                    pyramid.tweens.excview_tween_factory
                    pyramid_tm.tm_tween_factory

Is equivalent to using the following statements in your configuration code:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
 
   def main(global_config, **settings):
       settings['pyramid.tweens'] = [
               'pyramid_debugtoolbar.toolbar.tween_factory',
               'pyramid.tweebs.excview_tween_factory',
               'pyramid_tm.tm_tween_factory',
                ]
       config = Configurator(settings=settings)

It is fine to use both or either form.

Examples
--------

Let's presume your configuration file is named ``MyProject.ini``, and there is
a section representing your application named ``[app:main]`` within the file
that represents your :app:`Pyramid` application. The configuration file
settings documented in the above "Config File Setting Name" column would go in
the ``[app:main]`` section.  Here's an example of such a section:

.. code-block:: ini
  :linenos:

  [app:main]
  use = egg:MyProject
  pyramid.reload_templates = true
  pyramid.debug_authorization = true

You can also use environment variables to accomplish the same purpose for
settings documented as such.  For example, you might start your :app:`Pyramid`
application using the following command line:

.. code-block:: text

  $ PYRAMID_DEBUG_AUTHORIZATION=1 PYRAMID_RELOAD_TEMPLATES=1 \
         $VENV/bin/pserve MyProject.ini

If you started your application this way, your :app:`Pyramid` application would
behave in the same manner as if you had placed the respective settings in the
``[app:main]`` section of your application's ``.ini`` file.

If you want to turn all ``debug`` settings (every setting that starts with
``pyramid.debug_``) on in one fell swoop, you can use ``PYRAMID_DEBUG_ALL=1``
as an environment variable setting or you may use ``pyramid.debug_all=true`` in
the config file.  Note that this does not affect settings that do not start
with ``pyramid.debug_*`` such as ``pyramid.reload_templates``.

If you want to turn all ``pyramid.reload`` settings (every setting that starts
with ``pyramid.reload_``) on in one fell swoop, you can use
``PYRAMID_RELOAD_ALL=1`` as an environment variable setting or you may use
``pyramid.reload_all=true`` in the config file.  Note that this does not affect
settings that do not start with ``pyramid.reload_*`` such as
``pyramid.debug_notfound``.

.. note::
   Specifying configuration settings via environment variables is generally
   most useful during development, where you may wish to augment or override
   the more permanent settings in the configuration file. This is useful
   because many of the reload and debug settings may have performance or
   security (i.e., disclosure) implications that make them undesirable in a
   production environment.

.. index::
   single: reload_templates
   single: reload_assets

Understanding the Distinction Between ``reload_templates`` and ``reload_assets``
--------------------------------------------------------------------------------

The difference between ``pyramid.reload_assets`` and
``pyramid.reload_templates`` is a bit subtle. Templates are themselves also
treated by :app:`Pyramid` as asset files (along with other static files), so
the distinction can be confusing.  It's helpful to read
:ref:`overriding_assets_section` for some context about assets in general.

When ``pyramid.reload_templates`` is true, :app:`Pyramid` takes advantage of
the underlying templating system's ability to check for file modifications to
an individual template file.  When ``pyramid.reload_templates`` is true, but
``pyramid.reload_assets`` is *not* true, the template filename returned by the
``pkg_resources`` package (used under the hood by asset resolution) is cached
by :app:`Pyramid` on the first request.  Subsequent requests for the same
template file will return a cached template filename.  The underlying
templating system checks for modifications to this particular file for every
request.  Setting ``pyramid.reload_templates`` to ``True`` doesn't affect
performance dramatically (although it should still not be used in production
because it has some effect).

However, when ``pyramid.reload_assets`` is true, :app:`Pyramid` will not cache
the template filename, meaning you can see the effect of changing the content
of an overridden asset directory for templates without restarting the server
after every change.  Subsequent requests for the same template file may return
different filenames based on the current state of overridden asset directories.
Setting ``pyramid.reload_assets`` to ``True`` affects performance
*dramatically*, slowing things down by an order of magnitude for each template
rendering.  However, it's convenient to enable when moving files around in
overridden asset directories. ``pyramid.reload_assets`` makes the system *very
slow* when templates are in use.  Never set ``pyramid.reload_assets`` to
``True`` on a production system.

.. index::
   par: settings; adding custom

.. _adding_a_custom_setting:

Adding a Custom Setting
-----------------------

From time to time, you may need to add a custom setting to your application.
Here's how:

- If you're using an ``.ini`` file, change the ``.ini`` file, adding the
  setting to the ``[app:foo]`` section representing your Pyramid application.
  For example:

  .. code-block:: ini

    [app:main]
    # .. other settings
    debug_frobnosticator = True

- In the ``main()`` function that represents the place that your Pyramid WSGI
  application is created, anticipate that you'll be getting this key/value pair
  as a setting and do any type conversion necessary.

  If you've done any type conversion of your custom value, reset the converted
  values into the ``settings`` dictionary *before* you pass the dictionary as
  ``settings`` to the :term:`Configurator`.  For example:

  .. code-block:: python

     def main(global_config, **settings):
         # ...
         from pyramid.settings import asbool
         debug_frobnosticator = asbool(settings.get(
                    'debug_frobnosticator', 'false'))
         settings['debug_frobnosticator'] = debug_frobnosticator
         config = Configurator(settings=settings)

  .. note::
     It's especially important that you mutate the ``settings`` dictionary with
     the converted version of the variable *before* passing it to the
     Configurator: the configurator makes a *copy* of ``settings``, it doesn't
     use the one you pass directly.

-  When creating an ``includeme`` function that will be later added to your
   application's configuration you may access the ``settings`` dictionary
   through the instance of the :term:`Configurator` that is passed into the
   function as its only argument.  For Example:

  .. code-block:: python
     
     def includeme(config):
         settings = config.registry.settings
         debug_frobnosticator = settings['debug_frobnosticator']

- In the runtime code from where you need to access the new settings value,
  find the value in the ``registry.settings`` dictionary and use it.  In
  :term:`view` code (or any other code that has access to the request), the
  easiest way to do this is via ``request.registry.settings``.  For example:

  .. code-block:: python

     settings = request.registry.settings
     debug_frobnosticator = settings['debug_frobnosticator']

  If you wish to use the value in code that does not have access to the request
  and you wish to use the value, you'll need to use the
  :func:`pyramid.threadlocal.get_current_registry` API to obtain the current
  registry, then ask for its ``settings`` attribute.  For example:

  .. code-block:: python

     registry = pyramid.threadlocal.get_current_registry()
     settings = registry.settings
     debug_frobnosticator = settings['debug_frobnosticator']
