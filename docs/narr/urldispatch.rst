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
          code in bfg, you will map the URL patterm to a :term:`view`.
          As a result, there is a bit of mental gynmastics you'll need
          to do when dealing with Routes URL dispatch in bfg.  In
          general, whenever you see the name *controller* in the
          context of :term:`Routes`, you should map that mentally to
          the bfg term :term:`view`.  *Actions* do not exist in
          :mod:`repoze.bfg`: in other frameworks these may refer to
          methods of a *controller class*, but since views in
          :mod:`repoze.bfg` are simple callables (usually functions)
          as opposed to classes, there is no direct concept mapping of
          an action.

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

To this end, the :mod:`repoze.bfg` framework defines a module named
:mod:`repoze.bfg.urldispatch`.  This module contains a class named
:class:`RoutesMapper`.  An Instance of this class is willing to act as
a :mod:`repoze.bfg` ``get_root`` callable, and is willing to be
configured with *route mappings* as necessary via its ``.connect``
method.

A ``get_root`` callable is a callable passed to the :mod:`repoze.bfg`
framework by an application, allowing bfg to find the "root" object of
a traversal graph.  The :class:`RoutesMapper` is essentially willing
to act as the "root callable".  When it acts as such a callable, it is
willing to check the requested URL against a *routes map*, and
subsequently look up and call a :mod:`repoze.bfg` view with the
information it finds within a particular route, if any configured
route matches the currently requested URL.  If no URL matches, the
:class:`RoutesMapper` will fall back to calling a ``get_root``
callable that is passed in to it at construction time, which allows
your application to fall back to a different "root" (perhaps one based
on traversal).  By configuring a :class:`RoutesMapper` appropriately,
you can mix and match URL dispatch and traversal in this way.

.. note:: See :ref:`modelspy_project_section` for an example of a
          simple ``get_root`` callable.

Configuring a :class:`RoutesMapper` with individual routes is
performed by creating an instance of a :class:`RoutesMapper`, and
calling its ``.connect`` method with the same arguments you'd use if
you were creating a route mapping using a "raw" :term:`Routes`
``Mapper`` object.  See `Setting up routes
<http://routes.groovie.org/manual.html#setting-up-routes>`_ for
examples of using a Routes ``Mapper`` object.  When you are finished
configuring it, you can pass it as a ``get_root`` callable to
:mod:`repoze.bfg`.

When you configure a :class:`RoutesMapper` with a route via
``.connect``, you'll pass in the name of a ``controller`` as a keyword
argument.  This will be a string.  The string should match the
**name** of a :mod:`repoze.bfg` :term:`view` callable that is
registered for the type ``repoze.bfg.interfaces.IRoutesContext`` (via
a ZCML directive, see :ref:`views_chapter` for more information about
registering bfg views).  When a URL is matched, this view will be
called with a :term:`context` manufactured "on the fly" by the
:class:`RoutesMapper`.  The context object will have attributes which
match all of the :term:`Routes` matching arguments returned by the
mapper.

Example 1
---------

Below is an example of configuring a :class:`RoutesMapper` for usage
as a ``get_root`` callback.

.. code-block:: python
   :linenos:

   from repoze.bfg.urldispatch import RoutesMapper

   def fallback_get_root(environ):
       return {}

   root = RoutesMapper(fallback_get_root)
   root.connect('ideas/:idea', controller='ideas')
   root.connect('users/:user', controller='users')
   root.connect('tags/:tag', controller='tags')

The above configuration will allow the mapper to service URLs in the forms::

   /ideas/<ideaname>
   /users/<username>
   /tags/<tagname>

If this mapper is used as a ``get_root`` callback, when a URL matches
the pattern ``/ideas/<ideaname>``, the view registered with the name
'ideas' for the interface ``repoze.bfg.interfaces.IRoutesContext``
will be called.  An error will be raised if no view can be found with
that interfaces type or name.

The context object passed to a view found as the result of URL
dispatch will be an instance of the
``repoze.bfg.urldispatch.RoutesContext`` object.  You can override
this behavior by passing in a ``context_factory`` argument to the
mapper's connect method for a particular route.  The
``context_factory`` should be a callable that accepts arbitrary
keyword arguments and returns an instance of a class that will be the
context used by the view.

If no route matches in the above configuration, the routes mapper will
call the "fallback" ``get_root`` callable provided to it above.

Example 2
---------

An example of configuring a ``view`` declaration in ``configure.zcml``
that maps a context found via :term:`Routes` URL dispatch to a view
function is as follows:

.. code-block:: xml
   :linenos:

   <view
       for="repoze.bfg.interfaces.IRoutesContext"
       view=".views.articles_view"
       name="articles"
       />

All context objects found via Routes URL dispatch will provide the
``IRoutesContext`` interface (attached dynamically).  You might then
configure the ``RoutesMapper`` like so:

.. code-block:: python
   :linenos:

   from repoze.bfg.router import make_app
   from repoze.bfg.urldispatch import RoutesMapper

   def fallback_get_root(environ):
       return {} # the graph traversal root is empty in this example

   class Article(object):
       def __init__(self, **kw):
           self.__dict__.update(kw)

   get_root = RoutesMapper(fallback_get_root)
   get_root.connect('archives/:article', controller='articles',
                    context_factory=Article)

   import myapp
   app = make_app(get_root, myapp)

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
declarative security purposes.  A Routes 'trick' can allow for this.

Routes makes it possible to pass a ``conditions`` argument to the
``connect`` method of a mapper.  The value of ``conditions`` is a
dictionary.  If you pass a ``conditions`` dictionary to this
``connect`` method with a ``function`` key that has a value which is a
Python function, this function can be used to update the ``__acl__``
of the model object.

When Routes tries to resolve a particular route via a match, the route
object itself will pass the environment and the "match_dict" to the
``conditions`` function.  Typically, a ``conditions`` function decides
whether or not the route match should "succeed".  But we'll use it
differently: we'll use it to update the "match dict".  The match dict
is what is eventually returned by Routes to :mod:`repoze.bfg`.  If the
function that is used as the ``conditions`` function adds an
``__acl__`` key/value pair to the match dict and subsequently always
returns ``True`` (indicating that the "condition" passed), the
resulting ``__acl__`` key and its value will appear in the match
dictionary.  Since all values returned in the match dictionary are
eventually set on your context object, :mod:`repoze.bfg` will set an
``__acl__`` attribute on the context object returned to
:mod:`repoze.bfg` matching the value you've put into the match
dictionary under ``__acl__``, just in time for the :mod:`repoze.bfg`
security machinery to find it.  :mod:`repoze.bfg` security will allow
or deny further processing of the request based on the ACL.

Here's an example:

.. code-block:: python

   from repoze.bfg.router import make_app
   from repoze.bfg.security import Allow
   from repoze.bfg.urldispatch import RoutesMapper

   def fallback_get_root(environ):
       return {} # the graph traversal root is empty in this example

   class Article(object):
       def __init__(self, **kw):
           self.__dict__.update(kw)

   def add_acl(environ, match_dict):
       if match_dict.get('article') == 'article1':
           routes_dict['__acl__'] = [ (Allow, 'editor', 'view') ]

   get_root = RoutesMapper(fallback_get_root)
   get_root.connect('archives/:article', controller='articles',
                    context_factory=Article, conditions={'function':add_acl})

   import myapp
   app = make_app(get_root, myapp)

If the route ``archives/:article`` is matched, :mod:`repoze.bfg` will
generate an ``Article`` :term:`context` with an ACL on it that allows
the ``editor`` principal the ``view`` permission.  Obviously you can
do more generic things that inspect the routes match dict to see if
the ``article`` argument matches a particular string; our sample
``add_acl`` function is not very ambitious.

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

The `repoze.shootout <http://svn.repoze.org/repoze.shootout/trunk/>`_
application uses URL dispatch to serve its "ideas", "users" and "tags"
pages.
