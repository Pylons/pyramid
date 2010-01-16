.. _traversal_chapter:

Traversal
=========

:term:`traversal` is a :term:`context finding` mechanism that is used
by :mod:`repoze.bfg`. :term:`traversal` is the act of finding a
:term:`context` and a :term:`view name` by walking over an *object
graph*, starting from a :term:`root` object, using a :term:`request`
object as a source of path information.

In this chapter, we'll provide a high-level overview of traversal,
explain the concept of an *object graph*,

.. index::
   pair: traversal; high-level overview

A High-Level Overview of Traversal Mechanics
--------------------------------------------

:term:`Traversal` is dependent on information in a :term:`request`
object.  The :term:`request` object contains URL path information in
the ``PATH_INFO`` portion of the :term:`WSGI` environment.  The
``PATH_INFO`` portion of the WSGI environment is the URL data in a
request following the hostname and port number, but before any query
string elements or fragments, for example the ``/a/b/c`` portion of
the URL ``http://example.com/a/b/c?foo=1``.

Traversal treats the ``PATH_INFO`` segment of a URL as a sequence of
path segments.  For example, the ``PATH_INFO`` string ``/a/b/c`` is
treated as the sequence ``['a', 'b', 'c']``.  Traversal pops the first
element (``a``) from the path segment sequence and attempts to use it
as a lookup key into an object graph supplied by an application.  If
that succeeeds, the :term:`context` temporarily becomes the object
found via that lookup.  Then the next segment (``b``) is popped from
the sequence, and the object graph is queried for that segment; if
that lookup succeeds, the :term:`context` becomes that object.  This
process continues until the path segment sequence is exhausted or any
lookup for a name in the sequence fails.  In either case, a
:term:`context` is found.

The results of a :term:`traversal` also include a :term:`view name`.
The :term:`view name` is the *first* URL path segment in the set of
``PATH_INFO`` segments "left over" in the path segment list popped by
the traversal process.

The combination of the :term:`context` object and the :term:`view
name` found via traversal is used later in the same request by a
separate :mod:`repoze.bfg` subsystem -- the "view lookup" subsystem --
to find a :term:`view callable` later within the same request.  How
:mod:`repoze.bfg` performs view lookup is explained within the
:ref:`views_chapter` chapter.

.. index::
   single: object graph
   single: traversal graph
   single: model graph

The Object Graph
----------------

When your application uses :term:`traversal` to resolve URLs to code,
your application must supply an *object graph* to :mod:`repoze.bfg`.

Users interact with your :mod:`repoze.bfg` -based application via a
:term:`router`, which is just a fancy :term:`WSGI` application.  At
system startup time, the router is configured with a callback known as
a :term:`root factory`, supplied by the application developer.  The
root factory is passed a :term:`request` object and it is expected to
return an object which represents the root of the object graph.  All
:term:`traversal` will begin at this root object.  The root object is
usually a *mapping* object (such as a Python dictionary).

.. note:: If a :term:`root factory` is passed to the :mod:`repoze.bfg`
   :term:`Configurator` constructor as the value ``None``, a *default*
   root factory is used.  This is most useful when you're using
   :term:`URL dispatch` and you don't care very much about traversing
   any particular graph to resolve URLs to code.  It is also possible
   to use traversal and URL dispatch together.  When both a root
   factory (and therefore traversal) *and* "routes" declarations (and
   therefore url dispatch) are used, the url dispatch routes are
   checked first, and if none match, :mod:`repoze.bfg` will fall back
   to using traversal to attempt to map the request to a view.  If the
   name ``*traverse`` is in a route's ``path`` pattern, when it is
   matched, it is also possible to do traversal *after* a route has
   been matched.  See :ref:`hybrid_chapter` for more information.

.. warning:: In :mod:`repoze.bfg` 1.0 and prior versions, the root
   factory was passed a term WSGI *environment* object (a dictionary)
   while in :mod:`repoze.bfg` 1.1+ it is passed a :term:`request`
   object.  For backwards compatibility purposes, the request object
   passed to the root factory has a dictionary-like interface that
   emulates the WSGI environment, so code expecting the argument to be
   a dictionary will continue to work.

.. sidebar:: Emulating the Default Root Factory

   For purposes of understanding the default root factory better,
   we'll note that you can emulate the default root factory by using
   this code as an explicit root factory in your application setup:

   .. code-block:: python
      :linenos:

      class Root(object):
          def __init__(self, request):
              pass

      config = Configurator(root_factory=Root)

   The default root factory is just a really stupid object that has no
   behavior or state.

Using :term:`traversal` against an application that uses the object
graph supplied by the default root object is not very interesting,
because the default root object has no children.  In a more complex
:mod:`repoze.bfg` application, a root factory would be supplied which
would return an object that had children capable of being traversed,
and therefore there might be many :term:`context` objects to which
URLs might resolve, depending on the URL path.  However, in this toy
application, there's exactly one object in our object graph; the
default root object.  Therefore, there can only ever be one context:
the :term:`root` object itself.

We have only a single :term:`default view` registered (the
registration for the ``hello_world`` view callable).  Due to this set
of circumstances, you can consider the sole possible URL that will
resolve to a :term:`default view` in this application the root URL
``'/'``.  It is the only URL that will resolve to the :term:`view
name` of ``''`` (the empty string) when the default object graph is
traversed.

We have only a single view registered for the :term:`view name`
``goodbye`` (the registration for the ``goodbye_world`` view
callable).  Due to this set of circumstances, you can consider the
sole possible URL that will resolve to the ``goodbye_world`` in this
application the URL ``'/goodbye'`` because it is the only URL that
will result in the :term:`view name` of ``goodbye`` when the default
object graph is traversed.


Items contained within the object graph are sometimes analogous to the
concept of :term:`model` objects used by many other frameworks (and
:mod:`repoze.bfg` APIs often refers to them as "models", as well).
They are typically instances of Python classes.

.. index::
   single: traversal behavior

.. _traversal_behavior:

:mod:`repoze.bfg` Traversal Behavior
-------------------------------------

We need to use an analogy to clarify how :mod:`repoze.bfg` traversal
works against an arbitrary object graph.

Let's imagine an inexperienced UNIX computer user, wishing only to use
the command line to find a file and to invoke the ``cat`` command
against that file.  Because he is inexperienced, the only commands he
knows how to use are ``cd``, which changes the current directory and
``cat``, which prints the contents of a file.  And because he is
inexperienced, he doesn't understand that ``cat`` can take an absolute
path specification as an argument, so he doesn't know that you can
issue a single command command ``cat /an/absolute/path`` to get the
desired result.  Instead, this user believes he must issue the ``cd``
command, starting from the root, for each intermediate path segment,
*even the path segment that represents the file itself*.  Once he gets
an error (because you cannot successfully ``cd`` into a file), he knows
he has reached the file he wants, and he will be able to execute
``cat`` against the resulting path segment.

This inexperienced user's attempt to execute ``cat`` against the file
named ``/fiz/buz/myfile`` might be to issue the following set of UNIX
commands:

.. code-block::  text

   cd /
   cd fiz
   cd buz
   cd myfile

The user now know he has found a *file*, because the ``cd`` command
issues an error when he executed ``cd myfile``.  Now he knows that he
can run the ``cat`` command:

.. code-block::  text

   cat myfile

The contents of ``myfile`` are now printed on the user's behalf.

:mod:`repoze.bfg` is very much like this inexperienced UNIX user as it
uses :term:`traversal` against an object graph.  In this analogy, we
can map the ``cat`` program to the :mod:`repoze.bfg` concept of a
:term:`view callable`: it is a program that can be run against some
:term:`context`.  The file being operated on in this analogy is the
:term:`context` object; the context is the "last node found" in a
traversal.  The directory structure is the object graph being
traversed.  The act of progressively changing directories to find the
file as well as the handling of a ``cd`` error as a stop condition is
analogous to :term:`traversal`.

The object graph is traversed, beginning at a root object, represented
by the root URL (``/``); if there are further path segments in the
path info of the request being processed, the root object's
``__getitem__`` is called with the next path segment, and it is
expected to return another graph object.  The resulting object's
``__getitem__`` is called with the very next path segment, and it is
expected to return another graph object.  This happens *ad infinitum*
until all path segments are exhausted.  If at any point during
traversal any node in the graph doesn't *have* a ``__getitem__``
method, or if the ``__getitem__`` of a node raises a :exc:`KeyError`,
traversal ends immediately, and the node becomes the :term:`context`.

The object graph consists of *container* nodes and *leaf* nodes.
There is only one difference between a *container* node and a *leaf*
node: *container* nodes possess a ``__getitem__`` method while *leaf*
nodes do not.  The ``__getitem__`` method was chosen as the signifying
difference between the two types of nodes because the presence of this
method is how Python itself typically determines whether an object is
"containerish" or not.

Each container node is presumed to be willing to return a child node
or raise a ``KeyError`` based on a name passed to its ``__getitem__``.

No leaf-level instance is required to have a ``__getitem__``.  If
leaf-level instances happen to have a ``__getitem__`` (through some
historical inequity), you should subclass these node types and cause
their ``__getitem__`` methods to simply raise a ``KeyError``.  Or just
disuse them and think up another strategy.

Usually, the traversal root is a *container* node, and as such it
contains other nodes.  However, it doesn't *need* to be a container.
Your object graph can be as shallow or as deep as you require.

Traversal "stops" when :mod:`repoze.bfg` either reaches a leaf level
model instance in your object graph or when the path segments implied
by the URL "run out".  The object that traversal "stops on" becomes
the :term:`context`.

.. _how_bfg_traverses:

How :mod:`repoze.bfg` Processes a Request Using Traversal
---------------------------------------------------------

When a user requests a page from your :mod:`repoze.bfg` -powered
application, the system uses this algorithm to determine which Python
code to execute:

#.  The request for the page is presented to the :mod:`repoze.bfg`
    :term:`router` in terms of a standard :term:`WSGI` request, which
    is represented by a WSGI environment and a ``start_response``
    callable.

#.  The router creates a :term:`request` object based on the WSGI
    environment.

#.  The :term:`root factory` is called with the :term:`request`.  It
    returns a :term:`root` object.

#.  The router uses the WSGI environment's ``PATH_INFO`` information
    to determine the path segments to traverse.  The leading slash is
    stripped off ``PATH_INFO``, and the remaining path segments are
    split on the slash character to form a traversal sequence, so a
    request with a ``PATH_INFO`` variable of ``/a/b/c`` maps to the
    traversal sequence ``[u'a', u'b', u'c']``.  Note that each of the
    path segments in the sequence is converted to Unicode using the
    UTF-8 decoding (if the decoding fails, a :exc:`TypeError` is
    raised).

#.  :term:`Traversal` begins at the root object returned by the root
    factory.  For the traversal sequence ``[u'a', u'b', u'c']``, the
    root object's ``__getitem__`` is called with the name ``a``.
    Traversal continues through the sequence.  In our example, if the
    root object's ``__getitem__`` called with the name ``a`` returns
    an object (aka "object ``a``"), that object's ``__getitem__`` is
    called with the name ``b``.  If object A returns an object when
    asked for ``b``, "object ``b``"'s ``__getitem__`` is then asked
    for the name ``c``, and may return "object ``c``".

#.  Traversal ends when a) the entire path is exhausted or b) when any
    graph element raises a :exc:`KeyError` from its ``__getitem__`` or
    c) when any non-final path element traversal does not have a
    ``__getitem__`` method (resulting in a :exc:`NameError`) or d)
    when any path element is prefixed with the set of characters
    ``@@`` (indicating that the characters following the ``@@`` token
    should be treated as a :term:`view name`).

#.  When traversal ends for any of the reasons in the previous step,
    the the last object found during traversal is deemed to be the
    :term:`context`.  If the path has been exhausted when traversal
    ends, the :term:`view name` is deemed to be the empty string
    (``''``).  However, if the path was *not* exhausted before
    traversal terminated, the first remaining path element is treated
    as the view name.

    Any subsequent path elements after the view name are deemed the
    :term:`subpath`.  The subpath is always a sequence of path
    segments that come from ``PATH_INFO`` that are "left over" after
    traversal has completed. For instance, if ``PATH_INFO`` was
    ``/a/b`` and the root returned an "object ``a``", and "object
    ``a``" subsequently returned an "object ``b``", the router deems
    that the context is "object ``b``", the view name is the empty
    string, and the subpath is the empty sequence.  On the other hand,
    if ``PATH_INFO`` was ``/a/b/c`` and "object ``a``" was found but
    raised a ``KeyError`` for the name ``b``, the router deems that
    the context is "object ``a``", the view name is ``b`` and the
    subpath is ``('c',)``.

#.  If a :term:`authorization policy` is configured, the router
    performs a permission lookup.  If a permission declaration is
    found for the view name and context implied by the current
    request, the :term:`authorization policy` is consulted to see if
    the "current user" (as determined by the the active
    :term:`authentication policy`) can perform the action.  If he can,
    processing continues.  If he cannot, the :term:`forbidden view` is
    called (see also :ref:`changing_the_forbidden_view`).

#.  Armed with the context, the view name, and the subpath, the router
    performs a view lookup.  It attempts to look up a view from the
    :mod:`repoze.bfg` :term:`application registry` using the
    :term:`view name`, the :term:`context`, and the :term:`request`.
    If a view function is found, it is called with the context and the
    request.  It returns a response, which is fed back upstream.  If a
    view is not found, the :term:`not found view` is called (see
    :ref:`changing_the_notfound_view`).

In either case, the result is returned upstream via the :term:`WSGI`
protocol.

.. image:: modelgraphtraverser.png

.. index::
   pair: traversal; example

A Traversal Example
-------------------

Let's pretend the user asks for
``http://example.com/foo/bar/baz/biz/buz.txt``. Let's pretend that the
request's ``PATH_INFO`` in that case is ``/foo/bar/baz/biz/buz.txt``.
Let's further pretend that when this request comes in that we're
traversing the following graph::

  /--
     |
     |-- foo
          |
          ----bar

Here's what happens:

- :mod:`repoze.bfg` traverses the root, and attempts to find "foo",
  which it finds.

- :mod:`repoze.bfg` traverses "foo", and attempts to find "bar", which
  it finds.

- :mod:`repoze.bfg` traverses bar, and attempts to find "baz", which
  it does not find ("bar" raises a :exc:`KeyError` when asked for
  "baz").

The fact that it does not find "baz" at this point does not signify an
error condition.  It signifies that:

- the :term:`context` is "bar" (the context is the last item found
  during traversal).

- the :term:`view name` is ``baz``

- the :term:`subpath` is ``('biz', 'buz.txt')``

Because it's the "context", :mod:`repoze.bfg` examines "bar" to find
out what "type" it is. Let's say it finds that the context is an
``Bar`` type (because "bar" happens to be an instance of the class
``Bar``).

Using the :term:`view name` (``baz``) and the type, it asks the
:term:`application registry` this question:

- Please find me a :term:`view callable` registered using a
  :term:`view configuration` with the name "baz" that can be used for
  the class ``Bar``.

Let's say it finds no matching view type.  It then returns the result
of the :term:`not found view`.  The request ends.

However, for this graph::

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

- :mod:`repoze.bfg` traverses "foo", and attempts to find "bar", which
  it finds.

- :mod:`repoze.bfg` traverses "bar", and attempts to find "baz", which
  it finds.

- :mod:`repoze.bfg` traverses "baz", and attempts to find "biz", which
  it finds.

- :mod:`repoze.bfg` traverses "biz", and attempts to find "buz.txt"
  which it does not find.

The fact that it does not find "buz.txt" at this point does not
signify an error condition.  It signifies that:

- the :term:`context` is "biz" (the context is the last item found
  during traversal).

- the :term:`view name` is "buz.txt"

- the :term:`subpath` is an empty sequence ( ``()`` ).

Because it's the "context", :mod:`repoze.bfg` examines "biz" to find
out what "type" it is. Let's say it finds that the context is a
``Biz`` type (because "biz" is an instance of the Python class
``Biz``).

Using the :term:`view name` (``buz.txt``) and the type, it asks the
:term:`application registry` this question:

- Please find me a :term:`view callable` registered with a :term:`view
  configuration` with the name ``buz.txt`` that can be used for class
  ``Biz``.

Let's say that question is answered "here you go, here's a bit of code
that is willing to deal with that case", and returns a :term:`view
callable`.  The view callable is passed the "biz" object as the
"context" and the current :term:`WebOb` :term:`request` as the
"request".  It returns a :term:`response`.

There are two special cases:

- During traversal you will often end up with a :term:`view name` that
  is the empty string.  This indicates that :mod:`repoze.bfg` should
  look up the :term:`default view`.  The default view is a view that is
  registered with no name or a view which is registered with a name
  that equals the empty string.

- If any path segment element begins with the special characters
  ``@@`` (think of them as goggles), the value of that segment minus
  the goggle characters is considered the :term:`view name`
  immediately and traversal stops there.  This allows you to address
  views that may have the same names as model instance names in the
  graph unambiguously.

.. index::
   pair: debugging; not found errors

.. index::
   pair: traversal; unicode

Traversal and Unicode
---------------------

The traversal machinery by default attempts to first URL-unquote and
then Unicode-decode each path element in ``PATH_INFO`` from its
natural byte string (``str`` type) representation.  URL unquoting is
performed using the Python standard library ``urllib.unquote``
function.  Conversion from a URL-decoded string into Unicode is
attempted using the UTF-8 encoding.  If any URL-unquoted path segment
in ``PATH_INFO`` is not decodeable using the UTF-8 decoding, a
TypeError is raised.  A segment will be fully URL-unquoted and
UTF8-decoded before it is passed it to the ``__getitem__`` of any
model object during traversal.

References
----------

For a contextual example of how :term:`traversal` can be used to
create a :mod:`repoze.bfg` application, see the
:ref:`bfg_wiki_tutorial`.
