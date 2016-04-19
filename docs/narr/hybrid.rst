.. _hybrid_chapter:

Combining Traversal and URL Dispatch
====================================

When you write most :app:`Pyramid` applications, you'll be using one or the
other of two available :term:`resource location` subsystems: traversal or URL
dispatch.  However, to solve a limited set of problems, it's useful to use
*both* traversal and URL dispatch together within the same application.
:app:`Pyramid` makes this possible via *hybrid* applications.

.. warning::

   Reasoning about the behavior of a "hybrid" URL dispatch + traversal
   application can be challenging.  To successfully reason about using URL
   dispatch and traversal together, you need to understand URL pattern
   matching, root factories, and the :term:`traversal` algorithm, and the
   potential interactions between them.  Therefore, we don't recommend creating
   an application that relies on hybrid behavior unless you must.

A Review of Non-Hybrid Applications
-----------------------------------

When used according to the tutorials in its documentation, :app:`Pyramid` is a
"dual-mode" framework: the tutorials explain how to create an application in
terms of using either :term:`URL dispatch` *or* :term:`traversal`.  This
chapter details how you might combine these two dispatch mechanisms, but we'll
review how they work in isolation before trying to combine them.

URL Dispatch Only
~~~~~~~~~~~~~~~~~

An application that uses :term:`URL dispatch` exclusively to map URLs to code
will often have statements like this within its application startup
configuration:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

   config.add_route('foobar', '{foo}/{bar}')
   config.add_route('bazbuz', '{baz}/{buz}')

   config.add_view('myproject.views.foobar', route_name='foobar')
   config.add_view('myproject.views.bazbuz', route_name='bazbuz')

Each :term:`route` corresponds to one or more view callables.  Each view
callable is associated with a route by passing a ``route_name`` parameter that
matches its name during a call to
:meth:`~pyramid.config.Configurator.add_view`.  When a route is matched during
a request, :term:`view lookup` is used to match the request to its associated
view callable.  The presence of calls to
:meth:`~pyramid.config.Configurator.add_route` signify that an application is
using URL dispatch.

Traversal Only
~~~~~~~~~~~~~~

An application that uses only traversal will have view configuration
declarations that look like this:

.. code-block:: python
    :linenos:

    # config is an instance of pyramid.config.Configurator

    config.add_view('mypackage.views.foobar', name='foobar')
    config.add_view('mypackage.views.bazbuz', name='bazbuz')

When the above configuration is applied to an application, the
``mypackage.views.foobar`` view callable above will be called when the URL
``/foobar`` is visited.  Likewise, the view ``mypackage.views.bazbuz`` will be
called when the URL ``/bazbuz`` is visited.

Typically, an application that uses traversal exclusively won't perform any
calls to :meth:`pyramid.config.Configurator.add_route` in its startup code.

.. index::
   single: hybrid applications

Hybrid Applications
-------------------

Either traversal or URL dispatch alone can be used to create a :app:`Pyramid`
application.  However, it is also possible to combine the concepts of traversal
and URL dispatch when building an application, the result of which is a hybrid
application.  In a hybrid application, traversal is performed *after* a
particular route has matched.

A hybrid application is a lot more like a "pure" traversal-based application
than it is like a "pure" URL-dispatch based application. But unlike in a "pure"
traversal-based application, in a hybrid application :term:`traversal` is
performed during a request after a route has already matched.  This means that
the URL pattern that represents the ``pattern`` argument of a route must match
the ``PATH_INFO`` of a request, and after the route pattern has matched, most
of the "normal" rules of traversal with respect to :term:`resource location`
and :term:`view lookup` apply.

There are only four real differences between a purely traversal-based
application and a hybrid application:

- In a purely traversal-based application, no routes are defined.  In a hybrid
  application, at least one route will be defined.

- In a purely traversal-based application, the root object used is global,
  implied by the :term:`root factory` provided at startup time.  In a hybrid
  application, the :term:`root` object at which traversal begins may be varied
  on a per-route basis.

- In a purely traversal-based application, the ``PATH_INFO`` of the underlying
  :term:`WSGI` environment is used wholesale as a traversal path.  In a hybrid
  application, the traversal path is not the entire ``PATH_INFO`` string, but a
  portion of the URL determined by a matching pattern in the matched route
  configuration's pattern.

- In a purely traversal-based application, view configurations which do not
  mention a ``route_name`` argument are considered during :term:`view lookup`.
  In a hybrid application, when a route is matched, only view configurations
  which mention that route's name as a ``route_name`` are considered during
  :term:`view lookup`.

More generally, a hybrid application *is* a traversal-based application except:

- the traversal *root* is chosen based on the route configuration of the route
  that matched, instead of from the ``root_factory`` supplied during
  application startup configuration.

- the traversal *path* is chosen based on the route configuration of the route
  that matched, rather than from the ``PATH_INFO`` of a request.

- the set of views that may be chosen during :term:`view lookup` when a route
  matches are limited to those which specifically name a ``route_name`` in
  their configuration that is the same as the matched route's ``name``.

To create a hybrid mode application, use a :term:`route configuration` that
implies a particular :term:`root factory` and which also includes a ``pattern``
argument that contains a special dynamic part: either ``*traverse`` or
``*subpath``.

The Root Object for a Route Match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A hybrid application implies that traversal is performed during a request after
a route has matched.  Traversal, by definition, must always begin at a root
object.  Therefore it's important to know *which* root object will be traversed
after a route has matched.

Figuring out which :term:`root` object results from a particular route match is
straightforward.  When a route is matched:

- If the route's configuration has a ``factory`` argument which points to a
  :term:`root factory` callable, that callable will be called to generate a
  :term:`root` object.

- If the route's configuration does not have a ``factory`` argument, the
  *global* :term:`root factory` will be called to generate a :term:`root`
  object.  The global root factory is the callable implied by the
  ``root_factory`` argument passed to the :class:`~pyramid.config.Configurator`
  at application startup time.

- If a ``root_factory`` argument is not provided to the
  :class:`~pyramid.config.Configurator` at startup time, a *default* root
  factory is used.  The default root factory is used to generate a root object.

.. note::

   Root factories related to a route were explained previously within
   :ref:`route_factories`.  Both the global root factory and default root
   factory were explained previously within :ref:`the_resource_tree`.

.. index::
   pair: hybrid applications; *traverse route pattern

.. _using_traverse_in_a_route_pattern:

Using ``*traverse`` in a Route Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A hybrid application most often implies the inclusion of a route configuration
that contains the special token ``*traverse`` at the end of a route's pattern:

.. code-block:: python
   :linenos:

   config.add_route('home', '{foo}/{bar}/*traverse')

A ``*traverse`` token at the end of the pattern in a route's configuration
implies a "remainder" *capture* value.  When it is used, it will match the
remainder of the path segments of the URL.  This remainder becomes the path
used to perform traversal.

.. note::

   The ``*remainder`` route pattern syntax is explained in more detail within
   :ref:`route_pattern_syntax`.

A hybrid mode application relies more heavily on :term:`traversal` to do
:term:`resource location` and :term:`view lookup` than most examples indicate
within :ref:`urldispatch_chapter`.

Because the pattern of the above route ends with ``*traverse``, when this route
configuration is matched during a request, :app:`Pyramid` will attempt to use
:term:`traversal` against the :term:`root` object implied by the :term:`root
factory` that is implied by the route's configuration.  Since no
``root_factory`` argument is explicitly specified for this route, this will
either be the *global* root factory for the application, or the *default* root
factory.  Once :term:`traversal` has found a :term:`context` resource,
:term:`view lookup` will be invoked in almost exactly the same way it would
have been invoked in a "pure" traversal-based application.

Let's assume there is no *global* :term:`root factory` configured in this
application. The *default* :term:`root factory` cannot be traversed; it has no
useful ``__getitem__`` method.  So we'll need to associate this route
configuration with a custom root factory in order to create a useful hybrid
application.  To that end, let's imagine that we've created a root factory that
looks like so in a module named ``routes.py``:

.. code-block:: python
   :linenos:

   class Resource(object):
       def __init__(self, subobjects):
          self.subobjects = subobjects

       def __getitem__(self, name):
          return self.subobjects[name]

   root = Resource(
           {'a': Resource({'b': Resource({'c': Resource({})})})}
          )

   def root_factory(request):
       return root

Above we've defined a (bogus) resource tree that can be traversed, and a
``root_factory`` function that can be used as part of a particular route
configuration statement:

.. code-block:: python
   :linenos:

   config.add_route('home', '{foo}/{bar}/*traverse',
                    factory='mypackage.routes.root_factory')

The ``factory`` above points at the function we've defined.  It will return an
instance of the ``Resource`` class as a root object whenever this route is
matched.  Instances of the ``Resource`` class can be used for tree traversal
because they have a ``__getitem__`` method that does something nominally
useful. Since traversal uses ``__getitem__`` to walk the resources of a
resource tree, using traversal against the root resource implied by our route
statement is a reasonable thing to do.

.. note::

  We could have also used our ``root_factory`` function as the ``root_factory``
  argument of the :class:`~pyramid.config.Configurator` constructor, instead of
  associating it with a particular route inside the route's configuration.
  Every hybrid route configuration that is matched, but which does *not* name a
  ``factory`` attribute, will use the  global ``root_factory`` function to
  generate a root object.

When the route configuration named ``home`` above is matched during a request,
the matchdict generated will be based on its pattern:
``{foo}/{bar}/*traverse``.  The "capture value" implied by the ``*traverse``
element in the pattern will be used to traverse the resource tree in order to
find a context resource, starting from the root object returned from the root
factory.  In the above example, the :term:`root` object found will be the
instance named ``root`` in ``routes.py``.

If the URL that matched a route with the pattern ``{foo}/{bar}/*traverse`` is
``http://example.com/one/two/a/b/c``, the traversal path used against the root
object will be ``a/b/c``.  As a result, :app:`Pyramid` will attempt to traverse
through the edges ``'a'``, ``'b'``, and ``'c'``, beginning at the root object.

In our above example, this particular set of traversal steps will mean that the
:term:`context` resource of the view would be the ``Resource`` object we've
named ``'c'`` in our bogus resource tree, and the :term:`view name` resulting
from traversal will be the empty string.  If you need a refresher about why
this outcome is presumed, see :ref:`traversal_algorithm`.

At this point, a suitable view callable will be found and invoked using
:term:`view lookup` as described in :ref:`view_configuration`, but with a
caveat: in order for view lookup to work, we need to define a view
configuration that will match when :term:`view lookup` is invoked after a route
matches:

.. code-block:: python
   :linenos:

   config.add_route('home', '{foo}/{bar}/*traverse',
                    factory='mypackage.routes.root_factory')
   config.add_view('mypackage.views.myview', route_name='home')

Note that the above call to :meth:`~pyramid.config.Configurator.add_view`
includes a ``route_name`` argument.  View configurations that include a
``route_name`` argument are meant to associate a particular view declaration
with a route, using the route's name, in order to indicate that the view should
*only be invoked when the route matches*.

Calls to :meth:`~pyramid.config.Configurator.add_view` may pass a
``route_name`` attribute, which refers to the value of an existing route's
``name`` argument.  In the above example, the route name is ``home``, referring
to the name of the route defined above it.

The above ``mypackage.views.myview`` view callable will be invoked when the
following conditions are met:

- The route named "home" is matched.

- The :term:`view name` resulting from traversal is the empty string.

- The :term:`context` resource is any object.

It is also possible to declare alternative views that may be invoked when a
hybrid route is matched:

.. code-block:: python
   :linenos:

   config.add_route('home', '{foo}/{bar}/*traverse',
                    factory='mypackage.routes.root_factory')
   config.add_view('mypackage.views.myview', route_name='home')
   config.add_view('mypackage.views.another_view', route_name='home',
                   name='another')

The ``add_view`` call for ``mypackage.views.another_view`` above names a
different view and, more importantly, a different :term:`view name`.  The above
``mypackage.views.another_view`` view will be invoked when the following
conditions are met:

- The route named "home" is matched.

- The :term:`view name` resulting from traversal is ``another``.

- The :term:`context` resource is any object.

For instance, if the URL ``http://example.com/one/two/a/another`` is provided
to an application that uses the previously mentioned resource tree, the
``mypackage.views.another_view`` view callable will be called instead of the
``mypackage.views.myview`` view callable because the :term:`view name` will be
``another`` instead of the empty string.

More complicated matching can be composed.  All arguments to *route*
configuration statements and *view* configuration statements are supported in
hybrid applications (such as :term:`predicate` arguments).

Using the ``traverse`` Argument in a Route Definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rather than using the ``*traverse`` remainder marker in a pattern, you can use
the ``traverse`` argument to the :meth:`~pyramid.config.Configurator.add_route`
method.

When you use the ``*traverse`` remainder marker, the traversal path is limited
to being the remainder segments of a request URL when a route matches.
However, when you use the ``traverse`` argument or attribute, you have more
control over how to compose a traversal path.

Here's a use of the ``traverse`` pattern in a call to
:meth:`~pyramid.config.Configurator.add_route`:

.. code-block:: python
   :linenos:

   config.add_route('abc', '/articles/{article}/edit',
                    traverse='/{article}')

The syntax of the ``traverse`` argument is the same as it is for ``pattern``.

If, as above, the ``pattern`` provided is ``/articles/{article}/edit``, and the
``traverse`` argument provided is ``/{article}``, when a request comes in that
causes the route to match in such a way that the ``article`` match value is
``1`` (when the request URI is ``/articles/1/edit``), the traversal path will
be generated as ``/1``. This means that the root object's ``__getitem__`` will
be called with the name ``1`` during the traversal phase.  If the ``1`` object
exists, it will become the :term:`context` of the request. The
:ref:`traversal_chapter` chapter has more information about traversal.

If the traversal path contains segment marker names which are not present in
the pattern argument, a runtime error will occur.  The ``traverse`` pattern
should not contain segment markers that do not exist in the ``path``.

Note that the ``traverse`` argument is ignored when attached to a route that
has a ``*traverse`` remainder marker in its pattern.

Traversal will begin at the root object implied by this route (either the
global root, or the object returned by the ``factory`` associated with this
route).

.. index::
   pair: hybrid applications; global views

Making Global Views Match
+++++++++++++++++++++++++

By default, only view configurations that mention a ``route_name`` will be
found during view lookup when a route that has a ``*traverse`` in its pattern
matches.  You can allow views without a ``route_name`` attribute to match a
route by adding the ``use_global_views`` flag to the route definition.  For
example, the ``myproject.views.bazbuz`` view below will be found if the route
named ``abc`` below is matched and the ``PATH_INFO`` is ``/abc/bazbuz``, even
though the view configuration statement does not have the ``route_name="abc"``
attribute.

.. code-block:: python
   :linenos:

   config.add_route('abc', '/abc/*traverse', use_global_views=True)
   config.add_view('myproject.views.bazbuz', name='bazbuz')

.. index::
   pair: hybrid applications; *subpath
   single: route subpath
   single: subpath (route)

.. _star_subpath:

Using ``*subpath`` in a Route Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are certain extremely rare cases when you'd like to influence the
traversal :term:`subpath` when a route matches without actually performing
traversal.  For instance, the :func:`pyramid.wsgi.wsgiapp2` decorator and the
:class:`pyramid.static.static_view` helper attempt to compute ``PATH_INFO``
from the request's subpath when its ``use_subpath`` argument is ``True``, so
it's useful to be able to influence this value.

When ``*subpath`` exists in a pattern, no path is actually traversed, but the
traversal algorithm will return a :term:`subpath` list implied by the capture
value of ``*subpath``.  You'll see this pattern most commonly in route
declarations that look like this:

.. code-block:: python
   :linenos:

   from pyramid.static import static_view

   www = static_view('mypackage:static', use_subpath=True)

   config.add_route('static', '/static/*subpath')
   config.add_view(www, route_name='static')

``mypackage.views.www`` is an instance of :class:`pyramid.static.static_view`.
This effectively tells the static helper to traverse everything in the subpath
as a filename.


.. index::
   pair: hybrid URLs; generating

.. _generating_hybrid_urls:

Generating Hybrid URLs
----------------------

.. versionadded:: 1.5

The :meth:`pyramid.request.Request.resource_url` method and the
:meth:`pyramid.request.Request.resource_path` method both accept optional
keyword arguments that make it easier to generate route-prefixed URLs that
contain paths to traversal resources: ``route_name``, ``route_kw``, and
``route_remainder_name``.

Any route that has a pattern that contains a ``*remainder`` pattern (any
stararg remainder pattern, such as ``*traverse``, ``*subpath``, or ``*fred``)
can be used as the target name for ``request.resource_url(..., route_name=)``
and ``request.resource_path(..., route_name=)``.

For example, let's imagine you have a route defined in your Pyramid application
like so:

.. code-block:: python

   config.add_route('mysection', '/mysection*traverse')

If you'd like to generate the URL ``http://example.com/mysection/a/``, you can
use the following incantation, assuming that the variable ``a`` below points to
a resource that is a child of the root with a ``__name__`` of ``a``:

.. code-block:: python

   request.resource_url(a, route_name='mysection')

You can generate only the path portion ``/mysection/a/`` assuming the same:

.. code-block:: python

   request.resource_path(a, route_name='mysection')

The path is virtual host aware, so if the ``X-Vhm-Root`` environment variable
is present in the request, and it's set to ``/a``, the above call to
``request.resource_url`` would generate ``http://example.com/mysection/``, and
the above call to ``request.resource_path`` would generate ``/mysection/``. See
:ref:`virtual_root_support` for more information.

If the route you're trying to use needs simple dynamic part values to be filled
in to succesfully generate the URL, you can pass these as the ``route_kw``
argument to ``resource_url`` and ``resource_path``.  For example, assuming that
the route definition is like so:

.. code-block:: python

   config.add_route('mysection', '/{id}/mysection*traverse')

You can pass ``route_kw`` in to fill in ``{id}`` above:

.. code-block:: python

   request.resource_url(a, route_name='mysection', route_kw={'id':'1'})

If you pass ``route_kw`` but do not pass ``route_name``, ``route_kw`` will be
ignored.

By default this feature works by calling ``route_url`` under the hood, and
passing the value of the resource path to that function as ``traverse``. If
your route has a different ``*stararg`` remainder name (such as ``*subpath``),
you can tell ``resource_url`` or ``resource_path`` to use that instead of
``traverse`` by passing ``route_remainder_name``.  For example, if you have the
following route:

.. code-block:: python

   config.add_route('mysection', '/mysection*subpath')

You can fill in the ``*subpath`` value using ``resource_url`` by doing:

.. code-block:: python

   request.resource_path(a, route_name='mysection',
                         route_remainder_name='subpath')

If you pass ``route_remainder_name`` but do not pass ``route_name``,
``route_remainder_name`` will be ignored.

If you try to use ``resource_path`` or ``resource_url`` when the ``route_name``
argument points at a route that does not have a remainder stararg, an error
will not be raised, but the generated URL will not contain any remainder
information either.

All other values that are normally passable to ``resource_path`` and
``resource_url`` (such as ``query``, ``anchor``, ``host``, ``port``, and
positional elements) work as you might expect in this configuration.

Note that this feature is incompatible with the ``__resource_url__`` feature
(see :ref:`overriding_resource_url_generation`) implemented on resource
objects.  Any  ``__resource_url__`` supplied by your resource will be ignored
when you pass ``route_name``.
