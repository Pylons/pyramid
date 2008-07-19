repoze.bfg Introduction
=======================

``repoze.bfg`` is a system for routing web requests to applications
based on graph traversal.  It is inspired by Zope's publisher, and
uses Zope libraries to do much of its work.  However, it is less
ambitious and less featureful than any released version of Zope's
publisher.

``repoze.bfg`` uses the WSGI protocol to handle requests and
responses, and integrates Zope, Paste, and WebOb libraries to form the
basis for a simple web object publishing framework.

Graph Traversal
---------------

In many popular web frameworks, a "URL dispatcher" is used to
associate a particular URL with a bit of code (known somewhat
ambiguously as a "controller" or "view" depending upon the particular
vocabulary religion to which you subscribe).  These systems allow the
developer to create "urlconfs" or "routes" to controller/view Python
code using pattern matching against URL components.  Examples:
`Django's URL dispatcher
<http://www.djangoproject.com/documentation/url_dispatch/>`_ and the
`Routes URL mapping system <http://routes.groovie.org/>`_ .

It is however possible to map URLs to code differently, using object
graph traversal. The venerable Zope and CherryPy web frameworks offer
graph-traversal-based URL dispatch.  ``repoze.bfg`` also provides
graph-traversal-based dispatch of URLs to code.  Graph-traversal based
dispatching is useful if you like the URL to be representative of an
arbitrary hierarchy of potentially heterogeneous items.

Non-graph traversal based URL dispatch can easily handle URLs such as
``http://example.com/members/Chris``, where it's assumed that each
item "below" ``members`` in the URL represents a member in the system.
You just match everything "below" ``members`` to a particular view.
They are not very good, however, at inferring the difference between
sets of URLs such as ``http://example.com/members/Chris/document`` vs.
``http://example.com/members/Chris/stuff/page`` wherein you'd like the
``document`` in the first URL to represent, e.g. a PDF document, and
``/stuff/page`` in the second to represent, e.g. an OpenOffice
document in a "stuff" folder.  It takes more pattern matching
assertions to be able to make URLs like these work in URL-dispatch
based systems, and some assertions just aren't possible.  For example,
URL-dispatch based systems don't deal very well with URLs that
represent arbitrary-depth hierarchies.

Graph traversal works well if you need to divine meaning out of these
types of "ambiguous" URLs and URLs that represent arbitrary-depth
hierarchies.  Each URL segment represents a single traversal through
an edge of the graph.  So a URL like ``http://example.com/a/b/c`` can
be thought of as a graph traversal on the example.com site through the
edges "a", "b", and "c".

Finally, if you're willing to treat your application models as a graph
that can be traversed, it also becomes trivial to provide "row-level
security" (in common relational parlance): you just attach a security
declaration to each instance in the graph.  This is not as easy in
frameworks that use URL-based dispatch.

Graph traversal is materially more complex than URL-based dispatch,
however, if only because it requires the construction and maintenance
of a graph, and it requires the developer to think about mapping URLs
to code in terms of traversing the graph.  (How's *that* for
self-referential! ;-) That said, for developers comfortable with Zope,
in particular, and comfortable with hierarchical data stores like
ZODB, mapping a URL to a graph traversal it's a natural way to think
about creating a web application.

In essence, the choice to use graph traversal vs. URL dispatch is
largely religious in some sense.  Graph traversal dispatch probably
just doesn't make any sense when you possess completely "square" data
stored in a relational database.  However, when you have a
hierarchical data store, it can provide advantages over using
URL-based dispatch.

Similarities with Other Frameworks
----------------------------------

The Django docs state that Django is an "MTV" framework in their `FAQ
<http://www.djangoproject.com/documentation/faq/>`_.  This also
happens to be true for ``repoze.bfg``::

  Django appears to be a MVC framework, but you call the Controller
  the "view", and the View the "template". How come you don't use the
  standard names?

  Well, the standard names are debatable.

  In our interpretation of MVC, the "view" describes the data that
  gets presented to the user. It's not necessarily how the data looks,
  but which data is presented. The view describes which data you see,
  not how you see it. It's a subtle distinction.

  So, in our case, a "view" is the Python callback function for a
  particular URL, because that callback function describes which data
  is presented.

  Furthermore, it's sensible to separate content from presentation -
  which is where templates come in. In Django, a "view" describes
  which data is presented, but a view normally delegates to a
  template, which describes how the data is presented.

  Where does the "controller" fit in, then? In Django's case, it's
  probably the framework itself: the machinery that sends a request to
  the appropriate view, according to the Django URL configuration.

  If you're hungry for acronyms, you might say that Django is a "MTV"
  framework - that is, "model", "template", and "view." That breakdown
  makes much more sense.

How ``repoze.bfg`` is Configured
--------------------------------

Users interact with your ``repoze.bfg``-based application via a
"router", which is itself a WSGI application.  At system startup time,
the router must be configured with a root object from which all
traversal will begin.  The root object is a mapping object, such as a
Python dictionary.  In fact, all items contained in the graph are
either leaf nodes (these have no __getitem__) or container nodes
(these do have a __getitem__).

Items contained within the graph are analogous to the concept of
``model`` objects used by many other frameworks.  They are typically
instances of classes.  Each containerish instance is willing to return
a child or raise a KeyError based on a name passed to its __getitem__.
No leaf-level instance is required to have a __getitem__.

Jargon
------

The following jargon is used casually in descriptions of
``repoze.bfg`` operations.

request

  A ``WebOb`` request object.

response

  An object that has three attributes: app_iter (representing an
  iterable body), headerlist (representing the http headers sent
  upstream), and status (representing the http status string).  This
  is the interface defined for ``WebOb`` response objects.

view

  A "view" is a callable which returns a response object.  It should
  accept two values: context and request.

view name

  The "URL name" of a view, e.g "index.html".  If a view is configured
  without a name, its name is considered to be the empty string (which
  implies the "default view").

model

  An object representing data in the system.  A model is part of the
  object graph traversed by the system.  Models are traversed to
  determine a context.

context

  A model in the system that is the subject of a view.

view registry (aka application registry)

  A registry which maps a context and view name to a view callable and
  optionally a permission.

template

  A file that is capable of representing some text when rendered.

interface

  An attribute of a model object that determines its type.

security policy

  An object that provides a mechanism to check authorization using
  authentication data and a permission associated with a model.  It
  essentially returns "true" if the combination of the authorization
  information in the model (e.g. an ACL) and the authentication data
  in the request (e.g. the REMOTE_USER) allow the action implied by
  the permission associated with the view (e.g. "add").

principal

  A user id or group id.

permission

  A permission is a string token that is associated with a view name
  and a model type by the developer.  Models are decorated with
  security declarations (e.g. ACLs), which reference these tokens
  also.  A security policy attempts to match the view permission
  against the model's statements about which permissions are granted
  to which principal to answer the question "is this user allowed to
  do this".

How ``repoze.bfg`` Processes a Request
--------------------------------------

When a user requests a page from your ``repoze.bfg`` -powered
application, the system uses this algorithm to determine which Python
code to execute:

 1.  The request for the page is presented to ``repoze.bfg``'s
     "router" in terms of a standard WSGI request, which is
     represented by a WSGI environment and a start_response callable.

 2.  The router creates a `WebOb <http://pythonpaste.org/webob/>`_
     request object based on the WSGI environment.

 3.  The router uses the WSGI environment's ``PATH_INFO`` variable to
     determine the path segments to traverse.  The leading slash is
     stripped off `PATH_INFO``, and the remaining path segments are
     split on the slash character to form a traversal sequence, so a
     request with a ``PATH_INFO`` variable of ``/a/b/c`` maps to the
     traversal sequence ``['a', 'b', 'c']``.

 4.  Traversal begins at the root object.  For the traversal sequence
     ``['a', 'b', 'c']``, the root object's __getitem__ is called with
     the name ``a``.  Traversal continues through the sequence.  In
     our example, if the root object's __getitem__ called with the
     name ``a`` returns an object (aka "object A"), that object's
     __getitem__ is called with the name ``b``.  If object A returns
     an object when asked for ``b``, object B's __getitem__ is then
     asked for the name ``c``, and may return object C.

 5.  Traversal ends when a) the entire path is exhausted or b) when
     any graph element raises a KeyError from its __getitem__ or c)
     when any non-final path element traversal does not have a
     __getitem__ method (resulting in a NameError) or d) when any path
     element is prefixed with the set of characters ``@@`` (indicating
     that the characters following the ``@@`` token should be treated
     as a "view name").

 6.  When traversal ends for any of the reasons in the previous step,
     the the last object found during traversal is deemed to be the
     "context".  If the path has been exhausted when traversal ends,
     the "view name" is deemed to be the empty string (``''``).
     However, if the path was not exhausted before traversal
     terminated, the first remaining path element is treated as the
     view name.  Any subseqent path elements after the view name are
     deemed the "subpath".  For instance, if ``PATH_INFO`` was
     ``/a/b`` and the root returned an "A" object, and the "A" object
     returned a "B" object, the router deems that the context is
     "object B", the view name is the empty string, and the subpath is
     the empty sequence.  On the other hand, if ``PATH_INFO`` was
     ``/a/b/c`` and "object A" was found but raised a KeyError for the
     name ``b``, the router deems that the context is object A, the
     view name is ``b`` and the subpath is ``['c']``.

 7.  If a security policy is configured, the router performs a
     permission lookup.  If a permission declaration is found for the
     view name and context implied by the current request, the
     security policy is consulted to see if the "current user" (also
     determined by the security policy) can perform the action.  If he
     can, processing continues.  If he cannot, an HTTPUnauthorized
     error is raised.

 8.  Armed with the context, the view name, and the subpath, the
     router performs a view lookup.  It attemtps to look up a view
     from the ``repoze.bfg`` view registry using the view name and the
     context.  If a view factory is found, it is called with the
     context and the request.  It returns a response, which is fed
     back upstream.  If a view is not found, a generic WSGI
     ``NotFound`` application is constructed.

In either case, the result is returned upstream via the WSGI protocol.

A Traversal Example
-------------------

Let's pretend the user asks for
``http://example.com/foo/bar/baz/biz/buz.txt``. Let's pretend that the
request's ``PATH_INFO`` in that case is ``/foo/bar/baz/biz/buz.txt``.
Let's further pretend that when this request comes in that we're
traversing the follwing graph::

  /--
     |
     |-- foo
          |
          ----bar

Here's what happens:

  - bfg traverses the root, and attempts to find foo, which it finds.

  - bfg traverses foo, and attempts to find bar, which it finds.

  - bfg traverses bar, and attempts to find baz, which it does not
    find ('bar' raises a ``KeyError`` when asked for baz).

The fact that it does not find "baz" at this point does not signify an
error condition.  It signifies that:

  - the "context" is bar (the context is the last item found during
    traversal).

  - the "view name" is ``baz``

  - the "subpath" is ``['biz', 'buz.txt']``

Because it's the "context", bfg examimes "baz" to find out what "type"
it is. Let's say it finds that the context an ``IBar`` type (because
"bar" happens to have an attribute attached to it that indicates it's
an ``IBar``).

Using the "view name" ("baz") and the type, it asks the "view
registry" (configured separately, in our case via "configure.zcml")
this question:

  - Please find me a "view" (controller in some religions) with the
    name "baz" that can be used for the type ``IBar``.

Let's say it finds no matching view type.  It then returns a NotFound.
The request ends.  Everyone is sad.

But!  For this graph::

  /--
     |
     |-- foo
          |
          ----bar
               |
               ----baz
                      |
                      biz

The user asks for ``http://example.com/foo/bar/baz/biz/buz.txt``

  - bfg traverses foo, and attempts to find bar, which it finds.

  - bfg traverses bar, and attempts to find baz, which it finds.

  - bfg traverses baz, and attempts to find biz, which it finds.

  - bfg traverses biz, and attemtps to find "buz.txt" which it does
    not find.

The fact that it does not find "biz.txt" at this point does not
signify an error condition.  It signifies that:

  - the "context" is biz (the context is the last item found during traversal).

  - the "view name" is "buz.txt"

  - the "subpath" is the empty list []

Because it's the "context", bfg examimes "biz" to find out what "type"
it is. Let's say it finds that the context an ``IBiz`` type (because
"biz" happens to have an attribute attached to it that happens
indicates it's an ``IBiz``).

Using the "view name" ("buz.txt") and the type, it asks the "view
registry" (configured separately, in our case in "configure.zcml")
this question:

  - Please find me a "view" (controller in some religions) with the name
    "buz.txt" that can be used for type ``IBiz``.

Let's say that question is answered "here you go, here'a a bit of code
that is willing to deal with that case", and returns a view.  It is
passed the "biz" object as the "context" and the current WebOb request
as the "request".  It returns a response.

There are two special cases:

- During traversal you will often end up with a "view name" that is
  the empty string.  This indicates that ``repoze.bfg`` should look up
  the *default view*.  The default view is a view that is registered
  with no name or a view which is registered with a name that equals
  the empty string.

- If any path segment element begins with the special characters
  ``@@`` (think of them as goggles), that element is considered the
  view name immediately and traversal stops there.  This allows you to
  address views that may have the same names as model instance names
  without conflict.

A Sample Application
--------------------

A typical simple ``repoze.bfg`` application consists of four things:

  1. A ``views.py`` module, which contains view code.

  2. A ``models.py`` module, which contains model code.

  3. A ``configure.zcml`` file which maps view names to model types.
     This is also known as the "view registry", although it also
     often contains non-view-related declarations.

  4. A "templates" directory, which is full of zc3.pt templates.

An application must be a Python package (meaning it must have an
__init__.py and it must be findable on the PYTHONPATH).

We don't describe any security in our very simple sample application.
Security is optional in a repoze.bfg application; it needn't be used
until necessary.

views.py
~~~~~~~~

A views.py module might look like so::

  from webob import Response
  from repoze.bfg.template import render_template_to_response

  def my_hello_view(context, request):
      response = Response('Hello from %s @ %s' % (
                          context.__name__, 
                          request.environ['PATH_INFO']))
      return response

   def my_template_view(context, request):
       return render_template_to_response('templates/my.pt', name=context.__name__)

models.py
~~~~~~~~~

A models.py might look like so::

  from UserDict import UserDict

  from zope.interface import implements
  from zope.interface import Attribute
  from zope.interface import Interface

  class IMyModel(Interface):
      __name__ = Attribute('Name of the model instance')

  class MyModel(UserDict):
      implements(IMyModel)
      def __init__(self, name):
          self.__name__ = name
          UserDict.__init__(self, {})

  # model instance info would typically be stored in a database of some
  # kind; here we put it at module scope for demonstration purposes.

  root = MyModel('root')
  root['a'] = MyModel('a')
  root['b'] = MyModel('b')

  def get_root(environ):
      return root
    
configure.zcml
~~~~~~~~~~~~~~

A view registry might look like so::

  <configure xmlns="http://namespaces.zope.org/zope"
      xmlns:bfg="http://namespaces.repoze.org/bfg"
      i18n_domain="repoze.bfg">

    <!-- this must be included for the view declarations to work -->
    <include package="repoze.bfg" />

    <!-- the default view for a MyModel -->
    <bfg:view
        for=".models.IMyModel"
        view=".views.my_hello_view"
        permission="read"
        />

    <!-- the templated.html view for a MyModel -->
    <bfg:view
        for=".models.IMyModel"
        view=".views.my_template_view"
        name="templated.html"
        permission="read"
        />

  </configure>

templates/my.pt
~~~~~~~~~~~~~~~

A template that is used by a view might look like so::

  <html xmlns="http://www.w3.org/1999/xhtml"
       xmlns:tal="http://xml.zope.org/namespaces/tal">
  <head></head>
  <body>
    <h1>My template viewing ${name}</h1>
  </body>
  </html>

Running the Application
-----------------------

To run the application above, the simplest method is to run it
directly from a starter script (although you might also use Paste to
perform this task)::

  from paste import httpserver

  from repoze.bfg import make_app
  from myapp.models import get_root
  import myapp

  app = make_app(get_root, myapp)
  httpserver.serve(app, host='0.0.0.0', port='5432')
  
Viewing the Application
-----------------------

Visit http://localhost:5432/ in your browser.  You will see::

  Hello from root @ /

Visit http://localhost:5432/a in your browser.  You will see::

  Hello from a @ /a

Visit http://localhost:5432/b in your browser.  You will see::

  Hello from b @ /b

Visit http://localhost:5432/templated.html in your browser.  You will
see::

  My template viewing root


Visit http://localhost:5432/a/templated.html in your browser.  You
will see::

  My template viewing a

Visit http://localhost:5432/b/templated.html in your browser.  You
will see::

  My template viewing b

