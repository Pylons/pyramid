.. _events_chapter:

Using Events
=============

An *event* is an object broadcast by the :mod:`repoze.bfg` framework
at particularly interesting points during the lifetime of your
application.  You don't need to use, know about, or care about events
in order to create most :mod:`repoze.bfg` applications, but they can
be useful when you want to do slightly advanced operations, such as
"skinning" a site slightly differently based on, for example, the
hostname used to reach the site.

Events in :mod:`repoze.bfg` are always broadcast by the framework.
They only become useful when you register a *subscriber*.  A
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
registry` by modifying your application's ``configure.zcml``.  Here's
an example of a bit of XML you can add to the ``configure.zcml`` file
which registers the above ``mysubscriber`` function, which we assume
lives in a ``subscribers.py`` module within your application:

.. code-block:: xml
   :linenos:

   <subscriber
      for="repoze.bfg.interfaces.INewRequest"
      handler=".subscribers.mysubscriber"
    />

The above example means "every time the :mod:`repoze.bfg` framework
emits an event object that supplies an ``INewRequest`` interface, call
the ``mysubscriber`` function with the event object.  As you can see,
subscriptions are made to *interfaces*.  The event object sent to a
subscriber will always have an interface.  You can use the interface
itself to determine what attributes of the event are available.

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

This causes the functions as to be registered as event subscribers
within the :term:`application registry` .  Under this configuration,
when the application is run, every new request and every response will
be printed to the console.  We know that ``INewRequest`` events have a
``request`` attribute, which is a :term:`WebOb` request, because the
interface defined at ``repoze.bfg.interfaces.INewRequest`` says it
must.  Likewise, we know that ``INewResponse`` events have a
``response`` attribute, which is a response object constructed by your
application, because the interface defined at
``repoze.bfg.interfaces.INewResponse`` says it must.  These particular
interfaces are documented in the :ref:`events_module` API chapter.

The *subscriber* ZCML element takes two values: ``for``, which is the
interface the subscriber is registered for (which limits the events
that the subscriber will receive to those specified by the interface),
and ``handler`` which is a Python dotted-name path to the subscriber
function.

The return value of a subscriber function is ignored.

Uses For Events
---------------

Here are some things that events are useful for:

- Attaching different interfaces to the request to be able to
  differentiate e.g. requests from a browser against requests from an
  XML-RPC client within view code.  To do this, you'd subscribe a
  function to ```INewRequest``, and use the
  ``zope.interface.alsoProvides`` function to add one or more
  interfaces to the request object.

- Post-processing all response output by subscribing to
  ``INewResponse``, for example, modifying headers.

  .. note::

     Usually postprocessing requests is better handled in middleware
     components.  The ``INewResponse`` event exists purely for
     symmetry with ``INewRequest``, really.

