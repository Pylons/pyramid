.. _configuration_module:

:mod:`pyramid.config`
---------------------

.. automodule:: pyramid.config

  .. autoclass:: Configurator(registry=None, package=None, settings=None, root_factory=None, authentication_policy=None, authorization_policy=None, renderers=DEFAULT_RENDERERS, debug_logger=None, locale_negotiator=None, request_factory=None, renderer_globals_factory=None, default_permission=None, session_factory=None, autocommit=False)

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

     .. automethod:: setup_registry(settings=None, root_factory=None, authentication_policy=None, renderers=DEFAULT_RENDERERS, debug_logger=None, locale_negotiator=None, request_factory=None, renderer_globals_factory=None)

     .. automethod:: add_renderer(name, factory)

     .. automethod:: add_response_adapter

     .. automethod:: add_route

     .. automethod:: add_static_view(name, path, cache_max_age=3600, permission='__no_permission_required__')

     .. automethod:: add_settings

     .. automethod:: add_subscriber

     .. automethod:: add_translation_dirs

     .. automethod:: add_view

     .. automethod:: derive_view

     .. automethod:: make_wsgi_app()

     .. automethod:: override_asset(to_override, override_with)

     .. automethod:: scan

     .. automethod:: set_forbidden_view

     .. automethod:: set_notfound_view

     .. automethod:: set_locale_negotiator

     .. automethod:: set_default_permission

     .. automethod:: set_session_factory

     .. automethod:: set_request_factory

     .. automethod:: set_renderer_globals_factory(factory)

     .. automethod:: set_view_mapper

     .. automethod:: add_request_handler

     .. automethod:: testing_securitypolicy

     .. automethod:: testing_resources

     .. automethod:: testing_add_subscriber

     .. automethod:: testing_add_renderer

  .. attribute:: global_registries

     The set of registries that have been created for :app:`Pyramid`
     applications, one per each call to
     :meth:`pyramid.config.Configurator.make_wsgi_app` in the current
     process. The object itself supports iteration and has a ``last``
     property containing the last registry loaded.

     The registries contained in this object are stored as weakrefs,
     thus they will only exist for the lifetime of the actual
     applications for which they are being used.

