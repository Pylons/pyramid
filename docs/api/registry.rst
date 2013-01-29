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

   .. attribute:: introspector

     .. versionadded:: 1.3

     When a registry is set up (or created) by a :term:`Configurator`, the
     registry will be decorated with an instance named ``introspector``
     implementing the :class:`pyramid.interfaces.IIntrospector` interface.
     See also :attr:`pyramid.config.Configurator.introspector`.

     When a registry is created "by hand", however, this attribute will not
     exist until set up by a configurator.

     This attribute is often accessed as ``request.registry.introspector`` in
     a typical Pyramid application.

.. class:: Introspectable

   .. versionadded:: 1.3

   The default implementation of the interface
   :class:`pyramid.interfaces.IIntrospectable` used by framework exenders.
   An instance of this class is created when
   :attr:`pyramid.config.Configurator.introspectable` is called.

.. autoclass:: Deferred

   .. versionadded:: 1.4

.. autofunction:: undefer

   .. versionadded:: 1.4

.. autoclass:: predvalseq

   .. versionadded:: 1.4
