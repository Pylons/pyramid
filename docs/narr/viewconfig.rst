.. _view_config_chapter:

.. _view_configuration:

.. _view_lookup:

View Configuration
==================

.. index::
   single: view lookup

:term:`View lookup` is the :app:`Pyramid` subsystem responsible for finding
and invoking a :term:`view callable`.  :term:`View configuration` controls how
:term:`view lookup` operates in your application.  During any given request,
view configuration information is compared against request data by the view
lookup subsystem in order to find the "best" view callable for that request.

In earlier chapters, you have been exposed to a few simple view configuration
declarations without much explanation. In this chapter we will explore the
subject in detail.

.. index::
   pair: resource; mapping to view callable
   pair: URL pattern; mapping to view callable

Mapping a Resource or URL Pattern to a View Callable
----------------------------------------------------

A developer makes a :term:`view callable` available for use within a
:app:`Pyramid` application via :term:`view configuration`.  A view
configuration associates a view callable with a set of statements that
determine the set of circumstances which must be true for the view callable
to be invoked.

A view configuration statement is made about information present in the
:term:`context` resource and the :term:`request`.

View configuration is performed in one of two ways:

- by running a :term:`scan` against application source code which has a
  :class:`pyramid.view.view_config` decorator attached to a Python object as
  per :ref:`mapping_views_using_a_decorator_section`.

- by using the :meth:`pyramid.config.Configurator.add_view` method as per
  :ref:`mapping_views_using_imperative_config_section`.

.. index::
   single: view configuration parameters

.. _view_configuration_parameters:

View Configuration Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All forms of view configuration accept the same general types of arguments.

Many arguments supplied during view configuration are :term:`view predicate`
arguments.  View predicate arguments used during view configuration are used
to narrow the set of circumstances in which :term:`view lookup` will find a
particular view callable.

:term:`View predicate` attributes are an important part of view configuration
that enables the :term:`view lookup` subsystem to find and invoke the
appropriate view.  The greater number of predicate attributes possessed by a
view's configuration, the more specific the circumstances need to be before
the registered view callable will be invoked.  The fewer number of predicates
which are supplied to a particular view configuration, the more likely it is
that the associated view callable will be invoked.  A view with five
predicates will always be found and evaluated before a view with two, for
example.  All predicates must match for the associated view to be called.

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

Other view configuration arguments are non-predicate arguments.  These tend
to modify the response of the view callable or prevent the view callable from
being invoked due to an authorization policy.  The presence of non-predicate
arguments in a view configuration does not narrow the circumstances in which
the view callable will be invoked.

.. _nonpredicate_view_args:

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
  to the upstream :app:`Pyramid` machinery unchanged).  Note that if the
  view callable itself returns a :term:`response` (see :ref:`the_response`),
  the specified renderer implementation is never called.

``http_cache``
  When you supply an ``http_cache`` value to a view configuration, the
  ``Expires`` and ``Cache-Control`` headers of a response generated by the
  associated view callable are modified.  The value for ``http_cache`` may be
  one of the following:

  - A nonzero integer.  If it's a nonzero integer, it's treated as a number
    of seconds.  This number of seconds will be used to compute the
    ``Expires`` header and the ``Cache-Control: max-age`` parameter of
    responses to requests which call this view.  For example:
    ``http_cache=3600`` instructs the requesting browser to 'cache this
    response for an hour, please'.

  - A ``datetime.timedelta`` instance.  If it's a ``datetime.timedelta``
    instance, it will be converted into a number of seconds, and that number
    of seconds will be used to compute the ``Expires`` header and the
    ``Cache-Control: max-age`` parameter of responses to requests which call
    this view.  For example: ``http_cache=datetime.timedelta(days=1)``
    instructs the requesting browser to 'cache this response for a day,
    please'.

  - Zero (``0``).  If the value is zero, the ``Cache-Control`` and
    ``Expires`` headers present in all responses from this view will be
    composed such that client browser cache (and any intermediate caches) are
    instructed to never cache the response.

  - A two-tuple.  If it's a two tuple (e.g. ``http_cache=(1,
    {'public':True})``), the first value in the tuple may be a nonzero
    integer or a ``datetime.timedelta`` instance; in either case this value
    will be used as the number of seconds to cache the response.  The second
    value in the tuple must be a dictionary.  The values present in the
    dictionary will be used as input to the ``Cache-Control`` response
    header.  For example: ``http_cache=(3600, {'public':True})`` means 'cache
    for an hour, and add ``public`` to the Cache-Control header of the
    response'.  All keys and values supported by the
    ``webob.cachecontrol.CacheControl`` interface may be added to the
    dictionary.  Supplying ``{'public':True}`` is equivalent to calling
    ``response.cache_control.public = True``.

  Providing a non-tuple value as ``http_cache`` is equivalent to calling
  ``response.cache_expires(value)`` within your view's body.

  Providing a two-tuple value as ``http_cache`` is equivalent to calling
  ``response.cache_expires(value[0], **value[1])`` within your view's body.

  If you wish to avoid influencing, the ``Expires`` header, and instead wish
  to only influence ``Cache-Control`` headers, pass a tuple as ``http_cache``
  with the first element of ``None``, e.g.: ``(None, {'public':True})``.

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
  A :term:`dotted Python name` to a function (or the function itself) which
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
  The :term:`view name` required to match this view callable.  A ``name``
  argument is typically only used when your application uses
  :term:`traversal`. Read :ref:`traversal_chapter` to understand the concept
  of a view name.

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

  If ``route_name`` is not supplied, the view callable will only have a chance
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
  This value can be one of the strings ``GET``, ``POST``, ``PUT``,
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
  e.g. ``request_param="foo=123"``, then the key (``foo``) must both exist
  in the ``request.params`` dictionary, *and* the value must match the right
  hand side of the expression (``123``) for the view to "match" the current
  request.

  If ``request_param`` is not supplied, the view will be invoked without
  consideration of keys and values in the ``request.params`` dictionary.

``match_param``
  .. note:: This feature is new as of :app:`Pyramid` 1.2.

  This param may be either a single string of the format "key=value" or a
  dict of key/value pairs.

  This argument ensures that the view will only be called when the
  :term:`request` has key/value pairs in its :term:`matchdict` that equal
  those supplied in the predicate.  e.g. ``match_param="action=edit" would
  require the ``action`` parameter in the :term:`matchdict` match the right
  hande side of the expression (``edit``) for the view to "match" the current
  request.

  If the ``match_param`` is a dict, every key/value pair must match for the
  predicate to pass.

  If ``match_param`` is not supplied, the view will be invoked without
  consideration of the keys and values in ``request.matchdict``.

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

Adding View Configuration Using the ``@view_config`` Decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

   Using this feature tends to slows down application startup slightly, as
   more work is performed at application startup to scan for view
   configuration declarations.  For maximum startup performance, use the view
   configuration method described in
   :ref:`mapping_views_using_imperative_config_section` instead.

The :class:`~pyramid.view.view_config` decorator can be used to associate
:term:`view configuration` information with a function, method, or class that
acts as a :app:`Pyramid` view callable.

Here's an example of the :class:`~pyramid.view.view_config` decorator that
lives within a :app:`Pyramid` application module ``views.py``:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from resources import MyResource
   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(route_name='ok', request_method='POST', permission='read')
   def my_view(request):
       return Response('OK')

Using this decorator as above replaces the need to add this imperative
configuration stanza:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view('mypackage.views.my_view', route_name='ok', 
                   request_method='POST', permission='read')

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
:app:`Pyramid` process your :class:`pyramid.view.view_config` declarations,
you *must* use the ``scan`` method of a
:class:`pyramid.config.Configurator`:

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

All arguments to the :class:`~pyramid.view.view_config` decorator mean
precisely the same thing as they would if they were passed as arguments to
the :meth:`pyramid.config.Configurator.add_view` method save for the ``view``
argument.  Usage of the :class:`~pyramid.view.view_config` decorator is a
form of :term:`declarative configuration`, while
:meth:`pyramid.config.Configurator.add_view` is a form of :term:`imperative
configuration`.  However, they both do the same thing.

.. index::
   single: view_config placement

.. _view_config_placement:

``@view_config`` Placement
++++++++++++++++++++++++++

A :class:`~pyramid.view.view_config` decorator can be placed in various points
in your application.

If your view callable is a function, it may be used as a function decorator:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(route_name='edit')
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

   @view_config(route_name='hello')
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

   my_view = view_config(route_name='hello')(MyView)

More than one :class:`~pyramid.view.view_config` decorator can be stacked on
top of any number of others.  Each decorator creates a separate view
registration.  For example:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(route_name='edit')
   @view_config(route_name='change')
   def edit(request):
       return Response('edited!')

This registers the same view under two different names.

The decorator can also be used against a method of a class:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   class MyView(object):
       def __init__(self, request):
           self.request = request

       @view_config(route_name='hello')
       def amethod(self):
           return Response('hello')

When the decorator is used against a method of a class, a view is registered
for the *class*, so the class constructor must accept an argument list in one
of two forms: either it must accept a single argument ``request`` or it must
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

   @view_config(attr='amethod', route_name='hello')
   class MyView(object):
       def __init__(self, request):
           self.request = request

       def amethod(self):
           return Response('hello')


.. index::
   single: add_view

.. _mapping_views_using_imperative_config_section:

Adding View Configuration Using :meth:`~pyramid.config.Configurator.add_view`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`pyramid.config.Configurator.add_view` method within
:ref:`configuration_module` is used to configure a view "imperatively"
(without a :class:`~pyramid.view.view_config` decorator).  The arguments to
this method are very similar to the arguments that you provide to the
:class:`~pyramid.view.view_config` decorator.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def hello_world(request):
       return Response('hello!')

   # config is assumed to be an instance of the
   # pyramid.config.Configurator class
   config.add_view(hello_world, route_name='hello')

The first argument, ``view``, is required.  It must either be a Python object
which is the view itself or a :term:`dotted Python name` to such an object.
In the above example, ``view`` is the ``hello_world`` function.  All other
arguments are optional.  See :meth:`pyramid.config.Configurator.add_view` for
more information.

When you use only :meth:`~pyramid.config.Configurator.add_view` to add view
configurations, you don't need to issue a :term:`scan` in order for the view
configuration to take effect.

.. index::
   single: view_defaults class decorator

.. _view_defaults:

``@view_defaults`` Class Decorator
----------------------------------

.. note::

   This feature is new in Pyramid 1.3.

If you use a class as a view, you can use the
:class:`pyramid.view.view_defaults` class decorator on the class to provide
defaults to the view configuration information used by every ``@view_config``
decorator that decorates a method of that class.

For instance, if you've got a class that has methods that represent "REST
actions", all which are mapped to the same route, but different request
methods, instead of this:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response

   class RESTView(object):
       def __init__(self, request):
           self.request = request

       @view_config(route_name='rest', request_method='GET')
       def get(self):
           return Response('get')

       @view_config(route_name='rest', request_method='POST')
       def post(self):
           return Response('post')

       @view_config(route_name='rest', request_method='DELETE')
       def delete(self):
           return Response('delete')

You can do this:

.. code-block:: python
   :linenos:

   from pyramid.view import view_defaults
   from pyramid.view import view_config
   from pyramid.response import Response

   @view_defaults(route_name='rest')
   class RESTView(object):
       def __init__(self, request):
           self.request = request

       @view_config(request_method='GET')
       def get(self):
           return Response('get')

       @view_config(request_method='POST')
       def post(self):
           return Response('post')

       @view_config(request_method='DELETE')
       def delete(self):
           return Response('delete')

In the above example, we were able to take the ``route_name='rest'`` argument
out of the call to each individual ``@view_config`` statement, because we
used a ``@view_defaults`` class decorator to provide the argument as a
default to each view method it possessed.

Arguments passed to ``@view_config`` will override any default passed to
``@view_defaults``.

The ``view_defaults`` class decorator can also provide defaults to the
:meth:`pyramid.config.Configurator.add_view` directive when a decorated class
is passed to that directive as its ``view`` argument.  For example, instead
of this:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.config import Configurator

   class RESTView(object):
       def __init__(self, request):
           self.request = request

       def get(self):
           return Response('get')

       def post(self):
           return Response('post')

       def delete(self):
           return Response('delete')

   if __name__ == '__main__':
       config = Configurator()
       config.add_route('rest', '/rest')
       config.add_view(
           RESTView, route_name='rest', attr='get', request_method='GET')
       config.add_view(
           RESTView, route_name='rest', attr='post', request_method='POST')
       config.add_view(
           RESTView, route_name='rest', attr='delete', request_method='DELETE')

To reduce the amount of repetion in the ``config.add_view`` statements, we
can move the ``route_name='rest'`` argument to a ``@view_default`` class
decorator on the RESTView class:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config
   from pyramid.response import Response
   from pyramid.config import Configurator

   @view_defaults(route_name='rest')
   class RESTView(object):
       def __init__(self, request):
           self.request = request

       def get(self):
           return Response('get')

       def post(self):
           return Response('post')

       def delete(self):
           return Response('delete')

   if __name__ == '__main__':
       config = Configurator()
       config.add_route('rest', '/rest')
       config.add_view(RESTView, attr='get', request_method='GET')
       config.add_view(RESTView, attr='post', request_method='POST')
       config.add_view(RESTView, attr='delete', request_method='DELETE')

:class:`pyramid.view.view_defaults` accepts the same set of arguments that
:class:`pyramid.view.view_config` does, and they have the same meaning.  Each
argument passed to ``view_defaults`` provides a default for the view
configurations of methods of the class it's decorating.

Normal Python inheritance rules apply to defaults added via
``view_defaults``.  For example:

.. code-block:: python
   :linenos:

   @view_defaults(route_name='rest')
   class Foo(object):
       pass

   class Bar(Foo):
       pass

The ``Bar`` class above will inherit its view defaults from the arguments
passed to the ``view_defaults`` decorator of the ``Foo`` class.  To prevent
this from happening, use a ``view_defaults`` decorator without any arguments
on the subclass:

.. code-block:: python
   :linenos:

   @view_defaults(route_name='rest')
   class Foo(object):
       pass

   @view_defaults()
   class Bar(Foo):
       pass

The ``view_defaults`` decorator only works as a class decorator; using it
against a function or a method will produce nonsensical results.

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

   config.add_route('add', '/add.html', factory='mypackage.Blog')
   config.add_view('myproject.views.add_entry', route_name='add',
                   permission='add')

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
``pyramid.debug_notfound`` configuration file setting.  Details of why a view
was not found will be printed to ``stderr``, and the browser representation of
the error will include the same information.  See :ref:`environment_chapter`
for more information about how, and where to set these values.

.. index::
   single: HTTP caching

.. _influencing_http_caching:

Influencing HTTP Caching
------------------------

.. note:: This feature is new in Pyramid 1.1.

When a non-``None`` ``http_cache`` argument is passed to a view
configuration, Pyramid will set ``Expires`` and ``Cache-Control`` response
headers in the resulting response, causing browsers to cache the response
data for some time.  See ``http_cache`` in :ref:`nonpredicate_view_args` for
the its allowable values and what they mean.

Sometimes it's undesirable to have these headers set as the result of
returning a response from a view, even though you'd like to decorate the view
with a view configuration decorator that has ``http_cache``.  Perhaps there's
an alternate branch in your view code that returns a response that should
never be cacheable, while the "normal" branch returns something that should
always be cacheable.  If this is the case, set the ``prevent_auto`` attribute
of the ``response.cache_control`` object to a non-``False`` value.  For
example, the below view callable is configured with a ``@view_config``
decorator that indicates any response from the view should be cached for 3600
seconds.  However, the view itself prevents caching from taking place unless
there's a ``should_cache`` GET or POST variable:

.. code-block:: python

   from pyramid.view import view_config

   @view_config(http_cache=3600)
   def view(request):
       response = Response()
       if not 'should_cache' in request.params:
           response.cache_control.prevent_auto = True
       return response

Note that the ``http_cache`` machinery will overwrite or add to caching
headers you set within the view itself unless you use ``preserve_auto``.

You can also turn of the effect of ``http_cache`` entirely for the duration
of a Pyramid application lifetime.  To do so, set the
``PYRAMID_PREVENT_HTTP_CACHE`` environment variable or the
``pyramid.prevent_http_cache`` configuration value setting to a true value.
For more information, see :ref:`preventing_http_caching`.

Note that setting ``pyramid.prevent_http_cache`` will have no effect on caching
headers that your application code itself sets.  It will only prevent caching
headers that would have been set by the Pyramid HTTP caching machinery
invoked as the result of the ``http_cache`` argument to view configuration.

.. index::
   pair: view configuration; debugging

Debugging View Configuration
----------------------------

See :ref:`displaying_matching_views` for information about how to display
each of the view callables that might match for a given URL.  This can be an
effective way to figure out why a particular view callable is being called
instead of the one you'd like to be called.
