.. _configuration_module:

:mod:`pyramid.config`
---------------------

.. automodule:: pyramid.config

  .. autoclass:: Configurator

     .. attribute:: registry

        The :term:`application registry` which holds the configuration
        associated with this configurator.

     .. automethod:: begin

     .. automethod:: end

     .. automethod:: hook_zca

     .. automethod:: unhook_zca

     .. automethod:: get_settings

     .. automethod:: commit

     .. automethod:: action

     .. automethod:: include

     .. automethod:: add_directive

     .. automethod:: with_package

     .. automethod:: maybe_dotted

     .. automethod:: absolute_asset_spec

     .. automethod:: setup_registry

     .. automethod:: add_renderer

     .. automethod:: add_response_adapter

     .. automethod:: add_route

     .. automethod:: add_static_view(name, path, cache_max_age=3600, permission=NO_PERMISSION_REQUIRED)

     .. automethod:: add_settings

     .. automethod:: add_subscriber

     .. automethod:: add_translation_dirs

     .. automethod:: add_view

     .. automethod:: add_tween

     .. automethod:: derive_view

     .. automethod:: make_wsgi_app()

     .. automethod:: override_asset(to_override, override_with)

     .. automethod:: scan

     .. automethod:: set_locale_negotiator

     .. automethod:: set_default_permission

     .. automethod:: set_session_factory

     .. automethod:: set_request_factory

     .. automethod:: set_root_factory

     .. automethod:: set_view_mapper

     .. automethod:: set_authentication_policy

     .. automethod:: set_authorization_policy

     .. automethod:: testing_securitypolicy

     .. automethod:: testing_resources

     .. automethod:: testing_add_subscriber

     .. automethod:: testing_add_renderer

     .. automethod:: set_forbidden_view

     .. automethod:: set_notfound_view

     .. automethod:: set_renderer_globals_factory(factory)

     .. attribute:: introspectable

        A shortcut attribute which points to the
        :class:`pyramid.registry.Introspectable` class (used during
        directives to provide introspection to actions).

        This attribute is new as of :app:`Pyramid` 1.3.

     .. attribute:: introspector

        The :term:`introspector` related to this configuration.  It is an
        instance implementing the :class:`pyramid.interfaces.IIntrospector`
        interface.  If the Configurator constructor was supplied with an
        ``introspector`` argument, this attribute will be that value.
        Otherwise, it will be an instance of a default introspector type.

        This attribute is new as of :app:`Pyramid` 1.3.

  .. attribute:: global_registries

     The set of registries that have been created for :app:`Pyramid`
     applications, one per each call to
     :meth:`pyramid.config.Configurator.make_wsgi_app` in the current
     process. The object itself supports iteration and has a ``last``
     property containing the last registry loaded.

     The registries contained in this object are stored as weakrefs,
     thus they will only exist for the lifetime of the actual
     applications for which they are being used.

