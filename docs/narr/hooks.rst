.. _hooks_chapter:

Using ZCML Hooks
================

ZCML "hooks" can be used to influence the behavior of the
:mod:`repoze.bfg` framework in various ways.  This is an advanced
topic; not many people will want or need to do any of these things.

Changing the request factory
----------------------------

You may change the class used as the "request factory" from within the
:mod:`repoze.bfg` ``Router`` class (the ``Router`` class turns the
WSGI environment into a "request" object which is used ubiquitously
throughout :mod:`repoze.bfg`).  The default "request factory" is the
class ``webob.Request``.  You may change it by placing the following
ZCML in your ``configure.zcml`` file.

.. code-block:: xml
   :linenos:

   <utility provides="repoze.bfg.interfaces.IRequestFactory"
            component="helloworld.factories.request_factory"/>

Replace ``helloworld.factories.request_factory`` with the Python
dotted name to the request factory you want to use.  Here's some
sample code that implements a minimal request factory:

.. code-block:: python

   from webob import Request
   from repoze.bfg.interfaces import IRequest

   class MyRequest(Request):
       implements(IRequest)

   def request_factory():
       return MyRequest

.. warning:: If you register an ``IRequestFactory`` utility in this
   way, you *must* be sure that the factory returns an object that
   implements *at least* the ``repoze.bfg.interfaces.IRequest``
   interface.  Otherwise all application view lookups will fail (they
   will all return a 404 response code).  Likewise, if you want to be
   able to use method-related interfaces such as ``IGETRequest``,
   ``IPOSTRequest``, etc. in your view declarations, the callable
   returned by the factory must also do the same introspection of the
   environ that the default request factory does and decorate the
   returned object to implement one of these interfaces based on the
   ``HTTP_METHOD`` present in the environ.  Note that the above
   example does not do this, so lookups for method-related interfaces
   will fail.

Changing the response factory
-----------------------------

You may change the class used as the "response factory" from within
the :mod:`repoze.bfg` ``chameleon_zpt``, ``chameleon_genshi``,
``chameleon_text`` (the ``render_template_to_response`` function used
within each) and other various places where a Response object is
constructed by :mod:`repoze.bfg`.  The default "response factory" is
the class ``webob.Response``.  You may change it by placing the
following ZCML in your ``configure.zcml`` file.

.. code-block:: xml
   :linenos:

   <utility provides="repoze.bfg.interfaces.IResponseFactory"
            component="helloworld.factories.response_factory"/>

Replace ``helloworld.factories.response_factory`` with the Python
dotted name to the response factory you want to use.  Here's some
sample code that implements a minimal response factory:

.. code-block:: python

   from webob import Response

   class MyResponse(Response):
      pass

   def response_factory():
       return MyResponse

Unlike a request factory, a response factory does not need to return
an object that implements any particular interface; it simply needs
have a ``status`` attribute, a ``headerlist`` attribute, and and
``app_iter`` attribute.

Changing the Not Found View
---------------------------

When :mod:`repoze.bfg` can't map a URL to view code, it invokes a
notfound :term:`view`. The view it invokes can be customized by
placing something like the following ZCML in your ``configure.zcml``
file.

.. code-block:: xml
   :linenos:

   <utility provides="repoze.bfg.interfaces.INotFoundView"
            component="helloworld.views.notfound_view"/>

Replace ``helloworld.views.notfound_view`` with the Python dotted name
to the notfound view you want to use.  Here's some sample code that
implements a minimal NotFound view:

.. code-block:: python

   from webob.exc import HTTPNotFound

   def notfound_view(context, request):
       return HTTPNotFound()

.. note:: When a NotFound view is invoked, it is passed a request.
   The ``environ`` attribute of the request is the WSGI environment.
   Within the WSGI environ will be a key named ``repoze.bfg.message``
   that has a value explaining why the not found error was raised.
   This error will be different when the ``debug_notfound``
   environment setting is true than it is when it is false.

Changing the Forbidden View
---------------------------

When :mod:`repoze.bfg` can't authorize execution of a view based on
the authorization policy in use, it invokes a "forbidden view".  The
default forbidden response has a 401 status code and is very plain,
but it can be overridden as necessary by placing something like the
following ZCML in your ``configure.zcml`` file.

.. code-block:: xml
   :linenos:

   <utility provides="repoze.bfg.interfaces.IForbiddenView"
            component="helloworld.views.forbidden_view"/>

Replace ``helloworld.factories.forbidden_app_factory`` with the Python
dotted name to the forbidden view you want to use.  Like any other
view, the forbidden view must accept two parameters: ``context`` and
``request`` .  The ``context`` is the context found by the router when
the view invocation was denied.  The ``request`` is the current
:term:`request` representing the denied action.  Here's some sample
code that implements a minimal forbidden view:

.. code-block:: python

   from repoze.bfg.chameleon_zpt import render_template_to_response

   def forbidden_response_factory(context, request):
       return render_template_to_response('templates/login_form.pt')

.. note:: When an forbidden view is invoked, it is passed
   the request as the second argument.  An attribute of the request is
   ``environ``, which is the WSGI environment.  Within the WSGI
   environ will be a key named ``repoze.bfg.message`` that has a value
   explaining why the current view invocation was forbidden.  This
   error will be different when the ``debug_authorization``
   environment setting is true than it is when it is false.

.. warning:: the default forbidden view sends a response with a ``401
   Unauthorized`` status code for backwards compatibility reasons.
   You can influence the status code of Forbidden responses by using
   an alterate forbidden view.  For example, it would make sense to
   return a response with a ``403 Forbidden`` status code.

Changing the Default Routes Context Factory
-------------------------------------------

The default Routes "context factory" (the object used to create
context objects when you use ``<route..>`` statements in your ZCML) is
``repoze.bfg.urldispatch.DefaultRoutesContext``.  You may change the
class used as the Routes "context factory" by placing the following
ZCML in your ``configure.zcml`` file.

.. code-block:: xml
   :linenos:

   <utility provides="repoze.bfg.interfaces.IRoutesContextFactory"
            component="helloworld.factories.routes_context_factory"/>

Replace ``helloworld.factories.routes_context_factory`` with the
Python dotted name to the context factory you want to use.  Here's
some sample code that implements a minimal context factory:

.. code-block:: python

   class RoutesContextFactory(object):
       def __init__(self, **kw):
           self.__dict__.update(kw)

