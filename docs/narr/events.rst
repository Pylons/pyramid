.. _events_chapter:

Using Events
=============

An *event* is an object broadcast by the :mod:`repoze.bfg` framework
at particularly interesting points during the lifetime of an
application.  You don't need to use, know about, or care about events
in order to create most :mod:`repoze.bfg` applications, but they can
be useful when you want to do slightly advanced operations, such as
"skinning" a site slightly differently based on, for example, the
hostname used to reach the site.

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
interfaces, along with others, are documented in the
:ref:`events_module` API chapter.

.. note::

   Usually postprocessing requests is better handled in middleware
   components.  The ``INewResponse`` event exists purely for symmetry
   with ``INewRequest``, really.

The *subscriber* ZCML element takes two values: ``for``, which is the
interface the subscriber is registered for (which limits the events
that the subscriber will receive to those specified by the interface),
and ``handler`` which is a Python dotted-name path to the subscriber
function.

The return value of a subscriber function is ignored.

.. _using_an_event_to_vary_the_request_type:

Using An Event to Vary the Request Type
---------------------------------------

The most common usage of the ``INewRequestEvent`` is to attach an
:term:`interface` to the request to be able to differentiate, for
example, a request issued by a browser from a request issued by a JSON
client.  This differentiation makes it possible to register different
views against different ``request_type`` interfaces; for instance,
depending on the presence of a request header, you might return JSON
data.

To do this, you should subscribe an function to the ``INewRequest``
event type, and you should use the ``zope.interface.alsoProvides`` API
within the function to add one or more interfaces to the request
object provided by the event.  Here's an example.

.. code-block:: python
   :linenos:

   from zope.interface import alsoProvides
   from zope.interface import Interface

   class IJSONRequest(Interface):
       """ A request from a JSON client that sets and Accept: 
       application/json header """
 
   def categorize_request(event):
       request = event.request
       accept = request.headers.get('accept', '')
       if 'application/json' in accept:
           alsoProvides(request, IJSONRequest)

Then in your view registration ZCML, if you subscribe
``categorize_request`` for the ``repoze.bfg.interfaces.INewRequest``
type, you can use the ``request_type`` attribute to point at different
view functions depending upon the interface implemented by the
request.  For example, if the above subscriber function was
registered, the three view registrations below could be used to point
at separate view functions using separate request type interfaces for
the same model object.

.. code-block:: xml
   :linenos:

   <subscriber
      for="repoze.bfg.interfaces.INewRequest"
      handler=".subscribers.categorize_request"
    />

   <!-- html default view -->
   <view
      for=".models.MyModel"
      request_type="repoze.bfg.interfaces.IRequest"
      view=".views.html_view"/>

   <!-- JSON default view -->
   <view
      for=".models.MyModel"
      request_type=".interfaces.IJSONRequest"
      view=".views.json_view"/>

The interface ``repoze.bfg.interfaces.IRequest`` is automatically
implemented by every :mod:`repoze.bfg` request, so all requests will
implement that type, and views registered against models which do not
supply a ``request_type`` will be considered to be registered for this
``IRequest`` as a default.

Of course, you are not limited to using the ``Accept`` header to
determine which interfaces to attach to a request.  For example, you
might also choose to use hostname
(e.g. ``request.environ.get('HTTP_HOST',
request.environ['SERVER_NAME'])``) in order to "skin" your application
differently based on whether the user should see the "management"
(e.g. "manage.myapp.com") presentation of the application or the
"retail" presentation (e.g. "www.myapp.com").  By attaching to the
request an arbitrary interface after examining the hostname or any
other information available in the request within an ``INewRequest``
event subscriber, you can control view lookup precisely.  For example,
if you wanted to have two slightly different views for requests to two
different hostnames, you might register one view with a
``request_type`` of ``.interfaces.IHostnameFoo`` and another with a
``request_type`` of ``.interfaces.IHostnameBar`` and then arrange for
an event subscriber to attach ``.interfaces.IHostnameFoo`` to the
request when the HTTP_HOST is ``foo`` and ``.interfaces.IHostnameBar``
to the request when the HTTP_HOST is ``bar``.  The appropriate view
will be called.

You can also form an inheritance hierarchy out of ``request_type``
interfaces.  When :mod:`repoze.bfg` looks up a view, the most specific
view for the interface(s) found on the request based on standard
Python method resolution order through the interface class hierarchy
will be called.

:mod:`repoze.bfg` also makes available as interfaces standard request
type interfaces matching HTTP verbs.  When these are specified as a
``request_type`` for a view, the view will be called only when the
request has an HTTP verb (aka HTTP method) matching the request type.
For example, using the string ``repoze.bfg.interfaces.IPOST`` or the
imported interface definition itself matching that Python dotted name
as the request_type argument to a view definition is equivalent to
using the string ``POST``.  See :ref:`interfaces_module` for more
information about available request types.
