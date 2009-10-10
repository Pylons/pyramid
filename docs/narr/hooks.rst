.. _hooks_chapter:

Using ZCML Hooks
================

ZCML "hooks" can be used to influence the behavior of the
:mod:`repoze.bfg` framework in various ways.

.. _changing_the_notfound_view:

Changing the Not Found View
---------------------------

When :mod:`repoze.bfg` can't map a URL to view code, it invokes a
notfound :term:`view`. The view it invokes can be customized by
placing something like the following ZCML in your ``configure.zcml``
file.

.. code-block:: xml
   :linenos:

   <notfound 
       view="helloworld.views.notfound_view"/>

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

Other available attributes of the ``notfound`` ZCML directive are as
follows:

attr

  The attribute of the view callable to use if ``__call__`` is not
  correct (has the same meaning as in the context of
  :ref:`the_view_zcml_directive`; see the description of ``attr``
  there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

renderer

  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``) used when the view returns a
  non-:term:`response` object.  This attribute has the same meaning as
  it would in the context of :ref:`the_view_zcml_directive`; see the
  description of ``renderer`` there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

wrapper

  The :term:`view name` (*not* an object dotted name) of another view
  declared elsewhere in ZCML (or via the ``@bfg_view`` decorator)
  which will receive the response body of this view as the
  ``request.wrapped_body`` attribute of its own request, and the
  response returned by this view as the ``request.wrapped_response``
  attribute of its own request.  This attribute has the same meaning
  as it would in the context of :ref:`the_view_zcml_directive`; see
  the description of ``wrapper`` there).  Note that the wrapper view
  *should not* be protected by any permission; behavior is undefined
  if it does.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

.. _changing_the_forbidden_view:

Changing the Forbidden View
---------------------------

When :mod:`repoze.bfg` can't authorize execution of a view based on
the authorization policy in use, it invokes a "forbidden view".  The
default forbidden response has a 401 status code and is very plain,
but it can be overridden as necessary by placing something like the
following ZCML in your ``configure.zcml`` file.

.. code-block:: xml
   :linenos:

   <forbidden
       view="helloworld.views.forbidden_view"/>

Replace ``helloworld.views.forbidden_view`` with the Python
dotted name to the forbidden view you want to use.  Like any other
view, the forbidden view must accept two parameters: ``context`` and
``request`` .  The ``context`` is the context found by the router when
the view invocation was denied.  The ``request`` is the current
:term:`request` representing the denied action.  Here's some sample
code that implements a minimal forbidden view:

.. code-block:: python

   from repoze.bfg.chameleon_zpt import render_template_to_response

   def forbidden_view(context, request):
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
   an alternate forbidden view.  For example, it would make sense to
   return a response with a ``403 Forbidden`` status code.

Other available attributes of the ``forbidden`` ZCML directive are as
follows:

attr

  The attribute of the view callable to use if ``__call__`` is not
  correct (has the same meaning as in the context of
  :ref:`the_view_zcml_directive`; see the description of ``attr``
  there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

renderer

  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``) used when the view returns a
  non-:term:`response` object.  This attribute has the same meaning as
  it would in the context of :ref:`the_view_zcml_directive`; see the
  description of ``renderer`` there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

wrapper

  The :term:`view name` (*not* an object dotted name) of another view
  declared elsewhere in ZCML (or via the ``@bfg_view`` decorator)
  which will receive the response body of this view as the
  ``request.wrapped_body`` attribute of its own request, and the
  response returned by this view as the ``request.wrapped_response``
  attribute of its own request.  This attribute has the same meaning
  as it would in the context of :ref:`the_view_zcml_directive`; see
  the description of ``wrapper`` there).  Note that the wrapper view
  *should not* be protected by any permission; behavior is undefined
  if it does.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.


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


