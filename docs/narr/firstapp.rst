.. _firstapp_chapter:

Creating Your First :mod:`repoze.bfg` Application
=================================================

We will walk through the creation of a tiny :mod:`repoze.bfg`
application in this chapter.  After we're finished creating it, we'll
explain in more detail how the application works.

.. note::

   If you're a "theory-first" kind of person, you might choose to read
   :ref:`contextfinding_chapter` and :ref:`views_chapter` to augment
   your understanding before diving into the code that follows, but
   it's not necessary if -- like many programmers -- you're willing to
   "go with the flow".

.. _helloworld_imperative:

Hello World, Goodbye World (Imperative)
---------------------------------------

Here's one of the very simplest :mod:`repoze.bfg` applications,
configured imperatively:

.. code-block:: python
   :linenos:

   from webob import Response
   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.add_view(goodbye_world, name='goodbye')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

When this code is inserted into a Python script named
``helloworld.py`` and executed by a Python interpreter which has the
:mod:`repoze.bfg` software installed, an HTTP server is started on TCP
port 8080.  When port 8080 is visited by a browser on the root URL
(``/``), the server will simply serve up the text "Hello world!"  When
visited by a browser on the URL ``/goodbye``, the server will serve up
the text "Goodbye world!"
 
Now that we have a rudimentary understanding of what the application
does, let's examine it piece-by-piece.

Imports
~~~~~~~

The above script defines the following set of imports:

.. code-block:: python
   :linenos:

   from webob import Response
   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

:mod:`repoze.bfg` uses the :term:`WebOb` library as the basis for its
:term:`request` and :term:`response` objects.  The script uses the
:class:`webob.Response` class later in the script to create a
:term:`response` object.

Like many other Python web frameworks, :mod:`repoze.bfg` uses the
:term:`WSGI` protocol to connect an application and a web server
together.  The :mod:`paste.httpserver` server is used in this example
as a WSGI server for convenience, as the ``paste`` package is a
dependency of :mod:`repoze.bfg` itself.

The script also imports the ``Configurator`` class from the
``repoze.bfg.configuration`` module.  This class is used to configure
:mod:`repoze.bfg` for a particular application.  An instance of this
class provides methods which help configure various parts of
:mod:`repoze.bfg` for a given application deployment.

View Callable Declarations
~~~~~~~~~~~~~~~~~~~~~~~~~~

The above script, beneath its set of imports, defines two functions:
one named ``hello_world`` and one named ``goodbye_world``.

.. code-block:: python
   :linenos:

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

These functions don't do anything very taxing.  Both functions accept
a single argument (``request``).  The ``hello_world`` function does
nothing but return a response instance with the body ``Hello world!``.
The ``goodbye_world`` function returns a response instance with the
body ``Goodbye world!``.

Each of these functions is known as a :term:`view callable`.  View
callables in a :mod:`repoze.bfg` application accept a single argument,
``request`` and are expected to return a :term:`response` object.  A
view callable doesn't need to be a function; it can be represented via
another type of object, like a class or an instance, but for our
purposes here, a function serves us well.

A view callable is always called with a :term:`request` object.  A
request object is a representation of an HTTP request sent to
:mod:`repoze.bfg` via the active :term:`WSGI` server.

A view callable is required to return a :term:`response` object
because a response object has all the information necessary to
formulate an actual HTTP response; this object is then converted to
text by the upstream :term:`WSGI` server and sent back to the
requesting browser.  To return a response, each view callable creates
an instance of the :class:`webob.Response` class.  In the
``hello_world`` function, the string ``'Hello world!'`` is passed to
the ``Response`` constructor as the *body* of the response.  In the
``goodbye_world`` function, the string ``'Goodbye world!'`` is passed.

.. index::
   single: imperative configuration
   single: Configurator
   single: helloworld (imperative)

.. _helloworld_imperative_appconfig:

Application Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

In the above script, the following code, representing the
*configuration* of an application which uses the previously defined
imports and function definitions is placed within the confines of an
``if`` statement:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.add_view(goodbye_world, name='goodbye')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

Let's break this down this piece-by-piece.

Configurator Construction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()

The ``if __name__ == '__main__':`` line in the code sample above
represents a Python idiom: the code inside this if clause is not
invoked unless the script containing this code is run directly from
the command line. For example, if the file named ``helloworld.py``
contains the entire script body, the code within the ``if`` statement
will only be invoked when ``python helloworld.py`` is executed from
the operating system command line.

``helloworld.py`` in this case is a Python *module*.  Using the ``if``
clause is necessary -- or at least best practice -- because code in
any Python module may be imported by another Python module.  By using
this idiom, the script is indicating that it does not want the code
within the ``if`` statement to execute if this module is imported; the
code within the ``if`` block should only be run during a direct script
execution.

The ``config = Configurator()`` line above creates an instance of the
:class:`repoze.bfg.configuration.Configurator` class.  The resulting
``config`` object represents an API which the script uses to configure
this particular :mod:`repoze.bfg` application.  Methods called on the
Configurator will cause registrations to be made in a
:term:`application registry` associated with the application.

Beginning Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python

   config.begin()

The :meth:`repoze.bfg.configuration.Configurator.begin` method tells
the system that application configuration has begun.  In particular,
this causes the :term:`application registry` associated with this
configurator to become the "current" application registry, meaning
that code which attempts to use the application registry :term:`thread
local` will obtain the registry associated with the configurator.
This is an explicit step because it's sometimes convenient to use a
configurator without causing the registry associated with the
configurator to become "current".

.. note::

   See :ref:`threadlocals_chapter` for a discussion about what it
   means for an application registry to be "current".

.. _adding_configuration:

Adding Configuration
~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view(hello_world)
   config.add_view(goodbye_world, name='goodbye')

Each of these lines calls the
:meth:`repoze.bfg.configuration.Configurator.add_view` method.  The
``add_view`` method of a configurator registers a :term:`view
configuration` within the :term:`application registry`.  A :term:`view
configuration` represents a set of circumstances related to the
:term:`request` that will cause a specific :term:`view callable` to be
invoked.  This "set of circumstances" is provided as one or more
keyword arguments to the ``add_view`` method.  Each of these keyword
arguments is known as a view configuration :term:`predicate`.

The line ``config.add_view(hello_world)`` registers the
``hello_world`` function as a view callable.  The ``add_view`` method
of a Configurator must be called with a view callable object as its
first argument, so the first argument passed is the ``hello_world``
function.  This line calls ``add_view`` with a *default* value for the
:term:`predicate` argument, named ``name``.  The ``name`` predicate
defaults to a value equalling the empty string (``''``).  This means
that we're instructing :mod:`repoze.bfg` to invoke the ``hello_world``
view callable when the :term:`view name` is the empty string.  We'll
learn in later chapters what a :term:`view name` is, and under which
circumstances a request will have a view name that is the empty
string; in this particular application, it means that the
``hello_world`` view callable will be invoked when the root URL ``/``
is visited by a browser.

The line ``config.add_view(goodbye_world, name='goodbye')`` registers
the ``goodbye_world`` function as a view callable.  The line calls
``add_view`` with the view callable as the first required positional
argument, and a :term:`predicate` keyword argument ``name`` with the
value ``'goodbye'``.  The ``name`` argument supplied in this
:term:`view configuration` implies that only a request that has a
:term:`view name` of ``goodbye`` should cause the ``goodbye_world``
view callable to be invoked.  In this particular application, this
means that the ``goodbye_world`` view callable will be invoked when
the URL ``/goodbye`` is visited by a browser.

Each invocation of the ``add_view`` method implies a :term:`view
configuration` registration.  Each :term:`predicate` provided as a
keyword argument to the ``add_view`` method narrows the set of
circumstances which would cause the view configuration's callable to
be invoked.  In general, a greater number of predicates supplied along
with a view configuration will more strictly limit the applicability
of its associated view callable.  When :mod:`repoze.bfg` processes a
request, however, the view callable with the *most specific* view
configuration (the view configuration that matches the most specific
set of predicates) is always invoked.

In this application, :mod:`repoze.bfg` chooses the most specific view
callable based only on view :term:`predicate` applicability.  The
ordering of calls to
:meth:`repoze.bfg.configuration.Configurator.add_view` is never very
important.  We can register ``goodbye_world`` first and
``hello_world`` second; :mod:`repoze.bfg` will still give us the most
specific callable when a request is dispatched to it.

Ending Configuration
~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python

   config.end()

The :meth:`repoze.bfg.configuration.Configurator.end` method tells the
system that application configuration has ended.  It is the inverse of
:meth:`repoze.bfg.configuration.Configurator.begin`.  In particular,
this causes the :term:`application registry` associated with this
configurator to no longer be the "current" application registry,
meaning that code which attempts to use the application registry
:term:`thread local` will no longer obtain the registry associated
with the configurator.

.. note::

   See :ref:`threadlocals_chapter` for a discussion about what it
   means for an application registry to be "current".

.. index::
   single: make_wsgi_app
   single: WSGI application

WSGI Application Creation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python

   app = config.make_wsgi_app()

After configuring views and ending configuration, the script creates a
WSGI *application* via the
:meth:`repoze.bfg.configuration.Configurator.make_wsgi_app` method.  A
call to ``make_wsgi_app`` implies that all configuration is finished
(meaning all method calls to the configurator which set up views, and
various other configuration settings have been performed).  The
``make_wsgi_app`` method returns a :term:`WSGI` application object
that can be used by any WSGI server to present an application to a
requestor.  :term:`WSGI` is a protocol that allows servers to talk to
Python applications.  We don't discuss :term:`WSGI` in any depth
within this book, however, you can learn more about it by visiting
`wsgi.org <http://wsgi.org>`_.

The :mod:`repoze.bfg` application object, in particular, is an
instance of a class representing a :mod:`repoze.bfg` :term:`router`.
It has a reference to the :term:`application registry` which resulted
from method calls to the configurator used to configure it.  The
:term:`router` consults the registry to obey the policy choices made
by a single application.  These policy choices were informed by method
calls to the :term:`Configurator` made earlier; in our case, the only
policy choices made were implied by two calls to its ``add_view``
method.

WSGI Application Serving
~~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python

   serve(app, host='0.0.0.0')

Finally, we actually serve the application to requestors by starting
up a WSGI server.  We happen to use the :func:`paste.httpserver.serve`
WSGI server runner, passing it the ``app`` object (a :term:`router`)
as the application we wish to serve.  We also pass in an argument
``host=='0.0.0.0'``, meaning "listen on all TCP interfaces."  By
default, the Paste HTTP server listens only on the ``127.0.0.1``
interface, which is problematic if you're running the server on a
remote system and you wish to access it with a web browser from a
local system.  We don't specify a TCP port number to listen on; this
means we want to use the default TCP port, which is 8080.

When this line is invoked, it causes the server to start listening on
TCP port 8080.  It will serve requests forever, or at least until we
stop it by killing the process which runs it.

Conclusion
~~~~~~~~~~

Our hello world application is one of the simplest possible
:mod:`repoze.bfg` applications, configured "imperatively".  We can see
that it's configured imperatively because the full power of Python is
available to us as we perform configuration tasks.

.. index::
   single: helloworld (declarative)

.. _helloworld_declarative:

Hello World, Goodbye World (Declarative)
----------------------------------------

Another almost entirely equivalent mode of application configuration
exists named *declarative* configuration.  :mod:`repoze.bfg` can be
configured for the same "hello world" application "declaratively", if
so desired.

To do so, first, create a file named ``helloworld.py``:

.. code-block:: python
   :linenos:

   from webob import Response
   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

Then create a file named ``configure.zcml`` in the same directory as
the previously created ``helloworld.py``:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://namespaces.repoze.org/bfg">

     <include package="repoze.bfg.includes" />

     <view
        view="helloworld.hello_world"
        />

     <view
       name="goodbye"
       view="helloworld.goodbye_world"
       />

   </configure>

This pair of files forms an application functionally equivalent to the
application we created earlier in :ref:`helloworld_imperative`.
Let's examine the differences between the code in that section and the
code above.

In :ref:`helloworld_imperative_appconfig`, we had the following lines
within the ``if __name__ == '__main__'`` section of ``helloworld.py``:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.add_view(goodbye_world, name='goodbye')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

In our "declarative" code, we've added a call to the
:meth:`repoze.bfg.configuration.Configurator.load_zcml` method with
the value ``configure.zcml``, and we've removed the lines which read
``config.add_view(hello_world)`` and ``config.add_view(goodbye_world,
name='goodbye')``, so that it now reads as:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

Everything else is much the same.

The ``config.load_zcml('configure.zcml')`` line tells the configurator
to load configuration declarations from the ``configure.zcml`` file
which sits next to ``helloworld.py``.  Let's take a look at the
``configure.zcml`` file now:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://namespaces.repoze.org/bfg">

      <include package="repoze.bfg.includes" />

      <view
         view="helloworld.hello_world"
         />

      <view
         name="goodbye"
         view="helloworld.goodbye_world"
         />

   </configure>

We already understand what the view code does, because the application
is functionally equivalent to the application described in
:ref:`helloworld_imperative`, but use of :term:`ZCML` is new.  Let's
break that down tag-by-tag.

The ``<configure>`` Tag
~~~~~~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains this bit of XML:

.. code-block:: xml
   :linenos:

    <configure xmlns="http://namespaces.repoze.org/bfg">

       <!-- other directives -->

    </configure>

Because :term:`ZCML` is XML, and because XML requires a single root
tag for each document, every ZCML file used by :mod:`repoze.bfg` must
contain a ``configure`` container directive, which acts as the root
XML tag.  It is a "container" directive because its only job is to
contain other directives.

See also :ref:`configure_directive` and :ref:`word_on_xml_namespaces`.

The ``<include>`` Tag
~~~~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains this bit of XML within the
``<configure>`` root tag:

.. code-block:: xml

   <include package="repoze.bfg.includes" />

This self-closing tag instructs :mod:`repoze.bfg` to load a ZCML file
from the Python package with the :term:`dotted Python name`
``repoze.bfg.includes``, as specified by its ``package`` attribute.
This particular ``<include>`` declaration is required because it
actually allows subsequent declaration tags (such as ``<view>``, which
we'll see shortly) to be recognized.  The ``<include>`` tag
effectively just includes another ZCML file, causing its declarations
to be executed.  In this case, we want to load the declarations from
the file named ``configure.zcml`` within the
:mod:`repoze.bfg.includes` Python package.  We know we want to load
the ``configure.zcml`` from this package because ``configure.zcml`` is
the default value for another attribute of the ``<include>`` tag named
``file``.  We could have spelled the include tag more verbosely, but
equivalently as:

.. code-block:: xml
   :linenos:

   <include package="repoze.bfg.includes" 
            file="configure.zcml"/>

The ``<include>`` tag that includes the ZCML statements implied by the
``configure.zcml`` file from the Python package named
:mod:`repoze.bfg.includes` is basically required to come before any
other named declaration in an application's ``configure.zcml``.  If it
is not included, subsequent declaration tags will fail to be
recognized, and the configuration system will generate an error at
startup.  However, the ``<include package="repoze.bfg.includes"/>``
tag needs to exist only in a "top-level" ZCML file, it needn't also
exist in ZCML files *included by* a top-level ZCML file.

See also :ref:`include_directive`.

The ``<view>`` Tag
~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains these bits of XML *after* the
``<include>`` tag, but *within* the ``<configure>`` root tag:

.. code-block:: xml
   :linenos:

   <view
     view="helloworld.hello_world"
     />

   <view
     name="goodbye"
     view="helloworld.goodbye_world"
     />

These ``<view>`` declaration tags direct :mod:`repoze.bfg` to create
two :term:`view configuration` registrations.  The first ``<view>``
tag has an attribute (the attribute is also named ``view``), which
points at a :term:`dotted Python name`, referencing the
``hello_world`` function defined within the ``helloworld`` package.
The second ``<view>`` tag has a ``view`` attribute which points at a
:term:`dotted Python name`, referencing the ``goodbye_world`` function
defined within the ``helloworld`` package.  The second ``<view>`` tag
also has an attribute called ``name`` with a value of ``goodbye``.

These effect of the ``<view>`` tag declarations we've put into our
``configure.zcml`` is functionally equivalent to the effect of lines
we've already seen in an imperatively-configured application.  We're
just spelling things differently, using XML instead of Python.

In our previously defined application, in which we added view
configurations imperatively, we saw this code:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view(hello_world)
   config.add_view(goodbye_world, name='goodbye')

Each ``<view>`` declaration tag encountered in a ZCML file effectively
invokes the :meth:`repoze.bfg.configuration.Configurator.add_view`
method on the behalf of the developer.  Various attributes can be
specified on the ``<view>`` tag which influence the :term:`view
configuration` it creates.

Since the relative ordering of calls to
:meth:`repoze.bfg.configuration.Configurator.add_view` doesn't matter
(see the sidebar entitled *View Dispatch and Ordering* within
:ref:`adding_configuration`), the relative order of ``<view>`` tags in
ZCML doesn't matter either.  The following ZCML orderings are
completely equivalent:

.. topic:: Hello Before Goodbye

  .. code-block:: xml
     :linenos:

     <view
       view="helloworld.hello_world"
       />

     <view
       name="goodbye"
       view="helloworld.goodbye_world"
       />

.. topic:: Goodbye Before Hello

  .. code-block:: xml
     :linenos:

     <view
       name="goodbye"
       view="helloworld.goodbye_world"
       />

     <view
       view="helloworld.hello_world"
       />

We've now configured a :mod:`repoze.bfg` helloworld application
declaratively.  More information about this mode of configuration is
available in :ref:`declarative_configuration` and within
:ref:`zcml_reference`.

References
----------

For more information about the API of a :term:`Configurator` object,
see :class:`repoze.bfg.configuration.Configurator` .  The equivalent
ZCML declaration tags are introduced in :ref:`zcml_reference`.

For more information about :term:`view configuration`, see
:ref:`views_chapter`.

