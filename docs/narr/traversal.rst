.. _traversal_chapter:

Traversal
=========

The :mod:`repoze.bfg` *Router* parses the URL associated with the
request and traverses the graph based on path segments in the URL.
Based on these path segments, :mod:`repoze.bfg` traverses the *model
graph* in order to find a :term:`context`.  It then attempts to find a
:term:`view` based on the *type* of the context (specified by an
:term:`interface`).  If :mod:`repoze.bfg` finds a :term:`view` for the
context, it calls it and returns a response to the user.

The Model Graph
---------------

When your application uses :term:`traversal` to resolve URLs to code,
your application must supply a *model graph* to :mod:`repoze.bfg`.

Users interact with your :mod:`repoze.bfg` -based application via a
*router*, which is just a fancy :term:`WSGI` application.  At system
startup time, the router is configured with a single object which
represents the root of the model graph.  All traversal will begin at
this root object.  The root object is usually a *mapping* object (such
as a Python dictionary).

Items contained within the graph are analogous to the concept of
:term:`model` objects used by many other frameworks (and
:mod:`repoze.bfg` refers to them as models, as well).  They are
typically instances of Python classes.

The model graph consists of *container* nodes and *leaf* nodes.  There
is only one difference between a *container* node and a *leaf* node:
*container* nodes possess a ``__getitem__`` method while *leaf* nodes
do not.  The ``__getitem__`` method was chosen as the signifying
difference between the two types of nodes because the presence of this
method is how Python itself typically determines whether an object is
"containerish" or not.

A container node is presumed to be willing to return a child node or
raise a ``KeyError`` based on a name passed to its ``__getitem__``.

No leaf-level instance is required to have a ``__getitem__``.  If
leaf-level instances happen to have a ``__getitem__`` (through some
historical inequity), you should subclass these node types and cause
their ``__getitem__`` methods to simply raise a ``KeyError``.  Or just
disuse them and think up another strategy.

Usually, the traversal root is a *container* node, and as such it
contains other nodes.  However, it doesn't *need* to be a container.
Your model graph can be as shallow or as deep as you require.

Traversal "stops" when :mod:`repoze.bfg` either reaches a leaf level
model instance in your object graph or when the path segments implied
by the URL "run out".  The object that traversal "stops on" becomes
the :term:`context`.

How :mod:`repoze.bfg` Processes a Request Using Traversal
---------------------------------------------------------

When a user requests a page from your :mod:`repoze.bfg` -powered
application, the system uses this algorithm to determine which Python
code to execute:

#.  The request for the page is presented to :mod:`repoze.bfg`'s
     "router" in terms of a standard :term:`WSGI` request, which is
     represented by a WSGI environment and a ``start_response``
     callable.

#.  The router creates a :term:`WebOb` request object based on the
    WSGI environment.

#.  The router uses the WSGI environment's ``PATH_INFO`` variable to
    determine the path segments to traverse.  The leading slash is
    stripped off ``PATH_INFO``, and the remaining path segments are
    split on the slash character to form a traversal sequence, so a
    request with a ``PATH_INFO`` variable of ``/a/b/c`` maps to the
    traversal sequence ``[u'a', u'b', u'c']``.  Note that each of the
    path segments in the sequence is converted to Unicode using the
    UTF-8 decoding (if the decoding fails, a ``TypeError`` is raised).

#.  :term:`Traversal` begins at the root object.  For the traversal
    sequence ``[u'a', u'b', u'c']``, the root object's ``__getitem__``
    is called with the name ``a``.  Traversal continues through the
    sequence.  In our example, if the root object's ``__getitem__``
    called with the name ``a`` returns an object (aka "object ``a``"),
    that object's ``__getitem__`` is called with the name ``b``.  If
    object A returns an object when asked for ``b``, "object ``b``"'s
    ``__getitem__`` is then asked for the name ``c``, and may return
    "object ``c``".

#.  Traversal ends when a) the entire path is exhausted or b) when any
    graph element raises a ``KeyError`` from its ``__getitem__`` or c)
    when any non-final path element traversal does not have a
    ``__getitem__`` method (resulting in a ``NameError``) or d) when
    any path element is prefixed with the set of characters ``@@``
    (indicating that the characters following the ``@@`` token should
    be treated as a "view name").

#.  When traversal ends for any of the reasons in the previous step,
    the the last object found during traversal is deemed to be the
    :term:`context`.  If the path has been exhausted when traversal
    ends, the "view name" is deemed to be the empty string (``''``).
    However, if the path was *not* exhausted before traversal
    terminated, the first remaining path element is treated as the
    view name.

    Any subseqent path elements after the view name are deemed the
    :term:`subpath`.  The subpath is always a sequence of strings that
    come from ``PATH_INFO`` that are "left over" after traversal has
    completed. For instance, if ``PATH_INFO`` was ``/a/b`` and the
    root returned an "object ``a``", and "object ``a``" subsequently
    returned an "object ``b``", the router deems that the context is
    "object ``b``", the view name is the empty string, and the subpath
    is the empty sequence.  On the other hand, if ``PATH_INFO`` was
    ``/a/b/c`` and "object ``a``" was found but raised a ``KeyError``
    for the name ``b``, the router deems that the context is "object
    ``a``", the view name is ``b`` and the subpath is ``['c']``.

#.  If a :term:`security policy` is configured, the router performs a
    permission lookup.  If a permission declaration is found for the
    view name and context implied by the current request, the security
    policy is consulted to see if the "current user" (also determined
    by the security policy) can perform the action.  If he can,
    processing continues.  If he cannot, an ``HTTPUnauthorized`` error
    is raised.

#.  Armed with the context, the view name, and the subpath, the router
    performs a view lookup.  It attemtps to look up a view from the
    :mod:`repoze.bfg` :term:`application registry` using the view name
    and the context.  If a view function is found, it is called with
    the context and the request.  It returns a response, which is fed
    back upstream.  If a view is not found, a generic WSGI
    ``NotFound`` application is constructed and returned.

In either case, the result is returned upstream via the :term:`WSGI`
protocol.

.. _debug_notfound_section:

NotFound Errors
---------------

It's useful to be able to debug ``NotFound`` errors when they occur
unexpectedly due to an application registry misconfiguration.  To
debug these errors, use the ``BFG_DEBUG_NOTFOUND`` environment
variable or the ``debug_notfound`` configuration file setting.
Details of why a view was not found will be printed to stderr, and the
browser representation of the error will include the same information.
See :ref:`environment_chapter` for more information about how and
where to set these values.

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

Because it's the "context", bfg examimes "bar" to find out what "type"
it is. Let's say it finds that the context is an ``IBar`` type
(because "bar" happens to have an attribute attached to it that
indicates it's an ``IBar``).

Using the "view name" ("baz") and the type, it asks the
:term:`application registry` (configured separately, via
``configure.zcml``) this question:

  - Please find me a :term:`view` (aka *controller* in some religions)
    with the name "baz" that can be used for the type ``IBar``.

Let's say it finds no matching view type.  It then returns a
``NotFound``.  The request ends.  Everyone is sad.

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

The fact that it does not find "buz.txt" at this point does not
signify an error condition.  It signifies that:

  - the "context" is biz (the context is the last item found during traversal).

  - the "view name" is "buz.txt"

  - the "subpath" is the empty list []

Because it's the "context", bfg examimes "biz" to find out what "type"
it is. Let's say it finds that the context an ``IBiz`` type (because
"biz" happens to have an attribute attached to it that happens
indicates it's an ``IBiz``).

Using the "view name" ("buz.txt") and the type, it asks the
:term:`application registry` this question:

  - Please find me a :term:`view` (*controller* in some religions)
    with the name "buz.txt" that can be used for type ``IBiz``.

Let's say that question is answered "here you go, here'a a bit of code
that is willing to deal with that case", and returns a :term:`view`.
It is passed the "biz" object as the "context" and the current
:term:`WebOb` :term:`request` as the "request".  It returns a
term:`response`.

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

Traversal-Related Side Effects
------------------------------

The :term:`subpath` will always be available to a view as a the
``subpath`` attribute of the :term:`request` object.  It will be a
list containing zero or more elements (which will be strings).

The :term:`view name` will always be available to a view as the
``view_name`` attribute of the :term:`request` object.  It will be a
single string (possibly the empty string if we're rendering a default
view).

The :term:`root` will always be available to a view as the ``root``
attribute of the :term:`request` object.  It will be the model object
at which traversal started (the root).

The :term:`context` will always be available to a view as the
``context`` attribute of the :term:`request` object.  It will be the
context object implied by the current request.

Unicode and Traversal
---------------------

The traversal machinery by default attempts to decode each path
element in ``PATH_INFO`` from its natural byte string (``str`` type)
representation into Unicode using the UTF-8 encoding before passing it
to the ``__getitem__`` of a model object.  If any path segment in
``PATH_INFO`` is not decodeable using the UTF-8 decoding, a TypeError
is raised.

