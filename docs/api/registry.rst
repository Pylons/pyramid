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

   .. attribute:: package_name

     .. versionadded:: 1.6

     When a registry is set up (or created) by a :term:`Configurator`, this
     attribute will be the shortcut for
     :attr:`pyramid.config.Configurator.package_name`.

     This attribute is often accessed as ``request.registry.package_name`` or
     ``config.registry.package_name`` or ``config.package_name``
     in a typical Pyramid application.

   .. attribute:: introspector

     .. versionadded:: 1.3

     When a registry is set up (or created) by a :term:`Configurator`, the
     registry will be decorated with an instance named ``introspector``
     implementing the :class:`pyramid.interfaces.IIntrospector` interface.

     .. seealso::

        See also :attr:`pyramid.config.Configurator.introspector`.

     When a registry is created "by hand", however, this attribute will not
     exist until set up by a configurator.

     This attribute is often accessed as ``request.registry.introspector`` in
     a typical Pyramid application.

   .. method:: notify(*events)

     Fire one or more events. All event subscribers to the event(s)
     will be notified. The subscribers will be called synchronously.
     This method is often accessed as ``request.registry.notify``
     in Pyramid applications to fire custom events. See
     :ref:`custom_events` for more information.


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
