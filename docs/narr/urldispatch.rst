.. _urldispatch_chapter:

URL Dispatch
============

It is common for :mod:`repoze.bfg` developers to rely on
:term:`traversal` to map URLs to code.  However, :mod:`repoze.bfg` can
also map URLs to code via :term:`URL dispatch` using the
:term:`Routes` framework.  The :term:`Routes` framework is a Python
reimplementation of the `Rails routes system
<http://manuals.rubyonrails.com/read/chapter/65>`_.  It is a mechanism
which allows you to declaratively map URLs to code.  

.. note:: In common :term:`Routes` lingo, the code that it maps URLs
          to is defined by a *controller* and an *action*.  However,
          neither concept (controller nor action) exists within
          :mod:`repoze.bfg`.  Instead, when you map a URL pattern to
          code in bfg, you will map the URL patterm to a :term:`view`.
          Once the context and view are found, the view will be called
          with a :term:`context` and a :term:`request`.

It often makes a lot of sense to use :term:`URL dispatch` instead of
:term:`traversal` in an application that has no natural hierarchy.
For instance, if all the data in your application lives in a
relational database, and that relational database has no
self-referencing tables that form a natural hierarchy, URL dispatch is
easier to use than traversal, and is often a more natural fit for
creating an application that maniplates "flat" data.

Concept and Usage
-----------------

The URL dispatch features of :mod:`repoze.bfg` allow you to either
augment or replace :term:`traversal`, allowing URL dispatch to have
the "first crack" (and potentially the *only* crack) at resolving a
given URL to :term:`context` and :term:`view name`.  

To allow for URL dispatch to be used, the :mod:`repoze.bfg` framework
allows you to inject ``route`` ZCML directives into your application's
``configure.zcml`` file.

.. note:: Each ZCML ``route`` statement equates to a call to the
          :term:`Routes` ``Mapper`` object's ``connect`` method.  See
          `Setting up routes
          <http://routes.groovie.org/manual.html#setting-up-routes>`_
          for examples of using a Routes ``Mapper`` object outside of
          :mod:`repoze.bfg`.

When any ``route`` ZCML directive is present in an application's
``configure.zcml``, "under the hood" :mod:`repoze.bfg` wraps the
:term:`root factory` in a special ``RoutesRootFactory`` instance.  The
wrapper instance then acts as the effective root factory.  When it
acts as a root factory, it is willing to check the requested URL
against a *routes map* to find a :term:`context` and a :term:`view`
before traversal has a chance to find it first.  If a route matches, a
:term:`context` is generated and :mod:`repoze.bfg` will call the
:term:`view` specified with the context and the request.  If no route
matches, :mod:`repoze.bfg` will fail over to calling the :term:`root
factory` callable passed to the application in it's ``make_app``
function (usually a traversal function).

A root factory is not required for purely URL-dispatch-based apps: if
the root factory callable is passed as ``None`` to the ``make_app``
function, :mod:`repoze.bfg` will return a NotFound error to the user's
browser when no routes match.

.. note:: See :ref:`modelspy_project_section` for an example of a
          simple root factory callable that will use traversal.

.. _route_zcml_directive:

The ``route`` ZCML Directive
----------------------------

The ``route`` ZCML directive has these possible attributes.  All
attributes are optional unless the description names them as required.

path

  The `route path
  <http://routes.groovie.org/manual.html#route-path>`_,
  e.g. ``ideas/:idea``.  This attribute is required.

name

  The `route name
  <http://routes.groovie.org/manual.html#route-name>`_,
  e.g. ``myroute``.  This attribute is required.

view

  The Python dotted-path name to a function that will be used as a
  view callable when this route matches.
  e.g. ``mypackage.views.my_view``.

view_for

  The Python dotted-path name to a class or an interface that the
  :term:`context` of the view should match for the view named by the
  route to be used.  This attribute is only useful if the ``view``
  attribute is used.  If this attribute is not specified, the default
  (``None``) will be used.

permission

  The permission name required to invoke the view.
  e.g. ``edit``. (see :ref:`using_security_with_urldispatch` for more
  information about permissions).

factory

  The Python dotted-path name to a function that will generate a
  :mod:`repoze.bfg` context object when this route matches.
  e.g. ``mypackage.models.MyFactoryClass``.  If this argument is not
  specified, a default root factory will be used.

encoding

  The `URL encoding <http://routes.groovie.org/manual.html#unicode>`_
  for a match returned by this route.

static

  A boolean (true/false) indicating whether this route is `static
  <http://routes.groovie.org/manual.html#static-named-routes>`_.

filter

  A Python dotted-path name to a Routes `filter function
  <http://routes.groovie.org/manual.html#filter-functions>`_.

request_type

  The name of the HTTP method used as the Routes `condition method
  <http://routes.groovie.org/manual.html#conditions>`_.  A string,
  e.g. ``GET`` or ``POST``.  Note that :term:`interface` references
  don't work here as they do in the ``view`` decorator or ``bfg_view``
  ZCML directive.  Only strings representing an HTTP method will work.

condition_method

  An alias for the ``request_type`` attribute.

condition_subdomain

  A field that contain a Routes `condition subdomain
  <http://routes.groovie.org/manual.html#conditions>`_.

condition_function

  A python-dotted path name to a Routes `condition function
  <http://routes.groovie.org/manual.html#conditions>`_.

explicit

  A boolean (true/false) indicating whether this route is `explicit
  <http://routes.groovie.org/manual.html#overriding-route-memory>`_.

subdomains

  A field that contain one or more Routes `condition subdomains
  <http://routes.groovie.org/manual.html#conditions>`_.  If this field
  is used, the ``condition_subdomain`` attribute is ignored.

Using the ``requirement`` Subdirective
--------------------------------------

The ``route`` directive supports a subdirective named ``requirement``
that allows you to specify Routes `requirement
<http://routes.groovie.org/manual.html#requirements>`_ expressions.

For example:

.. code-block:: xml
   :linenos:

   <route 
     name="archive"
     path="archives/:year/:month"
     view=".views.archive_view">

   <requirement
      attr="year"
      expr="d{2,4}"
      />

   <requirement
      attr="month"
      expr="d{1,2}"
      />

   </route>

Example 1
---------

The simplest route delcaration:

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

   def hello_view(context, request):
       return Response('Hello!')

In this case the context object passed to the view will be an instance
of the ``repoze.bfg.urldispatch.DefaultRoutesContext``.  This is the
type of obejct created for a context when there is no "factory"
specified in the ``route`` declaration.  It is a mapping object, a lot
like a dictionary.

Example 2
---------

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

.. code-block:: bash
   :linenos:

   /ideas/<ideaname>
   /users/<username>
   /tags/<tagname>

When a URL matches the pattern ``/ideas/<ideaname>``, the view
registered with the name ``idea`` will be called.  This will be the
view available at the dotted Python pathname
``mypackage.views.idea_view``.  

Example 3
---------

The context object passed to a view found as the result of URL
dispatch will by default be an instance of the object returned by the
default :term:`root factory`.  You can override this behavior by
passing in a ``factory`` argument to the ZCML directive for a
particular route.  The ``factory`` should be a callable that accepts a
WSGI environment and returns an instance of a class that will be the
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

The above route will manufacture an ``Idea`` model as a context,
assuming that ``mypackage.models.Idea`` resolves to a class that
accepts a WSGI environment in its ``__init__``.

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
call the "fallback" :term:`root factory` callable provided to it
during ``make_app`.  If the "fallback" root factory is None, a
``NotFound`` error will be raised when no route matches.

.. note:: See :ref:`using_model_interfaces` for more information about
          how views are found when interfaces are attached to a
          context.  You can also map classes to views; interfaces are
          not used then.

Example 4
---------

An example of configuring a ``view`` declaration in ``configure.zcml``
that maps a context found via :term:`Routes` URL dispatch to a view
function is as follows:

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
       def __init__(self, environ):
           self.__dict__.update(environ['repoze.bfg.matchdict'])

       def is_root(self):
           return self['article'] == 'root'

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
the keys and values in the Routes routing dictionary associated with
the request.

In this case in particular, when a user visits
``/archives/something``, the context will be an instance of the
Article class and it will have an ``article`` attribute with the value
of ``something``.

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

Generating Route URLs
---------------------

Use the :mod:`repoze.bfg.url.route_url` function to generate URLs
based on route paths.  For example, if you've configured a route in
ZCML with the ``name`` "foo" and the ``path`` ":a/:b/:c", you might do
this.

.. code-block:: python

   from repoze.bfg.url import route_url
   url = route_url(request, 'foo', a='1', b='2', c='3')

This would return something like the string
``http://example.com/1/2/3`` (at least if the current protocol and
hostname implied ``http:/example.com``).

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
``mypackage`` BFG package that uses SQLAlchemy, and you'd like the
current SQLAlchemy database session to be removed after each request.
Put the following in the ``mypackage.run`` module:

.. code-block:: python

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
       def __init__(self, environ):
          matchdict = environ['bfg.routes.matchdict']
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

