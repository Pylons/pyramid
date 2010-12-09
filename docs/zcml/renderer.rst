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

The :meth:`pyramid.config.Configurator.add_renderer` method
is equivalent to the ``renderer`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`adding_and_overriding_renderers`.
