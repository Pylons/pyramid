.. _events_chapter:

Using Events
=============

An *event* is an object broadcast by the :mod:`repoze.bfg` framework
at interesting points during the lifetime of an application.  You
don't need to use, know about, or care about events in order to create
most :mod:`repoze.bfg` applications, but they can be useful when you
want to perform slightly advanced operations.  For example,
subscribing to an event can allow you to "skin" a site slightly
differently based on the hostname used to reach the site.

Events in :mod:`repoze.bfg` are always broadcast by the framework.
However, they only become useful when you register a *subscriber*.  A
subscriber is a function that accepts a single argument named `event`:

.. code-block:: python
   :linenos:

   def mysubscriber(event):
       print event

The above is a subscriber that simply prints the event to the console
when it's called.

The mere existence of a subscriber function, however, is not
sufficient to arrange for it to be called.  To arrange for the
subscriber to be called, you'll need to change your :term:`application
registry` by either of the following methods:

.. topic:: Configuring an Event Listener Imperatively

   You can imperatively configure a subscriber function to be called
   for some event type via the ``add_subscriber`` method of a
   :term:`Configurator`:

   .. code-block:: python
      :linenos:

      from repoze.bfg.interfaces import INewRequest

      from subscribers import mysubscriber

      config.add_subscriber(mysubscriber, INewRequest)

   The first argument to ``add_subscriber`` is the subscriber
   function; the second argument is the event type.  See
   :ref:`configuration_module` for API documentation related to the
   ``add_subscriber`` method of a :term:`Configurator`.

.. topic:: Configuring an Event Listener Through ZCML

   You can configure an event listener by modifying your application's
   ``configure.zcml``.  Here's an example of a bit of XML you can add
   to the ``configure.zcml`` file which registers the above
   ``mysubscriber`` function, which we assume lives in a
   ``subscribers.py`` module within your application:

   .. code-block:: xml
      :linenos:

      <subscriber
         for="repoze.bfg.interfaces.INewRequest"
         handler=".subscribers.mysubscriber"
       />

   The *subscriber* :term:`ZCML directive` takes two attributes:
   ``for``, and ``handler``.  The value of ``for`` is the interface
   the subscriber is registered for.  Registering a subscriber for a
   specific interface limits the event types that the subscriber will
   receive to those specified by the interface. The value of
   ``handler`` is a Python dotted-name path to the subscriber
   function.

Each of the above examples implies that every time the
:mod:`repoze.bfg` framework emits an event object that supplies an
``INewRequest`` interface, the ``mysubscriber`` function will be
called with an *event* object.

As you can see, a subscription is made in terms of an
:term:`interface`.  The event object sent to a subscriber will always
have possess an interface.  The interface itself provides
documentation of what attributes of the event are available.

For example, if you create event listener functions in a
``subscribers.py`` file in your application like so:

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
      handler=".subscribers.handle_new_request"
    />

   <subscriber
      for="repoze.bfg.interfaces.INewResponse"
      handler=".subscribers.handle_new_response"
    />

Or imperatively via the ``add_subscriber`` method of a
:term:`Configurator`:

.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import INewRequest
   from repoze.bfg.interfaces import INewResponse

   from subscribers import handle_new_request
   from subscribers import handle_new_response

   config.add_subscriber(handle_new_request, INewRequest)
   config.add_subscriber(handle_new_response, INewResponse)

This causes the functions as to be registered as event subscribers
within the :term:`application registry` .  Under this configuration,
when the application is run, each time a new request or response is
detected, a message will be printed to the console.

.. sidebar:: The ``INewResponse`` Event vs. Middleware

   Postprocessing a response is usually better handled in a WSGI
   :term:`middleware` component than in subscriber code that is called
   by an ``INewResponse`` event.  The :mod:`repoze.bfg`
   ``INewResponse`` event exists almost purely for symmetry with the
   ``INewRequest`` event.

We know that ``INewRequest`` events have a ``request`` attribute,
which is a :term:`WebOb` request, because the interface defined at
``repoze.bfg.interfaces.INewRequest`` says it must.  Likewise, we know
that ``INewResponse`` events have a ``response`` attribute, which is a
response object constructed by your application, because the interface
defined at ``repoze.bfg.interfaces.INewResponse`` says it must.

The return value of a subscriber function is ignored.  Subscribers to
the same event type are not guaranteed to be called in any particular
order relative to one another.

All other concrete event types are documented in the
:ref:`events_module` API chapter.

