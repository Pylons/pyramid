.. _urldispatch_module:

:mod:`repoze.bfg.urldispatch`
=============================

.. automodule:: repoze.bfg.urldispatch

  .. autoclass:: RoutesMapper
     :members:

You can configure the ``RoutesModelTraverser`` into your application's
configure.zcml like so::

  <adapter
      factory="repoze.bfg.urldispatch.RoutesModelTraverser"
      provides=".interfaces.ITraverserFactory"
      for="repoze.bfg.interfaces.IURLDispatchModel repoze.bfg.interfaces.IRequest"
  />

An example of configuring a view that is willing to handle this sort
of dispatch::

  <bfg:view
      for="repoze.bfg.interfaces.IURLDispatchModel"
      view=".views.url_dispatch_view"
      name="url_dispatch_controller"
      />

This view will be called with its context as a model with attributes
matching the Routes routing dictionary associated with the request.
