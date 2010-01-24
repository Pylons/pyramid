.. _hybrid_chapter:

Combining Traversal and URL Dispatch
====================================

:mod:`repoze.bfg` makes an honest attempt to unify the largely
incompatible concepts of :term:`traversal` and :term:`url dispatch`.

When you write most :mod:`repoze.bfg` applications, you'll be using
either one or the other subsystem, but not both, to perform
:term:`context finding`.  However, to solve specific problems, it's
useful to use *both* traversal *and* URL dispatch within the same
application.  :mod:`repoze.bfg` makes this possible via *hybrid*
applications.

.. warning::

   Creating an application that uses hybrid-mode features of
   :mod:`repoze.bfg` exposes non-trivial corner cases.  Reasoning
   about a "hybrid" URL dispatch + traversal model can be difficult
   because the combination of the two concepts seems to fall outside
   the sweet spot of `the magical number seven plus or minus 2
   <http://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two>`_.
   To reason successfully about using URL dispatch and traversal
   together, you need to understand 1) URL pattern matching, 2) root
   factories and 3) the traversal algorithm, and the interactions
   between all of them.  Therefore, we don't recommend creating an
   application that relies on hybrid behavior unless you must.

The Schism
----------

:mod:`repoze.bfg`, especially when used according to the tutorials in
its documentation is sort of a "dual-mode" framework.  The tutorials
explain how to create an application in terms of using either
:term:`url dispatch` *or* :term:`traversal`.  But not both.  It's
useful to examine that pattern in order to understand the schism
between the two.

URL Dispatch Only
~~~~~~~~~~~~~~~~~

An application that uses :term:`url dispatch` exclusively to map URLs
to code will often have declarations like this within :term:`ZCML`:

.. code-block:: xml

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

In other words, each :term:`route` typically corresponds to a single
view callable, and when that route is matched during a request, the
view callable attached to it is invoked.

"Under the hood", these ``<route>`` declarations register a view for
each route.  This view is registered for the following context/request
type/name triad:

- the context :term:`interface` ``None``, implying any context.

- Two :term:`request type` interfaces are attached to the request: the
  :class:`repoze.bfg.interfaces.IRequest` interface and a
  dynamically-constructed route-statement-specific :term:`interface`.

- the empty string as the :term:`view name`, implying the default
  view.

This usually ensures that the named view will only be called when the
route it's attached to actually matches.

Typically, an application that uses only URL dispatch won't perform
any view configuration in ZCML and won't have any calls to
:meth:`repoze.bfg.configuration.Configurator.add_view` in its startup
code.

Traversal Only
~~~~~~~~~~~~~~

An application that uses :term:`traversal` exclusively to map URLs to
code just won't have any ZCML ``<route>`` declarations nor will it
make any calls to the
:meth:`repoze.bfg.configuration.Configurator.add_route` method.
Instead, its view configuration will imply declarations that look like
this:

.. code-block:: xml

   <view
     name="foobar"
     view=".views.foobar"
     />

   <view
     name="bazbuz"
     view=".views.bazbuz"
     />

"Under the hood", the above view statements register a view using the
following context/request/name :term:`triad`:

- the :term:`context` interface ``None``

- the :class:`repoze.bfg.interfaces.IRequest` :term:`request type`
  interface

- a :term:`view name` matching the ``name=`` argument.

The ``.views.foobar`` view callable above will be called when the URL
``/a/b/c/foobar`` or ``/foobar``, etc, assuming that no view is named
``a``, ``b``, or ``c`` during traversal.

.. index::
   single: hybrid mode application

Hybrid Applications
-------------------

Clearly *either* traversal or url dispatch can be used to create a
:mod:`repoze.bfg` application.  However, it is possible to combine the
competing concepts of traversal and url dispatch to resolve URLs to
code within the same application.

To "turn on" hybrid mode, use a :term:`route configuration` that
includes a ``path`` argument that contains a special dynamic part:
either ``*traverse`` or ``*subpath``.

Using ``*traverse`` In a Route Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a hybrid application, combine traversal and URL dispatch by
using route configuration that contains the special token
``*traverse`` in the route *path*.  For example:

.. code-block:: xml

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

When the this route is matched, :mod:`repoze.bfg` will attempt to use
:term:`traversal` against the context implied by the :term:`root
factory` of this route.  The above example isn't very useful unless
you've defined a custom :term:`root factory` by passing it to
constructor of a :class:`repoze.bfg.configuration.Configurator`
because the *default* root factory cannot be traversed (it has no
useful ``__getitem__`` method).  But let's imagine that your root
factory looks like so:

.. code-block:: python

   class Traversable(object):
       def __init__(self, subobjects):
          self.subobjects = subobjects

       def __getitem__(self, name):
          return self.subobjects[name]

   root = Traversable(
           {'a':Traversable({'b':Traversable({'c':Traversable({})})})})

   def root_factory(request):
       return root

We've defined a bogus graph here that can be traversed, and a
``root_factory`` method that returns the root of the graph that we can
pass to our :class:`repoze.bfg.configuration.Configurator`.

Because the ``Traversable`` object we've defined has a ``__getitem__``
method that does something nominally useful, using traversal against
the root implied by a route statement becomes a not-completely-insane
thing to do.

Under the circumstance implied by ``:foo/:bar/*traverse``, traversal
is performed *after* the route matches.  If the root factory returns a
traversable object, the "capture value" implied by the ``*traverse``
element in the path pattern will be used to traverse the graph,
starting from the root object returned from the root factory.

For example, if the URL requested by a user was
``http://example.com/one/two/a/b/c``, and the above route was matched
(some other route might match before this one does), the traversal
path used against the root would be ``a/b/c``.  :mod:`repoze.bfg` will
attempt to traverse a graph through the edges ``a``, ``b``, and ``c``.
In our above example, that would imply that the *context* of the view
would be the ``Traversable`` object we've named ``c`` in our bogus
graph, using the ``.views.home`` view as the view callable.

We can also define extra views that match a route:

.. code-block:: xml

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

   <view
     route_name="home"
     name="another"
     view=".views.another"
     />

Views that spell a route name are meant to associate a particular view
declaration with a route, using the route's name, in order to indicate
that the view should *only be invoked when the route matches*.

View configurations may have a ``route_name`` attribute which refers
to the value of the ``<route>`` declaration's ``name`` attribute.  In
the above example, the route name is ``home``.

The ``<view>`` declaration above names a different view and (more
importantly) a different :term:`view name`.  It's :term:`view name`
will be looked for during traversal.  So if our URL is
"http://example.com/one/two/a/another", the ``.views.another`` view
callable will be called instead of the *default* view callable (the
one implied by the route with the name ``home``).

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

   <route
    path="/static/*subpath"
    name="static"
    view=".views.static_view"
    />

Where ``.views.static_view`` is an instance of
:class:`repoze.bfg.view.static`.  This effectively tells the static
helper to traverse everything in the subpath as a filename.

Making Global Views Match
~~~~~~~~~~~~~~~~~~~~~~~~~

By default, view configurations that don't mention a ``route_name``
will be found by view lookup when a route matches.  You can make these
match forcibly by adding the ``use_global_views`` flag to the route
definition.  For example, the ``views.bazbuz`` view below will be
found if the route named ``abc`` below is matched and the
``PATH_INFO`` is ``/abc/bazbuz``, even though the view configuration
statement does not have the ``route_name="abc"`` attribute.

.. code-block:: xml

   <route
     path="/abc/*traverse"
     name="abc"
     use_global_views="True"
     />

   <view
     name="bazbuz"
     view=".views.bazbuz"
     />

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

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

Can also be spelled like so:

.. code-block:: xml

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

The above ``<view>`` declaration is completely useless, because the
view name will never be matched when the route it references matches.
Only the view associated with the route itself (``.views.abc``) will
ever be invoked when the route matches, because the default view is
always invoked when a route matches and when no post-match traversal
is performed.  To make the below ``<view>`` declaration non-useless,
you must the special ``*traverse`` token to the route's "path."  For
example:

.. code-block:: xml

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

