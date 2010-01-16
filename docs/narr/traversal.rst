.. _traversal_chapter:

Traversal
=========

:term:`traversal` is a :term:`context finding` mechanism that is used
by :mod:`repoze.bfg`. :term:`traversal` is the act of finding a
:term:`context` and a :term:`view name` by walking over an *object
graph*, starting from a :term:`root` object, using a :term:`request`
object as a source of path information.

In this chapter, we'll provide a high-level overview of traversal,
we'll explain the concept of an *object graph*, and we'll show how
traversal might be used within an application.

.. index::
   pair: traversal; high-level overview

A High-Level Overview of Traversal
----------------------------------

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
separate :mod:`repoze.bfg` subsystem -- the :term:`view lookup`
subsystem -- to find a :term:`view callable` later within the same
request.  How :mod:`repoze.bfg` performs view lookup is explained
within the :ref:`views_chapter` chapter.

.. index::
   single: object graph
   single: traversal graph
   single: model graph

The Object Graph
----------------

When your application uses :term:`traversal` to resolve URLs to code,
your application must supply an *object graph* to :mod:`repoze.bfg`.

At system startup time, the :mod:`repoze.bfg` :term:`Router` is
configured with a callback known as a :term:`root factory`, supplied
by the application developer as the ``root_factory`` argument to a
:term:`Configurator`.

Here's an example of a simple root factory:

.. code-block:: python
   :linenos:

   class Root(dict):
       def __init__(self, request):
           pass

Here's an example of using this root factory within startup
configuration, by passing it to an instance of a :term:`Configurator`
named ``config``:

.. code-block:: python
   :linenos:

   config = Configurator(root_factory=Root)

Making a declaration like this at startup means that your
:mod:`repoze.bfg` application will call the root factory (in this
case, the class ``Root``) to generate a root object whenever a request
enters the application.  Usually a root factory for a traversal-based
application will be more complicated than the above ``Root`` object;
in particular it may be associated with a database connection or
another persistence mechanism.

A root factory is passed a :term:`request` object and it is expected
to return an object which represents the root of the object graph.
All :term:`traversal` will begin at this root object.  The root object
is often an instance of a class which has a ``__getitem__`` method.

.. warning:: In :mod:`repoze.bfg` 1.0 and prior versions, the root
   factory was passed a term WSGI *environment* object (a dictionary)
   while in :mod:`repoze.bfg` 1.1+ it is passed a :term:`request`
   object.  For backwards compatibility purposes, the request object
   passed to the root factory has a dictionary-like interface that
   emulates the WSGI environment, so code expecting the argument to be
   a dictionary will continue to work.

If a :term:`root factory` is passed to the :mod:`repoze.bfg`
:term:`Configurator` constructor as the value ``None``, a *default*
root factory is used.

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
   behavior or state.  Using :term:`traversal` against an application
   that uses the object graph supplied by the default root object is
   not very interesting, because the default root object has no
   children.  Its availability is more useful when you're developing
   an application using :term:`URL dispatch`.

Items contained within the object graph are sometimes analogous to the
concept of :term:`model` objects used by many other frameworks (and
:mod:`repoze.bfg` APIs often refers to them as "models", as well).
They are typically instances of Python classes.

.. index::
   single: traversal; algorithm

.. _traversal_behavior:

The :mod:`repoze.bfg` Traversal Algorithm
-----------------------------------------

This section will attempt to explain the :mod:`repoze.bfg` traversal
algorithm.  We'll provide an an analogy, a diagram of how the
traversal algorithm works, and some example traversal scenarios that
might aid in understanding how the traversal algorithm operates
against a specific object graph.

The :ref:`views_chapter` chapter discusses :term:`view lookup` in
detail, and it is the canonical source for information about views.
Technically, :term:`traversal` is a :mod:`repoze.bfg` subsystem that
is separated from traversal entirely.  However, we'll describe the
fundamental behavior of view lookup in the examples in the next few
sections to give you an idea of how traversal and view lookup
cooperate, because they are always used cooperatively.

.. index::
   single: traversal analogy

An Analogy
~~~~~~~~~~

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
:term:`context` as the result of :term:`view lookup`.  The file being
operated on in this analogy is the :term:`context` object; the context
is the "last node found" in a traversal.  The directory structure is
the object graph being traversed.  The act of progressively changing
directories to find the file as well as the handling of a ``cd`` error
as a stop condition is analogous to :term:`traversal`.

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

.. index::
   pair: traversal; unicode
   pair: traversal; algorithm

.. _how_bfg_traverses:

The Algorithm
~~~~~~~~~~~~~

When a user requests a page from your :mod:`traversal` -powered
application, the system uses this algorithm to determine which Python
code to execute:

#.  The request for the page is presented to the :mod:`repoze.bfg`
    :term:`router` in terms of a standard :term:`WSGI` request, which
    is represented by a WSGI environment and a WSGI ``start_response``
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
    UTF-8 decoding; if the decoding fails, a :exc:`TypeError` is
    raised.

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

Once :term:`context` and :term:`view name` and associated attributes
such as the :term:`subpath` are located, the job of :term:`traversal`
is finished.  It passes the back the information it obtained to its
caller, the :mod:`repoze.bfg` :term:`Router`, which subsequently
invokes :term:`view lookup` with the context and view name
information.

Note well that the traversal machinery by default attempts to first
URL-unquote and then Unicode-decode each path element in ``PATH_INFO``
from its natural byte string (``str`` type) representation.  URL
unquoting is performed using the Python standard library
``urllib.unquote`` function.  Conversion from a URL-decoded string
into Unicode is attempted using the UTF-8 encoding.  If any
URL-unquoted path segment in ``PATH_INFO`` is not decodeable using the
UTF-8 decoding, a :exc:`TypeError` is raised.  A segment will be fully
URL-unquoted and UTF8-decoded before it is passed it to the
``__getitem__`` of any model object during traversal.

The standard traversal algorithm exposes two special cases:

- You will often end up with a :term:`view name` that is the empty
  string as the result of a particular traversal.  This indicates that
  the view lookup machinery should look up the :term:`default view`.
  The default view is a view that is registered with no name or a view
  which is registered with a name that equals the empty string.

- If any path segment element begins with the special characters
  ``@@`` (think of them as goggles), the value of that segment minus
  the goggle characters is considered the :term:`view name`
  immediately and traversal stops there.  This allows you to address
  views that may have the same names as model instance names in the
  graph unambiguously.

.. image:: modelgraphtraverser.png

.. index::
   pair: traversal; example

Traversal Examples
~~~~~~~~~~~~~~~~~~

No one can be expected to understand the traversal algorithm by
analogy and description alone, so let's examine some traversal
scenarios that use concrete URLs and object graph compositions.

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

- :mod:`traversal` traverses the root, and attempts to find "foo",
  which it finds.

- :mod:`traversal` traverses "foo", and attempts to find "bar", which
  it finds.

- :mod:`traversal` traverses bar, and attempts to find "baz", which it
  does not find ("bar" raises a :exc:`KeyError` when asked for "baz").

The fact that it does not find "baz" at this point does not signify an
error condition.  It signifies that:

- the :term:`context` is "bar" (the context is the last item found
  during traversal).

- the :term:`view name` is ``baz``

- the :term:`subpath` is ``('biz', 'buz.txt')``

At this point, traversal has ended, and :term:`view lookup` begins.

Because it's the "context", the view lookup machinery examines "bar"
to find out what "type" it is. Let's say it finds that the context is
an ``Bar`` type (because "bar" happens to be an instance of the class
``Bar``).  Using the :term:`view name` (``baz``) and the type, view
lookup asks the :term:`application registry` this question:

- Please find me a :term:`view callable` registered using a
  :term:`view configuration` with the name "baz" that can be used for
  the class ``Bar``.

Let's say that view lookup finds no matching view type.  In this
circumstance, the :mod:`repoze.bfg` :term:`router` returns the result
of the :term:`not found view` and the request ends.

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

- :mod:`traversal` traverses "foo", and attempts to find "bar", which
  it finds.

- :mod:`traversal` traverses "bar", and attempts to find "baz", which
  it finds.

- :mod:`traversal` traverses "baz", and attempts to find "biz", which
  it finds.

- :mod:`traversal` traverses "biz", and attempts to find "buz.txt"
  which it does not find.

The fact that it does not find "buz.txt" at this point does not
signify an error condition.  It signifies that:

- the :term:`context` is "biz" (the context is the last item found
  during traversal).

- the :term:`view name` is "buz.txt"

- the :term:`subpath` is an empty sequence ( ``()`` ).

At this point, traversal has ended, and :term:`view lookup` begins.

Because it's the "context", the view lookup machinery examines "biz"
to find out what "type" it is. Let's say it finds that the context is
a ``Biz`` type (because "biz" is an instance of the Python class
``Biz``).  Using the :term:`view name` (``buz.txt``) and the type,
view lookup asks the :term:`application registry` this question:

- Please find me a :term:`view callable` registered with a :term:`view
  configuration` with the name ``buz.txt`` that can be used for class
  ``Biz``.

Let's say that question is answered by the application registry with
the equivalent of "here you go, here's a bit of code that is willing
to deal with that case"; the application registry returns a
:term:`view callable`.  The view callable is then called with the
current :term:`WebOb` :term:`request` as the sole argument:
``request``; it is expected to return a response.

.. sidebar:: The Example View Callables Accept Only a Request; How Do I Access the Context?

   Most of the examples in this book assume that a view callable is
   typically passed only a :term:`request` object.  Sometimes your
   view callables need access to the :term:`context`, especially when
   you use :term:`traversal`.  You might use a supported alternate
   view callable argument list in your view callables such as the
   ``(context, request)`` calling convention described in
   :ref:`request_and_context_view_definitions`.  But you don't need to
   if you don't want to.  In view callables that accept only a
   request, the :term:`context` found by traversal is available as the
   ``context`` attribute of the request object.  The :term:`view name`
   is available as the ``view_name`` attribute of the request object.
   Other :mod:`repoze.bfg` -speficic request attributes are also
   available as described in :ref:`special_request_attributes`.

References
----------

A tutorial showing how :term:`traversal` can be used to create a
:mod:`repoze.bfg` application exists in :ref:`bfg_wiki_tutorial`.

See the :ref:`views_chapter` chapter for detailed information about
:term:`view lookup`.
