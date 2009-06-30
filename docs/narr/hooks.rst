.. _hooks_chapter:

Using ZCML Hooks
================

ZCML "hooks" can be used to influence the behavior of the
:mod:`repoze.bfg` framework in various ways.

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
   an alterate forbidden view.  For example, it would make sense to
   return a response with a ``403 Forbidden`` status code.

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

.. _overriding_resources_section:

Overriding Resources
--------------------

A ZCML directive exists named "resource".  This ZCML directive allows
you to override Chameleon templates within a package (both directories
full of templates and individual template files) with other templates
in the same package or within another package.  This allows you to
"fake out" a view's use of a template, causing it to retrieve a
different template than the one actually named by a relative path to a
call like ``render_template_to_response('templates/mytemplate.pt')``.
For example, you can override a template file by doing::

    <resource
      to_override="some.package:templates/mytemplate.pt"
      override_with="another.package:othertemplates/anothertemplate.pt"
     />

The string passed to "to_override" and "override_with" is named a
"specification".  The colon separator in a specification separates the
package name from a package-relative directory name.  The colon and
the following relative path are optional.  If they are not specified,
the override attempts to resolve every lookup into a package from the
directory of another package.  For example::

    <resource
      to_override="some.package"
      override_with="another.package"
     />


Individual subdirectories within a package can also be overridden::

    <resource
      to_override="some.package:templates/"
      override_with="another.package:othertemplates/"
     />

If you wish to override a directory with another directory, you must
make sure to attach the slash to the end of both the ``to_override``
specification and the ``override_with`` specification.  If you fail to
attach a slash to the end of a specification that points a directory,
you will get unexpected results.  You cannot override a directory
specification with a file specification, and vice versa (a startup
error will occur if you try).

You cannot override a resource with itself (a startup error will
occur if you try).

Only individual *package* resources may be overridden.  Overrides will
not traverse through subpackages within an overridden package.  This
means that if you want to override resources for both
``some.package:templates``, and ``some.package.views:templates``, you
will need to register two overrides.

The package name in a specification may start with a dot, meaning that
the package is relative to the package in which the ZCML file resides.
For example::

    <resource
      to_override=".subpackage:templates/"
      override_with="another.package:templates/"
     />

Overrides for the same ``to_overrides`` specification can be named
multiple times within ZCML.  Each ``override_with`` path will be
consulted in the order defined within ZCML, forming an override search
path.

Resource overrides can actually override resources other than
templates.  Any software which uses the ``pkg_resources``
``get_resource_filename``, ``get_resource_stream`` or
``get_resource_string`` APIs will obtain an overridden file when an
override is used.  However, the only built-in facility which uses the
``pkg_resources`` API within BFG is the templating stuff, so we only
call out template overrides here.

