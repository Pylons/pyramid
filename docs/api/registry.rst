.. _registry_module:

:mod:`pyramid.registry`
---------------------------

.. module:: pyramid.registry

.. autoclass:: Registry

   .. attribute:: settings

     The dictionary-like :term:`deployment settings` object.  See
     :ref:`deployment_settings` for information.  This object is often
     accessed as ``request.registry.settings`` or
     ``config.registry.settings`` in a typical Pyramid application.

