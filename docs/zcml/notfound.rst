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

