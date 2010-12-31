.. _traversal_chapter:

Traversal
=========

A :term:`traversal` uses the URL (Universal Resource Locator) to find a
:term:`resource` located in a :term:`resource tree`, which is a set of
nested dictionary-like objects.  Traversal is done by using each segment
of the path portion of the URL to navigate through the :term:`resource
tree`.  You might think of this as looking up files and directories in a
file system.  Traversal walks down the path until it finds a published
"directory" or "file".  The resource we find as the result of a
traversal becomes the :term:`context`.  Then, the :term:`view lookup`
subsystem is used to find some view code willing "publish" this
resource.

Using :term:`Traversal` to map a URL to code is optional.  It is often
less easy to understand than :term:`URL dispatch`, so if you're a rank
beginner, it probably makes sense to use URL dispatch to map URLs to
code instead of traversal.  In that case, you can skip this chapter.

.. index::
   single: traversal details

Traversal Details
-----------------

:term:`Traversal` is dependent on information in a :term:`request` object.
Every :term:`request` object contains URL path information in the
``PATH_INFO`` portion of the :term:`WSGI` environment.  The ``PATH_INFO``
portion of the WSGI environment is the portion of a request's URL following
the hostname and port number, but before any query string elements or
fragment element.  For example the ``PATH_INFO`` portion of the URL
``http://example.com:8080/a/b/c?foo=1`` is ``/a/b/c``.

Traversal treats the ``PATH_INFO`` segment of a URL as a sequence of path
segments.  For example, the ``PATH_INFO`` string ``/a/b/c`` is converted to
the sequence ``['a', 'b', 'c']``.

After the path info is converted, a lookup is performed against the resource
tree for each path segment.  Each lookup uses the ``__getitem__`` method of a
resource in the tree.

For example, if the path info sequence is ``['a', 'b', 'c']``:

- :term:`Traversal` pops the first element (``a``) from the path segment
  sequence and attempts to call the root resource's ``__getitem__`` method
  using that value (``a``) as an argument; we'll presume it succeeds.

- When the root resource's ``__getitem__`` succeeds it will return another
  resource, which we'll call "A".  The :term:`context` temporarily becomes
  the "A" resource.

- The next segment (``b``) is popped from the path sequence, and the "A"
  resource's ``__getitem__`` is called with that value (``b``) as an
  argument; we'll presume it succeeds.

- When the "A" resource's ``__getitem__`` succeeds it will return another
  resource, which we'll call "B".  The :term:`context` temporarily becomes
  the "B" resource.

This process continues until the path segment sequence is exhausted or a path
element cannot be resolved to a resource.  In either case, a :term:`context`
resource is chosen.

Traversal "stops" when it either reaches a leaf level resource in your
resource tree or when the path segments from the URL "run out".  The
resource that traversal "stops on" becomes the :term:`context`.  If at any
point during traversal any resource in the tree doesn't have a
``__getitem__`` method, or if the ``__getitem__`` method of a resource raises
a :exc:`KeyError`, traversal ends immediately, and that resource becomes the
:term:`context`.

The results of a :term:`traversal` also include a :term:`view name`.  The
:term:`view name` is the *first* URL path segment in the set of ``PATH_INFO``
segments "left over" in the path segment list popped by the traversal process
*after* traversal finds a context resource.

The combination of the context resource and the :term:`view name` found
via traversal is used later in the same request by the :term:`view
lookup` subsystem to find a :term:`view callable`.  How :app:`Pyramid`
performs view lookup is explained within the :ref:`views_chapter`
chapter.

.. index::
   single: object tree
   single: traversal tree
   single: resource tree

.. _the_resource_tree:

The Resource Tree
-----------------

When your application uses :term:`traversal` to resolve URLs to code, the
application must supply a :term:`resource tree` to :app:`Pyramid`.  The
resource tree is a set of nested dictionary-like objects. The root of the
tree is represented by a :term:`root` resource.  The tree is effectively a
nested set of dictionary-like objects.

In order to supply a root resource for an application, at system startup
time, the :app:`Pyramid` :term:`Router` is configured with a callback known
as a :term:`root factory`.  The root factory is supplied by the application
developer as the ``root_factory`` argument to the application's
:term:`Configurator`.

Here's an example of a simple root factory:

.. code-block:: python
   :linenos:

   class Root(dict):
       def __init__(self, request):
           pass

Here's an example of using this root factory within startup configuration, by
passing it to an instance of a :term:`Configurator` named ``config``:

.. code-block:: python
   :linenos:

   config = Configurator(root_factory=Root)

Using the ``root_factory`` argument to a :class:`pyramid.config.Configurator`
constructor tells your :app:`Pyramid` application to call this root factory
to generate a root resource whenever a request enters the application.  This
root factory is also known as the global root factory.  A root factory can
alternately be passed to the ``Configurator`` as a :term:`dotted Python name`
which refers to a root factory defined in a different module.

A root factory is passed a :term:`request` object and it is expected to
return an object which represents the root of the resource tree.  All
:term:`traversal` will begin at this root resource.  Usually a root factory
for a traversal-based application will be more complicated than the above
``Root`` class; in particular it may be associated with a database connection
or another persistence mechanism.

If no :term:`root factory` is passed to the :app:`Pyramid`
:term:`Configurator` constructor, or the ``root_factory`` is specified as the
value ``None``, a *default* root factory is used.  The default root factory
always returns a resource that has no child resources.

.. sidebar:: Emulating the Default Root Factory

   For purposes of understanding the default root factory better, we'll note
   that you can emulate the default root factory by using this code as an
   explicit root factory in your application setup:

   .. code-block:: python
      :linenos:

      class Root(object):
          def __init__(self, request):
              pass

      config = Configurator(root_factory=Root)

   The default root factory is just a really stupid object that has no
   behavior or state.  Using :term:`traversal` against an application that
   uses the resource tree supplied by the default root resource is not very
   interesting, because the default root resource has no children.  Its
   availability is more useful when you're developing an application using
   :term:`URL dispatch`.

.. note::

   If the items contained within the resource tree are "persistent" (they
   have state that lasts longer than the execution of a single process), they
   become analogous to the concept of :term:`domain model` objects used by
   many other frameworks.

The resource tree consists of *container* resources and *leaf* resources.
There is only one difference between a *container* resource and a *leaf*
resource: *container* resources possess a ``__getitem__`` method (making it
"dictionary-like") while *leaf* resources do not.  The ``__getitem__`` method
was chosen as the signifying difference between the two types of resources
because the presence of this method is how Python itself typically determines
whether an object is "containerish" or not (dictionary objects are
"containerish").

Each container resource is presumed to be willing to return a child resource
or raise a ``KeyError`` based on a name passed to its ``__getitem__``.

Leaf-level instances must not have a ``__getitem__``.  If instances that
you'd like to be leaves already happen to have a ``__getitem__`` through some
historical inequity, you should subclass these resource types and cause their
``__getitem__`` methods to simply raise a ``KeyError``.  Or just disuse them
and think up another strategy.

Usually, the traversal root is a *container* resource, and as such it
contains other resources.  However, it doesn't *need* to be a container.
Your resource tree can be as shallow or as deep as you require.

In general, the resource tree is traversed beginning at its root resource
using a sequence of path elements described by the ``PATH_INFO`` of the
current request; if there are path segments, the root resource's
``__getitem__`` is called with the next path segment, and it is expected to
return another resource.  The resulting resource's ``__getitem__`` is called
with the very next path segment, and it is expected to return another
resource.  This happens *ad infinitum* until all path segments are exhausted.

.. index::
   single: traversal algorithm
   single: view lookup

.. _traversal_algorithm:

The Traversal Algorithm
-----------------------

This section will attempt to explain the :app:`Pyramid` traversal algorithm.
We'll provide a description of the algorithm, a diagram of how the algorithm
works, and some example traversal scenarios that might help you understand
how the algorithm operates against a specific resource tree.

We'll also talk a bit about :term:`view lookup`.  The :ref:`views_chapter`
chapter discusses :term:`view lookup` in detail, and it is the canonical
source for information about views.  Technically, :term:`view lookup` is a
:app:`Pyramid` subsystem that is separated from traversal entirely.  However,
we'll describe the fundamental behavior of view lookup in the examples in the
next few sections to give you an idea of how traversal and view lookup
cooperate, because they are almost always used together.

.. index::
   single: view name
   single: context
   single: subpath
   single: root factory
   single: default view

A Description of The Traversal Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a user requests a page from your :mod:`traversal` -powered application,
the system uses this algorithm to find a :term:`context` resource and a
:term:`view name`.

#.  The request for the page is presented to the :app:`Pyramid`
    :term:`router` in terms of a standard :term:`WSGI` request, which is
    represented by a WSGI environment and a WSGI ``start_response`` callable.

#.  The router creates a :term:`request` object based on the WSGI
    environment.

#.  The :term:`root factory` is called with the :term:`request`.  It returns
    a :term:`root` resource.

#.  The router uses the WSGI environment's ``PATH_INFO`` information to
    determine the path segments to traverse.  The leading slash is stripped
    off ``PATH_INFO``, and the remaining path segments are split on the slash
    character to form a traversal sequence.

    The traversal algorithm by default attempts to first URL-unquote and then
    Unicode-decode each path segment derived from ``PATH_INFO`` from its
    natural byte string (``str`` type) representation.  URL unquoting is
    performed using the Python standard library ``urllib.unquote`` function.
    Conversion from a URL-decoded string into Unicode is attempted using the
    UTF-8 encoding.  If any URL-unquoted path segment in ``PATH_INFO`` is not
    decodeable using the UTF-8 decoding, a :exc:`TypeError` is raised.  A
    segment will be fully URL-unquoted and UTF8-decoded before it is passed
    it to the ``__getitem__`` of any resource during traversal.

    Thus, a request with a ``PATH_INFO`` variable of ``/a/b/c`` maps to the
    traversal sequence ``[u'a', u'b', u'c']``.

#.  :term:`Traversal` begins at the root resource returned by the root
    factory.  For the traversal sequence ``[u'a', u'b', u'c']``, the root
    resource's ``__getitem__`` is called with the name ``a``.  Traversal
    continues through the sequence.  In our example, if the root resource's
    ``__getitem__`` called with the name ``a`` returns a resource (aka
    "resource ``a``"), that resource's ``__getitem__`` is called with the
    name ``b``.  If resource A returns a resource when asked for ``b``,
    "resource ``b``"'s ``__getitem__`` is then asked for the name ``c``, and
    may return "resource ``c``".

#.  Traversal ends when a) the entire path is exhausted or b) when any
    resouce raises a :exc:`KeyError` from its ``__getitem__`` or c) when any
    non-final path element traversal does not have a ``__getitem__`` method
    (resulting in a :exc:`NameError`) or d) when any path element is prefixed
    with the set of characters ``@@`` (indicating that the characters
    following the ``@@`` token should be treated as a :term:`view name`).

#.  When traversal ends for any of the reasons in the previous step, the last
    resource found during traversal is deemed to be the :term:`context`.  If
    the path has been exhausted when traversal ends, the :term:`view name` is
    deemed to be the empty string (``''``).  However, if the path was *not*
    exhausted before traversal terminated, the first remaining path segment
    is treated as the view name.

#.  Any subsequent path elements after the :term:`view name` is found are
    deemed the :term:`subpath`.  The subpath is always a sequence of path
    segments that come from ``PATH_INFO`` that are "left over" after
    traversal has completed.

Once the :term:`context` resource, the :term:`view name`, and associated
attributes such as the :term:`subpath` are located, the job of
:term:`traversal` is finished.  It passes back the information it obtained to
its caller, the :app:`Pyramid` :term:`Router`, which subsequently invokes
:term:`view lookup` with the context and view name information.

The traversal algorithm exposes two special cases:

- You will often end up with a :term:`view name` that is the empty string as
  the result of a particular traversal.  This indicates that the view lookup
  machinery should look up the :term:`default view`.  The default view is a
  view that is registered with no name or a view which is registered with a
  name that equals the empty string.

- If any path segment element begins with the special characters ``@@``
  (think of them as goggles), the value of that segment minus the goggle
  characters is considered the :term:`view name` immediately and traversal
  stops there.  This allows you to address views that may have the same names
  as resource names in the tree unambiguously.

Finally, traversal is responsible for locating a :term:`virtual root`.  A
virtual root is used during "virtual hosting"; see the
:ref:`vhosting_chapter` chapter for information.  We won't speak more about
it in this chapter.

.. image:: resourcetreetraverser.png

.. index::
   single: traversal examples

Traversal Algorithm Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No one can be expected to understand the traversal algorithm by analogy and
description alone, so let's examine some traversal scenarios that use
concrete URLs and resource tree compositions.

Let's pretend the user asks for
``http://example.com/foo/bar/baz/biz/buz.txt``. The request's ``PATH_INFO``
in that case is ``/foo/bar/baz/biz/buz.txt``.  Let's further pretend that
when this request comes in that we're traversing the following resource tree:

.. code-block:: text

  /--
     |
     |-- foo
          |
          ----bar

Here's what happens:

- :mod:`traversal` traverses the root, and attempts to find "foo", which it
  finds.

- :mod:`traversal` traverses "foo", and attempts to find "bar", which it
  finds.

- :mod:`traversal` traverses bar, and attempts to find "baz", which it does
  not find (the "bar" resource raises a :exc:`KeyError` when asked for
  "baz").

The fact that it does not find "baz" at this point does not signify an error
condition.  It signifies that:

- the :term:`context` is the "bar" resource (the context is the last resource
  found during traversal).

- the :term:`view name` is ``baz``

- the :term:`subpath` is ``('biz', 'buz.txt')``

At this point, traversal has ended, and :term:`view lookup` begins.

Because it's the "context" resource, the view lookup machinery examines "bar"
to find out what "type" it is. Let's say it finds that the context is a
``Bar`` type (because "bar" happens to be an instance of the class ``Bar``).
Using the :term:`view name` (``baz``) and the type, view lookup asks the
:term:`application registry` this question:

- Please find me a :term:`view callable` registered using a :term:`view
  configuration` with the name "baz" that can be used for the class ``Bar``.

Let's say that view lookup finds no matching view type.  In this
circumstance, the :app:`Pyramid` :term:`router` returns the result of the
:term:`not found view` and the request ends.

However, for this tree:

.. code-block:: text

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

- :mod:`traversal` traverses "foo", and attempts to find "bar", which it
  finds.

- :mod:`traversal` traverses "bar", and attempts to find "baz", which it
  finds.

- :mod:`traversal` traverses "baz", and attempts to find "biz", which it
  finds.

- :mod:`traversal` traverses "biz", and attempts to find "buz.txt" which it
  does not find.

The fact that it does not find a resource related to "buz.txt" at this point
does not signify an error condition.  It signifies that:

- the :term:`context` is the "biz" resource (the context is the last resource
  found during traversal).

- the :term:`view name` is "buz.txt"

- the :term:`subpath` is an empty sequence ( ``()`` ).

At this point, traversal has ended, and :term:`view lookup` begins.

Because it's the "context" resource, the view lookup machinery examines the
"biz" resource to find out what "type" it is. Let's say it finds that the
resource is a ``Biz`` type (because "biz" is an instance of the Python class
``Biz``).  Using the :term:`view name` (``buz.txt``) and the type, view
lookup asks the :term:`application registry` this question:

- Please find me a :term:`view callable` registered with a :term:`view
  configuration` with the name ``buz.txt`` that can be used for class
  ``Biz``.

Let's say that question is answered by the application registry; in such a
situation, the application registry returns a :term:`view callable`.  The
view callable is then called with the current :term:`WebOb` :term:`request`
as the sole argument: ``request``; it is expected to return a response.

.. sidebar:: The Example View Callables Accept Only a Request; How Do I Access the Context Resource?

   Most of the examples in this book assume that a view callable is typically
   passed only a :term:`request` object.  Sometimes your view callables need
   access to the :term:`context` resource, especially when you use
   :term:`traversal`.  You might use a supported alternate view callable
   argument list in your view callables such as the ``(context, request)``
   calling convention described in
   :ref:`request_and_context_view_definitions`.  But you don't need to if you
   don't want to.  In view callables that accept only a request, the
   :term:`context` resource found by traversal is available as the
   ``context`` attribute of the request object, e.g. ``request.context``.
   The :term:`view name` is available as the ``view_name`` attribute of the
   request object, e.g. ``request.view_name``.  Other :app:`Pyramid`
   -specific request attributes are also available as described in
   :ref:`special_request_attributes`.

References
----------

A tutorial showing how :term:`traversal` can be used within a :app:`Pyramid`
application exists in :ref:`bfg_wiki_tutorial`.

See the :ref:`views_chapter` chapter for detailed information about
:term:`view lookup`.

The :mod:`pyramid.traversal` module contains API functions that deal with
traversal, such as traversal invocation from within application code.

The :func:`pyramid.url.resource_url` function generates a URL when given a
resource retrieved from a resource tree.

