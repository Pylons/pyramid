.. _configuration_module:

:mod:`repoze.bfg.configuration`
-------------------------------

.. automodule:: repoze.bfg.configuration

  .. autoclass:: Configurator(registry=None, package=None, settings=None, root_factory=None, authentication_policy=None, authorization_policy=None, renderers=DEFAULT_RENDERERS, debug_logger=None)

     .. automethod:: begin

     .. automethod:: end

     .. automethod:: add_renderer(name, factory)

     .. automethod:: add_route

     .. automethod:: add_static_view(name, path, cache_max_age=3600)

     .. automethod:: add_subscriber

     .. automethod:: add_view

     .. automethod:: load_zcml(spec)

     .. automethod:: make_wsgi_app()

     .. automethod:: override_resource(to_override, override_with)

     .. automethod:: scan(package)

     .. automethod:: set_forbidden_view(view=None, attr=None, renderer=None, wrapper=None)

     .. automethod:: set_notfound_view(view=None, attr=None, renderer=None, wrapper=None)

