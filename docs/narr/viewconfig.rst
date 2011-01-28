.. _view_config_chapter:

.. _view_configuration:

View Configuration
==================

.. index::
   single: view lookup

:term:`View configuration` controls how :term:`view lookup` operates in
your application. In earlier chapters, you have been exposed to a few
simple view configuration declarations without much explanation. In this
chapter we will explore the subject in detail.

.. _view_lookup:

View Lookup and Invocation
--------------------------

:term:`View lookup` is the :app:`Pyramid` subsystem responsible for finding
an invoking a :term:`view callable`.  The view lookup subsystem is passed a
:term:`context` and a :term:`request` object.

:term:`View configuration` information stored within in the
:term:`application registry` is compared against the context and request by
the view lookup subsystem in order to find the "best" view callable for the
set of circumstances implied by the context and request.

:term:`View predicate` attributes are an important part of view
configuration that enables the :term:`View lookup` subsystem to find and
invoke the appropriate view.  Predicate attributes can be thought of
like "narrowers".  In general, the greater number of predicate
attributes possessed by a view's configuration, the more specific the
circumstances need to be before the registered view callable will be
invoked.

Mapping a Resource or URL Pattern to a View Callable
----------------------------------------------------

A developer makes a :term:`view callable` available for use within a
:app:`Pyramid` application via :term:`view configuration`.  A view
configuration associates a view callable with a set of statements that
determine the set of circumstances which must be true for the view callable
to be invoked.

A view configuration statement is made about information present in the
:term:`context` resource and the :term:`request`.

View configuration is performed in one of these ways:

- by running a :term:`scan` against application source code which has a
  :class:`pyramid.view.view_config` decorator attached to a Python object as
  per :ref:`mapping_views_using_a_decorator_section`.

- by using the :meth:`pyramid.config.Configurator.add_view` method as per
  :ref:`mapping_views_using_imperative_config_section`.

- By specifying a view within a :term:`route configuration`.  View
  configuration via a route configuration is performed by using the
  :meth:`pyramid.config.Configurator.add_route` method, passing a ``view``
  argument specifying a view callable.

.. note:: A package named ``pyramid_handlers`` (available from PyPI) provides
   an analogue of :term:`Pylons` -style "controllers", which are a special
   kind of view class which provides more automation when your application
   uses :term:`URL dispatch` solely.

.. _view_configuration_parameters:

View Configuration Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All forms of view configuration accept the same general types of arguments.

Many arguments supplied during view configuration are :term:`view predicate`
arguments.  View predicate arguments used during view configuration are used
to narrow the set of circumstances in which :term:`view lookup` will find a
particular view callable.  

In general, the fewer number of predicates which are supplied to a
particular view configuration, the more likely it is that the associated
view callable will be invoked.  The greater the number supplied, the
less likely.  A view with five predicates will always be found and
evaluated before a view with two, for example.  All predicates must
match for the associated view to be called.

This does not mean however, that :app:`Pyramid` "stops looking" when it
finds a view registration with predicates that don't match.  If one set
of view predicates does not match, the "next most specific" view (if
any) is consulted for predicates, and so on, until a view is found, or
no view can be matched up with the request.  The first view with a set
of predicates all of which match the request environment will be
invoked.

If no view can be found with predicates which allow it to be matched up with
the request, :app:`Pyramid` will return an error to the user's browser,
representing a "not found" (404) page.  See :ref:`changing_the_notfound_view`
for more information about changing the default notfound view.

Some view configuration arguments are non-predicate arguments.  These tend to
modify the response of the view callable or prevent the view callable from
being invoked due to an authorization policy.  The presence of non-predicate
arguments in a view configuration does not narrow the circumstances in which
the view callable will be invoked.

Non-Predicate Arguments
+++++++++++++++++++++++

``permission``
  The name of a :term:`permission` that the user must possess in order to
  invoke the :term:`view callable`.  See :ref:`view_security_section` for
  more information about view security and permissions.
  
  If ``permission`` is not supplied, no permission is registered for this
  view (it's accessible by any caller).

``attr``
  The view machinery defaults to using the ``__call__`` method of the
  :term:`view callable` (or the function itself, if the view callable is a
  function) to obtain a response.  The ``attr`` value allows you to vary the
  method attribute used to obtain the response.  For example, if your view
  was a class, and the class has a method named ``index`` and you wanted to
  use this method instead of the class' ``__call__`` method to return the
  response, you'd say ``attr="index"`` in the view configuration for the
  view.  This is most useful when the view definition is a class.

  If ``attr`` is not supplied, ``None`` is used (implying the function itself
  if the view is a function, or the ``__call__`` callable attribute if the
  view is a class).

``renderer``
  Denotes the :term:`renderer` implementation which will be used to construct
  a :term:`response` from the associated view callable's return value. (see
  also :ref:`renderers_chapter`).

  This is either a single string term (e.g. ``json``) or a string implying a
  path or :term:`asset specification` (e.g. ``templates/views.pt``) naming a
  :term:`renderer` implementation.  If the ``renderer`` value does not
  contain a dot (``.``), the specified string will be used to look up a
  renderer implementation, and that renderer implementation will be used to
  construct a response from the view return value.  If the ``renderer`` value
  contains a dot (``.``), the specified term will be treated as a path, and
  the filename extension of the last element in the path will be used to look
  up the renderer implementation, which will be passed the full path.

  When the renderer is a path, although a path is usually just a simple
  relative pathname (e.g. ``templates/foo.pt``, implying that a template
  named "foo.pt" is in the "templates" directory relative to the directory of
  the current :term:`package`), a path can be absolute, starting with a slash
  on UNIX or a drive letter prefix on Windows.  The path can alternately be a
  :term:`asset specification` in the form
  ``some.dotted.package_name:relative/path``, making it possible to address
  template assets which live in a separate package.

  The ``renderer`` attribute is optional.  If it is not defined, the "null"
  renderer is assumed (no rendering is performed and the value is passed back
  to the upstream :app:`Pyramid` machinery unmolested).  Note that if the
  view callable itself returns a :term:`response` (see :ref:`the_response`),
  the specified renderer implementation is never called.

``wrapper``
  The :term:`view name` of a different :term:`view configuration` which will
  receive the response body of this view as the ``request.wrapped_body``
  attribute of its own :term:`request`, and the :term:`response` returned by
  this view as the ``request.wrapped_response`` attribute of its own request.
  Using a wrapper makes it possible to "chain" views together to form a
  composite response.  The response of the outermost wrapper view will be
  returned to the user.  The wrapper view will be found as any view is found:
  see :ref:`view_lookup`.  The "best" wrapper view will be found based on the
  lookup ordering: "under the hood" this wrapper view is looked up via
  ``pyramid.view.render_view_to_response(context, request,
  'wrapper_viewname')``. The context and request of a wrapper view is the
  same context and request of the inner view.

  If ``wrapper`` is not supplied, no wrapper view is used.

``decorator``
  A :term:`dotted Python name` to function (or the function itself) which
  will be used to decorate the registered :term:`view callable`.  The
  decorator function will be called with the view callable as a single
  argument.  The view callable it is passed will accept ``(context,
  request)``.  The decorator must return a replacement view callable which
  also accepts ``(context, request)``.
          
``mapper``
  A Python object or :term:`dotted Python name` which refers to a :term:`view
  mapper`, or ``None``.  By default it is ``None``, which indicates that the
  view should use the default view mapper.  This plug-point is useful for
  Pyramid extension developers, but it's not very useful for 'civilians' who
  are just developing stock Pyramid applications. Pay no attention to the man
  behind the curtain.

Predicate Arguments
+++++++++++++++++++

These arguments modify view lookup behavior. In general, the more predicate
arguments that are supplied, the more specific, and narrower the usage of the
configured view.

``name``
  The :term:`view name` required to match this view callable.  Read
  :ref:`traversal_chapter` to understand the concept of a view name.

  If ``name`` is not supplied, the empty string is used (implying the default
  view).

``context``
  An object representing a Python class that the :term:`context` resource
  must be an instance of *or* the :term:`interface` that the :term:`context`
  resource must provide in order for this view to be found and called.  This
  predicate is true when the :term:`context` resource is an instance of the
  represented class or if the :term:`context` resource provides the
  represented interface; it is otherwise false.

  If ``context`` is not supplied, the value ``None``, which matches any
  resource, is used.

``route_name``
  If ``route_name`` is supplied, the view callable will be invoked only when
  the named route has matched.

  This value must match the ``name`` of a :term:`route configuration`
  declaration (see :ref:`urldispatch_chapter`) that must match before this
  view will be called.  Note that the ``route`` configuration referred to by
  ``route_name`` will usually have a ``*traverse`` token in the value of its
  ``pattern``, representing a part of the path that will be used by
  :term:`traversal` against the result of the route's :term:`root factory`.

  If ``route_name`` is not supplied, the view callable will be have a chance
  of being invoked if no other route was matched. This is when the
  request/context pair found via :term:`resource location` does not indicate
  it matched any configured route.

``request_type``
  This value should be an :term:`interface` that the :term:`request` must
  provide in order for this view to be found and called.

  If ``request_type`` is not supplied, the value ``None`` is used, implying
  any request type.

  *This is an advanced feature, not often used by "civilians"*.

``request_method``
  This value can either be one of the strings ``GET``, ``POST``, ``PUT``,
  ``DELETE``, or ``HEAD`` representing an HTTP ``REQUEST_METHOD``.  A view
  declaration with this argument ensures that the view will only be called
  when the request's ``method`` attribute (aka the ``REQUEST_METHOD`` of the
  WSGI environment) string matches the supplied value.

  If ``request_method`` is not supplied, the view will be invoked regardless
  of the ``REQUEST_METHOD`` of the :term:`WSGI` environment.

``request_param``
  This value can be any string.  A view declaration with this argument
  ensures that the view will only be called when the :term:`request` has a
  key in the ``request.params`` dictionary (an HTTP ``GET`` or ``POST``
  variable) that has a name which matches the supplied value.

  If the value supplied has a ``=`` sign in it,
  e.g. ``request_params="foo=123"``, then the key (``foo``) must both exist
  in the ``request.params`` dictionary, *and* the value must match the right
  hand side of the expression (``123``) for the view to "match" the current
  request.

  If ``request_param`` is not supplied, the view will be invoked without
  consideration of keys and values in the ``request.params`` dictionary.

``containment``
  This value should be a reference to a Python class or :term:`interface`
  that a parent object in the context resource's :term:`lineage` must provide
  in order for this view to be found and called.  The resources in your
  resource tree must be "location-aware" to use this feature.

  If ``containment`` is not supplied, the interfaces and classes in the
  lineage are not considered when deciding whether or not to invoke the view
  callable.

  See :ref:`location_aware` for more information about location-awareness.

``xhr``
  This value should be either ``True`` or ``False``.  If this value is
  specified and is ``True``, the :term:`WSGI` environment must possess an
  ``HTTP_X_REQUESTED_WITH`` (aka ``X-Requested-With``) header that has the
  value ``XMLHttpRequest`` for the associated view callable to be found and
  called.  This is useful for detecting AJAX requests issued from jQuery,
  Prototype and other Javascript libraries.

  If ``xhr`` is not specified, the ``HTTP_X_REQUESTED_WITH`` HTTP header is
  not taken into consideration when deciding whether or not to invoke the
  associated view callable.

``accept``
  The value of this argument represents a match query for one or more
  mimetypes in the ``Accept`` HTTP request header.  If this value is
  specified, it must be in one of the following forms: a mimetype match token
  in the form ``text/plain``, a wildcard mimetype match token in the form
  ``text/*`` or a match-all wildcard mimetype match token in the form
  ``*/*``.  If any of the forms matches the ``Accept`` header of the request,
  this predicate will be true.

  If ``accept`` is not specified, the ``HTTP_ACCEPT`` HTTP header is not
  taken into consideration when deciding whether or not to invoke the
  associated view callable.

``header``
  This value represents an HTTP header name or a header name/value pair.

  If ``header`` is specified, it must be a header name or a
  ``headername:headervalue`` pair.

  If ``header`` is specified without a value (a bare header name only,
  e.g. ``If-Modified-Since``), the view will only be invoked if the HTTP
  header exists with any value in the request.

  If ``header`` is specified, and possesses a name/value pair
  (e.g. ``User-Agent:Mozilla/.*``), the view will only be invoked if the HTTP
  header exists *and* the HTTP header matches the value requested.  When the
  ``headervalue`` contains a ``:`` (colon), it will be considered a
  name/value pair (e.g. ``User-Agent:Mozilla/.*`` or ``Host:localhost``).
  The value portion should be a regular expression.

  Whether or not the value represents a header name or a header name/value
  pair, the case of the header name is not significant.

  If ``header`` is not specified, the composition, presence or absence of
  HTTP headers is not taken into consideration when deciding whether or not
  to invoke the associated view callable.

``path_info``
  This value represents a regular expression pattern that will be tested
  against the ``PATH_INFO`` WSGI environment variable to decide whether or
  not to call the associated view callable.  If the regex matches, this
  predicate will be ``True``.

  If ``path_info`` is not specified, the WSGI ``PATH_INFO`` is not taken into
  consideration when deciding whether or not to invoke the associated view
  callable.

``custom_predicates``
  If ``custom_predicates`` is specified, it must be a sequence of references
  to custom predicate callables.  Use custom predicates when no set of
  predefined predicates do what you need.  Custom predicates can be combined
  with predefined predicates as necessary.  Each custom predicate callable
  should accept two arguments: ``context`` and ``request`` and should return
  either ``True`` or ``False`` after doing arbitrary evaluation of the
  context resource and/or the request.  If all callables return ``True``, the
  associated view callable will be considered viable for a given request.

  If ``custom_predicates`` is not specified, no custom predicates are
  used.

.. index::
   single: view_config decorator

.. _mapping_views_using_a_decorator_section:

View Configuration Using the ``@view_config`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For better locality of reference, you may use the
:class:`pyramid.view.view_config` decorator to associate your view functions
with URLs instead of using :term:`ZCML` or imperative configuration for the
same purpose.

.. warning::

   Using this feature tends to slows down application startup slightly, as
   more work is performed at application startup to scan for view
   declarations.

Usage of the ``view_config`` decorator is a form of :term:`declarative
configuration`, like ZCML, but in decorator form.
:class:`~pyramid.view.view_config` can be used to associate :term:`view
configuration` information -- as done via the equivalent imperative code or
ZCML -- with a function that acts as a :app:`Pyramid` view callable.  All
arguments to the :meth:`pyramid.config.Configurator.add_view` method (save
for the ``view`` argument) are available in decorator form and mean precisely
the same thing.

An example of the :class:`~pyramid.view.view_config` decorator might reside in
a :app:`Pyramid` application module ``views.py``:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from resources import MyResource
   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(name='my_view', request_method='POST', context=MyResource,
                permission='read')
   def my_view(request):
       return Response('OK')

Using this decorator as above replaces the need to add this imperative
configuration stanza:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view('.views.my_view', name='my_view', request_method='POST', 
                   context=MyResource, permission='read')

All arguments to ``view_config`` may be omitted.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config()
   def my_view(request):
       """ My view """
       return Response()

Such a registration as the one directly above implies that the view name will
be ``my_view``, registered with a ``context`` argument that matches any
resource type, using no permission, registered against requests with any
request method, request type, request param, route name, or containment.

The mere existence of a ``@view_config`` decorator doesn't suffice to perform
view configuration.  All that the decorator does is "annotate" the function
with your configuration declarations, it doesn't process them. To make
:app:`Pyramid` process your :class:`~pyramid.view.view_config` declarations,
you *must* do use the ``scan`` method of a
:class:`~pyramid.config.Configurator`:

.. code-block:: python
   :linenos:

   # config is assumed to be an instance of the
   # pyramid.config.Configurator class
   config.scan()

Please see :ref:`decorations_and_code_scanning` for detailed information
about what happens when code is scanned for configuration declarations
resulting from use of decorators like :class:`~pyramid.view.view_config`.

See :ref:`configuration_module` for additional API arguments to the
:meth:`~pyramid.config.Configurator.scan` method.  For example, the method
allows you to supply a ``package`` argument to better control exactly *which*
code will be scanned.

``@view_config`` Placement
++++++++++++++++++++++++++

A :class:`~pyramid.view.view_config` decorator can be placed in various points
in your application.

If your view callable is a function, it may be used as a function decorator:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(name='edit')
   def edit(request):
       return Response('edited!')

If your view callable is a class, the decorator can also be used as a class
decorator in Python 2.6 and better (Python 2.5 and below do not support class
decorators).  All the arguments to the decorator are the same when applied
against a class as when they are applied against a function.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config()
   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

You can use the :class:`~pyramid.view.view_config` decorator as a simple
callable to manually decorate classes in Python 2.5 and below without the
decorator syntactic sugar, if you wish:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   class MyView(object):
       def __init__(self, request):
           self.request = request

       def __call__(self):
           return Response('hello')

   my_view = view_config()(MyView)

More than one :class:`~pyramid.view.view_config` decorator can be stacked on
top of any number of others.  Each decorator creates a separate view
registration.  For example:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(name='edit')
   @view_config(name='change')
   def edit(request):
       return Response('edited!')

This registers the same view under two different names.

The decorator can also be used against class methods:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   class MyView(object):
       def __init__(self, request):
           self.request = request

       @view_config(name='hello')
       def amethod(self):
           return Response('hello')

When the decorator is used against a class method, a view is registered for
the *class*, so the class constructor must accept an argument list in one of
two forms: either it must accept a single argument ``request`` or it must
accept two arguments, ``context, request``.

The method which is decorated must return a :term:`response`.

Using the decorator against a particular method of a class is equivalent to
using the ``attr`` parameter in a decorator attached to the class itself.
For example, the above registration implied by the decorator being used
against the ``amethod`` method could be spelled equivalently as the below:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(attr='amethod', name='hello')
   class MyView(object):
       def __init__(self, request):
           self.request = request

       def amethod(self):
           return Response('hello')

.. index::
   single: add_view

.. _mapping_views_using_imperative_config_section:

View Registration Using :meth:`~pyramid.config.Configurator.add_view`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`pyramid.config.Configurator.add_view` method within
:ref:`configuration_module` is used to configure a view imperatively.  The
arguments to this method are very similar to the arguments that you provide
to the ``@view_config`` decorator.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def hello_world(request):
       return Response('hello!')

   # config is assumed to be an instance of the
   # pyramid.config.Configurator class
   config.add_view(hello_world, name='hello.html')

The first argument, ``view``, is required.  It must either be a Python object
which is the view itself or a :term:`dotted Python name` to such an object.
All other arguments are optional.  See
:meth:`pyramid.config.Configurator.add_view` for more information.

.. index::
   single: resource interfaces

.. _using_resource_interfaces:

Using Resource Interfaces In View Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of registering your views with a ``context`` that names a Python
resource *class*, you can optionally register a view callable with a
``context`` which is an :term:`interface`.  An interface can be attached
arbitrarily to any resource object.  View lookup treats context interfaces
specially, and therefore the identity of a resource can be divorced from that
of the class which implements it.  As a result, associating a view with an
interface can provide more flexibility for sharing a single view between two
or more different implementations of a resource type.  For example, if two
resource objects of different Python class types share the same interface,
you can use the same view configuration to specify both of them as a
``context``.

In order to make use of interfaces in your application during view dispatch,
you must create an interface and mark up your resource classes or instances
with interface declarations that refer to this interface.

To attach an interface to a resource *class*, you define the interface and
use the :func:`zope.interface.implements` function to associate the interface
with the class.

.. code-block:: python
   :linenos:

   from zope.interface import Interface
   from zope.interface import implements

   class IHello(Interface):
       """ A marker interface """

   class Hello(object):
       implements(IHello)

To attach an interface to a resource *instance*, you define the interface and
use the :func:`zope.interface.alsoProvides` function to associate the
interface with the instance.  This function mutates the instance in such a
way that the interface is attached to it.

.. code-block:: python
   :linenos:

   from zope.interface import Interface
   from zope.interface import alsoProvides

   class IHello(Interface):
       """ A marker interface """

   class Hello(object):
       pass

   def make_hello():
       hello = Hello()
       alsoProvides(hello, IHello)
       return hello

Regardless of how you associate an interface, with a resource instance, or a
resource class, the resulting code to associate that interface with a view
callable is the same.  Assuming the above code that defines an ``IHello``
interface lives in the root of your application, and its module is named
"resources.py", the interface declaration below will associate the
``mypackage.views.hello_world`` view with resources that implement, or
provide, this interface.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

   config.add_view('mypackage.views.hello_world', name='hello.html',
                   context='mypackage.resources.IHello')

Any time a resource that is determined to be the :term:`context` provides
this interface, and a view named ``hello.html`` is looked up against it as
per the URL, the ``mypackage.views.hello_world`` view callable will be
invoked.

Note, in cases where a view is registered against a resource class, and a
view is also registered against an interface that the resource class
implements, an ambiguity arises. Views registered for the resource class take
precedence over any views registered for any interface the resource class
implements. Thus, if one view configuration names a ``context`` of both the
class type of a resource, and another view configuration names a ``context``
of interface implemented by the resource's class, and both view
configurations are otherwise identical, the view registered for the context's
class will "win".

For more information about defining resources with interfaces for use within
view configuration, see :ref:`resources_which_implement_interfaces`.

.. index::
   single: view security
   pair: security; view

.. _view_security_section:

Configuring View Security
~~~~~~~~~~~~~~~~~~~~~~~~~

If an :term:`authorization policy` is active, any :term:`permission` attached
to a :term:`view configuration` found during view lookup will be verified.
This will ensure that the currently authenticated user possesses that
permission against the :term:`context` resource before the view function is
actually called.  Here's an example of specifying a permission in a view
configuration using :meth:`~pyramid.config.Configurator.add_view`:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

   config.add_view('myproject.views.add_entry', name='add.html',
                   context='myproject.resources.IBlog', permission='add')

When an :term:`authorization policy` is enabled, this view will be protected
with the ``add`` permission.  The view will *not be called* if the user does
not possess the ``add`` permission relative to the current :term:`context`.
Instead the :term:`forbidden view` result will be returned to the client as
per :ref:`protecting_views`.

.. index::
   single: debugging not found errors
   single: not found error (debugging)

.. _debug_notfound_section:

:exc:`NotFound` Errors
~~~~~~~~~~~~~~~~~~~~~~

It's useful to be able to debug :exc:`NotFound` error responses when they
occur unexpectedly due to an application registry misconfiguration.  To debug
these errors, use the ``PYRAMID_DEBUG_NOTFOUND`` environment variable or the
``debug_notfound`` configuration file setting.  Details of why a view was not
found will be printed to ``stderr``, and the browser representation of the
error will include the same information.  See :ref:`environment_chapter` for
more information about how, and where to set these values.

