.. _configuration_module:

:mod:`repoze.bfg.configuration`
-------------------------------

.. automodule:: repoze.bfg.configuration

  .. autoclass:: Configurator

     .. automethod:: route

     .. automethod:: view

     .. automethod:: authentication_policy(policy)

     .. automethod:: authorization_policy(policy)

     .. automethod:: forbidden(view=None, attr=None, renderer=None, wrapper=None)

     .. automethod:: notfound(view=None, attr=None, renderer=None, wrapper=None)

     .. automethod:: renderer(factory, name)

     .. automethod:: resource(to_override, override_with)

     .. automethod:: root_factory(factory)

     .. automethod:: scan(package)

     .. automethod:: settings

     .. automethod:: static(name, path, cache_max_age=3600)

     .. automethod:: load_zcml(spec)

     .. automethod:: make_wsgi_app()

 
