.. _hybrid_chapter:

Combining Traversal and URL Dispatch
====================================

:mod:`repoze.bfg` makes an honest attempt to unify the (largely
incompatible) concepts of :term:`traversal` and :term:`url dispatch`.
When you write *most* :mod:`repoze.bfg` applications, you'll be using
either one or the other concept, but not both, to resolve URLs to
:term:`view` callables.

However, for some problems, it's useful to use both traversal *and*
URL dispatch within the same application.  :mod:`repoze.bfg` makes
this possible.

Trying to explain a "hybrid" URL dispatch + traversal model is
difficult because combining the two concepts seems to break a law of
`the magical number seven plus or minus 2
<http://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two>`_
().  This is because, as a user, you need to understand 1) URL pattern
matching, 2) root factories and 3) the traversal algorithm, and the
interactions between all of them.  Therefore, use of this pattern is
not recommended unless you *really* need to use it.

It's useful to read :ref:`router_chapter` to get a more holistic
understanding of what's happening "under the hood" to use this
feature.

The Schism
----------

An application that uses :term:`url dispatch` exclusively to map URLs
to code will usually exlusively have declarations like this within
their ``configure.zcml`` file:

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

In other words, each route typically corresponds with a single view
function, and when the route is matched during a request, the view
attached to it is invoked.  Typically, applications that use only URL
dispatch won't have any ``<view>`` statements in the
``configure.zcml``.

"Under the hood", these ``<route>`` statements register a view for
each route for the context :term:`interface` ``None`` (implying any
context) and a route-statement-specific (dynamically-constructed)
:term:`request type` using the empty string as the :term:`view name`
(implying the default view).  This ensures that the named view will
only be called when the route it's attached to actually matches.

In application that uses :term:`traversal` exclusively to map URLs to
code just won't have any ``<route>`` declarations.  Instead, its ZCML
(or bfg_view decorators) will imply declarations that look like this:

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
:term:`context` interface ``None``, the IRequest :term:`request type`
with a :term:`view name` matching the name= argument.  The "foobar"
view above will match the URL ``/a/b/c/foobar`` or ``/foobar``, etc,
assuming that no view is named "a", "b", or "c" during traversal.

BFG, when used in these two styles is a sort of dual-mode framework
that can be used by people who prefer one style over the other.

Hybrid Applications
-------------------

It's not a very common requirement, but it is possible to combine the
competing concepts of traversal and url dispatch to resolve URLs to
code within the same application by using a ``<route>`` declaration
that contains the special token ``*traverse`` in its path.

.. code-block:: xml

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

When the view attached to this route is invoked, BFG will attempt to
use :term:`traversal` against the context implied by the :term:`root
factory` of this route.  The above example isn't very useful unless
you've defined a custom :term:`root factory` by passing it to the
``repoze.bfg.router.make_app`` function, because the *default* root
factory cannot be traversed (it has no useful ``__getitem__`` method).
But let's imagine that your root factory looks like so:

.. code-block:: python

   class Traversable(object):
       def __init__(self, subobjects):
          self.subobjects = subobjects

       def __getitem__(self, name):
          return self.subobjects[name]

   root = Traversable(None, None, 
           {'a':Traversable({'b':Traversable({'c':Traversable({})})})})

   def root_factory(environ):
       return root

We've defined a bogus graph here that can be traversed, and a
root_factory method that returns the root of the graph.  Because the
Traversable object we've defined has a ``__getitem__`` method that
does something (sort of) useful (see :ref:`traversal_chapter` for more
info about how traversal works), using traversal against the root
implied by a route statement becomes a not-completely-insane thing to
do.  So for this route:

.. code-block:: xml

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

Under this circumstance, traversal is performed *after* the route
matches.  If the root factory returns a traversable object, the
"capture value" implied by the ``*traverse`` element in the path
pattern will be used to traverse the graph.  For example, if the URL
requested by a user was "http://example.com/one/two/a/b/c", and the
above route was matched (some other route might match before this one
does), the traversal path used against the root would be ``a/b/c``.
BFG will attempt to traverse a graph through the edges "a", "b", and
"c".  In our above example, that would imply that the *context* of the
view would be the ``Traversable`` object we've named "c" in our bogus
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

Views declared *after* the route declaration may have a ``route_name``
attribute which refers to the value of the ``<route>`` declaration's
``name`` attribute ("home").  The ``<view>`` declaration above names
a different view and (more importantly) a different :term`view name`.
It's :term:`view name` will be looked for during traversal.  So if our
URL is "http://example.com/one/two/a/another", the ``.views.another``
view will be called.

A ``<route>`` declarations *must* precede (in XML order) any
``<view>`` declaration which names it as a ``route_name``.  If it does
not, at application startup time a ConfigurationError will be raised.

Corner Cases
------------

It is an error to provide *both* a ``view`` attribute on a ``<route>``
declaration *and* a ``<view>`` declaration that serves as a "default
view" (a view with no ``name`` attribute or the empty ``name``
attribute).  For example, this pair of route/view statements will
generate a "conflict" error at startup time.

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

This is because the "view" attribute of the ``<route>`` statement
above is an *implicit* default view when that route matches.
``<route>`` declarations don't *need* to supply a view attribute.
For example, this ``<route>`` statement:

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

The two spellings are logically equivalent.  

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
you must the special ``*traverse`` token to the route's "path"., e.g.:

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

Note that views that *don't* mention a ``route_name`` won't ever match
when any route matches.  For example, the "bazbuz" view below will
never be found if the route named "abc" below is matched.

.. code-block:: xml

   <route
     path="/abc/*traverse"
     name="abc"
     view=".views.abc"
     />

   <view
     name="bazbuz"
     view=".views.bazbuz"
     />

Views defined without a ``route_name`` will only be invoked when *no*
route matches.

One other thing to look out for: ``<route>`` statements need to be
ordered relative to each other; view statements don't.  <route>
statement ordering is very important, because routes are evaluated in
a specific order, unlike traversal, which depends on emergent behavior
rather than an ordered list of directives.

Route Factories
---------------

A "route" declaration can mention a "factory".  When a factory is
attached to a route, it is used to generate a root (it's a :term:`root
factory`) instead of the *default* root factory.

.. code-block:: xml

   <route
    factory=".models.root_factory"
    path="/abc/*traverse"
    name="abc"
    />

In this way, each route can use a different factory, making it
possible to traverse different graphs based on some routing parameter
within the same application.

