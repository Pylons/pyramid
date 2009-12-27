.. _zcml_directives:

ZCML Directives
----------------

:term:`ZCML` is an XML dialect that may be used by a :mod:`repoze.bfg`
application to perform :term:`declarative configuration`.  Each
:term:`ZCML directive` supplied by :mod:`repoze.bfg` is documented
in this chapter.

.. _configure_directive:

``configure``
-------------

Because :term:`ZCML` is XML, and because XML requires a single root
tag for each document, every ZCML file used by :mod:`repoze.bfg` must
contain a ``configure`` container directive, which acts as the root
XML tag.  It is a "container" directive because its only job is to
contain other directives.

Attributes
~~~~~~~~~~

``xmlns``

   The default XML namespace used for subdirectives.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <configure xmlns="http://namespaces.repoze.org/bfg">

      <!-- other directives -->

   </configure>

.. _word_on_xml_namespaces:

A Word On XML Namespaces
~~~~~~~~~~~~~~~~~~~~~~~~

Usually, the start tag of the ``<configure>`` container tag has a
default *XML namespace* associated with it. This is usually
``http://namepaces.repoze.org/bfg``, named by the ``xmlns`` attribute
of the ``configure`` start tag.

Using the ``http://namespaces.repoze.org/bfg`` namespace as the
default XML namespace isn't strictly necessary; you can use a
different default namespace as the default.  However, if you do, the
declaration tags which are defined by :mod:`repoze.bfg` such as the
``view`` declaration tag will need to be defined in such a way that
the XML parser that :mod:`repoze.bfg` uses knows which namespace the
:mod:`repoze.bfg` tags are associated with.  For example, the
following files are all completely equivalent:

.. topic:: Use of A Non-Default XML Namespace

  .. code-block:: xml
     :linenos:

      <configure xmlns="http://namespaces.zope.org/zope"
                 xmlns:bfg="http://namespaces.repoze.org/bfg">

        <include package="repoze.bfg.includes" />

        <bfg:view
           view="helloworld.hello_world"
           />

      </configure>

.. topic:: Use of A Per-Tag XML Namespace Without A Default XML Namespace

  .. code-block:: xml
     :linenos:

      <configure>

        <include package="repoze.bfg.includes" />

        <view xmlns="http://namespaces.repoze.org/bfg"
           view="helloworld.hello_world"
           />

      </configure>

For more information about XML namespaces, see `this older, but simple
XML.com article <http://www.xml.com/pub/a/1999/01/namespaces.html>`_.

The conventions in this document assume that the default XML namespace
is ``http://namespaces.repoze.org/bfg``.

Alternatives
~~~~~~~~~~~~

None.

See Also
~~~~~~~~

See also :ref:`helloworld_declarative`.

.. _include_directive:

``include``
-----------

The ``include`` directive includes configuration from an external ZCML
file.  Use of the ``include`` tag allows a user to split configuration
across multiple ZCML files, and allows package distributors to provide
default ZCML configuration for specific purposes which can be
included by the integrator of the package as necessary.

Attributes
~~~~~~~~~~

``package``

   A :term:`dotted Python name` which references a Python :term:`package`.

``filename``

   An absolute or relative filename which references a ZCML file.

The ``package`` and ``filename`` attributes can be used together or
separately as necessary.

Examples
~~~~~~~~

.. topic:: Loading the File Named ``configure.zcml`` from a Package Implicitly

   .. code-block:: xml
      :linenos:

      <include package="some.package" />

.. topic:: Loading the File Named ``other.zcml`` From the Current Package

   .. code-block:: xml
      :linenos:

      <include filename="other.zcml" />

.. topic:: Loading a File From a Subdirectory of the Current Package

   .. code-block:: xml
      :linenos:

      <include filename="subdir/other.zcml" />

.. topic:: Loading the File Named ``/absolute/path/other.zcml``

   .. code-block:: xml
      :linenos:

      <include filename="/absolute/path/other.zcml" />

.. topic:: Loading the File Named ``other.zcml`` From a Package Explicitly

   .. code-block:: xml
      :linenos:

      <include package="some.package" filename="other.zcml" />

Alternatives
~~~~~~~~~~~~

None.

See Also
~~~~~~~~

See also :ref:`helloworld_declarative`.

.. _view_directive:

``view``
--------

A ``view`` declaration directs :mod:`repoze.bfg` to create a single
:term:`view configuration` registration in the current
:term:`application registry`.

The ``view`` ZCML directive has many possible attributes.  Some of the
attributes are descriptive or influence rendering.  Other attributes
are :term:`predicate` attributes, meaning that they imply an
evaluation to true or false when view lookup is performed.

*All* predicates named in a view configuration must evaluate to true
in order for the view callable it names to be considered "invokable"
for a given request.  See :ref:`view_lookup_ordering` for a
description of how a view configuration matches (or doesn't match)
during a request.

The possible attributes of the ``view`` ZCML directive are described
below.  They are divided into predicate and non-predicate categories.

Attributes
~~~~~~~~~~

Non-Predicate Attributes
########################

``view``

  The :term:`dotted Python name` to a :term:`view callable`.  This
  attribute is required unless a ``renderer`` attribute also exists.
  If a ``renderer`` attribute exists on the directive, this attribute
  defaults to a view that returns an empty dictionary (see
  :ref:`views_which_use_a_renderer`).

``permission``

  The name of a *permission* that the user must possess in order to
  call the view.  See :ref:`view_security_section` for more
  information about view security and permissions.

``attr``

  The view machinery defaults to using the ``__call__`` method of the
  view callable (or the function itself, if the view callable is a
  function) to obtain a response dictionary.  The ``attr`` value
  allows you to vary the method attribute used to obtain the response.
  For example, if your view was a class, and the class has a method
  named ``index`` and you wanted to use this method instead of the
  class' ``__call__`` method to return the response, you'd say
  ``attr="index"`` in the view configuration for the view.  This is
  most useful when the view definition is a class.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``renderer``

  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``).  If the renderer value is a single
  term (does not contain a dot ``.``), the specified term will be used
  to look up a renderer implementation, and that renderer
  implementation will be used to construct a response from the view
  return value.  If the renderer term contains a dot (``.``), the
  specified term will be treated as a path, and the filename extension
  of the last element in the path will be used to look up the renderer
  implementation, which will be passed the full path.  The renderer
  implementation will be used to construct a response from the view
  return value.

  Note that if the view itself returns a response (see
  :ref:`the_response`), the specified renderer implementation is never
  called.

  When the renderer is a path, although a path is usually just a
  simple relative pathname (e.g. ``templates/foo.pt``, implying that a
  template named "foo.pt" is in the "templates" directory relative to
  the directory in which the ZCML file is defined), a path can be
  absolute, starting with a slash on UNIX or a drive letter prefix on
  Windows.  The path can alternately be a :term:`resource
  specification` in the form
  ``some.dotted.package_name:relative/path``, making it possible to
  address template resources which live in a separate package.

  The ``renderer`` attribute is optional.  If it is not defined, the
  "null" renderer is assumed (no rendering is performed and the value
  is passed back to the upstream BFG machinery unmolested).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``wrapper``

  The :term:`view name` (*not* an object dotted name) of another view
  declared elsewhere in ZCML (or via the ``@bfg_view`` decorator)
  which will receive the response body of this view as the
  ``request.wrapped_body`` attribute of its own request, and the
  response returned by this view as the ``request.wrapped_response``
  attribute of its own request.  Using a wrapper makes it possible to
  "chain" views together to form a composite response.  The response
  of the outermost wrapper view will be returned to the user.  The
  wrapper view will be found as any view is found: see
  :ref:`view_lookup_ordering`.  The "best" wrapper view will be found
  based on the lookup ordering: "under the hood" this wrapper view is
  looked up via ``repoze.bfg.view.render_view_to_response(context,
  request, 'wrapper_viewname')``. The context and request of a wrapper
  view is the same context and request of the inner view.  If this
  attribute is unspecified, no view wrapping is done.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

Predicate Attributes
####################

``name``

  The *view name*.  Read the :ref:`traversal_chapter` to understand
  the concept of a view name.

``for``

  A :term:`dotted Python name` representing the Python class that the
  :term:`context` must be an instance of, *or* the :term:`interface`
  that the :term:`context` must provide in order for this view to be
  found and called.  This predicate is true when the :term:`context`
  is an instance of the represented class or if the :term:`context`
  provides the represented interface; it is otherwise false.

``route_name``

  *This attribute services an advanced feature that isn't often used
  unless you want to perform traversal after a route has matched.*
  This value must match the ``name`` of a ``<route>`` declaration (see
  :ref:`urldispatch_chapter`) that must match before this view will be
  called.  Note that the ``route`` configuration referred to by
  ``route_name`` usually has a ``*traverse`` token in the value of its
  ``path``, representing a part of the path that will be used by
  traversal against the result of the route's :term:`root factory`.
  See :ref:`hybrid_chapter` for more information on using this
  advanced feature.

``request_type``

  This value should be a :term:`dotted Python name` string
  representing the :term:`interface` that the :term:`request` must
  have in order for this view to be found and called.  The presence of
  this attribute is largely for backwards compatibility with
  applications written for :mod:`repoze.bfg` version 1.0.  This value
  may be an HTTP ``REQUEST_METHOD`` string, e.g.  ('GET', 'HEAD',
  'PUT', 'POST', or 'DELETE').  Passing request method strings as a
  ``request_type`` is deprecated.  Use the ``request_method``
  attribute instead for maximum forward compatibility.

``request_method``

  This value can either be one of the strings 'GET', 'POST', 'PUT',
  'DELETE', or 'HEAD' representing an HTTP ``REQUEST_METHOD``.  A view
  declaration with this attribute ensures that the view will only be
  called when the request's ``method`` (aka ``REQUEST_METHOD``) string
  matches the supplied value.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``request_param``

  This value can be any string.  A view declaration with this
  attribute ensures that the view will only be called when the request
  has a key in the ``request.params`` dictionary (an HTTP ``GET`` or
  ``POST`` variable) that has a name which matches the supplied value.
  If the value supplied to the attribute has a ``=`` sign in it,
  e.g. ``request_params="foo=123"``, then the key (``foo``) must both
  exist in the ``request.params`` dictionary, and the value must match
  the right hand side of the expression (``123``) for the view to
  "match" the current request.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``containment``

  This value should be a :term:`dotted Python name` string
  representing the class that a graph traversal parent object of the
  :term:`context` must be an instance of (or :term:`interface` that a
  parent object must provide) in order for this view to be found and
  called.  Your models must be "location-aware" to use this feature.
  See :ref:`location_aware` for more information about
  location-awareness.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``xhr``

  This value should be either ``True`` or ``False``.  If this value is
  specified and is ``True``, the :term:`request` must possess an
  ``HTTP_X_REQUESTED_WITH`` (aka ``X-Requested-With``) header that has
  the value ``XMLHttpRequest`` for this view to be found and called.
  This is useful for detecting AJAX requests issued from jQuery,
  Prototype and other Javascript libraries.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``accept``

  The value of this attribute represents a match query for one or more
  mimetypes in the ``Accept`` HTTP request header.  If this value is
  specified, it must be in one of the following forms: a mimetype
  match token in the form ``text/plain``, a wildcard mimetype match
  token in the form ``text/*`` or a match-all wildcard mimetype match
  token in the form ``*/*``.  If any of the forms matches the
  ``Accept`` header of the request, this predicate will be true.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``header``

  The value of this attribute represents an HTTP header name or a
  header name/value pair.  If the value contains a ``:`` (colon), it
  will be considered a name/value pair (e.g. ``User-Agent:Mozilla/.*``
  or ``Host:localhost``).  The *value* of an attribute that represent
  a name/value pair should be a regular expression.  If the value does
  not contain a colon, the entire value will be considered to be the
  header name (e.g. ``If-Modified-Since``).  If the value evaluates to
  a header name only without a value, the header specified by the name
  must be present in the request for this predicate to be true.  If
  the value evaluates to a header name/value pair, the header
  specified by the name must be present in the request *and* the
  regular expression specified as the value must match the header
  value.  Whether or not the value represents a header name or a
  header name/value pair, the case of the header name is not
  significant.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``path_info``

  The value of this attribute represents a regular expression pattern
  that will be tested against the ``PATH_INFO`` WSGI environment
  variable.  If the regex matches, this predicate will be true.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``custom_predicates``

  This value should be a sequence of references to custom predicate
  callables (e.g. ``dotted.name.one dotted.name.two``, if used in
  ZCML; a :term:`dotted Python name` to each callable separated by a
  space).  Use custom predicates when no set of predefined predicates
  do what you need.  Custom predicates can be combined with predefined
  predicates as necessary.  Each custom predicate callable should
  accept two arguments: ``context`` and ``request`` and should return
  either ``True`` or ``False`` after doing arbitrary evaluation of the
  context and/or the request.  If all callables return ``True``, the
  associated view callable will be considered viable for a given
  request.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.2.

Examples
~~~~~~~~

.. topic:: Registering A Default View for a Class

  .. code-block:: xml
     :linenos:

        <view
           for=".models.MyModel"
           view=".views.hello_world"
         />

.. topic:: Registering A View With a Predicate

  .. code-block:: xml
     :linenos:

        <view
           for=".models.MyModel"
           view=".views.hello_world_post"
           request_method="POST"
         />

Alternatives
~~~~~~~~~~~~

You can also add a :term:`view configuration` via:

- Using the :class:`repoze.bfg.view.bfg_view` class as a decorator.

- Using the :meth:`repoze.bfg.configuration.Configurator.add_view` method.

See Also
~~~~~~~~

See also :ref:`views_chapter`.

.. _route_directive:

``route``
---------

The ``route`` directive adds a single :term:`route configuration` to
the :term:`application registry`.

Attributes
~~~~~~~~~~

``path``

  The path of the route e.g. ``ideas/:idea``.  This attribute is
  required.  See :ref:`route_path_pattern_syntax` for information
  about the syntax of route paths.

``name``

  The name of the route, e.g. ``myroute``.  This attribute is
  required.  It must be unique among all defined routes in a given
  configuration.

``factory``

  The :term:`dotted Python name` to a function that will generate a
  :mod:`repoze.bfg` context object when this route matches.
  e.g. ``mypackage.models.MyFactoryClass``.  If this argument is not
  specified, a default root factory will be used.

``view``

  The :term:`dotted Python name` to a function that will be used as a
  view callable when this route matches.
  e.g. ``mypackage.views.my_view``.

``xhr``

  This value should be either ``True`` or ``False``.  If this value is
  specified and is ``True``, the :term:`request` must possess an
  ``HTTP_X_REQUESTED_WITH`` (aka ``X-Requested-With``) header for this
  route to match.  This is useful for detecting AJAX requests issued
  from jQuery, Prototype and other Javascript libraries.  If this
  predicate returns false, route matching continues.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``request_method``

  A string representing an HTTP method name, e.g. ``GET``, ``POST``,
  ``HEAD``, ``DELETE``, ``PUT``.  If this argument is not specified,
  this route will match if the request has *any* request method.  If
  this predicate returns false, route matching continues.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``path_info``

  The value of this attribute represents a regular expression pattern
  that will be tested against the ``PATH_INFO`` WSGI environment
  variable.  If the regex matches, this predicate will be true.  If
  this predicate returns false, route matching continues.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``request_param``

  This value can be any string.  A view declaration with this
  attribute ensures that the associated route will only match when the
  request has a key in the ``request.params`` dictionary (an HTTP
  ``GET`` or ``POST`` variable) that has a name which matches the
  supplied value.  If the value supplied to the attribute has a ``=``
  sign in it, e.g. ``request_params="foo=123"``, then the key
  (``foo``) must both exist in the ``request.params`` dictionary, and
  the value must match the right hand side of the expression (``123``)
  for the route to "match" the current request.  If this predicate
  returns false, route matching continues.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``header``

  The value of this attribute represents an HTTP header name or a
  header name/value pair.  If the value contains a ``:`` (colon), it
  will be considered a name/value pair (e.g. ``User-Agent:Mozilla/.*``
  or ``Host:localhost``).  The *value* of an attribute that represent
  a name/value pair should be a regular expression.  If the value does
  not contain a colon, the entire value will be considered to be the
  header name (e.g. ``If-Modified-Since``).  If the value evaluates to
  a header name only without a value, the header specified by the name
  must be present in the request for this predicate to be true.  If
  the value evaluates to a header name/value pair, the header
  specified by the name must be present in the request *and* the
  regular expression specified as the value must match the header
  value.  Whether or not the value represents a header name or a
  header name/value pair, the case of the header name is not
  significant.  If this predicate returns false, route matching
  continues.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``accept``

  The value of this attribute represents a match query for one or more
  mimetypes in the ``Accept`` HTTP request header.  If this value is
  specified, it must be in one of the following forms: a mimetype
  match token in the form ``text/plain``, a wildcard mimetype match
  token in the form ``text/*`` or a match-all wildcard mimetype match
  token in the form ``*/*``.  If any of the forms matches the
  ``Accept`` header of the request, this predicate will be true.  If
  this predicate returns false, route matching continues.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``custom_predicates``

  This value should be a sequence of references to custom predicate
  callables.  Use custom predicates when no set of predefined
  predicates does what you need.  Custom predicates can be combined
  with predefined predicates as necessary.  Each custom predicate
  callable should accept two arguments: ``context`` and ``request``
  and should return either ``True`` or ``False`` after doing arbitrary
  evaluation of the context and/or the request.  If all callables
  return ``True``, the associated route will be considered viable for
  a given request.  If any custom predicate returns ``False``, route
  matching continues.  Note that the value ``context`` will always be
  ``None`` when passed to a custom route predicate.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.2.

``view_for``

  The :term:`dotted Python name` to a class or an interface that the
  :term:`context` of the view should match for the view named by the
  route to be used.  This attribute is only useful if the ``view``
  attribute is used.  If this attribute is not specified, the default
  (``None``) will be used.

  If the ``view`` attribute is not provided, this attribute has no
  effect.

  This attribute can also be spelled as ``for``.

``view_permission``

  The permission name required to invoke the view associated with this
  route.  e.g. ``edit``. (see :ref:`using_security_with_urldispatch`
  for more information about permissions).

  If the ``view`` attribute is not provided, this attribute has no
  effect.

  This attribute can also be spelled as ``permission``.

``view_renderer``

  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``).  If the renderer value is a single
  term (does not contain a dot ``.``), the specified term will be used
  to look up a renderer implementation, and that renderer
  implementation will be used to construct a response from the view
  return value.  If the renderer term contains a dot (``.``), the
  specified term will be treated as a path, and the filename extension
  of the last element in the path will be used to look up the renderer
  implementation, which will be passed the full path.  The renderer
  implementation will be used to construct a response from the view
  return value.  See :ref:`views_which_use_a_renderer` for more
  information.

  If the ``view`` attribute is not provided, this attribute has no
  effect.

  This attribute can also be spelled as ``renderer``.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``view_request_type``

  A :term:`dotted Python name` to an interface representing a
  :term:`request type`.  If this argument is not specified, any
  request type will be considered a match for the view associated with
  this route.

  If the ``view`` attribute is not provided, this attribute has no
  effect.

  This attribute can also be spelled as ``request_type``.

``view_containment``

  This value should be a :term:`dotted Python name` string
  representing the class that a graph traversal parent object of the
  :term:`context` must be an instance of (or :term:`interface` that a
  parent object must provide) in order for this view to be found and
  called.  Your models must be "location-aware" to use this feature.
  See :ref:`location_aware` for more information about
  location-awareness.

  If the ``view`` attribute is not provided, this attribute has no
  effect.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``view_attr``

  The view machinery defaults to using the ``__call__`` method of the
  view callable (or the function itself, if the view callable is a
  function) to obtain a response dictionary.  The ``attr`` value allows
  you to vary the method attribute used to obtain the response.  For
  example, if your view was a class, and the class has a method named
  ``index`` and you wanted to use this method instead of the class'
  ``__call__`` method to return the response, you'd say
  ``attr="index"`` in the view configuration for the view.  This is
  most useful when the view definition is a class.

  If the ``view`` attribute is not provided, this attribute has no
  effect.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

Alternatives
~~~~~~~~~~~~

You can also add a :term:`route configuration` via:

- Using the :meth:`repoze.bfg.configuration.Configurator.add_route` method.

See Also
~~~~~~~~

See also :ref:`urldispatch_chapter`.

.. _subscriber_directive:

``subscriber``
--------------

The ``subscriber`` ZCML directive configures an :term:`subscriber`
callable to listen for events broadcast by the :mod:`repoze.bfg` web
framework.

Attributes
~~~~~~~~~~

``for``

   The class or :term:`interface` that you are subscribing the
   listener for, e.g. :class:`repoze.bfg.interfaces.INewRequest`.
   Registering a subscriber for a specific class or interface limits
   the event types that the subscriber will receive to those specified
   by the interface or class.  Default: ``zope.interface.Interface``
   (implying *any* event type).

``handler``

   A :term:`dotted Python name` which references an event handler
   callable.  The callable should accept a single argument: ``event``.
   The return value of the callable is ignored.

Examples
~~~~~~~~

.. code-block:: xml
   :linenos:

   <subscriber
      for="repoze.bfg.interfaces.INewRequest"
      handler=".subscribers.handle_new_request"
    />

Alternatives
~~~~~~~~~~~~

You can also register an event listener by using the
:meth:`repoze.bfg.configuration.Configurator.add_subscriber` method.

See Also
~~~~~~~~

See also :ref:`events_chapter`.

.. _notfound_directive:

``notfound``
------------

When :mod:`repoze.bfg` can't map a URL to view code, it invokes a
:term:`not found view`.  The default not found view is very plain, but
the view callable used can be configured via the ``notfound`` ZCML
tag.

Attributes
~~~~~~~~~~

``view``

  The :term:`dotted Python name` to a :term:`view callable`.  This
  attribute is required unless a ``renderer`` attribute also exists.
  If a ``renderer`` attribute exists on the directive, this attribute
  defaults to a view that returns an empty dictionary (see
  :ref:`views_which_use_a_renderer`).

``attr``

  The attribute of the view callable to use if ``__call__`` is not
  correct (has the same meaning as in the context of
  :ref:`view_directive`; see the description of ``attr``
  there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``renderer``

  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``) used when the view returns a
  non-:term:`response` object.  This attribute has the same meaning as
  it would in the context of :ref:`view_directive`; see the
  description of ``renderer`` there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``wrapper``

  The :term:`view name` (*not* an object dotted name) of another view
  declared elsewhere in ZCML (or via the ``@bfg_view`` decorator)
  which will receive the response body of this view as the
  ``request.wrapped_body`` attribute of its own request, and the
  response returned by this view as the ``request.wrapped_response``
  attribute of its own request.  This attribute has the same meaning
  as it would in the context of :ref:`view_directive`; see
  the description of ``wrapper`` there).  Note that the wrapper view
  *should not* be protected by any permission; behavior is undefined
  if it does.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <notfound 
       view="helloworld.views.notfound_view"/>

Alternatives
~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.set_notfound_view`
method performs the same job as the ``notfound`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`changing_the_notfound_view`.

.. _forbidden_directive:

``forbidden``
-------------

When :mod:`repoze.bfg` can't authorize execution of a view based on
the :term:`authorization policy` in use, it invokes a :term:`forbidden
view`.  The default forbidden response has a 401 status code and is
very plain, but it can be overridden as necessary using the
``forbidden`` ZCML directive.

Attributes
~~~~~~~~~~

``view``

  The :term:`dotted Python name` to a :term:`view callable`.  This
  attribute is required unless a ``renderer`` attribute also exists.
  If a ``renderer`` attribute exists on the directive, this attribute
  defaults to a view that returns an empty dictionary (see
  :ref:`views_which_use_a_renderer`).

``attr``

  The attribute of the view callable to use if ``__call__`` is not
  correct (has the same meaning as in the context of
  :ref:`view_directive`; see the description of ``attr``
  there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``renderer``

  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``) used when the view returns a
  non-:term:`response` object.  This attribute has the same meaning as
  it would in the context of :ref:`view_directive`; see the
  description of ``renderer`` there).

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

``wrapper``

  The :term:`view name` (*not* an object dotted name) of another view
  declared elsewhere in ZCML (or via the ``@bfg_view`` decorator)
  which will receive the response body of this view as the
  ``request.wrapped_body`` attribute of its own request, and the
  response returned by this view as the ``request.wrapped_response``
  attribute of its own request.  This attribute has the same meaning
  as it would in the context of :ref:`view_directive`; see the
  description of ``wrapper`` there).  Note that the wrapper view
  *should not* be protected by any permission; behavior is undefined
  if it does.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <forbidden
       view="helloworld.views.forbidden_view"/>

Alternatives
~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.set_forbidden_view`
method performs the same job as the ``forbidden`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`changing_the_forbidden_view`.

.. _scan_directive:

``scan``
--------

To make use of :term:`configuration decoration` decorators, you must
perform a :term:`scan`.  A scan finds these decorators in code.  The
``scan`` ZCML directive tells :mod:`repoze.bfg` to begin such a scan.

Attributes
~~~~~~~~~~

``package``

    The package to scan or the single dot (``.``), meaning the
    "current" package (the package in which the ZCML file lives).

Example
~~~~~~~

.. code-block:: xml
   :linenos:
    
   <scan package="."/>

Alternatives
~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.scan` method performs
the same job as the ``scan`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`mapping_views_to_urls_using_a_decorator_section`.

.. _resource_directive:

``resource``
------------

The ``resource`` directive adds a resource override for a single
resource.

Attributes
~~~~~~~~~~

``to_override``

   A :term:`resource specification` specifying the resource to be
   overridden.

``override_with``

   A :term:`resource specification` specifying the resource which
   is used as the override.

Examples
~~~~~~~~

.. topic:: Overriding a Single Resource File

  .. code-block:: xml
     :linenos:

     <resource
       to_override="some.package:templates/mytemplate.pt"
       override_with="another.package:othertemplates/anothertemplate.pt"
     />

.. topic:: Overriding all Resources in a Package

  .. code-block:: xml
     :linenos:

     <resource
       to_override="some.package"
       override_with="another.package"
      />

.. topic:: Overriding all Resources in a Subdirectory of a Package

  .. code-block:: xml
     :linenos:

     <resource
       to_override="some.package:templates/"
       override_with="another.package:othertemplates/"
      />

Alternatives
~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.override_resource`
method can be used instead of the ``resource`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`resource_zcml_directive`.

.. _static_directive:

``static``
----------

Use of the ``static`` ZCML directive or allows you to serve static
resources (such as JavaScript and CSS files) within a
:mod:`repoze.bfg` application. Theis mechanism makes static files
available at a name relative to the application root URL.

Attributes
~~~~~~~~~~

``name``

  The (application-root-relative) URL prefix of the static directory.
  For example, to serve static files from ``/static`` in most
  applications, you would provide a ``name`` of ``static``.

``path``

  A path to a directory on disk where the static files live.  This
  path may either be 1) absolute (e.g. ``/foo/bar/baz``) 2)
  Python-package-relative (e.g. (``packagename:foo/bar/baz``) or 3)
  relative to the package directory in which the ZCML file which
  contains the directive (e.g. ``foo/bar/baz``).

``cache_max_age``

  The number of seconds that the static resource can be cached, as
  represented in the returned response's ``Expires`` and/or
  ``Cache-Control`` headers, when any static file is served from this
  directive.  This defaults to 3600 (5 minutes).  Optional.

Examples
~~~~~~~~

.. topic:: Serving Static Files from an Absolute Path

   .. code-block:: xml
      :linenos:

      <static
         name="static"
         path="/var/www/static"
         />

.. topic:: Serving Static Files from a Package-Relative Path

   .. code-block:: xml
      :linenos:

      <static
         name="static"
         path="some_package:a/b/c/static"
         />

.. topic:: Serving Static Files from a Current-Package-Relative Path

   .. code-block:: xml
      :linenos:

      <static
         name="static"
         path="static_files"
         />

Alternatives
~~~~~~~~~~~~

:meth:`repoze.bfg.configuration.configurator.add_static_view` can also
be used to add a static view.

See Also
~~~~~~~~

See also :ref:`static_resources_section` and
:ref:`generating_static_resource_urls`.

.. _renderer_directive:

``renderer``
------------

The ``renderer`` ZCML directive can be used to override an existing
existing :term:`renderer` or to add a new renderer.

Attributes
~~~~~~~~~~

``factory``

    A :term:`dotted Python name` referencing a callable object that
    accepts a renderer name and returns a :term:`renderer` object.

``name``

   The renderer name, which is a string.

Examples
~~~~~~~~

.. topic:: Registering a Non-Template Renderer

   .. code-block:: xml
      :linenos:

      <renderer
         factory="some.renderer"
         name="mynewrenderer"
         />

.. topic:: Registering a Template Renderer

   .. code-block:: xml
      :linenos:

      <renderer
         factory="some.jinja2.renderer"
         name=".jinja2"
         />

Alternatives
~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.add_renderer` method
is equivalent to the ``renderer`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`adding_and_overriding_renderers`.

.. _authtktauthenticationpolicy_directive:

``authtktauthenticationpolicy``
-------------------------------

When this directive is used, authentication information is obtained
from an :mod:`paste.auth.auth_tkt` cookie value, assumed to be set by
a custom login form.

Attributes
~~~~~~~~~~

``secret``

    The ``secret`` is a string that will be used to encrypt the data
    stored by the cookie.  It is required and has no default.

``callback``

    The ``callback`` is a Python dotted name to a function passed the
    string representing the userid stored in the cookie and the
    request as positional arguments.  The callback is expected to
    return None if the user represented by the string doesn't exist or
    a sequence of group identifiers (possibly empty) if the user does
    exist.  If ``callback`` is None, the userid will be assumed to
    exist with no groups.  It defaults to ``None``.

``cookie_name``

    The ``cookie_name`` is the name used for the cookie that contains
    the user information.  It defaults to ``repoze.bfg.auth_tkt``.

``secure``

    ``secure`` is a boolean value.  If it's set to "true", the cookie
    will only be sent back by the browser over a secure (HTTPS)
    connection.  It defaults to "false".

``include_ip``

    ``include_ip`` is a boolean value.  If it's set to true, the
    requesting IP address is made part of the authentication data in
    the cookie; if the IP encoded in the cookie differs from the IP of
    the requesting user agent, the cookie is considered invalid.  It
    defaults to "false".

``timeout``

    ``timeout`` is an integer value.  It represents the maximum age in
    seconds which the auth_tkt ticket will be considered valid.  If
    ``timeout`` is specified, and ``reissue_time`` is also specified,
    ``reissue_time`` must be a smaller value than ``timeout``.  It
    defaults to ``None``, meaning that the ticket will be considered
    valid forever.

``reissue_time``

    ``reissue_time`` is an integer value.  If ``reissue_time`` is
    specified, when we encounter a cookie that is older than the
    reissue time (in seconds), but younger that the ``timeout``, a new
    cookie will be issued.  It defaults to ``None``, meaning that
    authentication cookies are never reissued.  A value of ``0`` means
    reissue a cookie in the response to every request that requires
    authentication.

``max_age``

    ``max_age`` is the maximum age of the auth_tkt *cookie*, in
    seconds.  This differs from ``timeout`` inasmuch as ``timeout``
    represents the lifetime of the ticket contained in the cookie,
    while this value represents the lifetime of the cookie itself.
    When this value is set, the cookie's ``Max-Age`` and ``Expires``
    settings will be set, allowing the auth_tkt cookie to last between
    browser sessions.  It is typically nonsensical to set this to a
    value that is lower than ``timeout`` or ``reissue_time``, although
    it is not explicitly prevented.  It defaults to ``None``, meaning
    (on all major browser platforms) that auth_tkt cookies will last
    for the lifetime of the user's browser session.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <authtktauthenticationpolicy
    secret="goshiamsosecret"
    callback=".somemodule.somefunc"
    cookie_name="mycookiename"
    secure="false"
    include_ip="false"
    timeout="86400"
    reissue_time="600"
    max_age="31536000"
    />

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`repoze.bfg.authentication.AuthTktAuthenticationPolicy` and
pass it to the :class:`repoze.bfg.configuration.Configurator`
constructor as the ``authentication_policy`` argument during initial
application configuration.

See Also
~~~~~~~~

See also :ref:`authentication_policies_directives_section` and
:class:`repoze.bfg.authentication.AuthTktAuthenticationPolicy`.

.. _remoteuserauthenticationpolicy_directive:

``remoteuserauthenticationpolicy``
----------------------------------

When this directive is used, authentication information is obtained
from a ``REMOTE_USER`` key in the WSGI environment, assumed to
be set by a WSGI server or an upstream middleware component.

Attributes
~~~~~~~~~~

``environ_key``

    The ``environ_key`` is the name that will be used to obtain the
    remote user value from the WSGI environment.  It defaults to
    ``REMOTE_USER``.

``callback``

    The ``callback`` is a Python dotted name to a function passed the
    string representing the remote user and the request as positional
    arguments.  The callback is expected to return None if the user
    represented by the string doesn't exist or a sequence of group
    identifiers (possibly empty) if the user does exist.  If
    ``callback`` is None, the userid will be assumed to exist with no
    groups.  It defaults to ``None``.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <remoteuserauthenticationpolicy
    environ_key="REMOTE_USER"
    callback=".somemodule.somefunc"
    />

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`repoze.bfg.authentication.RemoteUserAuthenticationPolicy` and
pass it to the :class:`repoze.bfg.configuration.Configurator`
constructor as the ``authentication_policy`` argument during initial
application configuration.

See Also
~~~~~~~~

See also :ref:`authentication_policies_directives_section` and
:class:`repoze.bfg.authentication.RemoteUserAuthenticationPolicy`.

.. _repozewho1authenticationpolicy_directive:

``repozewho1authenticationpolicy``
----------------------------------

When this directive is used, authentication information is obtained
from a ``repoze.who.identity`` key in the WSGI environment, assumed to
be set by :term:`repoze.who` middleware.

Attributes
~~~~~~~~~~

``identifier_name``

    The ``identifier_name`` controls the name used to look up the
    :term:`repoze.who` "identifier" plugin within
    ``request.environ['repoze.who.plugins']`` which is used by this
    policy to "remember" and "forget" credentials.  It defaults to
    ``auth_tkt``.

``callback``

    The ``callback`` is a Python dotted name to a function passed the
    repoze.who identity and the request as positional arguments.  The
    callback is expected to return None if the user represented by the
    identity doesn't exist or a sequence of group identifiers
    (possibly empty) if the user does exist.  If ``callback`` is None,
    the userid will be assumed to exist with no groups.  It defaults
    to ``None``.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <repozewho1authenticationpolicy
    identifier_name="auth_tkt"
    callback=".somemodule.somefunc"
    />

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`repoze.bfg.authentication.RepozeWho1AuthenticationPolicy` and
pass it to the :class:`repoze.bfg.configuration.Configurator`
constructor as the ``authentication_policy`` argument during initial
application configuration.

See Also
~~~~~~~~

See also :ref:`authentication_policies_directives_section` and
:class:`repoze.bfg.authentication.RepozeWho1AuthenticationPolicy`.

.. _aclauthorizationpolicy_directive:

``aclauthorizationpolicy``
--------------------------

When this directive is used, authorization information is obtained
from :term:`ACL` objects attached to model instances.

Attributes
~~~~~~~~~~

None.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <aclauthorizationpolicy/>

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`repoze.bfg.authorization.ACLAuthorizationPolicy` and pass it
to the :class:`repoze.bfg.configuration.Configurator` constructor as
the ``authorization_policy`` argument during initial application
configuration.

See Also
~~~~~~~~

See also :ref:`authorization_policies_directives_section` and
:ref:`security_chapter`.

.. _adapter_directive:

``adapter``
-----------

Register a :term:`Zope Component Architecture` "adapter".

Attributes
~~~~~~~~~~

``factory``

  The adapter factory (often a class).

``provides``

  The :term:`interface` that an adapter instance resulting from a
  lookup will provide.

``for``

  Interfaces or classes to be adapted, separated by spaces,
  e.g. ``interfaces.IFoo interfaces.IBar``.

``name``

  The adapter name.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <adapter
     for=".foo.IFoo .bar.IBar"
     provides=".interfaces.IMyAdapter"
     factory=".adapters.MyAdapter"
     />

Alternatives
~~~~~~~~~~~~

Use the ``registerAdapter`` method of the ``registry`` attribute of a
:term:`Configurator` instance during initial application setup.

See Also
~~~~~~~~

None.

.. _utility_directive:

``utility``
-----------

Register a :term:`Zope Component Architecture` "utility".

Attributes
~~~~~~~~~~

``component``

  The utility component (cannot be specified if ``factory`` is
  specified).

``factory``

  A factory that creates a component (cannot be specified if
  ``component`` is specified).

``provides``

  The :term:`interface` that an utility instance resulting from a
  lookup will provide.

``name``

  The utility name.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <utility
     provides=".interfaces.IMyUtility"
     component=".utilities.MyUtility"
     />

Alternatives
~~~~~~~~~~~~

Use the ``registerUtility`` method of the ``registry`` attribute of a
:term:`Configurator` instance during initial application setup.

See Also
~~~~~~~~

None.


