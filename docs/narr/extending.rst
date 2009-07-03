.. _extending_chapter:

Extending An Existing :mod:`repoze.bfg` Application
===================================================

If the developer of a :mod:`repoze.bfg` has obeyed certain constraints
while building the application, a third party should be able to change
the behavior of that application without touching the actual source
code that makes up the application.  The behavior of a
:mod:`repoze.bfg` application that obeys these constraints can be
*extended* or *changed* without modification.

Rules for Building An Extensible Application
--------------------------------------------

There's only one rule you need to obey if you want to build an
application that is extensible using :mod:`repoze.bfg`: you must not
use the ``@bfg_view`` decorator (or any other decorator meant to be
detected via the ZCML ``<scan>`` directive) to associate a view with a
context.  Instead, you must use :term:`ZCML` for this
purpose. :term:`ZCML` statements that belong to an application can be
"overridden" by integrators as necessary, but decorators cannot.

It's also often helpful for third party application "extenders" (aka
"integrators") if you break your ZCML into separate files which do
very specific things, and include them in the application's main
``configure.zcml`` via ``<include file="otherfile.zcml"/>``
statements.  This way, an integrator can avoid including any ZCML he
does not want by including only the ZCML files which contain the
registrations he needs.

Extending an Existing Application
---------------------------------

If you've inherited a :mod:`repoze.bfg` application that you'd like to
extend which uses ``@bfg_view`` decorators, you'll unfortunately need
to change the source code of the original application, moving the view
declarations out of the decorators and into :term:`ZCML`.  Once this
is done, you should be able to extend or modify the application like
any other.

To extend or change the behavior of an existing application, you will
need to write some :term:`ZCML`, and perhaps some implementations of
the types of things you'd like to override (such as views), which are
referred to within that ZCML.

The general pattern for extending an application looks something like this:

- Create a new Python package.  The easiest way to do this is to
  create a new :mod:`repoze.bfg` application using the "paster"
  template mechanism.  See :ref:`creating_a_project` for more
  information.

- Install the new package into the same Python environment as the
  original application (e.g. ``python setup.py develop`` or ``python
  setup.py install``).

- Change the ``configure.zcml`` in the new package to include the
  original :mod:`repoze.bfg` application's ``configure.zcml`` via an
  include statement, e.g.  ``<include
  package="theoriginalapplication"/>``.

- On a line in the new package's ``configure.zcml`` file that falls
  after (XML-ordering-wise) the ``include`` of the original package,
  put an ``includeOverride`` statement that includes another ZCML file
  within the new package (for example ``<includeOverride
  file="overrides.zcml"/>``.

- Create an ``overrides.zcml`` file within the new package.  The
  statements in the ``overrides.zcml`` file will override any ZCML
  statements made within the original application (such as views).

- Create Python files containing views (and other overridden elements,
  such as templates) as necessary, and wire these up, either extending
  or overriding the original view registrations from the base
  application within the ``overrides.zcml`` file.  The ZCML ``<view>``
  statements you make which *modify* behavior will usually have the
  same ``for`` and ``name`` (and ``request_type`` if used) as the
  original, and will be in a form like::

    <view for="theoriginalapplication.models.SomeModel"
          name="theview"
          view=".views.a_view_that_does_something_slightly_different"
     />

  Views which modify the behavior of an application will usually be
  cutnpaste jobs from the original application with slight tweaks.

  A similar pattern can be used to extend the application.  Just
  register a new view against some existing model type.

- Change the Paste ``.ini`` file that starts up the original
  application.  Add a ``configure_zcml`` statement within the
  application's section in the file which points at your *new*
  package's ``configure.zcml`` file.  See :ref:`environment_chapter`
  for more information about this setting.

Dealing With ZCML Inclusions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it's possible to include only certain ZCML files from an
application that contain only the registrations you really need,
omitting others. But sometimes it's not.  For brute force purposes,
when you're getting ``view`` or ``route`` registrations that you don't
actually want in your overridden application, it's always appropriate
to just *not include* any ZCML file from the overridden application.
Instead, just cut and paste the entire contents of the
``configure.zcml`` (and any ZCML file included by the overridden
application's ``configure.zcml``) into your own package and omit the
``<include package=""/>`` ZCML statement in the overriding package's
``configure.zcml``.


