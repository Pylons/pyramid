.. index::
   single: context finding

.. _contextfinding_chapter:

Context Finding and View Lookup
-------------------------------

In order for a web application to perform any useful action, the web
framework must provide a mechanism to find and invoke code written by
the application developer based on parameters present in the
:term:`request`.

:mod:`repoze.bfg` uses two separate but cooperating subsystems to find
and invoke code written by the application developer: :term:`context
finding` and :term:`view lookup`.

- A :mod:`repoze.bfg` :term:`context finding` subsystem is given a
  :term:`request`; it is responsible for finding a :term:`context`
  object and a :term:`view name` based on information present in the
  request.

- Using the context and view name provided by :term:`context finding`,
  the :mod:`repoze.bfg` :term:`view lookup` subsystem is provided with
  a :term:`request`, a :term:`context` and a :term:`view name`.  It is
  then responsible for finding and invoking a :term:`view callable`.
  A view callable is a specific bit of code written and registered by
  the application developer which receives the :term:`request` and
  which returns a :term:`response`.

These two subsystems are used by :mod:`repoze.bfg` serially:
first, a :term:`context finding` subsystem does its job.  Then the
result of context finding is passed to the :term:`view lookup`
subsystem.  The view lookup system finds a :term:`view callable`
written by an application developer, and invokes it.  A view callable
returns a :term:`response`.  The response is returned to the
requesting user.

.. sidebar::  What Good is A Context Finding Subsystem?

   The :term:`URL dispatch` mode of :mod:`repoze.bfg` as well as many
   other web frameworks such as :term:`Pylons` or :term:`Django`
   actually collapse the two steps of context finding and view lookup
   into a single step.  In these systems, a URL can map *directly* to
   a view callable.  This makes them simpler to understand than
   systems which use distinct subsystems to locate a context and find
   a view.  However, explicitly finding a context provides extra
   flexibility.  For example, it makes it possible to protect your
   application with declarative context-sensitive instance-level
   :term:`authorization`, which is not well-supported in frameworks
   that do not provide a notion of a context.

There are two separate :term:`context finding` subsystems in
:mod:`repoze.bfg`: :term:`traversal` and :term:`URL dispatch`.  The
subsystems are documented within this chapter.  They can be used
separately or they can be combined.  Three chapters which follow
describe :term:`context finding`: :ref:`traversal_chapter`,
:ref:`urldispatch_chapter` and :ref:`hybrid_chapter`.

There is only one :term:`view lookup` subsystem present in
:mod:`repoze.bfg`.  Where appropriate, within this chapter, we
describe how view lookup interacts with context finding.  One chapter
which follows describes :term:`view lookup`: :ref:`views_chapter`.

Should I Use Traversal or URL Dispatch for Context Finding?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:term:`URL dispatch` is very straightforward.  When you limit your
application to using URL dispatch, you know every URL that your
application might generate or respond to, all the URL matching
elements are listed in a single place, and you needn't think about
:term:`context finding` or :term:`view lookup` at all.

URL dispatch can easily handle URLs such as
``http://example.com/members/Chris``, where it's assumed that each
item "below" ``members`` in the URL represents a single member in some
system.  You just match everything "below" ``members`` to a particular
:term:`view callable`, e.g. ``/members/:memberid``.

However, URL dispatch is not very convenient if you'd like your URLs
to represent an arbitrary hierarchy.  For example, if you need to
infer the difference between sets of URLs such as these, where the
``document`` in the first URL represents a PDF document, and
``/stuff/page`` in the second represents an OpenOffice document in a
"stuff" folder.

.. code-block:: text

   http://example.com/members/Chris/document
   http://example.com/members/Chris/stuff/page

It takes more pattern matching assertions to be able to make
hierarchies work in URL-dispatch based systems, and some assertions
just aren't possible.  Essentially, URL-dispatch based systems just
don't deal very well with URLs that represent arbitrary-depth
hierarchies.

But :term:`traversal` *does* work well for URLs that represent
arbitrary-depth hierarchies.  Since the path segments that compose a
URL are addressed separately, it becomes very easy to form URLs that
represent arbitrary depth hierarchies in a system that uses traversal.
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
use either exclusively or combine them as you see fit.

