.. _tweens_module:

:mod:`pyramid.tweens`
---------------------

.. automodule:: pyramid.tweens

   .. autofunction:: excview_tween_factory

   .. attribute:: MAIN

      Constant representing the main Pyramid handling function, for use in
      ``under`` and ``over`` arguments to
      :meth:`pyramid.config.Configurator.add_tween`.

   .. attribute:: INGRESS

      Constant representing the request ingress, for use in ``under`` and
      ``over`` arguments to :meth:`pyramid.config.Configurator.add_tween`.

   .. attribute:: EXCVIEW

      Constant representing the exception view tween, for use in ``under``
      and ``over`` arguments to
      :meth:`pyramid.config.Configurator.add_tween`.
