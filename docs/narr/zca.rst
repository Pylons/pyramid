.. index::
   single: ZCA
   single: Zope Component Architecture
   single: zope.component
   single: application registry
   single: getSiteManager
   single: getUtility

.. _zca_chapter:

Using the Zope Component Architecture in :mod:`repoze.bfg`
==========================================================

Under the hood, :mod:`repoze.bfg` uses a :term:`Zope Component
Architecture` component registry as its :term:`application registry`.
The Zope Component Architecture is referred to colloquially as the
"ZCA."

The ``zope.component`` API used to access data in a traditional Zope
application can be opaque.  For example, here is a typical "unnamed
utility" lookup using the :func:`zope.component.getUtility` global API
as it might appear in a traditional Zope application:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import ISettings
   from zope.component import getUtility
   settings = getUtility(ISettings)

After this code runs, ``settings`` will be a Python dictionary.  But
it's unlikely that any "civilian" will be able to figure this out just
by reading the code casually.  When the ``zope.component.getUtility``
API is used by a developer, the conceptual load on a casual reader of
code is high.

While the ZCA is an excellent tool with which to build a *framework*
such as :mod:`repoze.bfg`, it is not always the best tool with which
to build an *application* due to the opacity of the ``zope.component``
APIs.  Accordingly, :mod:`repoze.bfg` tends to hide the the presence
of the ZCA from application developers.  You needn't understand the
ZCA to create a :mod:`repoze.bfg` application; its use is effectively
only a framework implementation detail.

However, developers who are already used to writing :term:`Zope`
applications often still wish to use the ZCA while building a
:mod:`repoze.bfg` application; :mod:`repoze.bfg` makes this possible.

.. index::
   single: get_current_registry
   single: getUtility
   single: getSiteManager
   single: ZCA global API

Using the ZCA Global API in a :mod:`repoze.bfg` Application
-----------------------------------------------------------

:term:`Zope` uses a single ZCA registry -- the "global" ZCA registry
-- for all Zope applications run in the same Python process,
effectively making it impossible to run more than one Zope application
in a single process.

However, for ease of deployment, it's often useful to be able to run
more than a single application per process.  For example, use of a
:term:`Paste` "composite" allows you to run separate individual WSGI
applications in the same process, each answering requests for some URL
prefix.  This makes it possible to run, for example, a TurboGears
application at ``/turbogears`` and a BFG application at ``/bfg``, both
served up using the same :term:`WSGI` server within a single Python
process.

Most production Zope applications are relatively large, making it
impractical due to memory constraints to run more than one Zope
application per Python process.  However, a :mod:`repoze.bfg`
application may be very small and consume very little memory, so it's
a reasonable goal to be able to run more than one BFG application per
process.

In order to make it possible to run more than one :mod:`repoze.bfg`
application in a single process, :mod:`repoze.bfg` defaults to using a
separate ZCA registry *per application*.

While this services a reasonable goal, it causes some issues when
trying to use patterns which you might use to build a typical
:term:`Zope` application to build a :mod:`repoze.bfg` application.
Without special help, ZCA "global" APIs such as
``zope.component.getUtility`` and ``zope.component.getSiteManager``
will use the ZCA "global" registry.  Therefore, these APIs
will appear to fail when used in a :mod:`repoze.bfg` application,
because they'll be consulting the ZCA global registry rather than the
component registry associated with your :mod:`repoze.bfg` application.

There are three ways to fix this: by disusing the ZCA global API
entirely, by using
:meth:`repoze.bfg.configuration.Configurator.hook_zca` or by passing
the ZCA global registry to the :term:`Configurator` constructor at
startup time.  We'll describe all three methods in this section.

.. index::
   single: request.registry

.. _disusing_the_global_zca_api:

Disusing the Global ZCA API
+++++++++++++++++++++++++++

ZCA "global" API functions such as ``zope.component.getSiteManager``,
``zope.component.getUtility``, ``zope.component.getAdapter``, and
``zope.component.getMultiAdapter`` aren't strictly necessary.  Every
component registry has a method API that offers the same
functionality; it can be used instead.  For example, presuming the
``registry`` value below is a Zope Component Architecture component
registry, the following bit of code is equivalent to
``zope.component.getUtility(IFoo)``:

.. code-block:: python

   registry.getUtility(IFoo)

The full method API is documented in the ``zope.component`` package,
but it largely mirrors the "global" API almost exactly.

If you are willing to disuse the "global" ZCA APIs and use the method
interface of a registry instead, you need only know how to obtain the
:mod:`repoze.bfg` component registry.

There are two ways of doing so:

- use the :func:`repoze.bfg.threadlocal.get_current_registry`
  function within :mod:`repoze.bfg` view or model code.  This will
  always return the "current" :mod:`repoze.bfg` application registry.

- use the attribute of the :term:`request` object named ``registry``
  in your :mod:`repoze.bfg` view code, eg. ``request.registry``.  This
  is the ZCA component registry related to the running
  :mod:`repoze.bfg` application.

See :ref:`threadlocals_chapter` for more information about
:func:`repoze.bfg.threadlocal.get_current_registry`.

.. index::
   single: hook_zca (configurator method)

.. _hook_zca:

Enabling the ZCA Global API by Using ``hook_zca``
+++++++++++++++++++++++++++++++++++++++++++++++++

Consider the following bit of idiomatic :mod:`repoze.bfg` startup code:

.. code-block:: python
   :linenos:

   from zope.component import getGlobalSiteManager
   from repoze.bfg.configuration import Configurator

   def app(global_settings, **settings):
       config = Configurator(settings=settings)
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       return config.make_wsgi_app()

When the ``app`` function above is run, a :term:`Configurator` is
constructed.  When the configurator is created, it creates a *new*
:term:`application registry` (a ZCA component registry).  A new
registry is constructed whenever the ``registry`` argument is omitted
when a :term:`Configurator` constructor is called, or when a
``registry`` argument with a value of ``None`` is passed to a
:term:`Configurator` constructor.

During a request, the application registry created by the Configurator
is "made current".  This means calls to
:func:`repoze.bfg.threadlocal.get_current_registry` in the thread
handling the request will return the component registry associated
with the application.

As a result, application developers can use ``get_current_registry``
to get the registry and thus get access to utilities and such, as per
:ref:`disusing_the_global_zca_api`.  But they still cannot use the
global ZCA API.  Without special treatment, the ZCA global APIs will
always return the global ZCA registry (the one in
``zope.component.globalregistry.base``).

To "fix" this and make the ZCA global APIs use the "current" BFG
registry, you need to call
:meth:`repoze.bfg.configuration.Configurator.hook_zca` within your
setup code.  For example:

.. code-block:: python
   :linenos:

   from zope.component import getGlobalSiteManager
   from repoze.bfg.configuration import Configurator

   def app(global_settings, **settings):
       config = Configurator(settings=settings)
       config.hook_zca()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       return config.make_wsgi_app()

We've added a line to our original startup code, line number 6, which
calls ``config.hook_zca()``.  The effect of this line under the hood
is that an analogue of the following code is executed:

.. code-block:: python
   :linenos:

   from zope.component import getSiteManager
   from repoze.bfg.threadlocal import get_current_registry
   getSiteManager.sethook(get_current_registry)

This causes the ZCA global API to start using the :mod:`repoze.bfg`
application registry in threads which are running a :mod:`repoze.bfg`
request.

Calling ``hook_zca`` is usually sufficient to "fix" the problem of
being able to use the global ZCA API within a :mod:`repoze.bfg`
application.  However, it also means that a Zope application that is
running in the same process may start using the :mod:`repoze.bfg`
global registry instead of the Zope global registry, effectively
inverting the original problem.  In such a case, follow the steps in
the next section, :ref:`using_the_zca_global_registry`.

.. index::
   single: get_current_registry
   single: getGlobalSiteManager
   single: ZCA global registry

.. _using_the_zca_global_registry:

Enabling the ZCA Global API by Using The ZCA Global Registry
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

You can tell your :mod:`repoze.bfg` application to use the ZCA global
registry at startup time instead of constructing a new one:

.. code-block:: python
   :linenos:

   from zope.component import getGlobalSiteManager
   from repoze.bfg.configuration import Configurator

   def app(global_settings, **settings):
       globalreg = getGlobalSiteManager()
       config = Configurator(registry=globalreg)
       config.setup_registry(settings=settings)
       config.hook_zca()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       return config.make_wsgi_app()

Lines 5, 6, and 7 above are the interesting ones.  Line 5 retrieves
the global ZCA component registry.  Line 6 creates a
:term:`Configurator`, passing the global ZCA registry into its
constructor as the ``registry`` argument.  Line 7 "sets up" the global
registry with BFG-specific registrations; this is code that is
normally executed when a registry is constructed rather than created,
but we must call it "by hand" when we pass an explicit registry.

At this point, :mod:`repoze.bfg` will use the ZCA global registry
rather than creating a new application-specific registry; since by
default the ZCA global API will use this registry, things will work as
you might expect a Zope app to when you use the global ZCA API.

.. index::
   single: Zope ZCML directives
   single: getGlobalSiteManager
   single: getSiteManager

Using Broken ZCML Directives
----------------------------

Some :term:`Zope` and third-party :term:`ZCML` directives use the
``zope.component.getGlobalSiteManager`` API to get "the registry" when
they should actually be calling ``zope.component.getSiteManager``.

``zope.component.getSiteManager`` can be overridden by
:mod:`repoze.bfg` via
:meth:`repoze.bfg.configuration.Configurator.hook_zca`, while
``zope.component.getGlobalSiteManager`` cannot.  Directives that use
``zope.component.getGlobalSiteManager`` are effectively broken; no
ZCML directive should be using this function to find a registry to
populate.

You cannot use ZCML directives which use
``zope.component.getGlobalSiteManager`` within a :mod:`repoze.bfg`
application without passing the ZCA global registry to the
:term:`Configurator` constructor at application startup, as per
:ref:`using_the_zca_global_registry`.

One alternative exists: fix the ZCML directive to use
``getSiteManager`` rather than ``getGlobalSiteManager``.  If a
directive disuses ``getGlobalSiteManager``, the ``hook_zca`` method of
using a component registry as documented in :ref:`hook_zca` will begin
to work, allowing you to make use of the ZCML directive without
also using the ZCA global registry.

