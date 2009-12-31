.. index::
   single: frameworks vs. libraries
   single: framework

.. _configuration_narr:

Creating Your First :mod:`repoze.bfg` Application
=================================================

Most of the logic in a web application is completely
application-specific.  For example, the content of a web page served
by one web application might be a representation of the contents of an
accounting ledger, while the content of of a web page served by
another might be a listing of songs.  These applications probably
won't serve the same set of customers.  However, both the
ledger-serving and song-serving applications can be written using
:mod:`repoze.bfg`, because :mod:`repoze.bfg` is a very general
*framework* which can be used to create all kinds of web applications.
As a framework, the primary job of :mod:`repoze.bfg` is to make it
easier for a developer to create an arbitrary web application.

.. sidebar:: Frameworks vs. Libraries

   A *framework* differs from a *library* in one very important way:
   library code is always *called* by code that you write, while a
   framework always *calls* code that you write.  Using a set of
   libraries to create an application is usually easier than using a
   framework initially, because you can choose to cede control to
   library code you have not authored very selectively. But when you
   use a framework, you are required to cede a greater portion of
   control to code you have not authored: code that resides in the
   framework itself.  You needn't use a framework at all to create a
   web application using Python.  A rich set of libraries already
   exists for the platform.  In practice, however, using a framework
   to create an application is often more practical than rolling your
   own via a set of libraries if the framework provides a set of
   facilities that fits your application requirements.

Each deployment of an application written using :mod:`repoze.bfg`
implies a specific *configuration* of the framework itself.  For
example, a song-serving application might plug code into the framework
that manages songs, while the ledger- serving application might plug
in code that manages accounting information.  :mod:`repoze.bfg` refers
to the way in which code is plugged in to it for a specific
application as "configuration".

Most people understand "configuration" as coarse knobs that inform the
high-level operation of a specific application deployment.  For
instance, it's easy to think of the values implied by a ``.ini`` file
which is parsed at application startup time as "configuration".
:mod:`repoze.bfg` extends this pattern out to application development,
using the term "configuration" to express standardized ways that code
gets plugged into a deployment of the framework itself.  When you plug
code into the :mod:`repoze.bfg` framework, you are "configuring"
:mod:`repoze.bfg` for the purpose of creating a particular application
deployment.

There are a number of different mechanisms you may use to configure
:mod:`repoze.bfg` to create an application: *imperative* configuration
and *declarative* configuration.  We'll examine both modes in the
sections which follow.

.. index::
   pair: imperative; helloworld

.. _helloworld_imperative:

Hello World, Configured Imperatively
------------------------------------

Experienced Python programmers might find that "imperative"
configuration is easiest to use. This is the configuration mode in
which a developer cedes the least amount of control to the framework;
it's "imperative" because you express the configuration directly in
Python code.

Here's one of the simplest :mod:`repoze.bfg` applications, configured
imperatively:

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
       serve(app)

When this code is inserted into a Python script named
``helloworld.py`` and executed by a Python interpreter which has the
:mod:`repoze.bfg` software installed, an HTTP server is started on
port 8080.  When port 8080 is visited by a user agent on the root URL
(``/``), the server will simply serve up the text "Hello world!" with
the HTTP response values ``200 OK`` as a response code and a
``Content-Type`` header value of ``text/plain``.  But for reasons
we'll better understand shortly, when visited by a user agent on the
URL ``/goodbye``, the server will serve up "Goodbye world!".

Let's examine this program piece-by-piece.

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
as a WSGI server for convenience, as ``Paste`` is a dependency of
:mod:`repoze.bfg` itself.  However, :mod:`repoze.bfg` applications can
be served by any WSGI server.

The script also imports the ``Configurator`` class from the
``repoze.bfg.configuration`` module.  This class is used to configure
:mod:`repoze.bfg` for a particular application.  An instance of this
class provides methods which help configure various parts of
:mod:`repoze.bfg` for a given application deployment.

View Declaration
~~~~~~~~~~~~~~~~

The above script, beneath its set of imports, defines two functions:
one named ``hello_world`` and one named ``goodbye_world``.

.. code-block:: python
   :linenos:

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

Each function accepts a single argument (``request``) and returns an
instance of the :class:`webob.Response` class.  In the ``hello_world``
function, the string ``'Hello world!'`` is passed to the ``Response``
constructor as the *body* of the response.  In the ``goodbye_world``
function, the string ``'Goodbye world!'`` is passed.

Each of these functions is known as a :term:`view callable`.  View
callables in a "real" :mod:`repoze.bfg` application are often
functions which accept a :term:`request` and return a
:term:`response`.  A view callable can be represented via another type
of object, like a class or an instance, but for our purposes here, a
function serves us well.

A view callable is called with a :term:`request` object, which is a
representation of an HTTP request sent by a remote user agent.  A view
callable is required to return a :term:`response` object because a
response object has all the information necessary to formulate an
actual HTTP response; this object is then converted to text and sent
back to the requesting user agent.

The ``hello_world`` view callable defined by the script does nothing
but return a response with the body ``Hello world!``; the
``goodbye_world`` view callable returns a response with the body
``Goodbye world!``.

.. index::
   pair: traversal; introduction

.. _traversal_intro:

An Introduction to Traversal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you've run the code listed in :ref`helloworld_imperative` already,
you've unwittingly configured :mod:`repoze.bfg` to serve an
application that relies on :term:`traversal`.  A full explanation of
how :mod:`repoze.bfg` locates "the right" :term:`view callable` for a
given request requires some explanation of :term:`traversal`.

Traversal is part of a mechanism used by :mod:`repoze.bfg` to map the
URL of some request to a particular :term:`view callable`.  It is not
the only mechanism made available by :mod:`repoze.bfg` that allows the
mapping a URL to a view callable.  Another distinct mode known as
:term:`URL dispatch` can alternately be used to find a view callable
based on a URL.  However, our sample application uses only
:term:`traversal`.

In :mod:`repoze.bfg` terms, :term:`traversal` is the act of walking
over an object graph starting from a :term:`root` object in order to
find a :term:`context` object and a :term:`view name`.  Once a context
and a view name are found, these two bits of information, plus other
information from the request are used to look up a :term:`view
callable`.  :mod:`repoze.bfg` bothers to do traversal only because the
information returned from traversal allows a view callable to be
found.

The individual path segments of the "path info" portion of a URL (the
data following the hostname and port number, but before any query
string elements or fragments, for example the ``/a/b/c`` portion of
the URL ``http://example.com/a/b/c?foo=1``) are used as "steps" during
traversal.

.. note:: A useful analogy of how :mod:`repoze.bfg` :term:`traversal`
  works is available within the chapter section entitled
  :ref:`traversal_behavior`.

The results of a :term:`traversal` include a :term:`context` and a
:term:`view name`.  The :term:`view name` is the *first* URL path
segment in the set of path segments "left over" in the results of
:term:`traversal`.  This will either be the empty string (``''``) or a
non-empty string (one of the path segment strings).  The empty string
represents the :term:`default view` of a context object.

The :term:`default view` is found when all path elements in the URL
are exhausted before :term:`traversal` returns a :term:`context`
object, causing the :term:`view name` to be ``''`` (the empty string).
When no path segments are "left over" after traversal, the
:term:`default view` for the context found is invoked.

If traversal returns a non-empty :term:`view name`, it means that
traversal "ran out" of nodes in the graph before it finished
exhausting all the path segments implied by the path info of the URL:
no segments are "left over".  In this case, because the :term:`view
name` is non-empty, a *non-default* view callable will be invoked.

The combination of the :term:`context` object and the :term:`view
name` (and, in more complex configurations, other :term:`predicate`
values) are used to find "the right" :term:`view callable`, which will
be invoked after traversal.

The object graph of our hello world application is very simple:
there's exactly one object in our graph; the default :term:`root`
object.

Relating Traversal to the Hello World Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our application's :term:`root` object is the *default* root object
used when one isn't otherwise specified in application configuration.
This root object does not have a ``__getitem__`` method, thus it has
no children.  Although in a more complex system there can be many
contexts which URLs resolve to in our application, effectively there
is only ever one context: the root object.

We have only a single default view registered (the registration for
the ``hello_world`` view callable).  Due to this set of circumstances,
you can consider the sole possible URL that will resolve to a
:term:`default view` in this application the root URL ``'/'``.  It is
the only URL that will resolve to the :term:`view name` of ``''`` (the
empty string).

We have only a single view registered for the :term:`view name`
``goodbye`` (the registration for the ``goodbye_world`` view
callable).  Due to this set of circumstances, you can consider the
sole possible URL that will resolve to the ``goodbye_world`` in this
application the URL ``'/goodbye'`` because it is the only URL that
will resolve to the :term:`view name` of ``goodbye``.

.. index::
   pair: imperative; configuration
   single: Configurator

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
       simple_server.make_server('', 8080, app).serve_forever()

Let's break this down this piece-by-piece.

Configurator Construction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()

The ``if __name__ == '__main__':`` line above represents a Python
idiom: the code inside this if clause is not invoked unless the script
is run directly from the command line via, for example, ``python
helloworld.py`` where the file named ``helloworld.py`` contains the
entire script body.  ``helloworld.py`` in this case is a Python
*module*.  Using the ``if`` clause is necessary (or at least "best
practice") because code in any Python module may be imported by
another Python module.  By using this idiom, the script is indicating
that it does not want the code within the ``if`` statement to execute
if this module is imported; the code within the ``if`` block should
only be run during a direct script execution.

The ``config = Configurator()`` line above creates an instance of the
:class:`repoze.bfg.configuration.Configurator` class.  The resulting
``config`` object represents an API which the script uses to configure
this particular :mod:`repoze.bfg` application.

.. note::

   An instance of the :class:`repoze.bfg.configuration.Configurator`
   class is a *wrapper* object which mutates an :term:`application
   registry` as its methods are called.  An application registry
   represents the configuration state of a :mod:`repoze.bfg`
   application.  The ``Configurator`` is not itself an
   :term:`application registry`, it is a mechanism used to configure
   an application registry.  The underlying application registry
   object being configured by a ``Configurator`` is available as its
   ``registry`` attribute.

Beginning Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python

   config.begin()

The :meth:`repoze.bfg.configuration.Configurator.begin` method tells
the the system that application configuration has begun.  In
particular, this causes the :term:`application registry` associated
with this configurator to become the "current" application registry,
meaning that code which attempts to use the application registry
:term:`thread local` will obtain the registry associated with the
configurator.  This is an explicit step because it's sometimes
convenient to use a configurator without causing the registry
associated with the configurator to become "current".

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
configuration` represents a :term:`view callable` which must be
invoked when a set of circumstances related to the :term:`request` is
true.  This "set of circumstances" is provided as one or more keyword
arguments to the ``add_view`` method, otherwise known as
:term:`predicate` arguments.

The line ``config.add_view(hello_world)`` registers the
``hello_world`` function as a view callable.  The ``add_view`` method
of a Configurator must be called with a view callable object as its
first argument, so the first argument passed is ``hello_world``
function we'd like to use as a :term:`view callable`.  However, this
line calls ``add_view`` with a single default :term:`predicate`
argument, the ``name`` predicate with a value of ``''``, meaning that
we'd like :mod:`repoze.bfg` to invoke the ``hello_world`` view
callable for any request for the :term:`default view` of an object.

Our ``hello_world`` :term:`view callable` returns a Response instance
with a body of ``Hello world!`` in the configuration implied by this
script.  It is configured as a :term:`default view`.  Therefore, a
user agent contacting a server running this application will receive
the greeting ``Hello world!`` when any :term:`default view` is
invoked. 

.. sidebar:: View Dispatch and Ordering

   When :term:`traversal` is used, :mod:`repoze.bfg` chooses the most
   specific view callable based *only* on view :term:`predicate`
   applicability.  This is unlike :term:`URL dispatch`, another
   dispatch mode of :mod:`repoze.bfg` (and other frameworks, like
   :term:`Pylons` and :term:`Django`) which first uses an ordered
   routing lookup to resolve the request to a view callable by running
   it through a relatively-ordered series of URL path matches.  We're
   not really concerned about the finer details of :term:`URL
   dispatch` right now.  It's just useful to use for demonstrative
   purposes: the ordering of calls to
   :meth:`repoze.bfg.configuration.Configurator.add_view`` is never
   very important.  We can register ``goodbye_world`` first and
   ``hello_world`` second; :mod:`repoze.bfg` will still give us the
   most specific callable when a request is dispatched to it.

The line ``config.add_view(goodbye_world, name='goodbye')`` registers
the ``goodbye_world`` function as a view callable.  The line calls
``add_view`` with the view callable as the first required positional
argument, and a :term:`predicate` keyword argument ``name`` with the
value ``'goodbye'``.  This :term:`view configuration` implies that a
request with a :term:`view name` of ``goodbye`` should cause the
``goodbye_world`` view callable to be invoked.  For the purposes of
this discussion, the :term:`view name` can be considered the first
non-empty path segment in the URL: in particular, this view
configuration will match when the URL is ``/goodbye``.

Our ``goodbye_world`` :term:`view callable` returns a Response
instance with a body of ``Goodbye world!`` in the configuration
implied by this script.  It is configured as with a :term:`view name`
predicate of ``goodbye``.  Therefore, a user agent contacting a server
running this application will receive the greeting ``Goodbye world!``
when the path info part of the request is ``/goodbye``.

Each invocation of the ``add_view`` method implies a :term:`view
configuration` registration.  Each :term:`predicate` provided as a
keyword argument to the ``add_view`` method narrows the set of
circumstances which would cause the view configuration's callable to
be invoked.  In general, a greater number of predicates supplied along
with a view configuration will more strictly limit the applicability
of its associated view callable.  When :mod:`repoze.bfg` processes a
request, however, the view callable with the *most specific* view
configuration (the view configuration that matches the largest number
of predicates) is always invoked. 

Earlier we explained that the server would return ``Hello world!`` if
you visited the *root* (``/``) URL.  However, actually, because the
view configuration registration for the ``hello_world`` view callable
has no :term:`predicate` arguments, the ``hello_world`` view callable
is applicable for the :term:`default view` of any :term:`context`
resulting from a request.  This isn't all that interesting in this
application, because we always only have *one* potential context (the
root object): it is the only object in the graph.

We've also registered a view configuration for another circumstance:
the ``goodbye_world`` view callable has a ``name`` predicate of
``goodbye``, meaning that it will match for requests that have the
:term:`view name` ``goodbye`` unlike the ``hello_world`` view
configuration registration, which will only match the default view
(view name ``''``) of a request.  Because :mod:`repoze.bfg` chooses
the best view configuration for any request, the ``goodbye_world``
view callable will be used when the URL contains path information that
ends with ``/goodbye``.

Ending Configuration
~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python

   config.end()

The :meth:`repoze.bfg.configuration.Configurator.end` method tells the
the system that application configuration has ended.  It is the
inverse of :meth:`repoze.bfg.configuration.Configurator.begin`.  In
particular, this causes the :term:`application registry` associated
with this configurator to no longer be the "current" application
registry, meaning that code which attempts to use the application
registry :term:`thread local` will no longer obtain the registry
associated with the configurator.

.. index::
   single: make_wsgi_app
   pair: WSGI; application
   triple: WSGI; application; creation

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
requestor.

The :mod:`repoze.bfg` application object, in particular, is an
instance of the :class:`repoze.bfg.router.Router` class.  It has a
reference to the :term:`application registry` which resulted from
method calls to the configurator used to configure it.  The Router
consults the registry to obey the policy choices made by a single
application.  These policy choices were informed by method calls to
the ``Configurator`` made earlier; in our case, the only policy
choices made were implied by two calls to the ``add_view`` method,
telling our application that it should effectively serve up the
``hello_world`` view callable to any user agent when it visits the
root URL, and the ``goodbye_world`` view callable to any user agent
when it visits the URL with the path info ``/goodbye``.

WSGI Application Serving
~~~~~~~~~~~~~~~~~~~~~~~~

.. ignore-next-block
.. code-block:: python

   serve(app)

Finally, we actually serve the application to requestors by starting
up a WSGI server.  We happen to use the :func:`paste.httpserver.serve`
WSGI server runner, using the default TCP port of 8080, and we pass it
the ``app`` object (an instance of the
:class:`repoze.bfg.router.Router` class) as the application we wish to
serve.  This causes the server to start listening on the TCP port.  It
will serve requests forever, or at least until we stop it by killing
the process which runs it.

Conclusion
~~~~~~~~~~

Our hello world application is one of the simplest possible
:mod:`repoze.bfg` applications, configured "imperatively".  We can see
a good deal of what's going on "under the hood" when we configure a
:mod:`repoze.bfg` application imperatively.  However, another mode of
configuration exists named *declarative* configuration.

.. index::
   pair: helloworld; declarative
   single: helloworld

.. _helloworld_declarative:

Hello World, Configured Declaratively
-------------------------------------

:mod:`repoze.bfg` can be configured for the same "hello world"
application "declaratively", if so desired.  Declarative configuration
relies on *declarations* made external to the code in a configuration
file format named :term:`ZCML` (Zope Configuration Markup Language),
an XML dialect.

Declarative configuration mode is the configuration mode in which
developers cede the most amount of control to the framework itself.
Because application developers cede more control to the framework, it
is also harder to understand than purely imperative configuration.
However, using declarative configuration has a number of benefits, the
primary benefit being that applications configured declaratively can
be *overridden* and *extended* by third parties without requiring the
third party to change application code.

.. note::

   See :ref:`extending_chapter` for a discussion of extending and
   overriding :mod:`repoze.bfg` applications.

Unlike the simplest :mod:`repoze.bfg` application configured
imperatively, the simplest :mod:`repoze.bfg` application, configured
declaratively requires not one, but two files: a Python file and a
:term:`ZCML` file.

In a file named ``helloworld.py``:

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
       serve(app)

In a file named ``configure.zcml`` in the same directory as the
previously created ``helloworld.py``:

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
application we created earlier.  Let's examine the differences between
the code described in :ref:`helloworld_imperative` and the code above.

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
       simple_server.make_server('', 8080, app).serve_forever()

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
       simple_server.make_server('', 8080, app).serve_forever()

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

This singleton (self-closing) tag instructs ZCML to load a ZCML file
from the Python package with the :term:`dotted Python name`
:mod:`repoze.bfg.includes`, as specified by its ``package`` attribute.
This particular ``<include>`` declaration is required because it
actually allows subsequent declaration tags (such as ``<view>``, which
we'll see shortly) to be recognized.  The ``<include>`` tag
effectively just includes another ZCML file; this causes its
declarations to be executed.  In this case, we want to load the
declarations from the file named ``configure.zcml`` within the
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
recognized, and the configuration system will generate a traceback.
However, the ``<include package="repoze.bfg.includes"/>`` tag needs to
exist only in a "top-level" ZCML file, it needn't also exist in ZCML
files *included by* a top-level ZCML file.

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
(see the sidebar entitled *View Dispatch and Ordering*), the relative
order of ``<view>`` tags in ZCML doesn't matter either.  The following
ZCML orderings are completely equivalent:

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

The ``<view>`` tag is an example of a :mod:`repoze.bfg` declaration
tag.  Other such tags include ``<route>``, ``<scan>``, ``<notfound>``,
``<forbidden>``, and others.  Each of these tags is effectively a
"macro" which calls methods on the
:class:`repoze.bfg.configuration.Configurator` object on your behalf.

.. index::
   pair: ZCML; conflict detection

ZCML Conflict Detection
~~~~~~~~~~~~~~~~~~~~~~~

An additional feature of ZCML is *conflict detection*.  If you define
two declaration tags within the same ZCML file which logically
"collide", an exception will be raised, and the application will not
start.  For example, the following ZCML file has two conflicting
``<view>`` tags:

.. code-block:: xml
   :linenos:

    <configure xmlns="http://namespaces.repoze.org/bfg">

      <include package="repoze.bfg.includes" />

      <view
        view="helloworld.hello_world"
        />

      <view
        view="helloworld.hello_world"
        />

    </configure>

If you try to use this ZCML file as the source of ZCML for an
application, a :data:`repoze.bfg.exceptions.ConfigurationError` will
be raised when you attempt to start the application with information
about which tags might have conflicted.

Conclusions
-----------

.. sidebar::  Which Configuration Mode Should I Use?

  We recommend declarative configuration (:term:`ZCML`), because it's
  the more traditional form of configuration used by Zope-based
  systems, it can be overridden and extended by third party deployers,
  and there are more examples for it "in the wild".  However,
  imperative mode configuration can be simpler to understand.

:mod:`repoze.bfg` allows an application to perform configuration tasks
either imperatively or declaratively.  You can choose the mode that
best fits your brain as necessary.

For more information about the API of a ``Configurator`` object, see
:class:`repoze.bfg.configuration.Configurator` .  The equivalent ZCML
declaration tags are introduced in narrative documentation chapters as
necessary.

For more information about :term:`traversal`, see
:ref:`traversal_chapter`.

For more information about :term:`view configuration`, see
:ref:`views_chapter`.

