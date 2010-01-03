.. index::
   single: url dispatch

.. _urldispatch_chapter:

URL Dispatch
============

It is common for :mod:`repoze.bfg` developers to rely on
:term:`traversal` to map URLs to code.  However, :mod:`repoze.bfg` can
also map URLs to code via :term:`URL dispatch`.  The presence of
``<route>`` statements in a :term:`ZCML` file used by your application
or the presence of calls to the
:meth:`repoze.bfg.configuration.Configurator.add_route` method in
imperative configuration within your application is a sign that you're
using URL dispatch.  Using the ``add_route`` configurator method or
``<route>`` statements in ZCML allows you to declaratively map URLs to
code.  The syntax of the pattern matching language used by
:mod:`repoze.bfg` is close to that of :term:`Routes`.

It often makes a lot of sense to use :term:`URL dispatch` instead of
:term:`traversal` in an application that has no natural hierarchy.
For instance, if all the data in your application lives in a
relational database, and that relational database has no
self-referencing tables that form a natural hierarchy, URL dispatch is
easier to use than traversal, and is often a more natural fit for
creating an application that manipulates "flat" data.

Concept and Usage
-----------------

The URL dispatch features of :mod:`repoze.bfg` allow you to either
augment or replace :term:`traversal`, allowing URL dispatch to have
the "first crack" (and potentially the *only* crack) at resolving a
given URL to :term:`context` and :term:`view name`.  

To allow for URL dispatch to be used, the :mod:`repoze.bfg` framework
allows you to inject ``route`` ZCML directives into your application's
``configure.zcml`` file.

The mod:`repoze.bfg` :term:`Router` checks an incoming request against
a *routes map* to find a :term:`context` and a :term:`view callable`
before :term:`traversal` has a chance to find these things first.  If
a route matches, a :term:`context` is generated and :mod:`repoze.bfg`
will call the :term:`view callable` found due to the context and the
request.  If no route matches, :mod:`repoze.bfg` will fail over to
calling the :term:`root factory` callable passed to the
:term:`Configurator` for the application (usually a traversal
function).

A root factory is not required for purely URL-dispatch-based apps: if
the root factory callable is passed as ``None`` to the
:term:`Configurator`, :mod:`repoze.bfg` will return a :exc:`NotFound`
error to the user's browser when no routes match.

.. note:: See :ref:`modelspy_project_section` for an example of a
          simple root factory callable that will use traversal.

.. index::
   single: add_route

The ``add_route`` Configurator Method
-------------------------------------

The :meth:`repoze.bfg.configuration.Configurator.add_route` method
adds a single :term:`route configuration` to the :term:`application
registry`.  Here's an example:

.. ignore-next-block
.. code-block:: python

   config.add_route('myroute', '/prefix/:one/:two')

.. index::
   single: ZCML directive; route

Configuring a Route via ZCML
----------------------------

Instead of using the imperative method of adding a route, you can use
:term:`ZCML` for the same purpose.  For example:

.. code-block:: xml
   :linenos:

   <route
       name="myroute"
       path="/prefix/:one/:two"
    />

See :ref:`route_directive` for full ``route`` ZCML directive
documentation.

.. note:: The documentation that follows in this chapter assumes that
   :term:`ZCML` will be used to perform route configuration.

.. index::
   pair: URL dispatch; matchdict

The Matchdict
-------------

The main purpose of a route is to match (nor not match) the
``PATH_INFO`` present in the WSGI environment provided during a
request against a URL path pattern.  When this URL path pattern is
matched, a dictionary is placed on the request named ``matchdict``
with the values that match patterns in the ``path`` element.  If the
URL pattern does not match, no matchdict is generated.

.. index::
   pair: URL dispatch; path pattern syntax

.. _route_path_pattern_syntax:

Path Pattern Syntax
--------------------

The path pattern syntax is simple.

The path may start with a slash character.  If the path does not start
with a slash character, an implicit slash will be prepended to it at
matching time.  For example, the following paths are equivalent:

.. code-block:: text

   :foo/bar/baz

and:

.. code-block:: text

   /:foo/bar/baz

A path segment (an individual item between ``/`` characters in the
path) may either be a literal string (e.g. ``foo``) *or* it may
segment replacement marker (e.g. ``:foo``).  A segment replacement
marker is in the format ``:name``, where this means "accept any
characters up to the next slash and use this as the ``name`` matchdict
value."  For example, the following pattern defines one literal
segment ("foo") and two dynamic segments ("baz", and "bar"):

.. code-block:: text

   foo/:baz/:bar

The above pattern will match these URLs, generating the following
matchdicts:

.. code-block:: text

   foo/1/2        -> {'baz':u'1', 'bar':u'2'}
   foo/abc/def    -> {'baz':u'abc', 'bar':u'def'}

It will not match the following patterns however:

.. code-block:: text

   foo/1/2/        -> No match (trailing slash)
   bar/abc/def     -> First segment literal mismatch

Note that values representing path segments matched with a
``:segment`` match will be url-unquoted and decoded from UTF-8 into
Unicode within the matchdict.  So for instance, the following
pattern:

.. code-block:: text

   foo/:bar

When matching the following URL:

.. code-block:: text

   foo/La%20Pe%C3%B1a

The matchdict will look like so (the value is URL-decoded / UTF-8
decoded):

.. code-block:: text

   {'bar':u'La Pe\xf1a'}

If the pattern has a ``*`` in it, the name which follows it is
considered a "remainder match".  A remainder match *must* come at the
end of the path pattern.  Unlike segment replacement markers, it does
not need to be preceded by a slash.  For example:

.. code-block:: text

   foo/:baz/:bar*traverse

The above pattern will match these URLs, generating the following
matchdicts:

.. code-block:: text

   foo/1/2/           -> {'baz':1, 'bar':2, 'traverse':()}
   foo/abc/def/a/b/c  -> {'baz':abc, 'bar':def, 'traverse':('a', 'b', 'c')}

Note that when a ``*stararg`` remainder match is matched, the value
put into the matchdict is turned into a tuple of path segments
representing the remainder of the path.  These path segments are
url-unquoted and decoded from UTF-8 into Unicode.  For example, for
the following pattern:

.. code-block:: text

   foo/*traverse

When matching the following path:

.. code-block:: text

   /foo/La%20Pe%C3%B1a/a/b/c

Will generate the following matchdict:

.. code-block:: text

   {'traverse':(u'La Pe\xf1a', u'a', u'b', u'c')}

.. index::
   triple: ZCML directive; route; examples

``<route>`` Statement Examples
------------------------------

Let's check out some examples of how ``<route>`` statements might be
commonly declared.

Example 1
~~~~~~~~~

The simplest route declaration:

.. code-block:: xml
   :linenos:

   <route
    name="idea"
    path="hello.html"
    view="mypackage.views.hello_view"
    />

When the URL matches ``/hello.html``, the view callable at the Python
dotted path name ``mypackage.views.hello_view`` will be called with a
default context object and the request.  See :ref:`views_chapter` for
more information about views.

The ``mypackage.views`` module referred to above might look like so:

.. code-block:: python
   :linenos:

   from webob import Response

   def hello_view(request):
       return Response('Hello!')

.. note: the ``context`` attribute of the ``request`` object passed to
   the above view will be an instance of the
   :class:`repoze.bfg.urldispatch.DefaultRoutesContext` class.  This
   is the type of object created for a context when there is no
   "factory" specified in the ``route`` declaration.  It is a mapping
   object, a lot like a dictionary.

When using :term:`url dispatch` exclusively in an application (as
opposed to using both url dispatch and :term:`traversal`), the
:term:`context` of the view isn't always terribly interesting,
particularly if you never use a ``factory`` attribute on your route
definitions.  However, if you do use a ``factory`` attribute on your
route definitions, you may be very interested in the :term:`context`
of the view.  :mod:`repoze.bfg` supports view callables defined with
two arguments: ``context`` and ``request``.  For example, the below
view statement is completely equivalent to the above view statement:

.. code-block:: python
   :linenos:

   from webob import Response

   def hello_view(context, request):
       return Response('Hello!')

The ``context`` passed to this view will be an instance returned by
the default root factory or an instance returned by the ``factory``
argument to your route definition.

Even if you use the request-only argument format in view callables,
you can still get to the ``context`` of the view (if necessary) by
accessing ``request.context``.

See :ref:`request_and_context_view_definitions` for more information.

Example 2
~~~~~~~~~

Below is an example of some more complicated route statements you
might add to your ``configure.zcml``:

.. code-block:: xml
   :linenos:

   <route
    name="idea"
    path="ideas/:idea"
    view="mypackage.views.idea_view"
    />

   <route
    name="user"
    path="users/:user"
    view="mypackage.views.user_view"
    />

   <route 
    name="tag" 
    path="tags/:tag"
    view="mypackage.views.tag_view"
    />

The above configuration will allow :mod:`repoze.bfg` to service URLs
in these forms:

.. code-block:: text

   /ideas/<ideaname>
   /users/<username>
   /tags/<tagname>

When a URL matches the pattern ``/ideas/<ideaname>``, the view
registered with the name ``idea`` will be called.  This will be the
view available at the dotted Python pathname
``mypackage.views.idea_view``.  

Example 3
~~~~~~~~~

The context object passed to a view found as the result of URL
dispatch will by default be an instance of the object returned by the
default :term:`root factory`.  You can override this behavior by
passing in a ``factory`` argument to the ZCML directive for a
particular route.  The ``factory`` should be a callable that accepts a
:term:`request` and returns an instance of a class that will be the
context used by the view.

An example of using a route with a factory:

.. code-block:: xml
   :linenos:

   <route
    name="idea"
    path="ideas/:idea"
    view=".views.idea_view"
    factory=".models.Idea"
    />

The above route will manufacture an ``Idea`` model as a
:term:`context`, assuming that ``mypackage.models.Idea`` resolves to a
class that accepts a request in its ``__init__``.

.. note:: Values prefixed with a period (``.``) for the ``factory``
   and ``view`` attributes of a ``route`` (such as ``.models.Idea``
   and ``.views.idea_view``) above) mean "relative to the Python
   package directory in which this :term:`ZCML` file is stored".  So
   if the above ``route`` declaration was made inside a
   ``configure.zcml`` file that lived in the ``hello`` package, you
   could replace the relative ``.models.Idea`` with the absolute
   ``hello.models.Idea`` Either the relative or absolute form is
   functionally equivalent.  It's often useful to use the relative
   form, in case your package's name changes.  It's also shorter to
   type.

If no route matches in the above configuration, :mod:`repoze.bfg` will
call the "fallback" :term:`root factory` callable provided to the
:term:`Configurator` constructor.  If the "fallback" root factory is
None, a :exc:`NotFound` error will be raised when no route matches.

.. note:: See :ref:`using_model_interfaces` for more information about
          how views are found when interfaces are attached to a
          context.  You can also map classes to views; interfaces are
          not used then.

Example 4
~~~~~~~~~

An example of configuring a ``view`` declaration in ``configure.zcml``
that maps a context found via URL dispatch to a view function is as
follows:

.. code-block:: xml
   :linenos:

   <route
      name="article"
      path="archives/:article"
      view=".views.article_view"
      factory=".models.Article"
      />

The ``.models`` module referred to above might look like so:

.. code-block:: python
   :linenos:

   class Article(object):
       def __init__(self, request):
           self.__dict__.update(request.matchdict)

       def is_root(self):
           return self.article == 'root'

The ``.views`` module referred to above might look like so:

.. code-block:: python
   :linenos:

   from webob import Response

   def article_view(context, request):
       if context.is_root():
          return Response('Root article')
       else:
          return Response('Article with name %s' % context.article)

The effect of this configuration: when this :mod:`repoze.bfg`
application runs, if any URL matches the pattern
``archives/:article``, the ``.views.articles_view`` view will be
called with its :term:`context` as a instance of the ``Article``
class.  The ``Article`` instance will have keys and values matching
the keys and values in the routing dictionary associated with the
request.

In this case in particular, when a user visits
``/archives/something``, the context will be an instance of the
Article class and it will have an ``article`` attribute with the value
of ``something``.

.. index::
   pair: URL dispatch; catching root URL

Catching the Root URL
---------------------

It's not entirely obvious how to use a route to catch the root URL
("/").  To do so, give the empty string as a path in a ZCML ``route``
declaration:

.. code-block:: xml
   :linenos:

   <route
       path=""
       name="root"
       view=".views.root_view"
       />

Or provide the literal string ``/`` as the path:

.. code-block:: xml
   :linenos:

   <route
       path="/"
       name="root"
       view=".views.root_view"
       />

.. index::
   pair: URL dispatch; generating route URLs

Generating Route URLs
---------------------

Use the :func:`repoze.bfg.url.route_url` function to generate URLs
based on route paths.  For example, if you've configured a route in
ZCML with the ``name`` "foo" and the ``path`` ":a/:b/:c", you might do
this.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg.url import route_url
   url = route_url('foo', request, a='1', b='2', c='3')

This would return something like the string
``http://example.com/1/2/3`` (at least if the current protocol and
hostname implied ``http:/example.com``).  See the
:func:`repoze.bfg.url.route_url` API documentation for more
information.

.. index::
   pair: URL dispatch; slash-redirecting

Redirecting to Slash-Appended Routes
------------------------------------

For behavior like Django's ``APPEND_SLASH=True``, use the
:func:`repoze.bfg.view.append_slash_notfound_view` view as the
:term:`Not Found view` in your application.  When this view is the Not
Found view (indicating that no view was found), and any routes have
been defined in the configuration of your application, if the value of
``PATH_INFO`` does not already end in a slash, and if the value of
``PATH_INFO`` *plus* a slash matches any route's path, do an HTTP
redirect to the slash-appended ``PATH_INFO``.

Let's use an example, because this behavior is a bit magical.  If this
your route configuration is looks like so, and the
``append_slash_notfound_view`` is configured in your application:

.. code-block:: xml
   :linenos:

   <route
     view=".views.no_slash"
     path="no_slash"
    />

   <route
     view=".views.has_slash"
     path="has_slash/"
    />

If a request enters the application with the ``PATH_INFO`` value of
``/no_slash``, the first route will match.  If a request enters the
application with the ``PATH_INFO`` value of ``/no_slash/``, *no* route
will match, and the slash-appending "not found" view will *not* find a
matching route with an appended slash.

However, if a request enters the application with the ``PATH_INFO``
value of ``/has_slash/``, the second route will match.  If a request
enters the application with the ``PATH_INFO`` value of ``/has_slash``,
a route *will* be found by the slash appending notfound view.  An HTTP
redirect to ``/has_slash/`` will be returned to the user's browser.

Note that this will *lose* ``POST`` data information (turning it into
a GET), so you shouldn't rely on this to redirect POST requests.

To configure the slash-appending not found view in your application,
change the application's ``configure.zcml``, adding the following
stanza:

.. code-block:: xml
   :linenos:

   <notfound
     view="repoze.bfg.views.append_slash_notfound_view"
    />

See :ref:`view_module` and :ref:`changing_the_notfound_view` for more
information about the slash-appending not found view and for a more
general description of how to configure a not found view.

.. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

Cleaning Up After a Request
---------------------------

Often it's required that some cleanup be performed at the end of a
request when a database connection is involved.  When
:term:`traversal` is used, this cleanup is often done as a side effect
of the traversal :term:`root factory`.  Often the root factory will
insert an object into the WSGI environment that performs some cleanup
when its ``__del__`` method is called.  When URL dispatch is used,
however, no special root factory is required, so sometimes that option
is not open to you.

Instead of putting this cleanup logic in the root factory, however,
you can cause a subscriber to be fired when a new request is detected;
the subscriber can do this work.  For example, let's say you have a
``mypackage`` :mod:`repoze.bfg` application package that uses
SQLAlchemy, and you'd like the current SQLAlchemy database session to
be removed after each request.  Put the following in the
``mypackage.run`` module:

.. ignore-next-block
.. code-block:: python
   :linenos:

    from mypackage.sql import DBSession

    class Cleanup:
        def __init__(self, cleaner):
            self.cleaner = cleaner
        def __del__(self):
            self.cleaner()

    def handle_teardown(event):
        environ = event.request.environ
        environ['mypackage.sqlcleaner'] = Cleanup(DBSession.remove)

Then in the ``configure.zcml`` of your package, inject the following:

.. code-block:: xml

  <subscriber for="repoze.bfg.interfaces.INewRequest"
    handler="mypackage.run.handle_teardown"/>

This will cause the DBSession to be removed whenever the WSGI
environment is destroyed (usually at the end of every request).

.. index::
   pair: URL dispatch; security

.. _using_security_with_urldispatch:

Using :mod:`repoze.bfg` Security With URL Dispatch
--------------------------------------------------

:mod:`repoze.bfg` provides its own security framework which consults a
:term:`authorization policy` before allowing any application code to
be called.  This framework operates in terms of ACLs (Access Control
Lists, see :ref:`security_chapter` for more information about the
:mod:`repoze.bfg` authorization subsystem).  A common thing to want to
do is to attach an ``__acl__`` to the context object dynamically for
declarative security purposes.  You can use the ``factory`` argument
that points at a factory which attaches a custom ``__acl__`` to an
object at its creation time.

Such a ``factory`` might look like so:

.. code-block:: python
   :linenos:

   class Article(object):
       def __init__(self, request):
          matchdict = request.matchdict
          article = matchdict.get('article', None)
          if article == '1':
              self.__acl__ = [ (Allow, 'editor', 'view') ]

If the route ``archives/:article`` is matched, and the article number
is ``1``, :mod:`repoze.bfg` will generate an ``Article``
:term:`context` with an ACL on it that allows the ``editor`` principal
the ``view`` permission.  Obviously you can do more generic things
that inspect the routes match dict to see if the ``article`` argument
matches a particular string; our sample ``Article`` factory class is
not very ambitious.

.. note:: See :ref:`security_chapter` for more information about
   :mod:`repoze.bfg` security and ACLs.

