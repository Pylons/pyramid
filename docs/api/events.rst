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

See :ref:`events_chapter` for more information about how to register
code which subscribes to these events.

