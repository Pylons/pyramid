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

     When a registry is set up (or created) by a :term:`Configurator`, the
     registry will be decorated with an instance named ``introspector``
     implementing the :class:`pyramid.interfaces.IIntrospector` interface.
     See also :attr:`pyramid.config.Configurator.introspector``.

     When a registry is created "by hand", however, this attribute will not
     exist until set up by a configurator.

     This attribute is often accessed as ``request.registry.introspector`` in
     a typical Pyramid application.

     This attribute is new as of :app:`Pyramid` 1.3.

.. class:: Introspectable

   The default implementation of the interface
   :class:`pyramid.interfaces.IIntrospectable` used by framework exenders.
   An instance of this class is is created when
   :attr:`pyramid.config.Configurator.introspectable` is called.

   This class is new as of :app:`Pyramid` 1.3.

.. class:: noop_introspector

   An introspector which throws away all registrations, useful for disabling
   introspection altogether (pass as ``introspector`` to the
   :term:`Configurator` constructor).

   This class is new as of :app:`Pyramid` 1.3.
