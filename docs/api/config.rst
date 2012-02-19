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
    .. automethod:: set_forbidden_view
    .. automethod:: set_notfound_view

  :methodcategory:`Adding an Event Subscriber`

    .. automethod:: add_subscriber

  :methodcategory:`Using Security`

     .. automethod:: set_authentication_policy
     .. automethod:: set_authorization_policy
     .. automethod:: set_default_permission

   :methodcategory:`Setting Request Properties`

     .. automethod:: set_request_property

   :methodcategory:`Using I18N`

     .. automethod:: add_translation_dirs
     .. automethod:: set_locale_negotiator

   :methodcategory:`Overriding Assets`

     .. automethod:: override_asset(to_override, override_with)

   :methodcategory:`Setting Renderer Globals`

     .. automethod:: set_renderer_globals_factory(factory)

   :methodcategory:`Getting and Adding Settings`

     .. automethod:: add_settings
     .. automethod:: get_settings

   :methodcategory:`Hooking Pyramid Behavior`

     .. automethod:: add_renderer
     .. automethod:: add_resource_url_adapter
     .. automethod:: add_response_adapter
     .. automethod:: add_traverser
     .. automethod:: add_tween
     .. automethod:: set_request_factory
     .. automethod:: set_root_factory
     .. automethod:: set_session_factory
     .. automethod:: set_view_mapper

   :methodcategory:`Extension Author APIs`

     .. automethod:: action
     .. automethod:: add_directive
     .. automethod:: with_package

   :methodcategory:`Utility Methods`

     .. automethod:: absolute_asset_spec
     .. automethod:: derive_view
     .. automethod:: maybe_dotted
     .. automethod:: setup_registry

   :methodcategory:`ZCA-Related APIs`

     .. automethod:: hook_zca
     .. automethod:: unhook_zca

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

        .. note::

           This attribute is new as of :app:`Pyramid` 1.3.

     .. attribute:: introspector

        The :term:`introspector` related to this configuration.  It is an
        instance implementing the :class:`pyramid.interfaces.IIntrospector`
        interface.  If the Configurator constructor was supplied with an
        ``introspector`` argument, this attribute will be that value.
        Otherwise, it will be an instance of a default introspector type.

        .. note::

           This attribute is new as of :app:`Pyramid` 1.3.

     .. attribute:: registry

        The :term:`application registry` which holds the configuration
        associated with this configurator.

.. attribute:: global_registries

   The set of registries that have been created for :app:`Pyramid`
   applications, one per each call to
   :meth:`pyramid.config.Configurator.make_wsgi_app` in the current
   process. The object itself supports iteration and has a ``last`` property
   containing the last registry loaded.

   The registries contained in this object are stored as weakrefs, thus they
   will only exist for the lifetime of the actual applications for which they
   are being used.

