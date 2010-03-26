.. _extending_chapter:

Extending An Existing :mod:`repoze.bfg` Application
===================================================

If the developer of a :mod:`repoze.bfg` application has obeyed certain
constraints while building that application, a third party should be
able to change its behavior without needing to modify its source code.
The behavior of a :mod:`repoze.bfg` application that obeys certain
constraints can be *overridden* or *extended* without modification.

.. index::
   single: extensible application

Rules for Building An Extensible Application
--------------------------------------------

There's only one rule you need to obey if you want to build a
maximally extensible :mod:`repoze.bfg` application: you should not use
any :term:`configuration decoration` or :term:`imperative
configuration`. This means the application developer should avoid
relying on :term:`configuration decoration` meant to be detected via
a :term:`scan`, and you mustn't configure your :mod:`repoze.bfg`
application *imperatively* by using any code which configures the
application through methods of the :term:`Configurator` (except for
the :meth:`repoze.bfg.configuration.Configurator.load_zcml` method).

Instead, you must always use :term:`ZCML` for the equivalent
purposes. :term:`ZCML` declarations that belong to an application can
be "overridden" by integrators as necessary, but decorators and
imperative code which perform the same tasks cannot.  Use only
:term:`ZCML` to configure your application if you'd like it to be
extensible.

Fundamental Plugpoints
~~~~~~~~~~~~~~~~~~~~~~

The fundamental "plug points" of an application developed using
:mod:`repoze.bfg` are *routes*, *views*, and *resources*.  Routes are
declarations made using the ZCML ``<route>`` directive.  Views are
declarations made using the ZCML ``<view>`` directive (or the
``@bfg_view`` decorator).  Resources are files that are accessed by
repoze bfg using the :term:`pkg_resources` API such as static files
and templates.

.. index::
   single: ZCML granularity

ZCML Granularity
~~~~~~~~~~~~~~~~

It's extremely helpful to third party application "extenders" (aka
"integrators") if the :term:`ZCML` that composes the configuration for
an application is broken up into separate files which do very specific
things.  These more specific ZCML files can be reintegrated within the
application's main ``configure.zcml`` via ``<include
file="otherfile.zcml"/>`` declarations.  When ZCML files contain sets
of specific declarations, an integrator can avoid including any ZCML
he does not want by including only ZCML files which contain the
declarations he needs.  He is not forced to "accept everything" or
"use nothing".

For example, it's often useful to put all ``<route>`` declarations in
a separate ZCML file, as ``<route>`` statements have a relative
ordering that is extremely important to the application: if an
extender wants to add a route to the "middle" of the routing table, he
will always need to disuse all the routes and cut and paste the
routing configuration into his own application.  It's useful for the
extender to be able to disuse just a *single* ZCML file in this case,
accepting the remainder of the configuration from other :term:`ZCML`
files in the original application.

Granularizing ZCML is not strictly required.  An extender can always
disuse *all* your ZCML, choosing instead to copy and paste it into his
own package, if necessary.  However, doing so is considerate, and
allows for the best reusability.

.. index::
   single: extending an existing application

Extending an Existing Application
---------------------------------

The steps for extending an existing application depend largely on
whether the application does or does not use configuration decorators
and/or imperative code.

Extending an Application Which Possesses Configuration Decorators Or Which Does Configuration Imperatively
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you've inherited a :mod:`repoze.bfg` application which uses
:class:`repoze.bfg.view.bfg_view` decorators or which performs
configuration imperatively, one of two things may be true:

- If you just want to *extend* the application, you can write
  additional ZCML that registers more views or routes, loading any
  existing ZCML and continuing to use any existing imperative
  configuration done by the original application.

- If you want to *override* configuration in the application, you
  *may* need to change the source code of the original application.

  If the only source of trouble is the existence of
  :class:`repoze.bfg.view.bfg_view` decorators, you can just prevent a
  :term:`scan` from happening (by omitting the ``<scan>`` declaration
  from ZCML or omitting any call to the
  :meth:`repoze.bfg.configuration.Configurator.scan` method).  This
  will cause the decorators to do nothing.  At this point, you will
  need to convert all the configuration done in decorators into
  equivalent :term:`ZCML` and add that ZCML to a separate Python
  package as described in :ref:`extending_the_application`.

  If the source of trouble is configuration done imperatively in a
  function called during application startup, you'll need to change
  the code: convert imperative configuration statements into
  equivalent :term:`ZCML` declarations.

Once this is done, you should be able to extend or override the
application like any other (see :ref:`extending_the_application`).

.. _extending_the_application:

Extending an Application Which Does Not Possess Configuration Decorators or Imperative Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To extend or override the behavior of an existing application, you
will need to write some :term:`ZCML`, and perhaps some implementations
of the types of things you'd like to override (such as views), which
are referred to within that ZCML.

The general pattern for extending an existing application looks
something like this:

- Create a new Python package.  The easiest way to do this is to
  create a new :mod:`repoze.bfg` application using the "paster"
  template mechanism.  See :ref:`creating_a_project` for more
  information.

- Install the new package into the same Python environment as the
  original application (e.g. ``python setup.py develop`` or ``python
  setup.py install``).

- Change the ``configure.zcml`` in the new package to include the
  original :mod:`repoze.bfg` application's ``configure.zcml`` via an
  include statement, e.g.  ``<include package="theoriginalapp"/>``.
  Alternately, if the original application writer anticipated
  overriding some things and not others, instead of including the
  "main" ``configure.zcml`` of the original application, include only
  specific ZCML files from the original application using the ``file``
  attribute of the ``<include>`` statement, e.g. ``<include
  package="theoriginalapp" file="views.zcml"/>``.

- On a line in the new package's ``configure.zcml`` file that falls
  after (XML-ordering-wise) all the ``include`` statements of the original
  package ZCML, put an ``includeOverrides`` statement which identifies
  *another* ZCML file within the new package (for example
  ``<includeOverrides file="overrides.zcml"/>``.

- Create an ``overrides.zcml`` file within the new package.  The
  statements in the ``overrides.zcml`` file will override any ZCML
  statements made within the original application (such as view
  declarations).

- Create Python files containing views and other overridden elements,
  such as templates and static resources as necessary, and wire these
  up using ZCML registrations within the ``overrides.zcml`` file.
  These registrations may extend or override the original view
  registrations.  See :ref:`overriding_views`,
  :ref:`overriding_routes` and :ref:`overriding_resources`.

- Change the Paste ``.ini`` file that starts up the original
  application.  Add a ``configure_zcml`` key within the application's
  section in the file which points at your *new* package's
  ``configure.zcml`` file.  See :ref:`environment_chapter` for more
  information about this setting.

.. index::
   pair: overriding; views

.. _overriding_views:

Overriding Views
~~~~~~~~~~~~~~~~~

The ZCML ``<view>`` declarations you make which *override* application
behavior will usually have the same ``context`` and ``name`` (and
:term:`predicate` attributes, if used) as the original.  These
``<view>`` declarations will point at "new" view code.  The new view
code itself will usually be cut-n-paste copies of view callables from
the original application with slight tweaks.  For example:

.. code-block:: xml
   :linenos:

    <view context="theoriginalapplication.models.SomeModel"
          name="theview"
          view=".views.a_view_that_does_something_slightly_different"
     />

A similar pattern can be used to *extend* the application with
``<view>`` declarations.  Just register a new view against some
existing model type and make sure the URLs it implies are available on
some other page rendering.

.. index::
   pair: overriding; routes

.. _overriding_routes:

Overriding Routes
~~~~~~~~~~~~~~~~~

Route setup is currently typically performed in a sequence of ordered
ZCML ``<route>`` declarations.  Because these declarations are ordered
relative to each other, and because this ordering is typically
important, you should retain the relative ordering of these
declarations when performing an override.  Typically, this means
*copying* all the ``<route>`` declarations into an external ZCML file
and changing them as necessary.  Then disinclude any ZCML from the
original application which contains the original declarations.

.. index::
   pair: overriding; resources

.. _overriding_resources:

Overriding Resources
~~~~~~~~~~~~~~~~~~~~

"Resource" files are static files on the filesystem that are
accessible within a Python *package*.  An entire chapter is devoted to
resources: :ref:`resources_chapter`.  Within this chapter is a section
named :ref:`overriding_resources_section`.  This section of that
chapter describes in detail how to override package resources with
other resources by using :term:`ZCML` ``<resource>`` declarations.  Add
such ``<resource>`` declarations to your override package's
``configure.zcml`` to perform overrides.

.. index::
   single: ZCML inclusion

Dealing With ZCML Inclusions
----------------------------

Sometimes it's possible to include only certain ZCML files from an
application that contain only the registrations you really need,
omitting others. But sometimes it's not.  For brute force purposes,
when you're getting ``view`` or ``route`` registrations that you don't
actually want in your overridden application, it's always appropriate
to just *not include* any ZCML file from the overridden application.
Instead, just cut and paste the entire contents of the
``configure.zcml`` (and any ZCML file included by the overridden
application's ``configure.zcml``) into your own package and omit the
``<include package=""/>`` ZCML declaration in the overriding package's
``configure.zcml``.


