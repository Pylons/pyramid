.. index::
   single: resource location

.. _resourcelocation_chapter:

Resource Location and View Lookup
---------------------------------

:app:`Pyramid` uses two separate but cooperating subsystems to find and
invoke :term:`view callable` code written by the application developer:
:term:`resource location` and :term:`view lookup`.

- First, a :app:`Pyramid` :term:`resource location` subsystem is given a
  :term:`request`; it is responsible for finding a :term:`resource` object
  based on information present in the request.  When a resource is found via
  resource location, it becomes known as the :term:`context`.

- Next, using the context resource found by :term:`resource location` and the
  :term:`request`, :term:`view lookup` is then responsible for finding and
  invoking a :term:`view callable`.  A view callable is a specific bit of
  code written and registered by the application developer which receives the
  :term:`request` and which returns a :term:`response`.

These two subsystems are used by :app:`Pyramid` serially: first, a
:term:`resource location` subsystem does its job.  Then the result of
resource location is passed to the :term:`view lookup` subsystem.  The view
lookup system finds a :term:`view callable` written by an application
developer, and invokes it.  A view callable returns a :term:`response`.  The
response is returned to the requesting user.

There are two separate :term:`resource location` subsystems in
:app:`Pyramid`: :term:`traversal` and :term:`URL dispatch`. They can be used
separately or they can be combined.  Three chapters which follow describe
:term:`resource location`: :ref:`traversal_chapter`,
:ref:`urldispatch_chapter` and :ref:`hybrid_chapter`.

There is only one :term:`view lookup` subsystem present in :app:`Pyramid`.
Where appropriate, we will describe how view lookup interacts with context
finding.  One chapter which follows describes :term:`view lookup`:
:ref:`views_chapter`.

Should I Use Traversal or URL Dispatch for Resource Location?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you use :app:`Pyramid`, you have a choice about how you'd like to
resolve URLs to code: you can use either :term:`traversal` or :term:`URL
dispatch`.  The choice to use traversal vs. URL dispatch is largely
"religious".  Since :app:`Pyramid` provides support for both approaches, you
can use either exclusively or combine them as you see fit.

:term:`URL dispatch` is very straightforward.  When you limit your
application to using URL dispatch, you know every URL that your application
might generate or respond to, all the URL matching elements are listed in a
single place, and you needn't think about :term:`resource location` or
:term:`view lookup` at all.

URL dispatch can easily handle URLs such as
``http://example.com/members/Chris``, where it's assumed that each item
"below" ``members`` in the URL represents a single member in some system.
You just match everything "below" ``members`` to a particular :term:`view
callable`, e.g. ``/members/{memberid}``.

However, URL dispatch is not very convenient if you'd like your URLs to
represent an arbitrary-depth hierarchy.  For example, if you need to infer
the difference between sets of URLs such as these, where the ``document`` in
the first URL represents a PDF document, and ``/stuff/page`` in the second
represents an OpenOffice document in a "stuff" folder.

.. code-block:: text

   http://example.com/members/Chris/document
   http://example.com/members/Chris/stuff/page

It takes more pattern matching assertions to be able to make hierarchies work
in URL-dispatch based systems, and some assertions just aren't possible.
URL-dispatch based systems just don't deal very well with URLs that represent
arbitrary-depth hierarchies.

:term:`URL dispatch` tends to collapse the two steps of :term:`resource
location` and :term:`view lookup` into a single step.  Thus, a URL can map
*directly* to a view callable.  This makes URL dispatch easier to understand
than traversal, because traversal makes you understand how :term:`resource
location` works.  But explicitly locating a resource provides extra
flexibility.  For example, it makes it possible to protect your application
with declarative context-sensitive instance-level :term:`authorization`.

Unlike URL dispatch, :term:`traversal` works well for URLs that represent
arbitrary-depth hierarchies.  Since the path segments that compose a URL are
addressed separately, it becomes very easy to form URLs that represent
arbitrary depth hierarchies in a system that uses traversal.  When you're
willing to treat your application resources as a tree that can be traversed,
it also becomes easy to provide "instance-level security": you just attach an
:term:`ACL` security declaration to each resource in the tree.  This is not
nearly as easy to do when using URL dispatch.

Traversal probably just doesn't make any sense when you possess completely
"square" data stored in a relational database because it requires the
construction and maintenance of a resource tree and requires that the
developer think about mapping URLs to code in terms of traversing that tree.

We'll examine both :term:`URL dispatch` and :term:`traversal` in the next two
chapters.

