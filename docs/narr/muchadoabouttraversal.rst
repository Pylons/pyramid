.. _much_ado_about_traversal_chapter:

========================
Much Ado About Traversal
========================

.. note:: This chapter was adapted, with permission, from a blog post by `Rob
   Miller <http://blog.nonsequitarian.org/>`_, originally published at
   `http://blog.nonsequitarian.org/2010/much-ado-about-traversal/
   <http://blog.nonsequitarian.org/2010/much-ado-about-traversal/>`_.

A lot of folks who have been using Pylons (and, therefore, Routes-based
URL matching) are being exposed for the first time, via :app:`Pyramid`,
to new ideas such as ":term:`traversal`" and ":term:`view lookup`" as a
way to route incoming HTTP requests to callable code.  This has caused a
bit of consternation in some circles.  Many think that traversal is hard
to understand.  Others question its usefulness; URL matching has worked
for them so far, why should they even consider dealing with another
approach, one which doesn't fit their brain and which doesn't provide
any immediately obvious value?

This chapter is an attempt to counter these opinions.  Traversal and
view lookup *are* useful.  There are some straightforward, real-world
use cases that are much more easily served by a traversal-based approach
than by a pattern-matching mechanism.  Even if you haven't yet hit one
of these use cases yourself, understanding these new ideas is worth the
effort for any web developer so you know when you might want to use
them.  Especially because (WARNING: Bold Assertion Ahead) these ideas
are *not* particularly hard to understand.  In fact, :term:`traversal`
is a straightforward metaphor easily comprehended by anyone who's ever
used a run-of-the-mill file system with folders and files.

.. note::
   
   Those of you who are already familiar with traversal and view lookup
   conceptually, may want to skip directly to the
   :ref:`traversal_chapter` chapter, which discusses the technical
   details.

URL Dispatch
------------

Let's take a step back.  The problem we're trying to solve is
simple.  We have an HTTP request for a particular path that
has been routed to our web application.  The requested path will
possibly invoke a specific callable function defined somewhere in our
app, or it may point to nothing in which case a 404 response should be
generated.  What we're trying to do is figure out is which callable
function, if any, should be invoked for a given requested path.

URL matching (or :term:`URL dispatch` in :app:`Pyramid` parlance)
approaches this problem by parsing the URL path and comparing the
results to a set of registered "patterns", defined by a set of regular
expressions, or some other URL path templating syntax.  Each pattern is
mapped to a callable function somewhere; if the request path matches a
specific pattern, the associated function is called.  If the request
path matches more than one pattern, some conflict resolution scheme is
used, usually a simple order precedence so that the first match will
take priority over any subsequent matches.  If a request path doesn't
match any of the defined patterns, we've got a 404.

Just in case it's not crystal clear, we'll give an example.  Using
:app:`Pyramid`'s syntax, we might have a match pattern such as
``/{userid}/photos/{photoid}``, mapped to a ``photo_view()`` function
defined somewhere in our code.  Then a request for a path such as
``/joeschmoe/photos/photo1`` would be a match, and the ``photo_view()``
function would be invoked to handle the request.  Similarly,
``/{userid}/blog/{year}/{month}/{postid}`` might map to a
``blog_post_view()`` function, so
``/joeschmoe/blog/2010/12/urlmatching`` would trigger the function,
which presumably would know how to find and render the ``urlmatching``
blog post.

Historical Refresher
--------------------

Okay, we've got :term:`URL dispatch` out of the way, soon we'll dig in
to the supposedly "harder to understand" idea of traversal.  Before we
do, though, let's take a trip down memory lane.  If you've been doing
web work for a while, you may remember a time when we didn't have these
fancy web frameworks.  Instead, we had general purpose HTTP servers that
primarily served files off of a file system.  The "root" of a given site
mapped to a particular folder somewhere on the file system.  Each
segment of the request path represented a subdirectory.  The final path
segment would be either a directory or a file, and once the server found
the right file it would package it up in an HTTP response and send it
back to the client.  So serving up a request for
``/joeschmoe/photos/photo1`` literally meant that there was a
``joeschmoe`` folder somewhere, which contained a ``photos`` folder,
which in turn contained a ``photo1`` file.  If at any point along the
way we find that there is not a folder or file matching the requested
path, we return a 404 response.

As the web grew more dynamic, however, a little bit of extra
complexity was added.  Technologies such as CGI and HTTP server
modules were developed.  Files were still looked up on the file
system, but if the file ended with (for example) ``.cgi`` or ``.php``,
or if it lived in a special folder, instead of simply sending the file
to the client the server would read the file, execute it using an
interpreter of some sort, and then send the output from this process
to the client as the final result.  The server configuration specified
which files would trigger some dynamic code, with the default case
being to just serve the static file.

Traversal (aka Resource Location)
---------------------------------

You with me so far?  Good.  Because if you understand how serving
files from a file system works, then you pretty much understand
traversal.  And if you understand that a server might do something
different based on what type of file a given request specifies, then
you pretty much understand view lookup.

Wait... what!?!

.. index::
   single: traversal overview

The only difference between file system lookup and traversal is that a
file system lookup is stepping through nested directories and files in
a file system tree, while traversal is stepping through nested
dictionary-type objects in an object tree.  Let's take a detailed look
at one of our example paths, so we can see what I mean:

With ``/joeschmoe/photos/photo1``, we've got 4 segments: ``/``,
``joeschmoe/``, ``photos/`` and ``photo1``.  With file system
lookup we have a root folder (``/``) containing a nested folder
(``joeschmoe``), which contains ANOTHER nested folder (``photos``),
which finally contains a JPG file ("photo1").  With traversal, we
have a dictionary-like root object.  Asking for the ``joeschmoe`` key
gives us another dictionary-like object.  Asking this in turn for the
``photos`` key gives us yet another mapping object, which finally
(hopefully) contains the resource that we're looking for within its
values, referenced by the ``photo1`` key.

In pure Python terms, then, the traversal or "resource location"
portion of satisfying the ``/joeschmoe/photos/photo1`` request
will look like this::

    get_root()['joeschmoe']['photos']['photo1']

Where ``get_root()`` is some function that returns our root traversal
resource.  If all of the specified keys exist, then the returned object
will be the resource that is being requested, analogous to the JPG file
that was retrieved in the file system example.  If a :exc:`KeyError` is
generated anywhere along the way, we get a 404.  (Well, this isn't
precisely true, as you'll see when we learn about view lookup below, but
the basic idea holds.)

What is a "resource"?
---------------------

Okay, okay... files on a file system I understand, you might say.  But
what are these nested dictionary things?  Where do these objects, these
"resources", live?  What *are* they?

Well, since :app:`Pyramid` is not a highly opinionated framework, there
is no restriction on how a resource is implemented; the developer can do
whatever they want.  One common pattern is to persist all of the
resources, including the root, in a database.  The root object stores
the ids of all of its subresources, and provides a ``__getitem__``
implementation that fetches them.  So ``get_root()`` fetches the unique
root object, while ``get_root()['joeschmoe']`` returns a different
object, also stored in the database, which in turn has its own
subresources and ``__getitem__`` implementation, etc.  These resources
could be persisted in a relational database, one of the many "NoSQL"
solutions that are becoming popular these days, or anywhere else, it
doesn't matter.  As long as the returned objects provide the
dictionary-like API (i.e. as long as they have an appropriately
implemented ``__getitem__`` method) then traversal will work.

In fact, you don't need a "database" at all.  You could trivially
implement a set of objects with ``__getitem__`` methods that search
for files in specific directories, and thus precisely recreate the
older mechanism of having the URL path mapped directly to a folder
structure on the file system.  Traversal is in fact a superset of file
system lookup.

View Lookup
-----------

At this point we're nearly there.  We've covered traversal, which is
the process by which a specific resource is retrieved according to a
specific URL path.  But what is this "view lookup" business?

View lookup comes from a simple realization, namely, that there is more
than one possible action that you might want to take for a single
resource.  With our photo example, for instance, you might want to view
the photo in a page, but you might also want to provide a way for the
user to edit the photo and any associated metadata.  We'll call the
former the ``view`` view, and the latter will be the ``edit`` view
(Original, I know.)  :app:`Pyramid` has a centralized view registry
where named views can be associated with specific resource types.  So in
our example, we'll assume that we've registered ``view`` and ``edit``
views for photo objects, and that we've specified the ``view`` view as
the default, so that ``/joeschmoe/photos/photo1/view`` and
``/joeschmoe/photos/photo1`` are equivalent.  The edit view would
sensibly be provided by a request for ``/joeschmoe/photos/photo1/edit``.

Hopefully it's clear that the first portion of the edit view's URL path
is going to resolve to the same resource as the non-edit version,
specifically the resource returned by
``get_root()['joeschmoe']['photos']['photo1']``.  But traveral ends
there; the ``photo1`` resource doesn't have an ``edit`` key.  In fact,
it might not even be a dictionary-like object, in which case
``photo1['edit']`` would be meaningless.  When :app:`Pyramid`'s resource
location has resolved to a *leaf* resource but the entire request path
has not yet been expended, the next path segment is treated as a view
name.  The registry is then checked to see if a view of the given name
has been specified for a resource of the given type.  If so, the view
callable is invoked, with the resource passed in as the ``context``
object; if not, we 404.

This is a slight simplification, but to summarize you can think of a
request for ``/joeschmoe/photos/photo1/edit`` as ultimately converted
into the following piece of Python::
     
  context = get_root()['joeschmoe']['photos']['photo1']
  view_callable = registry.get_view(context, 'edit')
  view_callable(context, request)

That's not too hard to conceptualize, is it?

Use Cases
---------

Let's come back around to look at why we even care.  Yes, maybe
traversal and view lookup isn't mind-bending rocket science.  But URL
matching is easier to explain, and it's good enough, right?

In some cases, yes, but certainly not in all cases.  So far we've had
very structured URLs, where our paths have had a specific, small
number of pieces, like this::

  /{userid}/{typename}/{objectid}[/{view_name}]

In all of the examples thus far, we've hard coded the typename value,
assuming that we'd know at development time what names were going to
be used ("photos", "blog", etc.).  But what if we don't know what
these names will be?  Or, worse yet, what if we don't know *anything*
about the structure of the URLs inside a user's folder?  We could be
writing a CMS where we want the end user to be able to arbitrarily add
content and other folders inside his folder.  He might decide to nest
folders dozens of layers deep.  How would you construct matching
patterns that could account for every possible combination of paths
that might develop?

It may be possible, but it's tricky at best.  And your matching
patterns are going to become quite complex very quickly as you try
to handle all of the edge cases.

With traversal, however, it's straightforward.  You want 20 layers of
nesting?  No problem, :app:`Pyramid` will happily call ``__getitem__``
as long as it needs to, until it runs out of path segments or until it
gets a :exc:`KeyError`.  Each resource only needs to know how to fetch
its immediate children, the traversal algorithm takes care of the rest.

The key advantage of traversal here is that the structure of the
resource tree can live in the database, and not in the code. It's
simple to let users modify the tree at runtime to set up their own
personalized directory structures. 

Another use case in which traversal shines is when there is a need to
support a context-dependent security policy.  One example might be a
document management infrastructure for a large corporation, where
members of different departments have varying access levels to the
various other departments' files.  Reasonably, even specific files
might need to be made available to specific individuals.  Traversal
does well here because the idea of a resource context is baked right
into the code resolution and calling process.  Resource objects can
store ACLs, which can be inherited and/or overridden by the
subresources.

If each resource can thus generate a context-based ACL, then whenever
view code is attempting to perform a sensitive action, it can check
against that ACL to see whether the current user should be allowed to
perform the action.  In this way you achieve so called "instance based"
or "row level" security which is considerably harder to model using a
traditional tabular approach.  :app:`Pyramid` actively supports such a
scheme, and in fact if you register your views with guard permissions
and use an authorization policy, :app:`Pyramid` can check against a
resource's ACL when deciding whether or not the view itself is available
to the current user.

In summary, there are entire classes of problems that are more easily
served by traversal and view lookup than by :term:`URL dispatch`.  If
your problems aren't of this nature, great, stick with :term:`URL
dispatch`.  But if you're using :app:`Pyramid` and you ever find that
you *do* need to support one of these use cases, you'll be glad you have
traversal in your toolkit.

.. note::
   It is even possible to mix and match :term:`traversal` with
   :term:`URL dispatch` in the same :app:`Pyramid` application. See the
   :ref:`hybrid_chapter` chapter for details.
