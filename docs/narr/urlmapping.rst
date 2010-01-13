.. index::
   triple: differences; URL dispatch; traversal
   pair: mapping; URLs

.. _url_mapping_chapter:

Mapping URLs to Code
--------------------

:mod:`repoze.bfg` supports two methods by which a URL can be mapped to
code: :term:`URL dispatch` and :term:`traversal`.

.. note::

   The :mod:`repoze.bfg` support for :term:`URL dispatch` was inspired
   by the :term:`Routes` system used by :term:`Pylons`.
   :mod:`repoze.bfg` support for :term:`traversal` was inspired by
   :term:`Zope`.

:term:`URL dispatch` is convenient and straightforward: an incoming
URL is checked against a list of potential matches in a predefined
order.  When a match is found, it means that a particular :term:`view
callable` will be invoked.

:term:`URL dispatch` can easily handle URLs such as
``http://example.com/members/Chris``, where it's assumed that each
item "below" ``members`` in the URL represents a member in the system.
You just match everything "below" ``members`` to a particular
:term:`view callable`.  For example, you might configure URL dispatch
within :mod:`repoze.bfg` to match against the following URL patterns:

.. code-block:: text

   members/:membername
   archives/:year/:month/:day

In this configuration, there will be exactly two types of URLs that
will be meaningful to your application: URLs that start with
``/members`` which are followed by a path segment containing a
member's name.  And URLs that start with ``/archives`` and have
subsequent path elements that represent a year, month, and day.  Each
route pattern will be mapped to a specific :term:`view callable`.

URL dispatch is very straightforward.  When you limit your application
to using URL dispatch, you know every URL that your application might
generate or respond to, and all the URL matching elements are listed
in a single place.

URL dispatch is not very good, however, at inferring the difference
between sets of URLs such as these:

.. code-block:: text

   http://example.com/members/Chris/document
   http://example.com/members/Chris/stuff/page

If you'd like the ``document`` in the first URL above to represent a
PDF document, and ``/stuff/page`` in the second to represent an
OpenOffice document in a "stuff" folder, it's hard to express this
using URL dispatch.  It takes more pattern matching assertions to be
able to make hierarchies like these work in URL-dispatch based
systems, and some assertions just aren't possible.  Essentially,
URL-dispatch based systems just don't deal very well with URLs that
represent arbitrary-depth hierarchies.

However, the other URL mapping mode supported by :mod:`repoze.bfg`,
named :term:`traversal`, *does* work well for URLs that represent
arbitrary-depth hierarchies.  When traversal is used, each URL segment
represents a single traversal step through an edge of a graph, so a
URL like ``http://example.com/a/b/c`` can be thought of as a graph
traversal on the ``example.com`` site through the edges ``a``, ``b``,
and ``c``.  Since the path segments that compose a URL are addressed
separately, it becomes very easy to form URLs that represent arbitrary
depth hierarchies in a system that uses traversal.

When you're willing to treat your application models as a graph that
can be traversed, it also becomes easy to provide "instance-level
security": you just attach a security declaration to each instance in
the graph.  This is not nearly as easy to do when using URL dispatch.

In essence, the choice to use graph traversal vs. URL dispatch is
largely religious.  Graph traversal dispatch probably just doesn't
make any sense when you possess completely "square" data stored in a
relational database because it requires the construction and
maintenance of a graph and requires that the developer think about
mapping URLs to code in terms of traversing that graph.  However, when
you have a hierarchical data store, using traversal can provide
significant advantages over using URL-based dispatch.

Since :mod:`repoze.bfg` provides support for both approaches, you can
use either as you see fit; you can even combine them together if
necessary.

.. toctree::
   :maxdepth: 2

   traversal
   urldispatch
   hybrid
