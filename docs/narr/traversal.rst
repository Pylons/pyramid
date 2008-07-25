Traversal
=========

In many popular web frameworks, a "URL dispatcher" is used to
associate a particular URL with a bit of code (known somewhat
ambiguously as a "controller" or "view" depending upon the particular
vocabulary religion to which you subscribe).  These systems allow the
developer to create "urlconfs" or "routes" to controller/view Python
code using pattern matching against URL components.  Examples:
`Django's URL dispatcher
<http://www.djangoproject.com/documentation/url_dispatch/>`_ and the
`Routes URL mapping system <http://routes.groovie.org/>`_ .

It is possible, however, to map URLs to code differently, using
"object graph traversal". The venerable Zope and CherryPy web
frameworks offer graph-traversal-based URL dispatch.
:mod:`repoze.bfg` also provides graph-traversal-based dispatch of URLs
to code.  Graph-traversal based dispatching is useful if you like the
URL to represent an arbitrary hierarchy of potentially heterogeneous
items.

.. note::

  :mod:`repoze.bfg` features graph traversal.  However, via the
  inclusion of Routes, URL dispatch is also supported for the parts of
  your URL space that better fit that model.

Non-graph traversal based URL dispatch can easily handle URLs such as
``http://example.com/members/Chris``, where it's assumed that each
item "below" ``members`` in the URL represents a member in the system.
You just match everything "below" ``members`` to a particular view.
They are not very good, however, at inferring the difference between
sets of URLs such as::

       http://example.com/members/Chris/document
       http://example.com/members/Chris/stuff/page

...wherein you'd like the ``document`` in the first URL to represent a
PDF document, and ``/stuff/page`` in the second to represent an
OpenOffice document in a "stuff" folder.  It takes more pattern
matching assertions to be able to make URLs like these work in
URL-dispatch based systems, and some assertions just aren't possible.
For example, URL-dispatch based systems don't deal very well with URLs
that represent arbitrary-depth hierarchies.

Graph traversal works well if you need to divine meaning out of these
types of "ambiguous" URLs and URLs that represent arbitrary-depth
hierarchies.  Each URL segment represents a single traversal through
an edge of the graph.  So a URL like ``http://example.com/a/b/c`` can
be thought of as a graph traversal on the example.com site through the
edges "a", "b", and "c".

Finally, if you're willing to treat your application models as a graph
that can be traversed, it also becomes trivial to provide "row-level
security" (in common relational parlance): you just attach a security
declaration to each instance in the graph.  This is not as easy in
frameworks that use URL-based dispatch.

Graph traversal is materially more complex than URL-based dispatch,
however, if only because it requires the construction and maintenance
of a graph, and it requires the developer to think about mapping URLs
to code in terms of traversing the graph.  (How's *that* for
self-referential! ;-) That said, for developers comfortable with Zope
(and comfortable with hierarchical data stores like ZODB), mapping a
URL to a graph traversal is a natural way to think about creating a
web application.

In essence, the choice to use graph traversal vs. URL dispatch is
largely religious in some sense.  Graph traversal dispatch probably
just doesn't make any sense when you possess completely "square" data
stored in a relational database.  However, when you have a
hierarchical data store, it can provide advantages over using
URL-based dispatch.

Thus :mod:`repoze.bfg` provides support for both approaches, even
though the focus is on object graph traversal.

The Model Graph
---------------

Users interact with your :mod:`repoze.bfg`-based application via a
"router", which is itself a WSGI application.  At system startup time,
the router is configured with a root object from which all traversal
will begin.  The root object is a mapping object, such as a Python
dictionary.  In fact, all items contained in the graph are either leaf
nodes (these have no ``__getitem__``) or container nodes (these do
have a ``__getitem__``).

Items contained within the graph are analogous to the concept of
``model`` objects used by many other frameworks (and :mod:`repoze.bfg`
refers to them as models, as well).  They are typically instances of
classes.  Each containerish instance is willing to return a child or
raise a KeyError based on a name passed to its ``__getitem__``.  No
leaf-level instance is required to have a ``__getitem__``.

:mod:`repoze.bfg` traverses the model graph in order to find a
*context*.  It then attempts to find a *view* based on the type of the
context.

How :mod:`repoze.bfg` Processes a Request Using Traversal
---------------------------------------------------------

When a user requests a page from your :mod:`repoze.bfg` -powered
application, the system uses this algorithm to determine which Python
code to execute:

 1.  The request for the page is presented to :mod:`repoze.bfg`'s
     "router" in terms of a standard WSGI request, which is
     represented by a WSGI environment and a ``start_response``
     callable.

 2.  The router creates a `WebOb <http://pythonpaste.org/webob/>`_
     request object based on the WSGI environment.

 3.  The router uses the WSGI environment's ``PATH_INFO`` variable to
     determine the path segments to traverse.  The leading slash is
     stripped off ``PATH_INFO``, and the remaining path segments are
     split on the slash character to form a traversal sequence, so a
     request with a ``PATH_INFO`` variable of ``/a/b/c`` maps to the
     traversal sequence ``['a', 'b', 'c']``.

 4.  Traversal begins at the root object.  For the traversal sequence
     ``['a', 'b', 'c']``, the root object's ``__getitem__`` is called
     with the name ``a``.  Traversal continues through the sequence.
     In our example, if the root object's ``__getitem__`` called with
     the name ``a`` returns an object (aka "object A"), that object's
     ``__getitem__`` is called with the name ``b``.  If object A
     returns an object when asked for ``b``, object B's
     ``__getitem__`` is then asked for the name ``c``, and may return
     object C.

 5.  Traversal ends when a) the entire path is exhausted or b) when
     any graph element raises a KeyError from its ``__getitem__`` or
     c) when any non-final path element traversal does not have a
     ``__getitem__`` method (resulting in a NameError) or d) when any
     path element is prefixed with the set of characters ``@@``
     (indicating that the characters following the ``@@`` token should
     be treated as a "view name").

 6.  When traversal ends for any of the reasons in the previous step,
     the the last object found during traversal is deemed to be the
     "context".  If the path has been exhausted when traversal ends,
     the "view name" is deemed to be the empty string (``''``).
     However, if the path was *not* exhausted before traversal
     terminated, the first remaining path element is treated as the
     view name.

     Any subseqent path elements after the view name are deemed the
     "subpath".  For instance, if ``PATH_INFO`` was ``/a/b`` and the
     root returned an "A" object, and the "A" object returned a "B"
     object, the router deems that the context is "object B", the view
     name is the empty string, and the subpath is the empty sequence.
     On the other hand, if ``PATH_INFO`` was ``/a/b/c`` and "object A"
     was found but raised a KeyError for the name ``b``, the router
     deems that the context is object A, the view name is ``b`` and
     the subpath is ``['c']``.

 7.  If a security policy is configured, the router performs a
     permission lookup.  If a permission declaration is found for the
     view name and context implied by the current request, the
     security policy is consulted to see if the "current user" (also
     determined by the security policy) can perform the action.  If he
     can, processing continues.  If he cannot, an HTTPUnauthorized
     error is raised.

 8.  Armed with the context, the view name, and the subpath, the
     router performs a view lookup.  It attemtps to look up a view
     from the :mod:`repoze.bfg` application registry using the view
     name and the context.  If a view function is found, it is called
     with the context and the request.  It returns a response, which
     is fed back upstream.  If a view is not found, a generic WSGI
     ``NotFound`` application is constructed.

In either case, the result is returned upstream via the WSGI protocol.

A Traversal Example
-------------------

Let's pretend the user asks for
``http://example.com/foo/bar/baz/biz/buz.txt``. Let's pretend that the
request's ``PATH_INFO`` in that case is ``/foo/bar/baz/biz/buz.txt``.
Let's further pretend that when this request comes in that we're
traversing the follwing graph::

  /--
     |
     |-- foo
          |
          ----bar

Here's what happens:

  - bfg traverses the root, and attempts to find foo, which it finds.

  - bfg traverses foo, and attempts to find bar, which it finds.

  - bfg traverses bar, and attempts to find baz, which it does not
    find ('bar' raises a ``KeyError`` when asked for baz).

The fact that it does not find "baz" at this point does not signify an
error condition.  It signifies that:

  - the "context" is bar (the context is the last item found during
    traversal).

  - the "view name" is ``baz``

  - the "subpath" is ``['biz', 'buz.txt']``

Because it's the "context", bfg examimes "baz" to find out what "type"
it is. Let's say it finds that the context is an ``IBar`` type
(because "bar" happens to have an attribute attached to it that
indicates it's an ``IBar``).

Using the "view name" ("baz") and the type, it asks the "application
registry" (configured separately, via "configure.zcml") this question:

  - Please find me a "view" (controller in some religions) with the
    name "baz" that can be used for the type ``IBar``.

Let's say it finds no matching view type.  It then returns a NotFound.
The request ends.  Everyone is sad.

But!  For this graph::

  /--
     |
     |-- foo
          |
          ----bar
               |
               ----baz
                      |
                      biz

The user asks for ``http://example.com/foo/bar/baz/biz/buz.txt``

  - bfg traverses foo, and attempts to find bar, which it finds.

  - bfg traverses bar, and attempts to find baz, which it finds.

  - bfg traverses baz, and attempts to find biz, which it finds.

  - bfg traverses biz, and attemtps to find "buz.txt" which it does
    not find.

The fact that it does not find "biz.txt" at this point does not
signify an error condition.  It signifies that:

  - the "context" is biz (the context is the last item found during traversal).

  - the "view name" is "buz.txt"

  - the "subpath" is the empty list []

Because it's the "context", bfg examimes "biz" to find out what "type"
it is. Let's say it finds that the context an ``IBiz`` type (because
"biz" happens to have an attribute attached to it that happens
indicates it's an ``IBiz``).

Using the "view name" ("buz.txt") and the type, it asks the
"application registry" (configured separately, in "configure.zcml")
this question:

  - Please find me a "view" (controller in some religions) with the
    name "buz.txt" that can be used for type ``IBiz``.

Let's say that question is answered "here you go, here'a a bit of code
that is willing to deal with that case", and returns a view.  It is
passed the "biz" object as the "context" and the current WebOb request
as the "request".  It returns a response.

There are two special cases:

- During traversal you will often end up with a "view name" that is
  the empty string.  This indicates that :mod:`repoze.bfg` should look
  up the *default view*.  The default view is a view that is
  registered with no name or a view which is registered with a name
  that equals the empty string.

- If any path segment element begins with the special characters
  ``@@`` (think of them as goggles), that segment is considered the
  "view name" immediately and traversal stops there.  This allows you
  to address views that may have the same names as model instance
  names in the graph unambiguously.

