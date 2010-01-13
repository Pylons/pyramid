.. _configuration_narr:

Creating Your First :mod:`repoze.bfg` Application
=================================================

We will walk through the creation of a tiny :mod:`repoze.bfg`
application in this chapter and explain in more detail how the
application works.

But before we dive into the code, a short introduction to
:term:`traversal` is required.

.. index::
   pair: traversal; introduction

.. _traversal_intro:

An Introduction to Traversal
----------------------------

In order for a web application to perform any useful action, it needs
some way of finding and invoking code based on parameters present in
the :term:`request`.  :term:`traversal` is a mechanism that plays a
part in finding code when a request enters the system.

:term:`traversal` is the act of finding a :term:`context` and a
:term:`view name` by walking over a graph of objects starting from a
:term:`root` object, using the :term:`request` object as a source of
path information.

:term:`view` code is the code in an application that responds to a
request.  Traversal doesn't actually locate :term:`view` code by
itself: it only locates a :term:`context` and a :term:`view name`.
But the combination of the :term:`context` object and the :term:`view
name` found via traversal is used by a separate :mod:`repoze.bfg`
subsystem (the "view lookup" subsystem) to find a :term:`view
callable` later in the same request.  A view callable is a specific
bit of code that receives a :term:`request` and which returns a
:term:`response`.

.. note::

   Another distinct mode known as :term:`URL dispatch` can alternately
   be used to find a view callable based on a URL.  However, the
   application we're going to write uses only :term:`traversal`.

The ``PATH_INFO`` portion of a URL is the data following the hostname
and port number, but before any query string elements or fragments,
for example the ``/a/b/c`` portion of the URL
``http://example.com/a/b/c?foo=1``. 

Traversal treats the ``PATH_INFO`` segment of a URL as a sequence of
path segments.  For example, the ``PATH_INFO`` string ``/a/b/c`` is
treated as the sequence ``['a', 'b', 'c']``.  Traversal pops the first
element (``a``) from the segment sequence and attempts to use it as a
lookup key into an *object graph* supplied by our application.  If
that succeeeds, the :term:`context` temporarily becomes the object
found via that lookup.  Then the next segment (``b``) is popped from
the sequence, and the object graph is queried for that segment; if
that lookup succeeds, the :term:`context` becomes that object.  This
process continues until the path segment sequence is exhausted or any
lookup for a name in the sequence fails.

As we previously mentioned, the results of a :term:`traversal` include
a :term:`context` and a :term:`view name`.  The :term:`view name` is
the *first* URL path segment in the set of ``PATH_INFO`` segments
"left over" in the path segment list popped by :term:`traversal`.  It
will be the empty string (``''``) if no segments remain.  The
circumstance where the :term:`view name` is the empty string
represents that the :term:`default view` for a :term:`context` should
be invoked.

If the :term:`view name` is *not* the empty string, it means that
traversal "ran out" of nodes in the *object graph* before it finished
exhausting all the path segments implied by the URL path segments.  In
this case, because the :term:`view name` is non-empty, a *non-default*
view callable will be invoked.

This description of traversal is not comprehensive: it's tailored
towards understand the sample application we're about to create; we'll
cover traversal in more detail in the :term:`traversal_chapter`.

.. note::

   A detailed analogy of how :mod:`repoze.bfg` :term:`traversal` works
   is available within the chapter section entitled
   :ref:`traversal_behavior`.  If you're a "theory-first" person, you
   might choose to read this to augment your understanding of
   traversal while diving into the code that follows, but it's not
   necessary if you're willing to "go with the flow".

.. index::
   single: helloworld

.. _helloworld_imperative:

Hello World, Goodbye World (Imperative)
---------------------------------------

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
       serve(app, host='0.0.0.0')

When this code is inserted into a Python script named
``helloworld.py`` and executed by a Python interpreter which has the
:mod:`repoze.bfg` software installed, an HTTP server is started on
port 8080.  When port 8080 is visited by a user agent on the root URL
(``/``), the server will simply serve up the text "Hello world!" with
the HTTP response values ``200 OK`` as a response code and a
``Content-Type`` header value of ``text/plain``.  But for reasons
we'll better understand shortly, when visited by a user agent on the
URL ``/goodbye``, the server will serve up "Goodbye world!"
 
Our application's :term:`root` object is the *default* root object
used when one isn't otherwise specified in application configuration.
The default root object has no children.  

.. note::

   In a "real" traversal-based :mod:`repoze.bfg` application, we'd
   pass a ``root_factory`` to the ``Configurator`` object's
   constructor, which would provide our application with a custom root
   object instead of using the :mod:`repoze.bfg` default root object.
   Supplying a custom ``root_factory`` is how you provide a custom
   *object graph* to :mod:`repoze.bfg`.  However, because our
   application is so simple, we don't need a custom root object here.

In a more complex :mod:`repoze.bfg` application there will be many
:term:`context` objects to which URLs might resolve.  However, in this
toy application, effectively there is only ever one context: the
:term:`root` object.  This is because the object graph of our hello
world application is very simple: there's exactly one object in our
graph; the default root object.

We have only a single :term:`default view` registered (the
registration for the ``hello_world`` view callable).  Due to this set
of circumstances, you can consider the sole possible URL that will
resolve to a :term:`default view` in this application the root URL
``'/'``.  It is the only URL that will resolve to the :term:`view
name` of ``''`` (the empty string).

We have only a single view registered for the :term:`view name`
``goodbye`` (the registration for the ``goodbye_world`` view
callable).  Due to this set of circumstances, you can consider the
sole possible URL that will resolve to the ``goodbye_world`` in this
application the URL ``'/goodbye'`` because it is the only URL that
will result in the :term:`view name` of ``goodbye`` after traversal.

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
as a WSGI server for convenience, as ``Paste`` is a dependency of
:mod:`repoze.bfg` itself.

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
       serve(app, host='0.0.0.0')

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
configuration` represents a :term:`view callable` which must be
invoked when a set of circumstances related to the :term:`request` is
true.  This "set of circumstances" is provided as one or more keyword
arguments to the ``add_view`` method, otherwise known as
:term:`predicate` arguments.

The line ``config.add_view(hello_world)`` registers the
``hello_world`` function as a view callable.  The ``add_view`` method
of a Configurator must be called with a view callable object as its
first argument, so the first argument passed is ``hello_world``
function we'd like to use as a view callable.  However, this line
calls ``add_view`` with a single default :term:`predicate` argument,
the ``name`` predicate with a value of the empty string (``''``),
meaning that we'd like :mod:`repoze.bfg` to invoke the ``hello_world``
view callable for any request for the :term:`default view` of an
object.

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
   dispatch mode of :mod:`repoze.bfg` (and similar schemes used by
   other frameworks, like :term:`Pylons` and :term:`Django`) which
   first uses an ordered routing lookup to resolve the request to a
   view callable by running it through a relatively-ordered series of
   URL path matches.  We're not really concerned about the finer
   details of :term:`URL dispatch` right now.  It's just useful to use
   for comparative purposes: the ordering of calls to
   :meth:`repoze.bfg.configuration.Configurator.add_view` is never
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
configuration (the view configuration that matches the most specific
set of predicates) is always invoked.

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

.. note::

   See :ref:`threadlocals_chapter` for a discussion about what it
   means for an application registry to be "current".

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
instance of a class representing a :mod:`repoze.bfg` :term:`router`.
It has a reference to the :term:`application registry` which resulted
from method calls to the configurator used to configure it.  The
router consults the registry to obey the policy choices made by a
single application.  These policy choices were informed by method
calls to the ``Configurator`` made earlier; in our case, the only
policy choices made were implied by two calls to the ``add_view``
method, telling our application that it should effectively serve up
the ``hello_world`` view callable to any user agent when it visits the
root URL, and the ``goodbye_world`` view callable to any user agent
when it visits the URL with the path info ``/goodbye``.

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
a good deal of what's going on "under the hood" when we configure a
:mod:`repoze.bfg` application imperatively.  However, another mode of
configuration exists named *declarative* configuration.

.. index::
   pair: helloworld; declarative
   single: helloworld

.. _helloworld_declarative:

Hello World, Goodbye World (Declarative)
----------------------------------------

:mod:`repoze.bfg` can be configured for the same "hello world"
application "declaratively", if so desired, as described in
:ref:`declarative_configuration`.

Create a file named ``helloworld.py``:

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

Create a file named ``configure.zcml`` in the same directory as the
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
:ref:`adding_configuration), the relative order of ``<view>`` tags in
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
declaratively.

References
----------

For more information about the API of a ``Configurator`` object, see
:class:`repoze.bfg.configuration.Configurator` .  The equivalent ZCML
declaration tags are introduced in narrative documentation chapters as
necessary.

For more information about :term:`traversal`, see
:ref:`traversal_chapter`.

For more information about :term:`view configuration`, see
:ref:`views_chapter`.

