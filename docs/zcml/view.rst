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
for a given request.  See :ref:`view_lookup` for a description of how
a view configuration matches (or doesn't match) during a request.

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
  :ref:`view_lookup`.  The "best" wrapper view will be found based on
  the lookup ordering: "under the hood" this wrapper view is looked up
  via ``repoze.bfg.view.render_view_to_response(context, request,
  'wrapper_viewname')``. The context and request of a wrapper view is
  the same context and request of the inner view.  If this attribute
  is unspecified, no view wrapping is done.

  .. note:: This feature is new as of :mod:`repoze.bfg` 1.1.

Predicate Attributes
####################

``name``
  The *view name*.  Read the :ref:`traversal_chapter` to understand
  the concept of a view name.

``context``
  A :term:`dotted Python name` representing the Python class that the
  :term:`context` must be an instance of, *or* the :term:`interface`
  that the :term:`context` must provide in order for this view to be
  found and called.  This predicate is true when the :term:`context`
  is an instance of the represented class or if the :term:`context`
  provides the represented interface; it is otherwise false.  An
  alternate name for this attribute is ``for`` (this is an older
  spelling).

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
           context=".models.MyModel"
           view=".views.hello_world"
         />

.. topic:: Registering A View With a Predicate

  .. code-block:: xml
     :linenos:

        <view
           context=".models.MyModel"
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
