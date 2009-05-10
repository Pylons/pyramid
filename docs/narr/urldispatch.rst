.. _urldispatch_chapter:

URL Dispatch
============

It is common for :mod:`repoze.bfg` developers to rely on
:term:`traversal` to map URLs to code.  However, :mod:`repoze.bfg` can
also map URLs to code via :term:`URL dispatch` using the
:term:`Routes` framework.  The :term:`Routes` framework is a Python
reimplementation of the `Rails routes system
<http://manuals.rubyonrails.com/read/chapter/65>`_.  It is a mechanism
which allows you to declaratively map URLs to code.  Both traversal
and URL dispatch have the same goal: to find the context and the view
name.

.. note:: In common :term:`Routes` lingo, the code that it maps URLs
          to is defined by a *controller* and an *action*.  However,
          neither concept (controller nor action) exists within
          :mod:`repoze.bfg`.  Instead, when you map a URL pattern to
          code in bfg, you will map the URL patterm to a
          :term:`context` and a :term:`view name`.  Once the context
          and view name are found, the same :term:`view` lookup which
          is detailed in :ref:`traversal_chapter` will be done using
          the context and view name found via a route.

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
``configure.zcml``, "under the hood" :mod:`repoze.bfg` wraps the "root
factory" in a special ``RoutesRootFactory`` instance.  The wrapper
instance then acts as the root factory.  When it acts as a root
factory, it is willing to check the requested URL against a *routes
map* to find the :term:`context` and the :term:`view name` before
traversal has a chance to find it first.  If it finds a context and a
view name via a route, :mod:`repoze.bfg` will attempt to look up and
call a :mod:`repoze.bfg` :term:`view` that matches the context and the
view name.  If no route matches, :mod:`repoze.bfg` will fail over to
calling the root factory callable passed to the application in it's
``make_app`` function (usually a traversal function).  By configuring
your ZCML ``route`` statements appropriately, you can mix and match
URL dispatch and traversal in this way.

A root factory is not required for purely URL-dispatch-based apps: if
the root factory callable is ``None``, :mod:`repoze.bfg` will return a
NotFound error to the user's browser when no routes match.

.. note:: See :ref:`modelspy_project_section` for an example of a
          simple root factory callable that will use traversal.

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
  e.g. ``myroute``.

view_name

  The :mod:`repoze.bfg` :term:`view name` that should be looked up
  when this route matches a URL.

factory

  The Python dotted-path name to a function that will generate a
  :mod:`repoze.bfg` context object when this route matches.  By
  default, a ``repoze.bfg.urldispatch.DefaultRoutesContext`` object
  will be constructed if a factory is not provided.

provides

  One or more Python-dotted path names to :term:`interface` objects
  that the context should be decorated with when it's constructed
  (allowing it to be found by a particular view lookup).

encoding

  The `URL encoding <http://routes.groovie.org/manual.html#unicode>`_
  for a match returned by this route.

static

  A boolean (true/false) indicating whether this route is `static
  <http://routes.groovie.org/manual.html#static-named-routes>`_.

filter

  A Python dotted-path name to a Routes `filter function
  <http://routes.groovie.org/manual.html#filter-functions>`_.

absolute

  A boolean (true/false) indicating whether this route is absolute.

member_name

  The member name for this route.

collection_name

  The collection name for this route.

condition_method

  The name of the HTTP method used as the Routes `condition method
  <http://routes.groovie.org/manual.html#conditions>`_.

condition_subdomain

  A field that contain a Routes `condition subdomain
  <http://routes.groovie.org/manual.html#conditions>`_.

condition_function

  A python-dotted path name to a Routes `condition function
  <http://routes.groovie.org/manual.html#conditions>`_.

parent_member_name

  The parent member name for this route.

parent_collection_name

  The parent collection name for this route.

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

   <route path="archives/:year/:month">

   <requirement
      attr="year"
      expr="d{2,4}"/>

   <requirement
      attr="month"
      expr="d{1,2}"/>

   </route>

Example 1
---------

Below is an example of some route statements you might add to your
``configure.zcml``: 

.. code-block:: xml
   :linenos:

   <route
    path="ideas/:idea"
    view_name="ideas"/>

   <route
    path="users/:user"
    view_name="users"/>

   <route
    path="tags/:tag"
    view_name="tags"/>

The above configuration will allow :mod:`repoze.bfg` to service URLs
in these forms:

.. code-block:: bash
   :linenos:

   /ideas/<ideaname>
   /users/<username>
   /tags/<tagname>

When a URL matches the pattern ``/ideas/<ideaname>``, the view
registered with the name ``ideas`` for the interface
``repoze.bfg.interfaces.IRoutesContext`` will be called.  An error
will be raised if no view can be found with that interface type and
view name combination.

The context object passed to a view found as the result of URL
dispatch will by default be an instance of the
``repoze.bfg.urldispatch.DefaultRoutesContext`` object.  You can
override this behavior by passing in a ``factory`` argument to the
ZCML directive for a particular route.  The ``factory`` should be a
callable that accepts arbitrary keyword arguments and returns an
instance of a class that will be the context used by the view.

An example of using a route with a factory:

.. code-block:: xml
   :linenos:

   <route
    path="ideas/:idea"
    factory=".models.Idea"
    view_name="ideas"/>

The above route will manufacture an ``Idea`` model as a context,
assuming that ``.models.Idea`` resolves to a class that accepts
arbitrary key/value pair arguments.

.. note:: Values prefixed with a period (``.``) for the ``factory``
   and ``provides`` attributes of a ``route`` (such as
   ``.models.Idea`` above) mean "relative to the Python package
   directory in which this :term:`ZCML` file is stored".  So if the
   above ``route`` declaration was made inside a ``configure.zcml``
   file that lived in the ``hello`` package, you could replace the
   relative ``.models.Idea`` with the absolute ``hello.models.Idea``
   Either the relative or absolute form is functionally equivalent.
   It's often useful to use the relative form, in case your package's
   name changes.  It's also shorter to type.

All context objects manufactured via URL dispatch will be decorated by
default with the ``repoze.bfg.interfaces.IRoutesContext``
:term:`interface`.  To decorate a context found via a route with other
interfaces, you can use a ``provides`` attribute on the ZCML
statement.  It should be a space-separated list of dotted Python names
that point at interface definitions.

An example of using a route with a set of ``provides`` interfaces:

.. code-block:: xml
   :linenos:

   <route
    path="ideas/:idea"
    provides=".interfaces.IIdea .interfaces.IContent"
    view_name="ideas"/>

The above route will manufacture an instance of
``DefaultRoutesContext`` as a context; it will be decorate with the
``.interfaces.IIdea`` and ``.interfaces.IContent`` interfaces, as long
as those dotted names resolve to interfaces.

If no route matches in the above configuration, :mod:`repoze.bfg` will
call the "fallback" ``get_root`` callable provided to it during
``make_app`.  If the "fallback" ``get_root`` is None, a ``NotFound``
error will be raised when no route matches.

.. note:: See :ref:`using_model_interfaces` for more information about
          how views are found when interfaces are attached to a
          context.  You can also map classes to views; interfaces are
          not used then.

Example 2
---------

An example of configuring a ``view`` declaration in ``configure.zcml``
that maps a context found via :term:`Routes` URL dispatch to a view
function is as follows:

.. code-block:: xml
   :linenos:

   <view
       for=".interfaces.ISomeContext"
       view=".views.articles_view"
       name="articles"
       />

   <route
      path="archives/:article"
      view_name="articles"
      factory=".models.Article"
      provides=".interfaces.ISomeContext"
      />

All context objects found via Routes URL dispatch will provide the
``IRoutesContext`` interface (attached dynamically).  The above
``route`` statement will also cause contexts generated by the route to
have the ``.interfaces.ISomeContext`` interface as well.  The
``.models`` modulemight look like so:

.. code-block:: python
   :linenos:

   class Article(object):
       def __init__(self, **kw):
           self.__dict__.update(kw)

The effect of this configuration: when this :mod:`repoze.bfg`
application runs, if any URL matches the pattern
``archives/:article``, the ``.views.articles_view`` view will be
called with its :term:`context` as a instance of the ``Article``
class.  The ``Article`` instance will have attributes matching the
keys and values in the Routes routing dictionary associated with the
request.

In this case in particular, when a user visits
``/archives/something``, the context will be an instance of the
Article class and it will have an ``article`` attribute with the value
of ``something``.

Example 3
---------

You can also make the ``view_name`` into a routes path argument
instead of specifying it as an argument:

.. code-block:: xml
   :linenos:

   <view
       for="repoze.bfg.interfaces.IRoutesContext"
       view=".views.articles_view"
       name="articles"
       />

   <route
      path="archives/:view_name"
      />

When you do this, the :term:`view name` will be computed dynamically if
the route matches.  In the above example, if the ``view_name`` turns
out to be ``articles``, the articles view will eventually be called.

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
       view_name="root_view"
       />

Cleaning Up After a Request
---------------------------

Often it's required that some cleanup be performed at the end of a
request when a database connection is involved.  When
:term:`traversal` is used, this cleanup is often done as a side effect
of the traversal :term:`root factory`.  Often the root factory will
insert an object into the WSGI environment that performs some cleanup
when its ``__del__`` method is called.  When URL dispatch is used,
however, no root factory is required, so sometimes that option is not
open to you.

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

Using :mod:`repoze.bfg` Security With URL Dispatch
--------------------------------------------------

:mod:`repoze.bfg` provides its own security framework which consults a
:term:`security policy` before allowing any application code to be
called.  This framework operates in terms of ACLs (Access Control
Lists, see :ref:`security_chapter` for more information about the
:mod:`repoze.bfg` security subsystem).  A common thing to want to do
is to attach an ``__acl__`` to the context object dynamically for
declarative security purposes.  You can use the ``factory``
argument that points at a context factory which attaches a custom
``__acl__`` to an object at its creation time.

Such a ``factory`` might look like so:

.. code-block:: python
   :linenos:

   class Article(object):
       def __init__(self, **kw):
           self.__dict__.update(kw)

   def article_factory(**kw):
       model = Article(**kw)
       article = kw.get('article', None)
       if article == '1':
           model.__acl__ = [ (Allow, 'editor', 'view') ]
       return model

If the route ``archives/:article`` is matched, and the article number
is ``1``, :mod:`repoze.bfg` will generate an ``Article``
:term:`context` with an ACL on it that allows the ``editor`` principal
the ``view`` permission.  Obviously you can do more generic things
that inspect the routes match dict to see if the ``article`` argument
matches a particular string; our sample ``article_factory`` function
is not very ambitious.  Its job could have just as well been done in
the ``Article`` class' constructor, too.

.. note:: See :ref:`security_chapter` for more information about
   :mod:`repoze.bfg` security and ACLs.

.. note:: See `Conditions
   <http://routes.groovie.org/manual.html#conditions>`_ in the
   :term:`Routes` manual for a general overview of what the
   ``condition`` argument to ``.connect`` does.

Further Documentation and Examples
----------------------------------

The API documentation in :ref:`urldispatch_module` documents an older
(now-deprecated) version of Routes support in :mod:`repoze.bfg`.

