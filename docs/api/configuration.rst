.. _configuration_module:

:mod:`repoze.bfg.configuration`
-------------------------------

.. automodule:: repoze.bfg.configuration

  .. autoclass:: Configurator(registry=None, package=None, settings=None, root_factory=None, zcml_file=None, authentication_policy=None, authorization_policy=None, renderers=DEFAULT_RENDERERS)

     .. automethod:: route

     .. automethod:: view

     .. automethod:: security_policies

     .. automethod:: forbidden(view=None, attr=None, renderer=None, wrapper=None)

     .. automethod:: notfound(view=None, attr=None, renderer=None, wrapper=None)

     .. automethod:: renderer(factory, name)

     .. automethod:: resource(to_override, override_with)

     .. automethod:: scan(package)

     .. automethod:: static(name, path, cache_max_age=3600)

     .. automethod:: load_zcml(spec)

     .. automethod:: make_wsgi_app()

 
