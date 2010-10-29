.. _forbidden_directive:

``forbidden``
-------------

When :mod:`pyramid` can't authorize execution of a view based on
the :term:`authorization policy` in use, it invokes a :term:`forbidden
view`.  The default forbidden response has a 401 status code and is
very plain, but it can be overridden as necessary using the
``forbidden`` ZCML directive.

.. warning::

   The ``forbidden`` ZCML directive is deprecated in :mod:`pyramid`
   version 1.3.  Instead, you should use the :ref:`view_directive`
   directive with a ``context`` that names the
   :exc:`pyramid.exceptions.Forbidden` class.  See
   :ref:`changing_the_forbidden_view` form more information.

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

``renderer``
  This is either a single string term (e.g. ``json``) or a string
  implying a path or :term:`resource specification`
  (e.g. ``templates/views.pt``) used when the view returns a
  non-:term:`response` object.  This attribute has the same meaning as
  it would in the context of :ref:`view_directive`; see the
  description of ``renderer`` there).

``wrapper``
  The :term:`view name` (*not* an object dotted name) of another view
  declared elsewhere in ZCML (or via the ``@view_config`` decorator)
  which will receive the response body of this view as the
  ``request.wrapped_body`` attribute of its own request, and the
  response returned by this view as the ``request.wrapped_response``
  attribute of its own request.  This attribute has the same meaning
  as it would in the context of :ref:`view_directive`; see the
  description of ``wrapper`` there).  Note that the wrapper view
  *should not* be protected by any permission; behavior is undefined
  if it does.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <forbidden
       view="helloworld.views.forbidden_view"/>

Alternatives
~~~~~~~~~~~~

Use the :ref:`view_directive` directive with a ``context`` that names
the :exc:`pyramid.exceptions.Forbidden` class.

Use the :meth:`pyramid.configuration.Configurator.add_view` method,
passing it a ``context`` which is the
:exc:`pyramid.exceptions.Forbidden` class.

See Also
~~~~~~~~

See also :ref:`changing_the_forbidden_view`.
