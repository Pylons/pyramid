.. _events_module:

:mod:`repoze.bfg.events`
--------------------------

.. automodule:: repoze.bfg.events

  .. autoclass:: NewRequest

  .. autoclass:: NewResponse

You can write *listeners* for these event types and subsequently
register the listeners to be called when the events occur.  For
example, if you create event listener functions in a ``listeners.py``
file in your application like so:

.. code-block:: python
   :linenos:

   def handle_new_request(event):
       print 'request', event.request   

   def handle_new_response(event):
       print 'response', event.response

You may configure these functions to be called at the appropriate
times by adding the following to your application's ``configure.zcml``
file:

.. code-block:: xml
   :linenos:

   <subscriber
      for="repoze.bfg.interfaces.INewRequest"
      handler=".listeners.handle_new_request"
    />

   <subscriber
      for="repoze.bfg.interfaces.INewResponse"
      handler=".listeners.handle_new_response"
    />

This causes the functions as to be registered as event listeners
within the :term:`application registry` .  Under this configuration,
when the application is run, every new request and every response will
be printed to the console.

The return value of a listener function is ignored.

