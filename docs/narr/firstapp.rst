.. _firstapp_chapter:

Creating Your First :app:`Pyramid` Application
=================================================

In this chapter, we will walk through the creation of a tiny :app:`Pyramid`
application.  After we're finished creating the application, we'll explain in
more detail how it works.

.. note::

   If you're a "theory-first" kind of person, you might choose to read
   :ref:`urldispatch_chapter` and :ref:`views_chapter` before diving into
   the code that follows, but it's not necessary if -- like many programmers
   -- you're willing to "go with the flow".

.. _helloworld_imperative:

Hello World, Goodbye World
--------------------------

Here's one of the very simplest :app:`Pyramid` applications, configured
imperatively:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.response import Response
   from paste.httpserver import serve

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

   if __name__ == '__main__':
       config = Configurator()
       config.add_view(hello_world)
       config.add_view(goodbye_world, name='goodbye')
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

When this code is inserted into a Python script named ``helloworld.py`` and
executed by a Python interpreter which has the :app:`Pyramid` software
installed, an HTTP server is started on TCP port 8080:

.. code-block:: text

   $ python helloworld.py
   serving on 0.0.0.0:8080 view at http://127.0.0.1:8080

When port 8080 is visited by a browser on the root URL (``/``), the server
will simply serve up the text "Hello world!"  When visited by a browser on
the URL ``/goodbye``, the server will serve up the text "Goodbye world!"

Press ``Ctrl-C`` to stop the application.

Now that we have a rudimentary understanding of what the application does,
let's examine it piece-by-piece.

Imports
~~~~~~~

The above ``helloworld.py`` script uses the following set of import
statements:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.response import Response
   from paste.httpserver import serve

The script imports the :class:`~pyramid.config.Configurator` class from the
:mod:`pyramid.config` module.  An instance of the
:class:`~pyramid.config.Configurator` class is later used to configure your
:app:`Pyramid` application.

The script uses the :class:`pyramid.response.Response` class later in the
script to create a :term:`response` object.

Like many other Python web frameworks, :app:`Pyramid` uses the :term:`WSGI`
protocol to connect an application and a web server together.  The
:mod:`paste.httpserver` server is used in this example as a WSGI server for
convenience, as the ``paste`` package is a dependency of :app:`Pyramid`
itself.

View Callable Declarations
~~~~~~~~~~~~~~~~~~~~~~~~~~

The above script, beneath its set of imports, defines two functions: one
named ``hello_world`` and one named ``goodbye_world``.

.. code-block:: python
   :linenos:

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

These functions don't do anything very difficult.  Both functions accept a
single argument (``request``).  The ``hello_world`` function does nothing but
return a response instance with the body ``Hello world!``.  The
``goodbye_world`` function returns a response instance with the body
``Goodbye world!``.

Each of these functions is known as a :term:`view callable`.  A view callable
accepts a single argument, ``request``.  It is expected to return a
:term:`response` object.  A view callable doesn't need to be a function; it
can be represented via another type of object, like a class or an instance,
but for our purposes here, a function serves us well.

A view callable is always called with a :term:`request` object.  A request
object is a representation of an HTTP request sent to :app:`Pyramid` via the
active :term:`WSGI` server.

A view callable is required to return a :term:`response` object because a
response object has all the information necessary to formulate an actual HTTP
response; this object is then converted to text by the upstream :term:`WSGI`
server and sent back to the requesting browser.  To return a response, each
view callable creates an instance of the :class:`~pyramid.response.Response`
class.  In the ``hello_world`` function, the string ``'Hello world!'`` is
passed to the ``Response`` constructor as the *body* of the response.  In the
``goodbye_world`` function, the string ``'Goodbye world!'`` is passed.

.. note:: As we'll see in later chapters, returning a literal
   :term:`response` object from a view callable is not always required; we
   can instead use a :term:`renderer` in our view configurations.  If we use
   a renderer, our view callable is allowed to return a value that the
   renderer understands, and the renderer generates a response on our behalf.

.. index::
   single: imperative configuration
   single: Configurator
   single: helloworld (imperative)

.. _helloworld_imperative_appconfig:

Application Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

In the above script, the following code represents the *configuration* of
this simple application. The application is configured using the previously
defined imports and function definitions, placed within the confines of an
``if`` statement:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.add_view(hello_world)
       config.add_view(goodbye_world, name='goodbye')
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

Let's break this down this piece-by-piece.

Configurator Construction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()

The ``if __name__ == '__main__':`` line in the code sample above represents a
Python idiom: the code inside this if clause is not invoked unless the script
containing this code is run directly from the command line. For example, if
the file named ``helloworld.py`` contains the entire script body, the code
within the ``if`` statement will only be invoked when ``python
helloworld.py`` is executed from the operating system command line.

``helloworld.py`` in this case is a Python :term:`module`.  Using the ``if``
clause is necessary -- or at least best practice -- because code in any
Python module may be imported by another Python module.  By using this idiom,
the script is indicating that it does not want the code within the ``if``
statement to execute if this module is imported; the code within the ``if``
block should only be run during a direct script execution.

The ``config = Configurator()`` line above creates an instance of the
:class:`~pyramid.config.Configurator` class.  The resulting ``config`` object
represents an API which the script uses to configure this particular
:app:`Pyramid` application.  Methods called on the Configurator will cause
registrations to be made in a :term:`application registry` associated with
the application.

.. _adding_configuration:

Adding Configuration
~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view(hello_world)
   config.add_view(goodbye_world, name='goodbye')

Each of these lines calls the :meth:`pyramid.config.Configurator.add_view`
method.  The ``add_view`` method of a configurator registers a :term:`view
configuration` within the :term:`application registry`.  A :term:`view
configuration` represents a set of circumstances related to the
:term:`request` that will cause a specific :term:`view callable` to be
invoked.  This "set of circumstances" is provided as one or more keyword
arguments to the ``add_view`` method.  Each of these keyword arguments is
known as a view configuration :term:`predicate`.

The line ``config.add_view(hello_world)`` registers the ``hello_world``
function as a view callable.  The ``add_view`` method of a Configurator must
be called with a view callable object or a :term:`dotted Python name` as its
first argument, so the first argument passed is the ``hello_world`` function.
This line calls ``add_view`` with a *default* value for the :term:`predicate`
argument, named ``name``.  The ``name`` predicate defaults to a value
equalling the empty string (``''``).  This means that we're instructing
:app:`Pyramid` to invoke the ``hello_world`` view callable when the
:term:`view name` is the empty string.  We'll learn in later chapters what a
:term:`view name` is, and under which circumstances a request will have a
view name that is the empty string; in this particular application, it means
that the ``hello_world`` view callable will be invoked when the root URL
``/`` is visited by a browser.

The line ``config.add_view(goodbye_world, name='goodbye')`` registers the
``goodbye_world`` function as a view callable.  The line calls ``add_view``
with the view callable as the first required positional argument, and a
:term:`predicate` keyword argument ``name`` with the value ``'goodbye'``.
The ``name`` argument supplied in this :term:`view configuration` implies
that only a request that has a :term:`view name` of ``goodbye`` should cause
the ``goodbye_world`` view callable to be invoked.  In this particular
application, this means that the ``goodbye_world`` view callable will be
invoked when the URL ``/goodbye`` is visited by a browser.

Each invocation of the ``add_view`` method registers a :term:`view
configuration`.  Each :term:`predicate` provided as a keyword argument to the
``add_view`` method narrows the set of circumstances which would cause the
view configuration's callable to be invoked.  In general, a greater number of
predicates supplied along with a view configuration will more strictly limit
the applicability of its associated view callable.  When :app:`Pyramid`
processes a request, the view callable with the *most specific* view
configuration (the view configuration that matches the most specific set of
predicates) is always invoked.

In this application, :app:`Pyramid` chooses the most specific view callable
based only on view :term:`predicate` applicability.  The ordering of calls to
:meth:`~pyramid.config.Configurator.add_view` is never very important.  We can
register ``goodbye_world`` first and ``hello_world`` second; :app:`Pyramid`
will still give us the most specific callable when a request is dispatched to
it.

.. index::
   single: make_wsgi_app
   single: WSGI application

WSGI Application Creation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python
   :linenos:

   app = config.make_wsgi_app()

After configuring views and ending configuration, the script creates a WSGI
*application* via the :meth:`pyramid.config.Configurator.make_wsgi_app`
method.  A call to ``make_wsgi_app`` implies that all configuration is
finished (meaning all method calls to the configurator which set up views,
and various other configuration settings have been performed).  The
``make_wsgi_app`` method returns a :term:`WSGI` application object that can
be used by any WSGI server to present an application to a requestor.
:term:`WSGI` is a protocol that allows servers to talk to Python
applications.  We don't discuss :term:`WSGI` in any depth within this book,
however, you can learn more about it by visiting `wsgi.org
<http://wsgi.org>`_.

The :app:`Pyramid` application object, in particular, is an instance of a
class representing a :app:`Pyramid` :term:`router`.  It has a reference to
the :term:`application registry` which resulted from method calls to the
configurator used to configure it.  The :term:`router` consults the registry
to obey the policy choices made by a single application.  These policy
choices were informed by method calls to the :term:`Configurator` made
earlier; in our case, the only policy choices made were implied by two calls
to its ``add_view`` method.

WSGI Application Serving
~~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python
   :linenos:

   serve(app, host='0.0.0.0')

Finally, we actually serve the application to requestors by starting up a
WSGI server.  We happen to use the :func:`paste.httpserver.serve` WSGI server
runner, passing it the ``app`` object (a :term:`router`) as the application
we wish to serve.  We also pass in an argument ``host=='0.0.0.0'``, meaning
"listen on all TCP interfaces."  By default, the Paste HTTP server listens
only on the ``127.0.0.1`` interface, which is problematic if you're running
the server on a remote system and you wish to access it with a web browser
from a local system.  We don't specify a TCP port number to listen on; this
means we want to use the default TCP port, which is 8080.

When this line is invoked, it causes the server to start listening on TCP
port 8080.  It will serve requests forever, or at least until we stop it by
killing the process which runs it (usually by pressing ``Ctrl-C`` in the
terminal we used to start it).

Conclusion
~~~~~~~~~~

Our hello world application is one of the simplest possible :app:`Pyramid`
applications, configured "imperatively".  We can see that it's configured
imperatively because the full power of Python is available to us as we
perform configuration tasks.

References
----------

For more information about the API of a :term:`Configurator` object,
see :class:`~pyramid.config.Configurator` .

For more information about :term:`view configuration`, see
:ref:`view_config_chapter`.

An example of using *declarative* configuration (:term:`ZCML`) instead of
imperative configuration to create a similar "hello world" is available
within the documentation for :term:`pyramid_zcml`.
