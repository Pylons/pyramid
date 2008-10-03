.. _environment_chapter:

Environment and Configuration
=============================

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

+-----------------------------+--------------------------+-------------------------------------+
| Environment Variable Name   | Config File Setting Name |       Further Information           |
+=============================+==========================+=====================================+
| ``BFG_RELOAD_TEMPLATES``    |  ``reload_templates``    |  Reload templates without restart   |
|                             |                          |  when true                          |
|                             |                          |  See also:                          |
|                             |                          |  :ref:`reload_templates_section`    |
+-----------------------------+--------------------------+-------------------------------------+
| ``BFG_DEBUG_AUTHORIZATION`` |  ``debug_authorization`` |  Print authorization failure/success|
|                             |                          |  messages to stderr when true       |
|                             |                          |  See also:                          |
|                             |                          |  :ref:`debug_authorization_section` |
+-----------------------------+--------------------------+-------------------------------------+

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
