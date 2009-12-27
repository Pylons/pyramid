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

Reasoning about a "hybrid" URL dispatch + traversal model can be
difficult because the combination of the two concepts seems to fall
outside the sweet spot of `the magical number seven plus or minus 2
<http://en.wikipedia.org/wiki/The_Magical_Number_Seven,_Plus_or_Minus_Two>`_.
To reason successfully about using URL dispatch and traversal
together, you need to understand 1) URL pattern matching, 2) root
factories and 3) the traversal algorithm, and the interactions between
all of them.  Therefore, use of this pattern is not recommended unless
you *really* need to use it.

.. warning:: Creating applications that use hybrid-mode features of
   :mod:`repoze.bfg` is a advanced topic that exposes non-trivial
   corner cases; you may need to understand more deeply how
   :mod:`repoze.bfg` works to understand the concepts discussed in
   this chapter.  To that end, it's useful to read
   :ref:`router_chapter` to get a more holistic understanding of
   what's happening "under the hood" to use this feature.

The Schism
----------

BFG, when used according to the currently published tutorials in its
documentation is sort of a dual-mode framework.  The tutorials explain
how to create an application terms of using either :term:`url
dispatch` *or* :term:`traversal`.  It's useful to examine that pattern
in order to understand the schism between the two.

URL Dispatch Only
~~~~~~~~~~~~~~~~~

An application that uses :term:`url dispatch` exclusively to map URLs
to code will usually exclusively have declarations like this within
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

Traversal Only
~~~~~~~~~~~~~~

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
:term:`context` interface ``None``, the
:class:`repoze.bfg.interfaces.IRequest` :term:`request type` with a
:term:`view name` matching the name= argument.  The "foobar" view
above will match the URL ``/a/b/c/foobar`` or ``/foobar``, etc,
assuming that no view is named "a", "b", or "c" during traversal.

.. index::
   single: hybrid mode application

Hybrid Applications
-------------------

We've seen how the current crop of tutorials explain that you can use
*either* traversal or url dispatch to create a :mod:`repoze.bfg`
application.  However, it is possible to combine the competing
concepts of traversal and url dispatch to resolve URLs to code within
the same application by using a ``<route>`` declaration that contains
the special token ``*traverse`` in its path.

.. code-block:: xml

   <route
     path=":foo/:bar/*traverse"
     name="home"
     view=".views.home"
     />

When the view attached to this route is invoked, :mod:`repoze.bfg`
will attempt to use :term:`traversal` against the context implied by
the :term:`root factory` of this route.  The above example isn't very
useful unless you've defined a custom :term:`root factory` by passing
it to constructor of a :class:`repoze.bfg.configuration.Configurator`
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
requested by a user was ``http://example.com/one/two/a/b/c``, and the
above route was matched (some other route might match before this one
does), the traversal path used against the root would be ``a/b/c``.
:mod:`repoze.bfg` will attempt to traverse a graph through the edges
"a", "b", and "c".  In our above example, that would imply that the
*context* of the view would be the ``Traversable`` object we've named
"c" in our bogus graph, using the ``.views.home`` view as the view
callable.

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
``name`` attribute ("home").  The ``<view>`` declaration above names a
different view and (more importantly) a different :term:`view name`.
It's :term:`view name` will be looked for during traversal.  So if our
URL is "http://example.com/one/two/a/another", the ``.views.another``
view will be called.

.. index::
   pair: route; factory
   single: route factory

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

.. index::
   pair: subpath; route

.. _star_subpath:

Using ``*subpath`` in a Route Path
----------------------------------

There are certain (extremely rare) cases when you'd like to influence
the traversal :term:`subpath` when a route matches without actually
performing traversal.  For instance, the
:func:`repoze.bfg.wsgi.wsgiapp2` decorator and the
:class:`repoze.bfg.view.static` helper attempt to compute
``PATH_INFO`` from the request's subpath, so it's useful to be able to
influence this value.  When ``*subpath`` exists in a path pattern, no
path is actually traversed, but the traversal algorithm will return a
:term:`subpath` list implied by the capture value of ``*subpath``.
You'll see this pattern most commonly in route declarations that look
like this:

.. code-block:: xml

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
application.  Let's see what they are.

.. _globalviews_corner_case:

"Global" Views Match Any Route When A More Specific View Doesn't
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note that views that don't mention a ``route_name`` will *also* match
when *any* route matches.  For example, the "bazbuz" view below will
be found if the route named "abc" below is matched.

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

To override the behavior of the "bazbuz" view when this route matches,
use an additional view that mentions the route name explicitly.

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

   <view
     name="bazbuz"
     route_name="abc"
     view=".views.bazbuz2"
     />

In the above setup, when no route matches, and traversal finds the
view name to be "bazbuz", the ``.views.bazbuz`` view will be used.
However, if the "abc" route matches, and traversal finds the view name
to be "bazbuz", the ``.views.bazbuz2`` view will be used.

``context`` Type (aka "for") Registrations Bind More Tightly Than ``request``  Type Registrations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This corner case is only interesting if you are using a hybrid
application and you believe the "wrong" view is being called for a
given request.

This explanation requires a little "inside baseball" knowledge of how
:mod:`repoze.bfg` works.  :mod:`repoze.bfg` uses the :term:`Zope
Component Architecture` under the hood to dispatch a request to a
:term:`view`.  In Zope Component Architecture-speak, a view is a
"multi adapter" registered for a :term:`context` type and a
:term:`request` type as well as a particular :term:`view name`.  When
a request is generated and a context is found by the :mod:`repoze.bfg`
:term:`router`, it uses these two values, along with the :term:`view
name` to try to locate a view callable.

A view is registered for a ``route`` either as its default view via
the ``view=`` attribute of a ``route`` declaration in ZCML *or* as a
standalone ``<view>`` declaration (or via the ``@bfg_route``
decorator) which has a ``route_name`` that matches the route's name.
At startup time, when such a registration is encountered, the view is
registered for the ``context`` type ``None`` (meaning *any* context)
and a *special* request type which is dynamically generated.  This
request type also derives from a "base" request type, which is what
allows it to match against views defined without a route name (see
:ref:`globalviews_corner_case`).

When a request URL matches a ``<route>`` path, the special request
type interface mentioned in the previous paragraph is attached to the
``request`` object as it is created.  The *root* found by the router
is based on either the route's ``factory`` (or the default root
factory if no ``factory`` is mentioned in the ``<route>``
declaration).  This root is eventually resolved to a ``context`` via
:term:`traversal`.  This ``context`` will either have some particular
interface, or it won't, depending on the result of traversal.

Given how view dispatch works, since the registration made "under the
hood" for views that match a route use the (very weakly binding)
``None`` value as the context value's interface, if the context that
is found has a specific interface, and a global view statement is
registered against this interface as its context interface, it's
likely that the *global* view will match *before* the view that is
attached to the route unless the ``view_for`` attribute is used on the
``route`` registration to match the "correct" interface first (because
then both the request type and the context type are "more specific"
for the view registration).

What it all boils down to is: if a request that matches a route
resolves to a view you don't expect it to, use the ``view_for``
attribute of the ``route`` statement (*or* the ``for`` attribute of
the ZCML statement that also has a ``route_name`` *or* the equivalent
``for_`` parameter to the :class:`repoze.bfg.view.bfg_view` decorator
that also has a ``route_name`` parameter) to name the specific context
interface you want the route-related view to match.

Yes, that was as painful for me to write as it was for you to read.

Registering a Default View for a Route That has a ``view`` attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

The two spellings are logically equivalent.  

Binding Extra Views Against a  ``<route>`` Statement that Doesn't Have a ``*traverse`` Element In Its Path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. index::
   pair: route; ordering

Route Ordering
~~~~~~~~~~~~~~

One other thing to look out for: ``<route>`` statements need to be
ordered relative to each other; view statements don't.  ``<route>``
statement ordering is very important, because routes are evaluated in
a specific order, unlike traversal, which depends on emergent behavior
rather than an ordered list of directives.

