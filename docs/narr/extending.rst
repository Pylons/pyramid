.. _extending_chapter:

Extending an Existing :app:`Pyramid` Application
================================================

If a :app:`Pyramid` developer has obeyed certain constraints while building an
application, a third party should be able to change the application's behavior
without needing to modify its source code.  The behavior of a :app:`Pyramid`
application that obeys certain constraints can be *overridden* or *extended*
without modification.

We'll define some jargon here for the benefit of identifying the parties
involved in such an effort.

Developer
  The original application developer.

Integrator
  Another developer who wishes to reuse the application written by the original
  application developer in an unanticipated context.  They may also wish to
  modify the original application without changing the original application's
  source code.

The Difference Between "Extensible" and "Pluggable" Applications
----------------------------------------------------------------

Other web frameworks, such as :term:`Django`, advertise that they allow
developers to create "pluggable applications".  They claim that if you create
an application in a certain way, it will be integratable in a sensible,
structured way into another arbitrarily-written application or project created
by a third-party developer.

:app:`Pyramid`, as a platform, does not claim to provide such a feature.  The
platform provides no guarantee that you can create an application and package
it up such that an arbitrary integrator can use it as a subcomponent in a
larger Pyramid application or project.  Pyramid does not mandate the
constraints necessary for such a pattern to work satisfactorily.  Because
Pyramid is not very "opinionated", developers are able to use wildly different
patterns and technologies to build an application.  A given Pyramid application
may happen to be reusable by a particular third party integrator because the
integrator and the original developer may share similar base technology choices
(such as the use of a particular relational database or ORM).  But the same
application may not be reusable by a different developer, because they have
made different technology choices which are incompatible with the original
developer's.

As a result, the concept of a "pluggable application" is left to layers built
above Pyramid, such as a "CMS" layer or "application server" layer.  Such
layers are apt to provide the necessary "opinions" (such as mandating a storage
layer, a templating system, and a structured, well-documented pattern of
registering that certain URLs map to certain bits of code) which makes the
concept of a "pluggable application" possible.  "Pluggable applications", thus,
should not plug into Pyramid itself but should instead plug into a system
written atop Pyramid.

Although it does not provide for "pluggable applications", Pyramid *does*
provide a rich set of mechanisms which allows for the extension of a single
existing application.  Such features can be used by frameworks built using
Pyramid as a base.  All Pyramid applications may not be *pluggable*, but all
Pyramid applications are *extensible*.

.. index::
   single: extensible application

.. _building_an_extensible_app:

Rules for Building an Extensible Application
--------------------------------------------

There is only one rule you need to obey if you want to build a maximally
extensible :app:`Pyramid` application: as a developer, you should factor any
overridable :term:`imperative configuration` you've created into functions
which can be used via :meth:`pyramid.config.Configurator.include`, rather than
inlined as calls to methods of a :term:`Configurator` within the ``main``
function in your application's ``__init__.py``.  For example, rather than:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   if __name__ == '__main__':
       config = Configurator()
       config.add_view('myapp.views.view1', name='view1')
       config.add_view('myapp.views.view2', name='view2')

You should move the calls to ``add_view`` outside of the (non-reusable) ``if
__name__ == '__main__'`` block, and into a reusable function:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   if __name__ == '__main__':
       config = Configurator()
       config.include(add_views)

   def add_views(config):
       config.add_view('myapp.views.view1', name='view1')
       config.add_view('myapp.views.view2', name='view2')

Doing this allows an integrator to maximally reuse the configuration statements
that relate to your application by allowing them to selectively include or
exclude the configuration functions you've created from an "override package".

Alternatively you can use :term:`ZCML` for the purpose of making configuration
extensible and overridable. :term:`ZCML` declarations that belong to an
application can be overridden and extended by integrators as necessary in a
similar fashion.  If you use only :term:`ZCML` to configure your application,
it will automatically be maximally extensible without any manual effort.  See
:term:`pyramid_zcml` for information about using ZCML.

Fundamental Plugpoints
~~~~~~~~~~~~~~~~~~~~~~

The fundamental "plug points" of an application developed using :app:`Pyramid`
are *routes*, *views*, and *assets*.  Routes are declarations made using the
:meth:`pyramid.config.Configurator.add_route` method.  Views are declarations
made using the :meth:`pyramid.config.Configurator.add_view` method.  Assets are
files that are accessed by :app:`Pyramid` using the :term:`pkg_resources` API
such as static files and templates via a :term:`asset specification`.  Other
directives and configurator methods also deal in routes, views, and assets.
For example, the ``add_handler`` directive of the ``pyramid_handlers`` package
adds a single route and some number of views.

.. index::
   single: extending an existing application

Extending an Existing Application
---------------------------------

The steps for extending an existing application depend largely on whether the
application does or does not use configuration decorators or imperative code.

If the Application Has Configuration Decorations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You've inherited a :app:`Pyramid` application which you'd like to extend or
override that uses :class:`pyramid.view.view_config` decorators or other
:term:`configuration decoration` decorators.

If you just want to *extend* the application, you can run a :term:`scan`
against the application's package, then add additional configuration that
registers more views or routes.

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config.scan('someotherpackage')
       config.add_view('mypackage.views.myview', name='myview')

If you want to *override* configuration in the application, you *may* need to
run :meth:`pyramid.config.Configurator.commit` after performing the scan of the
original package, then add additional configuration that registers more views
or routes which perform overrides.

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config.scan('someotherpackage')
       config.commit()
       config.add_view('mypackage.views.myview', name='myview')

Once this is done, you should be able to extend or override the application
like any other (see :ref:`extending_the_application`).

You can alternatively just prevent a :term:`scan` from happening by omitting
any call to the :meth:`pyramid.config.Configurator.scan` method.  This will
cause the decorators attached to objects in the target application to do
nothing.  At this point, you will need to convert all the configuration done in
decorators into equivalent imperative configuration or ZCML, and add that
configuration or ZCML to a separate Python package as described in
:ref:`extending_the_application`.

.. _extending_the_application:

Extending the Application
~~~~~~~~~~~~~~~~~~~~~~~~~

To extend or override the behavior of an existing application, you will need to
create a new package which includes the configuration of the old package, and
you'll perhaps need to create implementations of the types of things you'd like
to override (such as views), to which they are referred within the original
package.

The general pattern for extending an existing application looks something like
this:

- Create a new Python package.  The easiest way to do this is to create a new
  :app:`Pyramid` application using a :term:`cookiecutter`.  See
  :ref:`creating_a_project` for more information.

- In the new package, create Python files containing views and other overridden
  elements, such as templates and static assets as necessary.

- Install the new package into the same Python environment as the original
  application (e.g., ``$VENV/bin/pip install -e .`` or ``$VENV/bin/pip install
  .``).

- Change the ``main`` function in the new package's ``__init__.py`` to include
  the original :app:`Pyramid` application's configuration functions via
  :meth:`pyramid.config.Configurator.include` statements or a :term:`scan`.

- Wire the new views and assets created in the new package up using imperative
  registrations within the ``main`` function of the ``__init__.py`` file of the
  new application.  This wiring should happen *after* including the
  configuration functions of the old application.  These registrations will
  extend or override any registrations performed by the original application.
  See :ref:`overriding_views`, :ref:`overriding_routes`, and
  :ref:`overriding_resources`.

.. index::
   pair: overriding; views

.. _overriding_views:

Overriding Views
~~~~~~~~~~~~~~~~

The :term:`view configuration` declarations that you make which *override*
application behavior will usually have the same :term:`view predicate`
attributes as the original that you wish to override.  These ``<view>``
declarations will point at "new" view code in the override package that you've
created.  The new view code itself will usually be copy-and-paste copies of
view callables from the original application with slight tweaks.

For example, if the original application has the following ``configure_views``
configuration method:

.. code-block:: python
    :linenos:

    def configure_views(config):
        config.add_view('theoriginalapp.views.theview', name='theview')

You can override the first view configuration statement made by
``configure_views`` within the override package, after loading the original
configuration function:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from originalapp import configure_views

   if __name == '__main__':
       config = Configurator()
       config.include(configure_views)
       config.add_view('theoverrideapp.views.theview', name='theview')

In this case, the ``theoriginalapp.views.theview`` view will never be executed.
Instead, a new view, ``theoverrideapp.views.theview`` will be executed when
request circumstances dictate.

A similar pattern can be used to *extend* the application with ``add_view``
declarations.  Just register a new view against some other set of predicates to
make sure the URLs it implies are available on some other page rendering.

.. index::
   pair: overriding; routes

.. _overriding_routes:

Overriding Routes
~~~~~~~~~~~~~~~~~

Route setup is currently typically performed in a sequence of ordered calls to
:meth:`~pyramid.config.Configurator.add_route`.  Because these calls are
ordered relative to each other, and because this ordering is typically
important, you should retain their relative ordering when performing an
override.  Typically this means *copying* all the ``add_route`` statements into
the override package's file and changing them as necessary.  Then exclude any
``add_route`` statements from the original application.

.. index::
   pair: overriding; assets

.. _overriding_resources:

Overriding Assets
~~~~~~~~~~~~~~~~~

Assets are files on the filesystem that are accessible within a Python
*package*.  An entire chapter is devoted to assets: :ref:`assets_chapter`.
Within this chapter is a section named :ref:`overriding_assets_section`. This
section of that chapter describes in detail how to override package assets with
other assets by using the :meth:`pyramid.config.Configurator.override_asset`
method.  Add such ``override_asset`` calls to your override package's
``__init__.py`` to perform overrides.
