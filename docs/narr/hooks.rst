.. _hooks_chapter:

Using ZCML Hooks
================

ZCML "hooks" can be used to influence the behavior of the
:mod:`repoze.bfg` framework in various ways.  This is an advanced
topic; very few people will want or need to do any of these things.

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
            component=".my.request.factory"/>

Replace ``my.request.factory`` with the Python dotted name to the
request factory you want to use.

.. warning:: If you register an IRequestFactory utility in such a way,
   you *must* be sure that the factory returns an object that
   implements *at least* the ``repoze.bfg.interfaces.IRequest``
   interface.  Otherwise all application view lookups will fail (they
   will all return a 404 response code).  Likewise, if you want to be
   able to use method-related interfaces such as ``IGETRequest``,
   ``IPOSTRequest``, etc. in your view declarations, your factory must
   also do the same introspection of the environ that the default
   request factory does, and cause the custom factory to decorate the
   returned object to implement one of these interfaces based on the
   ``HTTP_METHOD`` present in the environ.

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
            component=".my.response.factory"/>

Replace ``my.response.factory`` with the Python dotted name to the
response factory you want to use.

