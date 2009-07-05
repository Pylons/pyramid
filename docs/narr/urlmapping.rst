.. _url_mapping_chapter:

Mapping URLs to Code
====================

Many popular web frameworks today use :term:`URL dispatch` to
associate a particular URL with a bit of code.  In these systems, the
bit of code associated with a URL is known somewhat ambiguously as a
"controller" or :term:`view` depending upon the particular vocabulary
religion to which you subscribe.  Such systems allow the developer to
create "urlconfs" or "routes" to controller/view Python code using
pattern matching against URL components.  Examples: `Django's URL
dispatcher
<http://www.djangoproject.com/documentation/url_dispatch/>`_ and the
:term:`Routes` URL mapping system.

:mod:`repoze.bfg` supports :term:`URL dispatch` via a subsystem that
was inspired by :term:`Routes`.  :term:`URL dispatch` is convenient
and straightforward.  When you limit your application to using URL
dispatch, you know every URL that your application might generate or
respond to, and all the URL matching elements are listed in a single
place.

Like :term:`Zope`, :mod:`repoze.bfg`, in contrast to URL dispatch, can
also map URLs to code slightly differently, by using using object
graph :term:`traversal`.  Graph-traversal based dispatching is useful
if you like your URLs to represent an arbitrary hierarchy of
potentially heterogeneous items, or if you need to attach
"instance-level" security (akin to "row-level" security in relational
parlance) declarations to :term:`model` instances.

Differences Between Traversal and URL Dispatch
----------------------------------------------

:term:`URL dispatch` can easily handle URLs such as
``http://example.com/members/Chris``, where it's assumed that each
item "below" ``members`` in the URL represents a member in the system.
You just match everything "below" ``members`` to a particular view.

For example, you might configure a :term:`route` to match against the
following URL patterns::

  archives/:year/:month/:day
  members/:membername

In this configuration, there are exactly two types of URLs that will
match views in your application: ones that start with ``/archives``
and have subsequent path elements that represent a year, month, and
day.  And ones that start with ``/members`` which are followed by a
path segment containing a member's name.  This is very simple.

:term:`URL dispatch` is not very good, however, at inferring the
difference between sets of URLs such as::

       http://example.com/members/Chris/document
       http://example.com/members/Chris/stuff/page

...wherein you'd like the ``document`` in the first URL to represent a
PDF document, and ``/stuff/page`` in the second to represent an
*OpenOffice* document in a "stuff" folder.  It takes more pattern
matching assertions to be able to make URLs like these work in
URL-dispatch based systems, and some assertions just aren't possible.
For example, URL-dispatch based systems don't deal very well with URLs
that represent arbitrary-depth hierarchies.

Graph :term:`traversal` works well if you need to divine meaning from
of these types of "ambiguous" URLs and from URLs that represent
arbitrary-depth hierarchies.  When traversal is used, each URL segment
represents a single traversal step through an edge of a graph.  So a
URL like ``http://example.com/a/b/c`` can be thought of as a graph
traversal on the ``example.com`` site through the edges ``a``, ``b``,
and ``c``.

If you're willing to treat your application models as a graph that can
be traversed, it also becomes easy to provide "row-level security" (in
common relational parlance): you just attach a security declaration to
each instance in the graph.  This is not as easy in frameworks that
use URL-based dispatch.

Graph traversal is materially more complex than URL-based dispatch,
however, if only because it requires the construction and maintenance
of a graph, and it requires the developer to think about mapping URLs
to code in terms of traversing the graph.  (How's *that* for
self-referential! ;-) ) 

In essence, the choice to use graph traversal vs. URL dispatch is
largely religious in some sense.  Graph traversal dispatch probably
just doesn't make any sense when you possess completely "square" data
stored in a relational database.  However, when you have a
hierarchical data store, it can provide advantages over using
URL-based dispatch.

:mod:`repoze.bfg` provides support for both approaches.  You can use
either as you see fit.

