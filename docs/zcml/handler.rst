.. _handler_directive:

``handler``
-----------

The ``handler`` directive adds the configuration of a :term:`view handler` to
the :term:`application registry`.

Attributes
~~~~~~~~~~

``route_name``
  The name of the route, e.g. ``myroute``.  This attribute is required.  It
  must be unique among all defined handler and route names in a given
  configuration.

``pattern``
  The pattern of the route e.g. ``ideas/{idea}``.  This attribute is
  required.  See :ref:`route_pattern_syntax` for information about the syntax
  of route patterns.  The name ``{action}`` is treated specially in handler
  patterns.  See :ref:`using_add_handler` for a discussion of how
  ``{action}`` in handler patterns is treated.

``action``
  If the action name is not specified in the ``pattern``, use this name as the 
  handler action (method name).

``factory``
  The :term:`dotted Python name` to a function that will generate a
  :app:`Pyramid` context object when the associated route matches.
  e.g. ``mypackage.models.MyFactoryClass``.  If this argument is not
  specified, a default root factory will be used.

``xhr``
  This value should be either ``True`` or ``False``.  If this value is
  specified and is ``True``, the :term:`request` must possess an
  ``HTTP_X_REQUESTED_WITH`` (aka ``X-Requested-With``) header for this
  route to match.  This is useful for detecting AJAX requests issued
  from jQuery, Prototype and other Javascript libraries.  If this
  predicate returns false, route matching continues.

``traverse``
  If you would like to cause the :term:`context` to be something other
  than the :term:`root` object when this route matches, you can spell
  a traversal pattern as the ``traverse`` argument.  This traversal
  pattern will be used as the traversal path: traversal will begin at
  the root object implied by this route (either the global root, or
  the object returned by the ``factory`` associated with this route).

  The syntax of the ``traverse`` argument is the same as it is for
  ``pattern``. For example, if the ``pattern`` provided to the
  ``route`` directive is ``articles/{article}/edit``, and the
  ``traverse`` argument provided to the ``route`` directive is
  ``/{article}``, when a request comes in that causes the route to
  match in such a way that the ``article`` match value is '1' (when
  the request URI is ``/articles/1/edit``), the traversal path will be
  generated as ``/1``.  This means that the root object's
  ``__getitem__`` will be called with the name ``1`` during the
  traversal phase.  If the ``1`` object exists, it will become the
  :term:`context` of the request.  :ref:`traversal_chapter` has more
  information about traversal.

  If the traversal path contains segment marker names which are not
  present in the ``pattern`` argument, a runtime error will occur.
  The ``traverse`` pattern should not contain segment markers that do
  not exist in the ``pattern``.

  A similar combining of routing and traversal is available when a
  route is matched which contains a ``*traverse`` remainder marker in
  its ``pattern`` (see :ref:`using_traverse_in_a_route_pattern`).  The
  ``traverse`` argument to the ``route`` directive allows you to
  associate route patterns with an arbitrary traversal path without
  using a a ``*traverse`` remainder marker; instead you can use other
  match information.

  Note that the ``traverse`` argument to the ``handler`` directive is
  ignored when attached to a route that has a ``*traverse`` remainder
  marker in its pattern.

``request_method``
  A string representing an HTTP method name, e.g. ``GET``, ``POST``,
  ``HEAD``, ``DELETE``, ``PUT``.  If this argument is not specified,
  this route will match if the request has *any* request method.  If
  this predicate returns false, route matching continues.

``path_info``
  The value of this attribute represents a regular expression pattern
  that will be tested against the ``PATH_INFO`` WSGI environment
  variable.  If the regex matches, this predicate will be true.  If
  this predicate returns false, route matching continues.

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

``accept``
  The value of this attribute represents a match query for one or more
  mimetypes in the ``Accept`` HTTP request header.  If this value is
  specified, it must be in one of the following forms: a mimetype
  match token in the form ``text/plain``, a wildcard mimetype match
  token in the form ``text/*`` or a match-all wildcard mimetype match
  token in the form ``*/*``.  If any of the forms matches the
  ``Accept`` header of the request, this predicate will be true.  If
  this predicate returns false, route matching continues.

``custom_predicates``
  This value should be a sequence of references to custom predicate
  callables.  Use custom predicates when no set of predefined
  predicates does what you need.  Custom predicates can be combined
  with predefined predicates as necessary.  Each custom predicate
  callable should accept two arguments: ``info`` and ``request``
  and should return either ``True`` or ``False`` after doing arbitrary
  evaluation of the info and/or the request.  If all custom and
  non-custom predicate callables return ``True`` the associated route
  will be considered viable for a given request.  If any predicate
  callable returns ``False``, route matching continues.  Note that the
  value ``info`` passed to a custom route predicate is a dictionary
  containing matching information; see :ref:`custom_route_predicates`
  for more information about ``info``.


Alternatives
~~~~~~~~~~~~

You can also add a :term:`route configuration` via:

- Using the :meth:`pyramid.config.Configurator.add_handler` method.

See Also
~~~~~~~~

See also :ref:`handlers_chapter`.
