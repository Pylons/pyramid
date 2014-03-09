.. _paste_chapter:

PasteDeploy Configuration Files
===============================

Packages generated via a :term:`scaffold` make use of a system created by Ian
Bicking named :term:`PasteDeploy`.  PasteDeploy defines a way to declare
:term:`WSGI` application configuration in an ``.ini`` file.

Pyramid uses this configuration file format in input to its :term:`WSGI`
server runner ``pserve``, as well as other commands such as ``pviews``,
``pshell``, ``proutes``, and ``ptweens``.

PasteDeploy is not a particularly integral part of Pyramid.  It's possible to
create a Pyramid application which does not use PasteDeploy at all.  We show
a Pyramid application that doesn't use PasteDeploy in
:ref:`firstapp_chapter`.  However, all Pyramid scaffolds render PasteDeploy
configuration files, to provide new developers with a standardized way of
setting deployment values, and to provide new users with a standardized way
of starting, stopping, and debugging an application.

This chapter is not a replacement for documentation about PasteDeploy; it
only contextualizes the use of PasteDeploy within Pyramid.  For detailed
documentation, see http://pythonpaste.org/deploy/.

PasteDeploy
-----------

:term:`PasteDeploy` is the system that Pyramid uses to allow
:term:`deployment settings` to be spelled using an ``.ini`` configuration
file format.  It also allows the ``pserve`` command to work.  Its
configuration format provides a convenient place to define application
:term:`deployment settings` and WSGI server settings, and its server runner
allows you to stop and start a Pyramid application easily.

.. _pastedeploy_entry_points:

Entry Points and PasteDeploy ``.ini`` Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the :ref:`project_narr` chapter, we breezed over the meaning of a
configuration line in the ``deployment.ini`` file.  This was the ``use =
egg:MyProject`` line in the ``[app:main]`` section.  We breezed over it
because it's pretty confusing and "too much information" for an introduction
to the system.  We'll try to give it a bit of attention here.  Let's see the
config file again:

.. literalinclude:: MyProject/development.ini
   :language: ini
   :linenos:

The line in ``[app:main]`` above that says ``use = egg:MyProject`` is
actually shorthand for a longer spelling: ``use = egg:MyProject#main``.  The
``#main`` part is omitted for brevity, as ``#main`` is a default defined by
PasteDeploy.  ``egg:MyProject#main`` is a string which has meaning to
PasteDeploy.  It points at a :term:`setuptools` :term:`entry point` named
``main`` defined in the ``MyProject`` project.

Take a look at the generated ``setup.py`` file for this project.

.. literalinclude:: MyProject/setup.py
   :language: python
   :linenos:

Note that ``entry_points`` is assigned a string which
looks a lot like an ``.ini`` file.  This string representation of an ``.ini``
file has a section named ``[paste.app_factory]``.  Within this section, there
is a key named ``main`` (the entry point name) which has a value
``myproject:main``.  The *key* ``main`` is what our ``egg:MyProject#main``
value of the ``use`` section in our config file is pointing at, although it
is actually shortened to ``egg:MyProject`` there.  The value represents a
:term:`dotted Python name` path, which refers to a callable in our
``myproject`` package's ``__init__.py`` module.

The ``egg:`` prefix in ``egg:MyProject`` indicates that this is an entry
point *URI* specifier, where the "scheme" is "egg".  An "egg" is created when
you run ``setup.py install`` or ``setup.py develop`` within your project.

In English, this entry point can thus be referred to as a "PasteDeploy
application factory in the ``MyProject`` project which has the entry point
named ``main`` where the entry point refers to a ``main`` function in the
``mypackage`` module".  Indeed, if you open up the ``__init__.py`` module
generated within any scaffold-generated package, you'll see a ``main``
function.  This is the function called by :term:`PasteDeploy` when the
``pserve`` command is invoked against our application.  It accepts a global
configuration object and *returns* an instance of our application.

.. _defaults_section_of_pastedeploy_file:

``[DEFAULT]`` Section of a PasteDeploy ``.ini`` File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add a ``[DEFAULT]`` section to your PasteDeploy ``.ini`` file.  Such
a section should consists of global parameters that are shared by all the
applications, servers and :term:`middleware` defined within the configuration
file.  The values in a ``[DEFAULT]`` section will be passed to your
application's ``main`` function as ``global_config`` (see the reference to
the ``main`` function in :ref:`init_py`).


