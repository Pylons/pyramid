.. _view_module:

:mod:`pyramid.view`
----------------------

.. automodule:: pyramid.view

  .. autofunction:: render_view_to_response

  .. autofunction:: render_view_to_iterable

  .. autofunction:: render_view

  .. autoclass:: view_config
     :members:

  .. autoclass:: view_defaults
     :members:

  .. autoclass:: notfound_view_config
     :members:

  .. autoclass:: forbidden_view_config
     :members:

  .. autoclass:: exception_view_config
     :members:

  .. attribute:: UseSubrequest

     Object passed to :meth:`pyramid.config.Configurator.add_notfound_view` as
     the value to ``append_slash`` if you wish to cause a :term:`subrequest`
     rather than a redirect.
