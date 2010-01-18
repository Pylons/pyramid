What's New In :mod:`repoze.bfg` 1.1
===================================

This article explains the new features in :mod:`repoze.bfg` version
1.1 as compared to the previous 1.0 release.  It also documents
backwards incompatibilities between the two versions and deprecations
added to 1.1, as well as software dependency changes and notable
documentation additions.

Major Feature Additions
-----------------------

The major feature additions of 1.1 are:

- Allow the use of additional :term:`view predicate` parameters to
  more finely control view matching.

- Allow the use of :term:`route predicate` parameters to more finely
  control route matching.

- Make it possible to write views that use a :term:`renderer`.

- Make it possible to write views that use a "wrapper view".

- Added ``<static>`` ZCML directive which registers a view which
  serves up files in a package directory.

- A new API function: ``repoze.bfg.url.static_url`` is available to
  compute the path of static resources.

- View configurations can now name an ``attr`` representing the method
  or attribute of the view callable that should be called to return a
  response.

- ``@bfg_view`` decorators may now be stacked, allowing for the same
  view callable to be associated with multiple different view
  configurations without resorting to ZCML for view configuration.

- ``@bfg_view`` decorators may now be placed on a class method.

- ``paster bfgshell`` now supports IPython if it is found in the
  Python environment invoking Paster.

- Commonly executed codepaths have been accelerated.

.. _view_predicates_in_1dot1:

View Predicates
~~~~~~~~~~~~~~~

:mod:`repoze.bfg` 1.0, :term:`view configuration` allowed relatively
coarse matching of a :term:`request` to a :term:`view callable`.
Individual view configurations could match the same URL depending on
the :term:`context` and the URL path, as well as a limited number of
other request values.

For example, two view configurations mentioning the same :term:`view
name` could be spelled via a ``@bfg_view`` decorator with a different
``for_`` parameter.  The view ultimately chosen would be based on the
:term:`context` type based on the ``for_`` attribute like so:

.. ignore-next-block
.. code-block:: python

   from webob import Response
   from repoze.bfg.view import bfg_view
   from myapp.models import Document
   from myapp.models import Folder

   @bfg_view(name='index.html', for_=Document)
   def document_view(context, request):
       return Response('document view')

   @bfg_view(name='index.html', for_=Folder)
   def folder_view(context, request):
       return Response('folder view')

In the above configuration, the ``document_view`` :term:`view
callable` will be chosen when the :term:`context` is of the class
``myapp.models.Document``, while the ``folder_view`` view callable
will be chosen when the context is of class ``myapp.models.Folder``.

There were a number of other attributes that could influence the
choosing of view callables, such as ``request_type``, and others.
However, the matching algorithm was rather limited.

In :mod:`repoze.bfg` 1.1, this facility has been enhanced via the
availability of additional :term:`view predicate` attributes.  For
example, one view predicate new to 1.1 is ``containment``, which
implies that the view will be called when the class or interface
mentioned as ``containment`` is present with respect to any instance
in the :term:`lineage` of the context:

.. ignore-next-block
.. code-block:: python

   from webob import Response
   from repoze.bfg.view import bfg_view
   from myapp.models import Document
   from myapp.models import Folder
   from myapp.models import Blog
   from myapp.models import Calendar

   @bfg_view(name='index.html', for_=Document, containment=Blog)
   def blog_document_view(context, request):
       return Response('blog document view')

   @bfg_view(name='index.html', for_=Folder, containment=Blog)
   def blog_folder_view(context, request):
       return Response('blog folder view')

   @bfg_view(name='index.html', for_=Document, containment=Calendar)
   def calendar_document_view(context, request):
       return Response('calendar document view')

   @bfg_view(name='index.html', for_=Folder, containment=Calendar)
   def calendar_folder_view(context, request):
       return Response('calendar folder view')

As might be evident in the above example, you can use the
``containment`` predicate to arrange for different view callables to
be called based on the lineage of the context.  In the above example,
the ``blog_document_view`` will be called when the context is of the
class ``myapp.models.Document`` and the containment has an instance of
the class ``myapp.models.Blog`` in it.  But when all else is equal,
except the containment has an instance of the class
``myapp.models.Calendar`` in it instead of ``myapp.models.Blog``, the
``calendar_document_view`` will be called instead.

All view predicates configurable via the ``@bfg_view`` decorator are
available via :term:`ZCML` :term:`view configuration` as well.

Additional new 1.1 view predicates besides ``containment`` are:

``request_method``

  True if the specified value (e.g. GET/POST/HEAD/PUT/DELETE) is the
  request.method value.

``request_param``

  True if the specified value is present in the request.GET or
  request.POST multidicts.

``xhr``

  True if the request.is_xhr attribute is ``True``, meaning that the
  request has an ``X-Requested-With`` header with the value
  ``XMLHttpRequest``

``accept``

  True if the value of this attribute represents matches one or more
  mimetypes in the ``Accept`` HTTP request header.

``header`` 

  True if the value of this attribute represents an HTTP header name
  or a header name/value pair present in the request.

``path_info``

  True if the value of this attribute (a regular expression pattern)
  matches the ``PATH_INFO`` WSGI environment variable.

All other existing view configuration parameters from 1.0 still exist.

Any number of view predicates can be specified in a view
configuration.  All view predicates in a view configuration must be
True for a view callable to be invoked.  If one does not evaluate to
True, the view will not be invoked, and view matching will continue,
until all potential matches are exhausted (and the Not Found view is
invoked).

.. _route_predicates_in_1dot1:

Route Predicates
~~~~~~~~~~~~~~~~

In :mod:`repoze.bfg` 1.0, a :term:`route` would match or not match
based on only one value: the ``PATH_INFO`` value of the WSGI
environment, as specified by the ``path`` parameter of the ``<route>``
ZCML directive.

In 1.1, matching can be more finely controlled via the use of one or
more :term:`route predicate` attributes.

The additional route predicates in 1.1 are:

``xhr``

  True if the request.is_xhr attribute is ``True``, meaning that the
  request has an ``X-Requested-With`` header with the value
  ``XMLHttpRequest``.

``request_method``

  True if the specified value (e.g. GET/POST/HEAD/PUT/DELETE) is the
  request.method value.

``path_info``

  True if the value of this attribute (a regular expression pattern)
  matches the ``PATH_INFO`` WSGI environment variable.

``request_param``

  True if the specified value is present in either of the
  ``request.GET`` or ``request.POST`` multidicts.

``header`` 

  True if the value of this attribute represents an HTTP header name
  or a header name/value pair present in the request.

``accept``

  True if the value of this attribute represents matches one or more
  mimetypes in the ``Accept`` HTTP request header.

All other existing route configuration parameters from 1.0 still exist.

Any number of route predicates can be specified in a route
configuration.  All route predicates in a route configuration must be
True for a route to match a request.  If one does not evaluate to
True, the route will not be invoked, and route matching will continue,
until all potential routes are exhausted (at which point, traversal is
attempted).

View Renderers
~~~~~~~~~~~~~~

In :mod:`repoze.bfg` 1.0 and prior, views were required to return a
:term:`response` object unconditionally.

In :mod:`repoze.bfg` 1.1, a :term:`view configuration` can name a
:term:`renderer`.  A renderer can either be a template or a token that
is associated with a serialization technique (e.g. ``json``).  When a
view configuration names a renderer, the view can return a data
structure understood by the renderer (such as a dictionary), and the
renderer will convert the data structure to a response on the behalf
of the developer.

View configuration can vary the renderer associated with a view via
the ``renderer`` attribute to the configuration.  For example, this
ZCML associates the ``json`` renderer with a view:

.. code-block:: xml
   :linenos:

   <view
     view=".views.my_view"
     renderer="json"
     />

The ``@bfg_view`` decorator can also associate a view callable with a
renderer:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='json')
   def my_view(context, request):
       return {'abc':123}

The ``json`` renderer renders view return values to a :term:`JSON`
serialization.

Another built-in renderer uses the :term:`Chameleon` templating
language to render a dictionary to a response.  For example:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='templates/my_template.pt')
   def my_view(context, request):
       return {'abc':123}

See :ref:`built_in_renderers` for the available built-in renderers.

If the ``view`` callable associated with a ``view`` directive returns
a Response object (an object with the attributes ``status``,
``headerlist`` and ``app_iter``), any renderer associated with the
``view`` declaration is ignored, and the response is passed back to
BFG unmolested.  For example, if your view callable returns an
``HTTPFound`` response, no renderer will be employed.

.. code-block:: python
   :linenos:

   from webob.exc import HTTPFound
   from repoze.bfg.view import bfg_view

   @bfg_view(renderer='templates/my_template.pt')
   def my_view(context, request):
       return HTTPFound(location='http://example.com') # renderer avoided

Additional renderers can be added to the system as necessary via a
ZCML directive (see :ref:`adding_and_overriding_renderers`).

If you do not define a ``renderer`` attribute in view configuration
for a view, no renderer is associated with the view.  In such a
configuration, an error is raised when a view does not return an
object which implements :term:`Response` interface, as was the case
under BFG 1.0.

Views Which Use Wrappers
~~~~~~~~~~~~~~~~~~~~~~~~

In :mod:`repoze.bfg` 1.1, view configuration may specify a ``wrapper``
attribute.  For example:

.. code-block:: xml
   :linenos:

   <view
     name="one"
     view=".views.wrapper_view"
     />

   <view
     name="two"
     view=".views.my_view"
     wrapper="one"
     />

The ``wrapper`` attribute of a view configuration is a :term:`view
name` (*not* an object dotted name).  It specifies *another* view
callable declared elsewhere in :term:`view configuration`.  In the
above example, the wrapper of the ``two`` view is the ``one`` view.

The wrapper view will be called when after the wrapped view is
invoked; it will receive the response body of the wrapped view as the
``wrapped_body`` attribute of its own request, and the response
returned by this view as the ``wrapped_response`` attribute of its own
request.

Using a wrapper makes it possible to "chain" views together to form a
composite response.  The response of the outermost wrapper view will
be returned to the user.

The wrapper view will be found as any view is found: see
:ref:`view_lookup`.  The "best" wrapper view will be found based on
the lookup ordering: "under the hood" this wrapper view is looked up
via ``repoze.bfg.view.render_view_to_response(context, request,
'wrapper_viewname')``. The context and request of a wrapper view is
the same context and request of the inner view.

If the ``wrapper`` attribute is unspecified in a view configuration,
no view wrapping is done.

The ``@bfg_view`` decorator accepts a ``wrapper`` parameter, mirroring
its ZCML view configuration counterpart.

``<static>`` ZCML Directive
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A new ZCML directive named ``static`` has been added.  Inserting a
``static`` declaration in a ZCML file will cause static resources to
be served at a configurable URL.

Here's an example of a ``static`` directive that will serve files up
from the ``templates/static`` directory of the :mod:`repoze.bfg`
application containing the following configuration at the URL
``/static``.

.. code-block:: xml
   :linenos:

   <static
      name="static"
      path="templates/static"
      />

Using the ``static`` ZCML directive is now the preferred way to serve
static resources (such as JavaScript and CSS files) within a
:mod:`repoze.bfg` application.  Previous strategies for serving static
resources will still work, however.

New ``static_url`` API
~~~~~~~~~~~~~~~~~~~~~~

The new ``repoze.bfg.url.static_url`` API generates a fully qualified
URL to a static resource available via a path exposed via the
``<static>`` ZCML directive (see :ref:`static_resources_section`).
For example, if a ``<static>`` directive is in ZCML configuration like
so:

.. code-block:: xml
   :linenos:

   <static
      name="static"
      path="templates/static"
      />

You can generate a URL to a resource which lives within the
``templates/static`` subdirectory using the ``static_url`` API like
so:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg.url import static_url
   url = static_url('templates/static/example.css', request)

Use of the ``static_url`` API prevents the developer from needing to
hardcode path values in template URLs.

``attr`` View Configuration Value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The view machinery defaults to using the ``__call__`` method of the
view callable (or the function itself, if the view callable is a
function) to obtain a response.

In :mod:`repoze.bfg` 1.1, the ``attr`` view configuration value allows
you to vary the attribute of a view callable used to obtain the
response.

For example, if your view is a class, and the class has a method named
``index`` and you want to use this method instead of the class'
``__call__`` method to return the response, you'd say ``attr="index"``
in the view configuration for the view.

Specifying ``attr`` is most useful when the view definition is a
class.  For example:

.. code-block:: xml
   :linenos:

   <view
      view=".views.MyViewClass"
      attr="index"
      />

The referenced ``MyViewClass`` might look like so:

.. code-block:: python
   :linenos:

   from webob import Response

   class MyViewClass(object):
       def __init__(context, request):
           self.context = context
           self.request = request

       def index(self):
           return Response('OK')

The ``index`` method of the class will be used to obtain a response.

``@bfg_view`` Decorators May Now Be Stacked
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

More than one ``@bfg_view`` decorator may now be stacked on top of any
number of others.  Each invocation of the decorator registers a single
view configuration.  For instance, the following combination of
decorators and a function will register two view configurations for
the same view callable:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view

   @bfg_view(name='edit')
   @bfg_view(name='change')
   def edit(context, request):
       pass

This makes it possible to associate more than one view configuration
with a single callable without requiring any ZCML.

Stacking ``@bfg_view`` decorators was not possible in
:mod:`repoze.bfg` 1.0.

``@bfg_view`` Decorators May Now Be Applied to A Class Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In :mod:`repoze.bfg` 1.0, the ``@bfg_view`` decorator could not be
used on class methods.  In 1.1, the ``@bfg_view`` decorator can be
used against a class method:

.. code-block:: python
   :linenos:

   from webob import Response
   from repoze.bfg.view import bfg_view

   class MyView(object):
       def __init__(self, context, request):
           self.context = context
           self.request = request

       @bfg_view(name='hello')
       def amethod(self):
           return Response('hello from %s!' % self.context)

When the bfg_view decorator is used against a class method, a view is
registered for the *class* (it's a "class view" where the "attr"
happens to be the name of the method it is attached to), so the class
it's defined within must have a suitable constructor: one that accepts
``context, request`` or just ``request``.

IPython Support
~~~~~~~~~~~~~~~

If it is installed in the environment used to run :mod:`repoze.bfg`,
an `IPython <http://ipython.scipy.org/moin/>`_ shell will be opened
when the ``paster bfgshell`` command is invoked.

Common Codepaths Have Been Accelerated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:mod:`repoze.bfg` 1.1 is roughly 10% - 20% faster in commonly executed
codepaths than :mod:`repoze.bfg` 1.0 was on average.  Accelerated APIs
include ``repoze.bfg.location.lineage``, ``repoze.bfg.url.model_url``,
and ``repoze.bfg.url.route_url``.  Other internal (non-API) functions
were similarly accelerated.

Minor Miscellaneous Feature Additions
-------------------------------------

- For behavior like Django's ``APPEND_SLASH=True``, use the
  ``repoze.bfg.view.append_slash_notfound_view`` view as the Not Found
  view in your application.  When this view is the Not Found view
  (indicating that no view was found), and any routes have been
  defined in the configuration of your application, if the value of
  ``PATH_INFO`` does not already end in a slash, and if the value of
  ``PATH_INFO`` *plus* a slash matches any route's path, do an HTTP
  redirect to the slash-appended PATH_INFO.  Note that this will
  *lose* ``POST`` data information (turning it into a GET), so you
  shouldn't rely on this to redirect POST requests.

- Add ``repoze.bfg.testing.registerSettings`` API, which is documented
  in the "repoze.bfg.testing" API chapter.  This allows for
  registration of "settings" values obtained via
  ``repoze.bfg.settings.get_settings()`` for use in unit tests.

- Added ``max_age`` parameter to ``authtktauthenticationpolicy`` ZCML
  directive.  If this value is set, it must be an integer representing
  the number of seconds which the auth tkt cookie will survive.
  Mainly, its existence allows the auth_tkt cookie to survive across
  browser sessions.

- The ``reissue_time`` argument to the ``authtktauthenticationpolicy``
  ZCML directive now actually works.  When it is set to an integer
  value, an authticket set-cookie header is appended to the response
  whenever a request requires authentication and 'now' minus the
  authticket's timestamp is greater than ``reissue_time`` seconds.

- Expose and document ``repoze.bfg.testing.zcml_configure`` API.  This
  function populates a component registry from a ZCML file for testing
  purposes.  It is documented in the "Unit and Integration Testing"
  chapter.

- Virtual hosting narrative docs chapter updated with info about
  ``mod_wsgi``.

- Added "Creating Integration Tests" section to unit testing narrative
  documentation chapter.  As a result, the name of the unittesting
  chapter is now "Unit and Integration Testing".

- Add a new ``repoze.bfg.testing`` API: ``registerRoute``, for
  registering routes to satisfy calls to
  e.g. ``repoze.bfg.url.route_url`` in unit tests.

- Added a tutorial which explains how to use ``repoze.session``
  (ZODB-based sessions) in a ZODB-based repoze.bfg app.

- Added a tutorial which explains how to add ZEO to a ZODB-based
  ``repoze.bfg`` application.

- Added a tutorial which explains how to run a ``repoze.bfg``
  application under `mod_wsgi <http://code.google.com/p/modwsgi/>`_.
  See "Running a repoze.bfg Application under mod_wsgi" in the
  tutorials section of the documentation.

- Allow ``repoze.bfg.traversal.find_interface`` API to use a class
  object as the argument to compare against the ``model`` passed in.
  This means you can now do ``find_interface(model, SomeClass)`` and
  the first object which is found in the lineage which has
  ``SomeClass`` as its class (or the first object found which has
  ``SomeClass`` as any of its superclasses) will be returned.

- The ordering of route declarations vs. the ordering of view
  declarations that use a "route_name" in ZCML no longer matters.
  Previously it had been impossible to use a route_name from a route
  that had not yet been defined in ZCML (order-wise) within a "view"
  declaration.

- The repoze.bfg router now catches both
  ``repoze.bfg.exceptions.Unauthorized`` and
  ``repoze.bfg.exceptions.NotFound`` exceptions while rendering a view.
  When the router catches an ``Unauthorized``, it returns the
  registered forbidden view.  When the router catches a ``NotFound``,
  it returns the registered notfound view.

- Add a new event type: ``repoze.bfg.events.AfterTraversal``.  Events
  of this type will be sent after traversal is completed, but before
  any view code is invoked.  Like ``repoze.bfg.events.NewRequest``,
  This event will have a single attribute: ``request`` representing
  the current request.  Unlike the request attribute of
  ``repoze.bfg.events.NewRequest`` however, during an AfterTraversal
  event, the request object will possess attributes set by the
  traverser, most notably ``context``, which will be the context used
  when a view is found and invoked.  The interface
  ``repoze.bfg.events.IAfterTraversal`` can be used to subscribe to
  the event.  For example::

    <subscriber for="repoze.bfg.interfaces.IAfterTraversal"
                handler="my.app.handle_after_traverse"/>

  Like any framework event, a subscriber function should expect one
  parameter: ``event``.

- A ``repoze.bfg.testing.registerRoutesMapper`` testing facility has
  been added.  This testing function registers a routes "mapper"
  object in the registry, for tests which require its presence.  This
  function is documented in the ``repoze.bfg.testing`` API
  documentation.

Backwards Incompatibilities
---------------------------

- The ``authtkt`` authentication policy ``remember`` method now no
  longer honors ``token`` or ``userdata`` keyword arguments.

- Importing ``getSiteManager`` and ``get_registry`` from
  ``repoze.bfg.registry`` is no longer supported.  These imports were
  deprecated in repoze.bfg 1.0.  Import of ``getSiteManager`` should
  be done as ``from zope.component import getSiteManager``.  Import of
  ``get_registry`` should be done as ``from repoze.bfg.threadlocal
  import get_current_registry``.  This was done to prevent a circular
  import dependency.

- Code bases which alternately invoke both
  ``zope.testing.cleanup.cleanUp`` and ``repoze.bfg.testing.cleanUp``
  (treating them equivalently, using them interchangeably) in the
  setUp/tearDown of unit tests will begin to experience test failures
  due to lack of test isolation.  The "right" mechanism is
  ``repoze.bfg.testing.cleanUp`` (or the combination of
  ``repoze.bfg.testing.setUp`` and
  ``repoze.bfg.testing.tearDown``). but a good number of legacy
  codebases will use ``zope.testing.cleanup.cleanUp`` instead.  We
  support ``zope.testing.cleanup.cleanUp`` but not in combination with
  ``repoze.bfg.testing.cleanUp`` in the same codebase.  You should use
  one or the other test cleanup function in a single codebase, but not
  both.

- In 0.8a7, the return value expected from an object implementing
  ``ITraverserFactory`` was changed from a sequence of values to a
  dictionary containing the keys ``context``, ``view_name``,
  ``subpath``, ``traversed``, ``virtual_root``, ``virtual_root_path``,
  and ``root``.  Until now, old-style traversers which returned a
  sequence have continued to work but have generated a deprecation
  warning.  In this release, traversers which return a sequence
  instead of a dictionary will no longer work.

- The interfaces ``IPOSTRequest``, ``IGETRequest``, ``IPUTRequest``,
  ``IDELETERequest``, and ``IHEADRequest`` have been removed from the
  ``repoze.bfg.interfaces`` module.  These were not documented as APIs
  post-1.0.  Instead of using one of these, use a ``request_method``
  ZCML attribute or ``request_method`` bfg_view decorator parameter
  containing an HTTP method name (one of ``GET``, ``POST``, ``HEAD``,
  ``PUT``, ``DELETE``) instead of one of these interfaces if you were
  using one explicitly.  Passing a string in the set (``GET``,
  ``HEAD``, ``PUT``, ``POST``, ``DELETE``) as a ``request_type``
  argument will work too.  Rationale: instead of relying on interfaces
  attached to the request object, BFG now uses a "view predicate" to
  determine the request type.

- Views registered without the help of the ZCML ``view`` directive are
  now responsible for performing their own authorization checking.

- The ``registry_manager`` backwards compatibility alias importable
  from "repoze.bfg.registry", deprecated since repoze.bfg 0.9 has been
  removed.  If you are trying to use the registry manager within a
  debug script of your own, use a combination of the
  "repoze.bfg.paster.get_app" and "repoze.bfg.scripting.get_root" APIs
  instead.

- The ``INotFoundAppFactory`` interface has been removed; it has
  been deprecated since repoze.bfg 0.9.  If you have something like
  the following in your ``configure.zcml``::

   <utility provides="repoze.bfg.interfaces.INotFoundAppFactory"
            component="helloworld.factories.notfound_app_factory"/>

  Replace it with something like::

   <notfound 
       view="helloworld.views.notfound_view"/>

  See "Changing the Not Found View" in the "Hooks" chapter of the
  documentation for more information.

- The ``IUnauthorizedAppFactory`` interface has been removed; it has
  been deprecated since repoze.bfg 0.9.  If you have something like
  the following in your ``configure.zcml``::

   <utility provides="repoze.bfg.interfaces.IUnauthorizedAppFactory"
            component="helloworld.factories.unauthorized_app_factory"/>

  Replace it with something like::

   <forbidden
       view="helloworld.views.forbidden_view"/>

  See "Changing the Forbidden View" in the "Hooks" chapter of the
  documentation for more information.

- ``ISecurityPolicy``-based security policies, deprecated since
  repoze.bfg 0.9, have been removed.  If you have something like this
  in your ``configure.zcml``, it will no longer work::

   <utility
     provides="repoze.bfg.interfaces.ISecurityPolicy"
     factory="repoze.bfg.security.RemoteUserInheritingACLSecurityPolicy"
     />

   If ZCML like the above exists in your application, you will receive
   an error at startup time.  Instead of the above, you'll need
   something like::

     <remoteuserauthenticationpolicy/>
     <aclauthorizationpolicy/>

   This is just an example.  See the "Security" chapter of the
   repoze.bfg documentation for more information about configuring
   security policies.

- The ``repoze.bfg.scripting.get_root`` function now expects a
  ``request`` object as its second argument rather than an
  ``environ``.

Deprecations and Behavior Differences
-------------------------------------

- In previous versions of BFG, the "root factory" (the ``get_root``
  callable passed to ``make_app`` or a function pointed to by the
  ``factory`` attribute of a route) was called with a "bare" WSGI
  environment.  In this version, and going forward, it will be called
  with a ``request`` object.  The request object passed to the factory
  implements dictionary-like methods in such a way that existing root
  factory code which expects to be passed an environ will continue to
  work.

- The ``__call__`` of a plugin "traverser" implementation (registered
  as an adapter for ``ITraverser`` or ``ITraverserFactory``) will now
  receive a *request* as the single argument to its ``__call__``
  method.  In previous versions it was passed a WSGI ``environ``
  object.  The request object passed to the factory implements
  dictionary-like methods in such a way that existing traverser code
  which expects to be passed an environ will continue to work.

- The request implements dictionary-like methods that mutate and query
  the WSGI environ.  This is only for the purpose of backwards
  compatibility with root factories which expect an ``environ`` rather
  than a request.

- The order in which the router calls the request factory and the root
  factory has been reversed.  The request factory is now called first;
  the resulting request is passed to the root factory.

- Add ``setUp`` and ``tearDown`` functions to the
  ``repoze.bfg.testing`` module.  Using ``setUp`` in a test setup and
  ``tearDown`` in a test teardown is now the recommended way to do
  component registry setup and teardown.  Previously, it was
  recommended that a single function named
  ``repoze.bfg.testing.cleanUp`` be called in both the test setup and
  tear down.  ``repoze.bfg.testing.cleanUp`` still exists (and will
  exist "forever" due to its widespread use); it is now just an alias
  for ``repoze.bfg.testing.setUp`` and is nominally deprecated.

- The import of ``repoze.bfg.security.Unauthorized`` is deprecated in
  favor of ``repoze.bfg.exceptions.Forbidden``.  The old location
  still functions but emits a deprecation warning.  The rename from
  ``Unauthorized`` to ``Forbidden`` brings parity to the name of the
  exception and the system view it invokes when raised.

- Custom ZCML directives which register an authentication or
  authorization policy (ala "authtktauthenticationpolicy" or
  "aclauthorizationpolicy") should register the policy "eagerly" in
  the ZCML directive instead of from within a ZCML action.  If an
  authentication or authorization policy is not found in the component
  registry by the view machinery during deferred ZCML processing, view
  security will not work as expected.

Dependency Changes
------------------

- When used under Python < 2.6, BFG now has an installation time
  dependency on the ``simplejson`` package.

