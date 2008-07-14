repoze.bfg
==========

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

It is however possible to map URLs to code slightly differently, using
object graph traversal. The venerable Zope and CherryPy web frameworks
offer traversal-based URL dispatch.  ``repoze.bfg`` also provides
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
based systems.  Over time, the more assertions you make, the more
fragile the URL dispatch lookup logic becomes.  URL-dispatch based
systems don't deal very well with URLs that represent arbitrary-depth
hierarchies.

Graph traversal works well if you need to divine meaning out of these
types of "ambiguous" URLs and URLs that represent arbitrary-depth
hierarchies.  Each URL segment represents a single traversal through
an edge of the graph.  So a URL like ``http://example.com/a/b/c`` can
be thought of as a graph traversal on the example.com site through the
edges "a", "b", and "c".

Graph traversal is materially more complex than URL-based dispatch,
however, if only because it requires the construction and maintenance
of a graph, and it requires the developer to think about mapping URLs
to code in terms of traversing the graph.  (How's *that* for
self-referential! ;-) That said, for developers comfortable with Zope,
in particular, and comfortable with hierarchical data stores like
ZODB, mapping a URL to a graph traversal it's a natural way to think
about creating a web application.  In essence, the choice to use graph
traversal vs. URL dispatch is largely "religious" in some sense and
often doesn't make sense for completely "square" data, but old habits
die hard for folks used to graph-traversal-based lookup.
``repoze.bfg`` is for those folks.

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

Similarities with Other Frameworks
----------------------------------

The Django docs state that Django is an "MTV" framework in their `FAQ
<http://www.djangoproject.com/documentation/faq/>`_.  This also
happens to be true for ``repoze.bfg``::

  Django appears to be a MVC framework, but you call the Controller
  the "view", and the View the "template". How come you don’t use the
  standard names?

  Well, the standard names are debatable.

  In our interpretation of MVC, the "view" describes the data that
  gets presented to the user. It’s not necessarily how the data looks,
  but which data is presented. The view describes which data you see,
  not how you see it. It’s a subtle distinction.

  So, in our case, a "view" is the Python callback function for a
  particular URL, because that callback function describes which data
  is presented.

  Furthermore, it’s sensible to separate content from presentation —
  which is where templates come in. In Django, a "view" describes
  which data is presented, but a view normally delegates to a
  template, which describes how the data is presented.

  Where does the "controller" fit in, then? In Django’s case, it’s
  probably the framework itself: the machinery that sends a request to
  the appropriate view, according to the Django URL configuration.

  If you’re hungry for acronyms, you might say that Django is a "MTV"
  framework — that is, "model", "template", and "view." That breakdown
  makes much more sense.

Jargon
------

The following jargon is used casually in descriptions of
``repoze.bfg`` operations.

mapply

  code which dynamically ("magically") determines which arguments to
  pass to a view based on environment and request parameters.

request

  A ``WebOb`` request object.

response

  An object that has three attributes: app_iter (representing an
  iterable body), headerlist (representing the http headers sent
  upstream), and status (representing the http status string).  This
  is the interface defined for ``WebOb`` response objects.

view

  A callable that accepts arbitrary values (mapped into it by
  "mapply") and which returns a response object.

view constructor

  A callable which returns a view object.  It should accept two
  values: context and request.

model

  An object representing data in the system.  A model is part of the
  object graph traversed by the system.  Models are traversed to
  determine a context.

context

  A model in the system that is the subject of a view.

view registry

  A registry which maps a context and view name to a view constructor.

template

  A file that is capable of representing some text when rendered.

interface

  An attribute of a model object that determines its type.

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

 7.  Armed with the context, the view name, and the subpath, the
     router performs a view lookup.  It attemtps to look up a view
     constructor from the ``repoze.bfg`` view registry using the view
     name and the context.  If a view constructor is found, it is
     converted into a WSGI application: it is "wrapped in" ( aka
     "adapted to") a WSGI application using mapply.  The WSGI adapter
     uses mapply to map request and environment variables into the
     view when it is called.  If a view constructor is not found, a
     generic WSGI ``NotFound`` application is constructed. 

In either case, the resulting WSGI application is called.  The WSGI
application's return value is an iterable.  This is returned upstream
to the WSGI server.  The WSGI application also calls start_response
with a status code and a header list.

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

views.py
~~~~~~~~

A views.py module might look like so::

  from webob import Response
  from repoze.bfg.view import TemplateView

  class MyHelloView(object):
      def __init__(self, context, request):
          self.context = context
          self.request = request

      def __call__(self):
          response = Response('Hello from %s @ %s' % (
                                  self.context.__name__, 
                                  self.request.environ['PATH_INFO']))
          return response

  class MyTemplateView(TemplateView):

       template = 'templates/my.pt'

       def getInfo(self):
           return {'name':self.context.__name__}

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

  root = Model('root')
  root['a'] = Model('a')
  root['b'] = Model('b')

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
        factory=".views.MyHelloView"
        permission="repoze.view"
        />

    <!-- the templated view for a MyModel -->
    <bfg:view
        for=".models.IMyModel"
        factory=".views.MyTemplateView"
        name="templated.html"
        permission="repoze.view"
        />

  </configure>

templates/my.pt
~~~~~~~~~~~~~~~

A template that is used by a view might look like so::

  <html xmlns="http://www.w3.org/1999/xhtml"
       xmlns:tal="http://xml.zope.org/namespaces/tal">
  <head></head>
  <body tal:define="info view.getInfo()">
    <h1>My template viewing ${info.name}</h1>
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

  app = make_app(myapp.get_root, myapp)
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
