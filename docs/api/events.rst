.. _events_module:

:mod:`pyramid.events`
--------------------------

.. automodule:: pyramid.events

Functions
~~~~~~~~~

.. autofunction:: subscriber

.. _event_types:

Event Types
~~~~~~~~~~~

.. autoclass:: ApplicationCreated

.. autoclass:: NewRequest

.. autoclass:: ContextFound

.. autoclass:: NewResponse

.. autoclass:: BeforeRender
   :members:
   :inherited-members:
   :exclude-members: update

   .. method:: update(E, **F)

      Update D from dict/iterable E and F. If E has a .keys() method, does:
      for k in E: D[k] = E[k] If E lacks .keys() method, does: for (k, v) in
      E: D[k] = v.  In either case, this is followed by: for k in F: D[k] =
      F[k].

See :ref:`events_chapter` for more information about how to register
code which subscribes to these events.

