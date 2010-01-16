.. index::
   triple: differences; URL dispatch; traversal
   pair: mapping; URLs

.. _urlmapping_chapter:

Mapping URLs to Code
--------------------

In order for a web application to perform any useful action, it needs
some way of finding and invoking code written by the application
developer based on parameters present in the :term:`request`.

:mod:`repoze.bfg` uses two separate but cooperating subsystems to
ultimately find and invoke code written by the application developer:
:term:`context finding` and :term:`view lookup` .

- A :mod:`repoze.bfg` "context finding" subsystem is given a
  :term:`request`; it is responsible for finding a :term:`context`
  object and a :term:`view name` based on information present in the
  request.

- The :mod:`repoze.bfg` view lookup subsystem is provided with a
  :term:`request`, a :term:`context` and a :term:`view name`, and is
  responsible for finding and invoking a :term:`view callable`.  A
  view callable is a specific bit of code that receives the
  :term:`request` and which returns a :term:`response`, written and
  registered by the application developer.

These two subsystems are are used by :mod:`repoze.bfg` serially: a
:term:`context finding` subsystem does its job, then the result of
context finding is passed to the :term:`view lookup` subsystem.  The
view lookup system finds a :term:`view callable` written by an
application developer, and invokes it.  A view callable returns a
:term:`response`.  The response is returned to the requesting user.

.. sidebar::  What Good is A Context Finding Subsystem?

   Many other web frameworks such as :term:`Pylons` or :term:`Django`
   actually collapse the two steps of context finding and view lookup
   into a single step.  In such systems, a URL maps *directly* to a
   view callable.  These systems possess no analogue to a
   context finding subsystem: they are "context-free".  This makes
   them simpler to understand than systems which use "context".
   However, using an explicit context finding step provides extra
   flexibility.  For example, it makes it possible to protect your
   application with declarative context-sensitive instance-level
   :term:`authorization`, which is not well supported in frameworks
   that do not provide a notion of a context.  See the
   :ref:`security_chapter` for more information.

There are two separate context finding subsystems in
:mod:`repoze.bfg`: :term:`traversal` and :term:`URL dispatch`.  The
subsystems are documented within this chapter.  They can be used
separately or they can be combined.

There is only one view lookup subsystem present in :mod:`repoze.bfg`.
It is not documented in this chapter.  Instead, it is documented
within :ref:`views_chapter`.

.. toctree::
   :maxdepth: 2

   traversal
   urldispatch
   hybrid

Should I Use Traversal or URL Dispatch for Context Finding?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

In essence, the choice to use traversal vs. URL dispatch is largely
religious.  Traversal dispatch probably just doesn't make any sense
when you possess completely "square" data stored in a relational
database because it requires the construction and maintenance of a
graph and requires that the developer think about mapping URLs to code
in terms of traversing that graph.  However, when you have a
hierarchical data store, using traversal can provide significant
advantages over using URL-based dispatch.

Since :mod:`repoze.bfg` provides support for both approaches, you can
use either as you see fit; you can even combine them together if
necessary.

