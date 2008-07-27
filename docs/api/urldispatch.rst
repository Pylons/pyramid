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
      provides="repoze.bfg.interfaces.ITraverserFactory"
      for="repoze.bfg.interfaces.IURLDispatchModel
           repoze.bfg.interfaces.IRequest"
  />

An example of configuring a view that is willing to handle this sort
of dispatch::

  <bfg:view
      for="repoze.bfg.interfaces.IURLDispatchModel"
      view=".views.articles_view"
      name="articles"
      />

You might then configure the ``RoutesMapper`` like so::

  def fallback_get_root(environ):
      return {} # the graph traversal root is empty in this example

  get_root = RoutesMapper(fallback_get_root)
  get_root.connect('archives/:article', controller='articles')

  import myapp
  from repoze.bfg.router import make_app

  app = make_app(get_root, myapp)

At this point, if any URL matches the pattern ``archives/:article``,
the ``.views.articles_view`` view will be called with its context as a
only-the-fly-generated-model with attributes matching the Routes
routing dictionary associated with the request.  In particular, in
this case the model will have an ``article`` attribute matching the
article picked off the URL by Routes.
