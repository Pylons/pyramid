.. _configuration_module:

.. role:: methodcategory
   :class: methodcategory

:mod:`pyramid.config`
---------------------

.. automodule:: pyramid.config

.. autoclass:: Configurator

  :methodcategory:`Controlling Configuration State`

    .. automethod:: commit
    .. automethod:: begin
    .. automethod:: end
    .. automethod:: include
    .. automethod:: make_wsgi_app()
    .. automethod:: scan

  :methodcategory:`Adding Routes and Views`

    .. automethod:: add_route
    .. automethod:: add_static_view(name, path, cache_max_age=3600, permission=NO_PERMISSION_REQUIRED)
    .. automethod:: add_view
    .. automethod:: add_notfound_view
    .. automethod:: add_forbidden_view
    .. automethod:: add_exception_view

  :methodcategory:`Adding an Event Subscriber`

    .. automethod:: add_subscriber

  :methodcategory:`Using Security`

     .. automethod:: set_authentication_policy
     .. automethod:: set_authorization_policy
     .. automethod:: set_default_csrf_options
     .. automethod:: set_csrf_storage_policy
     .. automethod:: set_default_permission
     .. automethod:: add_permission

   :methodcategory:`Extending the Request Object`

     .. automethod:: add_request_method
     .. automethod:: set_request_property

   :methodcategory:`Using I18N`

     .. automethod:: add_translation_dirs
     .. automethod:: set_locale_negotiator

   :methodcategory:`Overriding Assets`

     .. automethod:: override_asset(to_override, override_with)

   :methodcategory:`Getting and Adding Settings`

     .. automethod:: add_settings
     .. automethod:: get_settings

   :methodcategory:`Hooking Pyramid Behavior`

     .. automethod:: add_renderer
     .. automethod:: add_resource_url_adapter
     .. automethod:: add_response_adapter
     .. automethod:: add_traverser
     .. automethod:: add_tween
     .. automethod:: add_route_predicate
     .. automethod:: add_subscriber_predicate
     .. automethod:: add_view_predicate
     .. automethod:: add_view_deriver
     .. automethod:: set_execution_policy
     .. automethod:: set_request_factory
     .. automethod:: set_root_factory
     .. automethod:: set_session_factory
     .. automethod:: set_view_mapper

   :methodcategory:`Extension Author APIs`

     .. automethod:: action
     .. automethod:: add_directive
     .. automethod:: with_package
     .. automethod:: derive_view

   :methodcategory:`Utility Methods`

     .. automethod:: absolute_asset_spec
     .. automethod:: maybe_dotted

   :methodcategory:`ZCA-Related APIs`

     .. automethod:: hook_zca
     .. automethod:: unhook_zca
     .. automethod:: setup_registry

   :methodcategory:`Testing Helper APIs`

     .. automethod:: testing_add_renderer
     .. automethod:: testing_add_subscriber
     .. automethod:: testing_resources
     .. automethod:: testing_securitypolicy

   :methodcategory:`Attributes`

     .. attribute:: introspectable

        A shortcut attribute which points to the
        :class:`pyramid.registry.Introspectable` class (used during
        directives to provide introspection to actions).

        .. versionadded:: 1.3

     .. attribute:: introspector

        The :term:`introspector` related to this configuration.  It is an
        instance implementing the :class:`pyramid.interfaces.IIntrospector`
        interface.

        .. versionadded:: 1.3

     .. attribute:: registry

        The :term:`application registry` which holds the configuration
        associated with this configurator.

.. attribute:: global_registries

   The set of registries that have been created for :app:`Pyramid`
   applications, one for each call to
   :meth:`pyramid.config.Configurator.make_wsgi_app` in the current
   process. The object itself supports iteration and has a ``last`` property
   containing the last registry loaded.

   The registries contained in this object are stored as weakrefs, thus they
   will only exist for the lifetime of the actual applications for which they
   are being used.

.. autoclass:: not_

.. attribute:: PHASE0_CONFIG
.. attribute:: PHASE1_CONFIG
.. attribute:: PHASE2_CONFIG
.. attribute:: PHASE3_CONFIG
