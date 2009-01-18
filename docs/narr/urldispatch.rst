.. _urldispatch_chapter:

URL Dispatch
============

It is common for :mod:`repoze.bfg` users to rely on :term:`traversal`
to map URLs to code.  However, :mod:`repoze.bfg` can also map URLs to
code via :term:`URL dispatch` using the :term:`Routes` framework.  The
:term:`Routes` framework is a Python reimplementation of the `Rails
routes system <http://manuals.rubyonrails.com/read/chapter/65>`_.  It
is a mechanism which allows you to declaratively map URLs to code.

.. note:: In :term:`Routes` lingo, the code that it allows you to map
          to is defined by a *controller* and an *action*.  However,
          neither concept (controller nor action) exists within
          :mod:`repoze.bfg`.  Instead, when you map a URL pattern to
          code in bfg, you will map the URL patterm to a
          :term:`context` and a :term:`view name`.  Once the context
          is found, "normal" :mod:`repoze.bfg` :term:`view` lookup
          will be done using the context and the view name.

It often makes a lot of sense to use :term:`URL dispatch` instead of
:term:`traversal` in an application that has no natural hierarchy.
For instance, if all the data in your application lives in a
relational database, and that relational database has no
self-referencing tables that form a natural hierarchy, URL dispatch is
easier to use than traversal, and is often a more natural fit for
creating an application that maniplates "flat" data.

Concept and Usage
-----------------

The urldispatch features of :mod:`repoze.bfg` allow you to coopt
natural :term:`traversal`, allowing a :term:`Routes` "mapper" object
to have the "first crack" at resolving a given URL, allowing the
framework to fall back to traversal as necessary.

To this end, the :mod:`repoze.bfg` framework allows you to inject
``route` ZCML directives into your application's ``configure.zcml``
file.  These directives have much the same job as imperatively using
the ``.connect`` method of a routes Mapper object, with some
BFG-specific behavior.

When any ``route`` ZCML directive is used, BFG wraps the "default"
"root factory" (aka ``get_root``) in a special ``RoutesRootFactory``
instance.  This then acts as the root factory (a callable).  When it
acts as such a callable, it is willing to check the requested URL
against a *routes map* to find the :term:`context` and the
:term:`view name`.  Subsequently, BFG will look up and call a
:mod:`repoze.bfg` view with the information it finds within a
particular route, if any configured route matches the currently
requested URL.  If no route matches the configured routes,
:mod:`repoze.bfg` will fail over to calling the ``get_root`` callable
passed to the application in it's ``make_app`` function.  By
configuring your ZCML ``route`` statements appropriately, you can mix
and match URL dispatch and traversal in this way.

.. note:: See :ref:`modelspy_project_section` for an example of a
          simple ``get_root`` callable that will use traversal.

Each ZCML ``route``statement equals a call to the term:`Routes`
``Mapper`` object's ``connect`` method.  See `Setting up routes
<http://routes.groovie.org/manual.html#setting-up-routes>`_ for
examples of using a Routes ``Mapper`` object outside of
:mod:`repoze.bfg`.

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
registered with the name 'ideas' for the interface
``repoze.bfg.interfaces.IRoutesContext`` will be called.  An error
will be raised if no view can be found with that interfaces type or
name.

The context object passed to a view found as the result of URL
dispatch will be an instance of the
``repoze.bfg.urldispatch.RoutesContext`` object.  You can override
this behavior by passing in a ``context_factory`` argument to the ZCML
directive for a particular route.  The ``context_factory`` should be a
callable that accepts arbitrary keyword arguments and returns an
instance of a class that will be the context used by the view.

The context object will be decorated by default with the
``repoze.bfg.interfaces.IRoutesContext`` interface.  To decorate a
context found via a route with other interfaces, you can use a
``context_interfaces`` attribute on the ZCML statement.  It should be
a space-separated list of dotted Python names that point at interfaces.

If no route matches in the above configuration, :mod:`repoze.bfg` will
call the "fallback" ``get_root`` callable provided to it during
``make_app`.  If the "fallback" ``get_root`` is None, a ``NotFound``
error will be raised when no route matches.

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
      context_factory=".models.Article"
      context_interfaces=".interfaces.ISomeContext"
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

Using :mod:`repoze.bfg` Security With URL Dispatch
--------------------------------------------------

:mod:`repoze.bfg` provides its own security framework which consults a
:term:`security policy` before allowing any application code to be
called.  This framework operates in terms of ACLs (Access Control
Lists, see :ref:`security_chapter` for more information about the
:mod:`repoze.bfg` security subsystem).  A common thing to want to do
is to attach an ``__acl__`` to the context object dynamically for
declarative security purposes.  You can use the ``context_factory``
argument that points at a context factory which attaches a custom
``__acl__`` to an object at its creation time.

Such a ``context_factory`` might look like so:

.. code-block:: python
   :linenos:

   class Article(object):
       def __init__(self, **kw):
           self.__dict__.update(kw)

   def article_context_factory(**kw):
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
matches a particular string; our sample ``article_context_factory``
function is not very ambitious.

.. note:: See :ref:`security_chapter` for more information about
   :mod:`repoze.bfg` security and ACLs.

.. note:: See `Conditions
   <http://routes.groovie.org/manual.html#conditions>`_ in the
   :term:`Routes` manual for a general overview of what the
   ``condition`` argument to ``.connect`` does.

Further Documentation and Examples
----------------------------------

URL-dispatch related API documentation is available in
:ref:`urldispatch_module` .

