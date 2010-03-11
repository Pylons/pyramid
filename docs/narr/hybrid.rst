.. _hybrid_chapter:

Combining Traversal and URL Dispatch
====================================

When you write most :mod:`repoze.bfg` applications, you'll be using
one or the other of two available :term:`context finding` subsystems:
traversal or URL dispatch.  However, to solve a limited set of
problems, it's useful to use *both* traversal and URL dispatch
together within the same application.  :mod:`repoze.bfg` makes this
possible via *hybrid* applications.

.. warning::

   Reasoning about the behavior of a "hybrid" URL dispatch + traversal
   application can be challenging.  To successfully reason about using
   URL dispatch and traversal together, you need to understand URL
   pattern matching, root factories, and the :term:`traversal`
   algorithm, and the potential interactions between them.  Therefore,
   we don't recommend creating an application that relies on hybrid
   behavior unless you must.

A Review of Non-Hybrid Applications
-----------------------------------

When used according to the tutorials in its documentation
:mod:`repoze.bfg` is a "dual-mode" framework: the tutorials explain
how to create an application in terms of using either :term:`url
dispatch` *or* :term:`traversal`.  This chapter details how you might
combine these two dispatch mechanisms, but we'll review how they work
in isolation before trying to combine them.

URL Dispatch Only
~~~~~~~~~~~~~~~~~

An application that uses :term:`url dispatch` exclusively to map URLs
to code will often have declarations like this within :term:`ZCML`:

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar"
     name="foobar"
     view=".views.foobar"
     />

   <route
     path=":baz/:buz"
     name="bazbuz"
     view=".views.bazbuz"
     />

Each :term:`route` typically corresponds to a single view callable,
and when that route is matched during a request, the view callable
named by the ``view`` attribute is invoked.

Typically, an application that uses only URL dispatch won't perform
any configuration in ZCML that includes a ``<view>`` declaration and
won't have any calls to
:meth:`repoze.bfg.configuration.Configurator.add_view` in its startup
code.

Traversal Only
~~~~~~~~~~~~~~

An application that uses only traversal will have view configuration
declarations that look like this:

.. code-block:: xml
   :linenos:

   <view
     name="foobar"
     view=".views.foobar"
     />

   <view
     name="bazbuz"
     view=".views.bazbuz"
     />

When the above configuration is applied to an application, the
``.views.foobar`` view callable above will be called when the URL
``/foobar`` is visited.  Likewise, the view ``.views.bazbuz`` will be
called when the URL ``/bazbuz`` is visited.

An application that uses :term:`traversal` exclusively to map URLs to
code usually won't have any ZCML ``<route>`` declarations nor will it
make any calls to the
:meth:`repoze.bfg.configuration.Configurator.add_route` method.

Hybrid Applications
-------------------

Either traversal or url dispatch alone can be used to create a
:mod:`repoze.bfg` application.  However, it is also possible to
combine the concepts of traversal and url dispatch when building an
application: the result is a hybrid application.  In a hybrid
application, traversal is performed *after* a particular route has
matched.

A hybrid application is a lot more like a "pure" traversal-based
application than it is like a "pure" URL-dispatch based application.
But unlike in a "pure" traversal-based application, in a hybrid
application, :term:`traversal` is performed during a request after a
route has already matched.  This means that the URL pattern that
represents the ``path`` argument of a route must match the
``PATH_INFO`` of a request, and after the route path has matched, most
of the "normal" rules of traversal with respect to :term:`context
finding` and :term:`view lookup` apply.

There are only four real differences between a purely traversal-based
application and a hybrid application:

- In a purely traversal based application, no routes are defined; in a
  hybrid application, at least one route will be defined.

- In a purely traversal based application, the root object used is
  global implied by the :term:`root factory` provided at startup
  time; in a hybrid application, the :term:`root` object at which
  traversal begins may be varied on a per-route basis.

- In a purely traversal-based application, the ``PATH_INFO`` of the
  underlying :term:`WSGI` environment is used wholesale as a traversal
  path; in a hybrid application, the traversal path is not the entire
  ``PATH_INFO`` string, but a portion of the URL determined by a
  matching pattern in the matched route configuration's path.

- In a purely traversal based application, view configurations which
  do not mention a ``route_name`` argument are considered during
  :term:`view lookup`; in a hybrid application, when a route is
  matched, only view configurations which mention that route's name as
  a ``route_name`` are considered during :term:`view lookup`.

More generally, a hybrid application *is* a traversal-based
application except:

- the traversal *root* is chosen based on the route configuration of
  the route that matched instead of from the ``root_factory`` supplied
  during application startup configuration.

- the traversal *path* is chosen based on the route configuration of
  the route that matched rather than from the ``PATH_INFO`` of a
  request.

- the set of views that may be chosen during :term:`view lookup` when
  a route matches are limited to those which specifically name a
  ``route_name`` in their configuration that is the same as the
  matched route's ``name``.

To create a hybrid mode application, use a :term:`route configuration`
that implies a particular :term:`root factory` and which also includes
a ``path`` argument that contains a special dynamic part: either
``*traverse`` or ``*subpath``.

The Root Object for a Route Match
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A hybrid application implies that traversal is performed during a
request after a route has matched.  Traversal, by definition, must
always begin at a root object.  Therefore it's important to know
*which* root object will be traversed after a route has matched.

Figuring out which :term:`root` object results from a particular route
match is straightforward.  When a route is matched:

- If the route's configuration has a ``root_factory`` argument which
  points to a :term:`root factory` callable, that callable will be
  called to generate a :term:`root` object.

- If the route's configuration does not have a ``root_factory``
  argument, the *global* :term:`root factory` will be called to
  generate a :term:`root` object.  The global root factory is the
  callable implied by the ``root_factory`` argument passed to
  :class:`repoze.bfg.configuration.Configurator` at application
  startup time.

- If a ``root_factory`` argument is not provided to the
  :class:`repoze.bfg.configuration.Configurator` at startup time, a
  *default* root factory is used.  The default root factory is used to
  generate a root object.

.. note::

   Root factories related to a route were explained previously within
   :ref:`route_factories`.  Both the global root factory and default
   root factory were explained previously within
   :ref:`the_object_graph`.  

Using ``*traverse`` In a Route Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A hybrid application most often implies the inclusion of a route
configuration that contains the special token ``*traverse`` at the end
of a route's path:

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar/*traverse"
     name="home"
     />

A ``*traverse`` token at the end of the path in a route's
configuration implies a "stararg" *capture* value.  When it is used,
it will match the remainder of the path segments of the URL.  This
remainder becomes the path used to perform traversal.

.. note::

   The ``*stararg`` route path pattern syntax is explained in more
   detail within :ref:`route_path_pattern_syntax`.

Note that unlike the examples provided within
:ref:`urldispatch_chapter`, the ``<route>`` configuration named
previously does not name a ``view`` attribute.  This is because a
hybrid mode application relies on :term:`traversal` to do
:term:`context finding` and :term:`view lookup` instead of invariably
invoking a specific view callable named directly within the matched
route's configuration.

Because the path of the above route ends with ``*traverse``, when this
route configuration is matched during a request, :mod:`repoze.bfg`
will attempt to use :term:`traversal` against the :term:`root` object
implied by the :term:`root factory` implied by the route's
configuration.  Once :term:`traversal` has found a :term:`context`,
:term:`view lookup` will be invoked in almost exactly the same way it
would have been invoked in a "pure" traversal-based application.

The *default* :term:`root factory` cannot be traversed: it has no
useful ``__getitem__`` method.  So we'll need to associate this route
configuration with a non-default root factory in order to create a
useful hybrid application.  To that end, let's imagine that we've
created a root factory that looks like so in a module named
``routes.py``:

.. code-block:: python
   :linenos:

   class Traversable(object):
       def __init__(self, subobjects):
          self.subobjects = subobjects

       def __getitem__(self, name):
          return self.subobjects[name]

   root = Traversable(
           {'a':Traversable({'b':Traversable({'c':Traversable({})})})}
          )

   def root_factory(request):
       return root

Above, we've defined a (bogus) graph here that can be traversed, and a
``root_factory`` function that can be used as part of a particular
route configuration statement:

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar/*traverse"
     name="home"
     root_factory=".routes.root_factory"
     />

The ``root_factory`` above points at the function we've defined.  It
will return an instance of the ``Traversable`` class as a root object
whenever this route is matched.  Because the ``Traversable`` object
we've defined has a ``__getitem__`` method that does something
nominally useful, and because traversal uses ``__getitem__`` to walk
the nodes that make up an object graph, using traversal against the
root object implied by our route statement becomes a reasonable thing
to do.

.. note::

  We could have also used our ``root_factory`` callable as the
  ``root_factory`` argument of the
  :class:`repoze.bfg.configuration.Configurator` constructor instead
  of associating it with a particular route inside the route's
  configuration.  Every hybrid route configuration that is matched but
  which does *not* name a ``root_factory``` attribute will use the use
  global ``root_factory`` function to generate a root object.

When the route configuration named ``home`` above is matched during a
request, the matchdict generated will be based on its path:
``:foo/:bar/*traverse``.  The "capture value" implied by the
``*traverse`` element in the path pattern will be used to traverse the
graph in order to find a context, starting from the root object
returned from the root factory.  In the above example, the
:term:`root` object found will be the instance named ``root`` in
``routes.py``.

If the URL that matched a route with the path ``:foo/:bar/*traverse``,
is ``http://example.com/one/two/a/b/c``, the traversal path used
against the root object will be ``a/b/c``.  As a result,
:mod:`repoze.bfg` will attempt to traverse through the edges ``a``,
``b``, and ``c``, beginning at the root object.

In our above example, this particular set of traversal steps will mean
that the :term:`context` of the view would be the ``Traversable``
object we've named ``c`` in our bogus graph and the :term:`view name`
resulting from traversal will be the empty string; if you need a
refresher about why this outcome is presumed, see
:ref:`traversal_algorithm`.

At this point, a suitable view callable will be found and invoked
using :term:`view lookup` as described in :ref:`view_configuration`,
but with a caveat: in order for view lookup to work, we need to define
a view configuration that will match when :term:`view lookup` is
invoked after a route matches:

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar/*traverse"
     name="home"
     root_factory=".routes.root_factory"
     />

   <view
     route_name="home"
     view=".views.myview"
     />

Note that the above ``view`` declaration includes a ``route_name``
argument.  Views that include a ``route_name`` argument are meant to
associate a particular view declaration with a route, using the
route's name, in order to indicate that the view should *only be
invoked when the route matches*.

View configurations may have a ``route_name`` attribute which refers
to the value of the ``<route>`` declaration's ``name`` attribute.  In
the above example, the route name is ``home``, referring to the name
of the route defined above it.

The above ``.views.myview`` view will be invoked when:

- the route named "home" is matched

- the :term:`view name` resulting from traversal is the empty string.

- the :term:`context` is any object.

It is also possible to declare alternate views that may be invoked
when a hybrid route is matched:

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar/*traverse"
     name="home"
     root_factory=".routes.root_factory"
     />

   <view
     route_name="home"
     view=".views.myview"
     />

   <view
     route_name="home"
     name="another"
     view=".views.another_view"
     />

The ``view`` declaration for ``.views.another_view`` above names a
different view and, more importantly, a different :term:`view name`.
The above ``.views.another_view`` view will be invoked when:

- the route named "home" is matched

- the :term:`view name` resulting from traversal is ``another``.

- the :term:`context` is any object.

For instance, if the URL ``http://example.com/one/two/a/another`` is
provided to an application that uses the previously mentioned object
graph, the ``.views.another`` view callable will be called instead of
the ``.views.myview`` view callable because the :term:`view name` will
be ``another`` instead of the empty string.

More complicated matching can be composed.  All arguments to *route*
configuration statements and *view* configuration statements are
supported in hybrid applications (such as :term:`predicate`
arguments).

Making Global Views Match
+++++++++++++++++++++++++

By default, view configurations that don't mention a ``route_name``
will be not found by view lookup when a route that mentions a
``*traverse`` in its path matches.  You can make these match forcibly
by adding the ``use_global_views`` flag to the route definition.  For
example, the ``views.bazbuz`` view below will be found if the route
named ``abc`` below is matched and the ``PATH_INFO`` is
``/abc/bazbuz``, even though the view configuration statement does not
have the ``route_name="abc"`` attribute.

.. code-block:: xml
   :linenos:

   <route
     path="/abc/*traverse"
     name="abc"
     use_global_views="True"
     />

   <view
     name="bazbuz"
     view=".views.bazbuz"
     />

.. index::
   single: route subpath
   single: subpath (route)

.. _star_subpath:

Using ``*subpath`` in a Route Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are certain extremely rare cases when you'd like to influence
the traversal :term:`subpath` when a route matches without actually
performing traversal.  For instance, the
:func:`repoze.bfg.wsgi.wsgiapp2` decorator and the
:class:`repoze.bfg.view.static` helper attempt to compute
``PATH_INFO`` from the request's subpath, so it's useful to be able to
influence this value.

When ``*subpath`` exists in a path pattern, no path is actually
traversed, but the traversal algorithm will return a :term:`subpath`
list implied by the capture value of ``*subpath``.  You'll see this
pattern most commonly in route declarations that look like this:

.. code-block:: xml
   :linenos:

   <route
    path="/static/*subpath"
    name="static"
    view=".views.static_view"
    />

Where ``.views.static_view`` is an instance of
:class:`repoze.bfg.view.static`.  This effectively tells the static
helper to traverse everything in the subpath as a filename.

Corner Cases
------------

A number of corner case "gotchas" exist when using a hybrid
application.  We'll detail them here.

Registering a Default View for a Route That Has a ``view`` Attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is an error to provide *both* a ``view`` argument to a :term:`route
configuration` *and* a :term:`view configuration` which names a
``route_name`` that has no ``name`` value or the empty ``name`` value.
For example, this pair of route/view ZCML declarations will generate a
"conflict" error at startup time.

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

   <view
     route_name="home"
     view=".views.another"
     />

This is because the ``view`` attribute of the ``<route>`` statement
above is an *implicit* default view when that route matches.
``<route>`` declarations don't *need* to supply a view attribute.  For
example, this ``<route>`` statement:

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

Can also be spelled like so:

.. code-block:: xml
   :linenos:

   <route
     path=":foo/:bar/*traverse"
     name="home"
     />

   <view
     route_name="home"
     view=".views.home"
     />

The two spellings are logically equivalent.  In fact, the former is
just a syntactical shortcut for the latter.

Binding Extra Views Against a Route Configuration that Doesn't Have a ``*traverse`` Element In Its Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's another corner case that just makes no sense.

.. code-block:: xml
   :linenos:

   <route
     path="/abc"
     name="abc"
     view=".views.abc"
     />

   <view
     name="bazbuz"
     view=".views.bazbuz"
     route_name="abc"
     />

The above ``<view>`` declaration is useless, because it will never be
matched when the route it references has matched.  Only the view
associated with the route itself (``.views.abc``) will ever be invoked
when the route matches, because the default view is always invoked
when a route matches and when no post-match traversal is performed.

To make the above ``<view>`` declaration non-useless, the special
``*traverse`` token must end the route's path.  For example:

.. code-block:: xml
   :linenos:

   <route
     path="/abc/*traverse"
     name="abc"
     view=".views.abc"
     />

   <view
     name="bazbuz"
     view=".views.bazbuz"
     route_name="abc"
     />

