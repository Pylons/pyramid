.. _paste_chapter:

PasteDeploy Configuration Files
===============================

Packages generated via a :term:`cookiecutter` make use of a system created by Ian
Bicking named :term:`PasteDeploy`.  PasteDeploy defines a way to declare
:term:`WSGI` application configuration in an ``.ini`` file.

Pyramid uses this configuration file format as input to its :term:`WSGI` server
runner ``pserve``, as well as other commands such as ``pviews``, ``pshell``,
``proutes``, and ``ptweens``.

PasteDeploy is not a particularly integral part of Pyramid.  It's possible to
create a Pyramid application which does not use PasteDeploy at all.  We show a
Pyramid application that doesn't use PasteDeploy in :ref:`firstapp_chapter`.
However, all Pyramid cookiecutters render PasteDeploy configuration files, to
provide new developers with a standardized way of setting deployment values,
and to provide new users with a standardized way of starting, stopping, and
debugging an application.

This chapter is not a replacement for documentation about PasteDeploy; it only
contextualizes the use of PasteDeploy within Pyramid.  For detailed
documentation, see http://pythonpaste.org/deploy/.

PasteDeploy
-----------

:term:`plaster` is the system that Pyramid uses to load settings from configuration files. The most common format for these files is an ``.ini`` format structured in a way defined by :term:`PasteDeploy`.  The format supports mechanisms to define WSGI app :term:`deployment settings`, WSGI server settings and logging. This allows the ``pserve`` command to work, allowing you to stop and start a Pyramid application easily.

.. _pastedeploy_entry_points:

Entry Points and PasteDeploy ``.ini`` Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the :ref:`project_narr` chapter, we breezed over the meaning of a
configuration line in the ``deployment.ini`` file.  This was the ``use =
egg:myproject`` line in the ``[app:main]`` section.  We breezed over it because
it's pretty confusing and "too much information" for an introduction to the
system.  We'll try to give it a bit of attention here.  Let's see the config
file again:

.. literalinclude:: myproject/development.ini
   :language: ini
   :linenos:

The line in ``[app:main]`` above that says ``use = egg:myproject`` is actually
shorthand for a longer spelling: ``use = egg:myproject#main``.  The ``#main``
part is omitted for brevity, as ``#main`` is a default defined by PasteDeploy.
``egg:myproject#main`` is a string which has meaning to PasteDeploy.  It points
at a :term:`setuptools` :term:`entry point` named ``main`` defined in the
``myproject`` project.

Take a look at the generated ``setup.py`` file for this project.

.. literalinclude:: myproject/setup.py
   :language: python
   :linenos:

Note that ``entry_points`` is assigned a string which looks a lot like an
``.ini`` file.  This string representation of an ``.ini`` file has a section
named ``[paste.app_factory]``.  Within this section, there is a key named
``main`` (the entry point name) which has a value ``myproject:main``.  The
*key* ``main`` is what our ``egg:myproject#main`` value of the ``use`` section
in our config file is pointing at, although it is actually shortened to
``egg:myproject`` there.  The value represents a :term:`dotted Python name`
path, which refers to a callable in our ``myproject`` package's ``__init__.py``
module.

The ``egg:`` prefix in ``egg:myproject`` indicates that this is an entry point
*URI* specifier, where the "scheme" is "egg".  An "egg" is created when you run
``setup.py install`` or ``setup.py develop`` within your project.

In English, this entry point can thus be referred to as a "PasteDeploy
application factory in the ``myproject`` project which has the entry point
named ``main`` where the entry point refers to a ``main`` function in the
``mypackage`` module".  Indeed, if you open up the ``__init__.py`` module
generated within any cookiecutter-generated package, you'll see a ``main``
function.  This is the function called by :term:`PasteDeploy` when the
``pserve`` command is invoked against our application.  It accepts a global
configuration object and *returns* an instance of our application.

.. _defaults_section_of_pastedeploy_file:

``[DEFAULT]`` Section of a PasteDeploy ``.ini`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add a ``[DEFAULT]`` section to your PasteDeploy ``.ini`` file.  Such a
section should consist of global parameters that are shared by all the
applications, servers, and :term:`middleware` defined within the configuration
file.  The values in a ``[DEFAULT]`` section will be passed to your
application's ``main`` function as ``global_config`` (see the reference to the
``main`` function in :ref:`init_py`).

Alternative Configuration File Formats
--------------------------------------

It is possible to use different file formats with :app:`Pyramid` if you do not like :term:`PasteDeploy`. Under the hood all command-line scripts such as ``pserve`` and ``pshell`` pass the ``config_uri`` (e.g. ``development.ini`` or ``production.ini``) to the :term:`plaster` library which performs a lookup for an appropriate parser. For ``.ini`` files it uses PasteDeploy but you can register your own configuration formats that plaster will find instead.
