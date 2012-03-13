.. index::
   single: hello world program

.. _firstapp_chapter:

Creating Your First :app:`Pyramid` Application
=================================================

In this chapter, we will walk through the creation of a tiny :app:`Pyramid`
application.  After we're finished creating the application, we'll explain in
more detail how it works.

.. _helloworld_imperative:

Hello World
-----------

Here's one of the very simplest :app:`Pyramid` applications:

.. literalinclude:: helloworld.py
   :linenos:

When this code is inserted into a Python script named ``helloworld.py`` and
executed by a Python interpreter which has the :app:`Pyramid` software
installed, an HTTP server is started on TCP port 8080.

On UNIX:

.. code-block:: text

   $ /path/to/your/virtualenv/bin/python helloworld.py

On Windows:

.. code-block:: text

   C:\> \path\to\your\virtualenv\Scripts\python.exe helloworld.py

This command will not return and nothing will be printed to the console.
When port 8080 is visited by a browser on the URL ``/hello/world``, the
server will simply serve up the text "Hello world!".  If your application is
running on your local system, using ``http://localhost:8080/hello/world``
in a browser will show this result.

Each time you visit a URL served by the application in a browser, a logging
line will be emitted to the console displaying the hostname, the date, the
request method and path, and some additional information.  This output is
done by the wsgiref server we've used to serve this application.  It logs an
"access log" in Apache combined logging format to the console.

Press ``Ctrl-C`` (or ``Ctrl-Break`` on Windows) to stop the application.

Now that we have a rudimentary understanding of what the application does,
let's examine it piece-by-piece.

Imports
~~~~~~~

The above ``helloworld.py`` script uses the following set of import
statements:

.. literalinclude:: helloworld.py
   :linenos:
   :lines: 1-3

The script imports the :class:`~pyramid.config.Configurator` class from the
:mod:`pyramid.config` module.  An instance of the
:class:`~pyramid.config.Configurator` class is later used to configure your
:app:`Pyramid` application.

Like many other Python web frameworks, :app:`Pyramid` uses the :term:`WSGI`
protocol to connect an application and a web server together.  The
:mod:`wsgiref` server is used in this example as a WSGI server for
convenience, as it is shipped within the Python standard library.

The script also imports the :class:`pyramid.response.Response` class for
later use.  An instance of this class will be used to create a web response.

View Callable Declarations
~~~~~~~~~~~~~~~~~~~~~~~~~~

The above script, beneath its set of imports, defines a function
named ``hello_world``.

.. literalinclude:: helloworld.py
   :linenos:
   :pyobject: hello_world

The function accepts a single argument (``request``) and it returns an
instance of the :class:`pyramid.response.Response` class.  The single
argument to the class' constructor is a string computed from parameters
matched from the URL.  This value becomes the body of the response.

This function is known as a :term:`view callable`.  A view callable
accepts a single argument, ``request``.  It is expected to return a
:term:`response` object.  A view callable doesn't need to be a function; it
can be represented via another type of object, like a class or an instance,
but for our purposes here, a function serves us well.

A view callable is always called with a :term:`request` object.  A request
object is a representation of an HTTP request sent to :app:`Pyramid` via the
active :term:`WSGI` server.

A view callable is required to return a :term:`response` object because a
response object has all the information necessary to formulate an actual HTTP
response; this object is then converted to text by the :term:`WSGI` server
which called Pyramid and it is sent back to the requesting browser.  To
return a response, each view callable creates an instance of the
:class:`~pyramid.response.Response` class.  In the ``hello_world`` function,
a string is passed as the body to the response.

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

.. literalinclude:: helloworld.py
   :linenos:
   :lines: 8-13

Let's break this down piece-by-piece.

Configurator Construction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: helloworld.py
   :linenos:
   :lines: 8-9

The ``if __name__ == '__main__':`` line in the code sample above represents a
Python idiom: the code inside this if clause is not invoked unless the script
containing this code is run directly from the operating system command
line. For example, if the file named ``helloworld.py`` contains the entire
script body, the code within the ``if`` statement will only be invoked when
``python helloworld.py`` is executed from the command line.

Using the ``if`` clause is necessary -- or at least best practice -- because
code in a Python ``.py`` file may be eventually imported via the Python
``import`` statement by another ``.py`` file.  ``.py`` files that are
imported by other ``.py`` files are referred to as *modules*.  By using the
``if __name__ == '__main__':`` idiom, the script above is indicating that it does
not want the code within the ``if`` statement to execute if this module is
imported from another; the code within the ``if`` block should only be run
during a direct script execution.

The ``config = Configurator()`` line above creates an instance of the
:class:`~pyramid.config.Configurator` class.  The resulting ``config`` object
represents an API which the script uses to configure this particular
:app:`Pyramid` application.  Methods called on the Configurator will cause
registrations to be made in an :term:`application registry` associated with
the application.

.. _adding_configuration:

Adding Configuration
~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. literalinclude:: helloworld.py
   :linenos:
   :lines: 10-11

First line above calls the :meth:`pyramid.config.Configurator.add_route`
method, which registers a :term:`route` to match any URL path that begins
with ``/hello/`` followed by a string.

The second line, ``config.add_view(hello_world, route_name='hello')``,
registers the ``hello_world`` function as a :term:`view callable` and makes
sure that it will be called when the ``hello`` route is matched.

.. index::
   single: make_wsgi_app
   single: WSGI application

WSGI Application Creation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. literalinclude:: helloworld.py
   :linenos:
   :lines: 12

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
earlier; in our case, the only policy choices made were implied by calls
to its ``add_view`` and ``add_route`` methods.

WSGI Application Serving
~~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. literalinclude:: helloworld.py
   :linenos:
   :lines: 13

Finally, we actually serve the application to requestors by starting up a
WSGI server.  We happen to use the :mod:`wsgiref` ``make_server`` server
maker for this purpose.  We pass in as the first argument ``'0.0.0.0'``,
which means "listen on all TCP interfaces."  By default, the HTTP server
listens only on the ``127.0.0.1`` interface, which is problematic if you're
running the server on a remote system and you wish to access it with a web
browser from a local system.  We also specify a TCP port number to listen on,
which is 8080, passing it as the second argument.  The final argument is the
``app`` object (a :term:`router`), which is the the application we wish to
serve.  Finally, we call the server's ``serve_forever`` method, which starts
the main loop in which it will wait for requests from the outside world.

When this line is invoked, it causes the server to start listening on TCP
port 8080.  The server will serve requests forever, or at least until we stop
it by killing the process which runs it (usually by pressing ``Ctrl-C``
or ``Ctrl-Break`` in the terminal we used to start it).

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

