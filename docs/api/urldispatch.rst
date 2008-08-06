.. _urldispatch_module:

:mod:`repoze.bfg.urldispatch`
=============================

.. automodule:: repoze.bfg.urldispatch

  .. autoclass:: RoutesMapper
     :members:

An example of configuring a ``bfg:view`` stanza in ``configure.zcml``
that maps a context found via :term:`Routes` URL dispatch to a view
function is as follows:

.. code-block:: xml
   :linenos:

   <bfg:view
       for="repoze.bfg.interfaces.IRoutesContext"
       view=".views.articles_view"
       name="articles"
       />

All context objects found via Routes URL dispatch will provide the
``IRoutesContext`` interface (attached dynamically).  You might then
configure the ``RoutesMapper`` like so:

.. code-block:: python
   :linenos:

   def fallback_get_root(environ):
       return {} # the graph traversal root is empty in this example

   class Article(object):
       def __init__(self, **kw):
           self.__dict__update(kw)

   get_root = RoutesMapper(fallback_get_root)
   get_root.connect('archives/:article', controller='articles',
                    context_factory=Article)

   import myapp
   from repoze.bfg.router import make_app

   app = make_app(get_root, myapp)

The effect of this configuration: when this :mod:`repoze.bfg`
application runs, if any URL matches the pattern
``archives/:article``, the ``.views.articles_view`` view will be
called with its :term:`context` as a instance of the ``Article``
class.  The ``Article`` instance will have attributes matching the
keys and values in the Routes routing dictionary associated with the
request.

In this case in particular, when a user visits
``/archives/something``, the context will be an instance of the
Article class and it will have an ``article`` attribute with the value
of ``something``.
