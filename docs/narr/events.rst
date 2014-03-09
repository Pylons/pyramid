.. index::
   single: event
   single: subscriber
   single: INewRequest
   single: INewResponse
   single: NewRequest
   single: NewResponse

.. _events_chapter:

Using Events
=============

An *event* is an object broadcast by the :app:`Pyramid` framework
at interesting points during the lifetime of an application.  You
don't need to use events in order to create most :app:`Pyramid`
applications, but they can be useful when you want to perform slightly
advanced operations.  For example, subscribing to an event can allow
you to run some code as the result of every new request.

Events in :app:`Pyramid` are always broadcast by the framework.
However, they only become useful when you register a *subscriber*.  A
subscriber is a function that accepts a single argument named `event`:

.. code-block:: python
   :linenos:

   def mysubscriber(event):
       print(event)

The above is a subscriber that simply prints the event to the console
when it's called.

The mere existence of a subscriber function, however, is not sufficient to
arrange for it to be called.  To arrange for the subscriber to be called,
you'll need to use the
:meth:`pyramid.config.Configurator.add_subscriber` method or you'll
need to use the :func:`pyramid.events.subscriber` decorator to decorate a
function found via a :term:`scan`.

Configuring an Event Listener Imperatively
------------------------------------------

You can imperatively configure a subscriber function to be called
for some event type via the
:meth:`~pyramid.config.Configurator.add_subscriber`
method:

.. code-block:: python
  :linenos:

  from pyramid.events import NewRequest

  from subscribers import mysubscriber

  # "config" below is assumed to be an instance of a
  # pyramid.config.Configurator object

  config.add_subscriber(mysubscriber, NewRequest)

The first argument to
:meth:`~pyramid.config.Configurator.add_subscriber` is the
subscriber function (or a :term:`dotted Python name` which refers
to a subscriber callable); the second argument is the event type.

.. seealso::

    See also :term:`Configurator`.

Configuring an Event Listener Using a Decorator
-----------------------------------------------

You can configure a subscriber function to be called for some event
type via the :func:`pyramid.events.subscriber` function.

.. code-block:: python
  :linenos:

  from pyramid.events import NewRequest
  from pyramid.events import subscriber

  @subscriber(NewRequest)
  def mysubscriber(event):
      event.request.foo = 1

When the :func:`~pyramid.events.subscriber` decorator is used a
:term:`scan` must be performed against the package containing the
decorated function for the decorator to have any effect.

Either of the above registration examples implies that every time the
:app:`Pyramid` framework emits an event object that supplies an
:class:`pyramid.events.NewRequest` interface, the ``mysubscriber`` function
will be called with an *event* object.

As you can see, a subscription is made in terms of a *class* (such as
:class:`pyramid.events.NewResponse`).  The event object sent to a subscriber
will always be an object that possesses an :term:`interface`.  For
:class:`pyramid.events.NewResponse`, that interface is
:class:`pyramid.interfaces.INewResponse`. The interface documentation
provides information about available attributes and methods of the event
objects.

The return value of a subscriber function is ignored.  Subscribers to
the same event type are not guaranteed to be called in any particular
order relative to each other.

All the concrete :app:`Pyramid` event types are documented in the
:ref:`events_module` API documentation.

An Example
----------

If you create event listener functions in a ``subscribers.py`` file in
your application like so:

.. code-block:: python
   :linenos:

   def handle_new_request(event):
       print('request', event.request)

   def handle_new_response(event):
       print('response', event.response)

You may configure these functions to be called at the appropriate
times by adding the following code to your application's
configuration startup:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator

   config.add_subscriber('myproject.subscribers.handle_new_request',
                         'pyramid.events.NewRequest')
   config.add_subscriber('myproject.subscribers.handle_new_response',
                         'pyramid.events.NewResponse')

Either mechanism causes the functions in ``subscribers.py`` to be
registered as event subscribers.  Under this configuration, when the
application is run, each time a new request or response is detected, a
message will be printed to the console.

Each of our subscriber functions accepts an ``event`` object and
prints an attribute of the event object.  This begs the question: how
can we know which attributes a particular event has?

We know that :class:`pyramid.events.NewRequest` event objects have a
``request`` attribute, which is a :term:`request` object, because the
interface defined at :class:`pyramid.interfaces.INewRequest` says it must.
Likewise, we know that :class:`pyramid.interfaces.NewResponse` events have a
``response`` attribute, which is a response object constructed by your
application, because the interface defined at
:class:`pyramid.interfaces.INewResponse` says it must
(:class:`pyramid.events.NewResponse` objects also have a ``request``).

.. _custom_events:

Creating Your Own Events
------------------------

In addition to using the events that the Pyramid framework creates,
you can create your own events for use in your application. This can
be useful to decouple parts of your application.

For example, suppose your application has to do many things when a new
document is created. Rather than putting all this logic in the view
that creates the document, you can create the document in your view
and then fire a custom event. Subscribers to the custom event can take
other actions, such as indexing the document, sending email, or
sending a message to a remote system.

An event is simply an object. There are no required attributes or
method for your custom events. In general, your events should keep
track of the information that subscribers will need. Here are some
example custom event classes:

.. code-block:: python
    :linenos:

    class DocCreated(object):
        def __init__(self, doc, request):
            self.doc = doc
            self.request = request

    class UserEvent(object):
        def __init__(self, user):
            self.user = user

    class UserLoggedIn(UserEvent):
        pass

Some Pyramid applications choose to define custom events classes in an
``events`` module.

You can subscribe to custom events in the same way that you subscribe
to Pyramid events -- either imperatively or with a decorator. You can
also use custom events with :ref:`subscriber predicates
<subscriber_predicates>`. Here's an example of subscribing to a custom
event with a decorator:

.. code-block:: python
    :linenos:

    from pyramid.events import subscriber
    from .events import DocCreated
    from .index import index_doc

    @subscriber(DocCreated)
    def index_doc(event):
        # index the document using our application's index_doc function
        index_doc(event.doc, event.request)

The above example assumes that the application defines a
``DocCreated`` event class and an ``index_doc`` function.

To fire your custom events use the
:meth:`pyramid.registry.Registry.notify` method, which is most often
accessed as ``request.registry.notify``. For example:

.. code-block:: python
    :linenos:

    from .events import DocCreated

    def new_doc_view(request):
        doc = MyDoc()
        event = DocCreated(doc, request)
        request.registry.notify(event)
        return {'document': doc}

This example view will notify all subscribers to the custom
``DocCreated`` event.

Note that when you fire an event, all subscribers are run
synchronously so it's generally not a good idea
to create event handlers that may take a long time to run. Although
event handlers could be used as a central place to spawn tasks on your
own message queues.
