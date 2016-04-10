.. _viewderivers_module:

:mod:`pyramid.viewderivers`
---------------------------

.. automodule:: pyramid.viewderivers

   .. attribute:: INGRESS

      Constant representing the request ingress, for use in ``under``
      arguments to :meth:`pyramid.config.Configurator.add_view_deriver`.

   .. attribute:: VIEW

      Constant representing the :term:`view callable` at the end of the view
      pipeline, for use in ``over`` arguments to
      :meth:`pyramid.config.Configurator.add_view_deriver`.
