.. _configuration_narr:

Creating Your First :mod:`repoze.bfg` Application
=================================================

The majority of the logic in any web application is completely
application-specific.  For example, the body of a web page served by
one web application might be a representation of the contents of an
accounting ledger, while the content of of a web page served by
another might be a listing of songs.  These applications obviously
might not service the same set of customers.  However, both the
ledger-serving and song-serving applications can be written using
:mod:`repoze.bfg`, because :mod:`repoze.bfg` is a very general
*framework* which can be used to create all kinds of web
applications.

.. sidebar:: Frameworks vs. Libraries

   A *framework* differs from a *library* in one very important way:
   library code is always *called* by code that you write, while a
   framework always *calls* code that you write.  Using a set of
   libraries to create an application is often initially easier than
   using a framework to create an application, because the developer
   can choose to cede control to library code he has not authored
   selectively, making the resulting application easier to understand
   for the original developer.  When using a framework, the developer
   is typically required to cede a greater portion of control to code
   he has not authored: code that resides in the framework itself.
   You needn't use a framework at all to create a web application
   using Python.  A rich set of libraries exists for the platform
   which you can snap together to effectively create your own
   framework.  In practice, however, using an existing framework to
   create an application is often more practical than rolling your own
   via a set of libraries if the framework provides a set of
   facilities and assumptions that fit your application domain's
   requirements.  :mod:`repoze.bfg` is a framework that fits a large
   set of assumptions in the domain of web application creation.

As a framework, the primary job of :mod:`repoze.bfg` is to make it
easier for a developer to create an arbitrary web application.  From
the perspective of the authors of :mod:`repoze.bfg`, each deployment
of an application written using :mod:`repoze.bfg` implies a specific
*configuration* of the framework itself.  For example, a song-serving
application might plug code into the framework that manages songs,
while the ledger- serving application might plug code that manages
accounting information.  :mod:`repoze.bfg` refers to the way in which
code is plugged in to it for a specific deployment as "configuration".

Many people think of "configuration" as coarse knobs that inform the
high-level operation of a specific application deployment; for
instance, it's easy to think of the values implied by a ``.ini`` file
that is read at application startup time as "configuration".
:mod:`repoze.bfg` goes a bit further than that, because it uses
standardized ways of plugging code into the framework, and these can
be expressed via configuration as well.  Thus, when you plug code into
it in various ways, you are indeed "configuring" :mod:`repoze.bfg` for
the purpose of creating an application deployment.

From the perspective of a developer creating an application using
:mod:`repoze.bfg`, performing the tasks that :mod:`repoze.bfg` calls
"configuration" might alternately be referred to as "wiring" or
"plumbing". :mod:`repoze.bfg` refers to it as "configuration", for
lack of a more fitting term.

There are a number of different mechanisms you may use to configure
:mod:`repoze.bfg` to create an application: *imperative* configuration
and *declarative* configuration.  We'll examine both modes in the
sections which follow.

.. _helloworld_imperative:

Hello World, Configured Imperatively
------------------------------------

Experienced Python programmers may find the "imperative" configuration
mechanism fits the way they already do things. This is the configuration
mode in which developers cede the least amount of control to the framework.
Because of this, it is also the easiest configuration mode to understand.

Here's the simplest :mod:`repoze.bfg` application, configured
imperatively:

.. code-block:: python
   :linenos:

   from webob import Response
   from wsgiref import simple_server
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.add_view(hello_world)
       app = config.make_wsgi_app()
       simple_server.make_server('', 8080, app).serve_forever()

When this code is inserted into a Python script named
``helloworld.py`` and executed by a Python interpreter which has the
:mod:`repoze.bfg` software installed, this code starts an HTTP server
on port 8080.  When visited by a user agent on any applicable URL, the
server simply serves serves up the words "Hello world!" with the HTTP
response values ``200 OK`` as a response code and a ``Content-Type``
header value of ``text/plain``.

.. warning::

   If you are using Python 2.4 (as opposed to Python 2.5 or 2.6), you
   will need to install the ``wsgiref`` package for its import to
   work.  Use ``easy_install wsgiref`` to get it installed.

Let's examine this program piece-by-piece.

Imports
~~~~~~~

The above script defines the following set of imports:

.. code-block:: python
   :linenos:

   from webob import Response
   from wsgiref import simple_server
   from repoze.bfg.configuration import Configurator

:mod:`repoze.bfg` uses the :term:`WebOb` library as the basis for its
:term:`request` and :term:`response` objects.  The script uses the
``webob.Response`` class later in the script to create a
:term:`response` object.

Like many other Python web frameworks, :mod:`repoze.bfg` uses the
:term:`WSGI` protocol as a basis between an application and a web
server.  The ``wsgiref.simple_server`` server is used in this example
as a WSGI server, purely for convenience.  :mod:`repoze.bfg`
applications can be served via any WSGI server.

The script also imports the ``Configurator`` class from the
``repoze.bfg.configuration`` module.  This class is used to configure
:mod:`repoze.bfg` for a particular application.  An instance of this
class provides methods which help configure various parts of
:mod:`repoze.bfg` for a given application deployment.

View Declaration
~~~~~~~~~~~~~~~~

The above script, beneath its set of imports, defines a function named
``hello_world``.

.. code-block:: python
   :linenos:

   def hello_world(request):
       return Response('Hello world!')

This function accepts a single argument (``request``), and returns an
instance of the ``webob.Response`` class.  The string ``'Hello
world!'`` is passed to the ``Response`` constructor as the *body* of
the response.

Such a function is known as a :term:`view callable`.  View callables
in a "real" :mod:`repoze.bfg` application are often functions which
accept a request and return a response.  A view callable can be
represented via another type of object, like a class or an instance,
but for our purposes here, a function serves us well.

A :term:`view callable` is invoked by the :mod:`repoze.bfg` web
framework when a request "matches" its :term:`view configuration`.  It
is called with a :term:`request` object, which is a representation of
an HTTP request sent by a remote user agent.  A view callable is
required to return a :term:`response` object because a response object
has all the information necessary to formulate an actual HTTP
response; this object is then converted to text and sent back to the
requesting user agent.

The view callable defined by the script does nothing but return a
response with the body ``Hello world!``.

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
       config.add_view(hello_world)
       app = config.make_wsgi_app()
       simple_server.make_server('', 8080, app).serve_forever()

Let's break this down this line-by-line:

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
``repoze.bfg.configuration.Configurator`` class.  The resulting
``config`` object represents an API which the script uses to configure
this particular :mod:`repoze.bfg` application.  An instance of the
``Configurator`` class is a wrapper object which mutates an
:term:`application registry` as its methods are called.  

.. note::

   The ``Configurator`` is not itself an :term:`application registry`.
   It is only a mechanism used to configure an application registry.
   The underlying application registry object being configured by a
   ``Configurator`` is available as its ``registry`` attribute.

.. code-block:: python
   :linenos:

       config.add_view(hello_world)

This line calls the ``add_view`` method of the ``Configurator``.  The
``add_view`` method of a configurator creates a :term:`view
configuration` within the :term:`application registry`.  A :term:`view
configuration` represents a set of circumstances which must be true
for a particular :term:`view callable` to be called when a WSGI
request is handled by :mod:`repoze.bfg`.

The first argument of the configurator's ``add_view`` method must
always be a reference to the :term:`view callable` that is meant to be
invoked when the view configuration implied by the remainder of the
arguments passed to ``add_view`` is found to "match" during a request.
This particular invocation of the ``add_view`` method passes no other
arguments; this implies that there are no circumstances which would
limit the applicability of this view callable.  The view configuration
implied by this call to ``add_view`` thus will match during *any*
request.  Since our ``hello_world`` view callable returns a Response
instance with a body of ``Hello world!```, this means, in the
configuration implied by the script, that any URL visited by a user
agent to a server running this application will receive the greeting
``Hello world!``.

WGSI Application Creation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :linenos:

       app = config.make_wsgi_app()

After configuring a single view, the script creates a WSGI
*application* via the ``config.make_wsgi_app`` method.  A call to
``make_wsgi_app`` implies that all "configuration" is finished
(meaning all method calls to the configurator which set up views, and
various other configuration settings have been performed).  The
``make_wsgi_app`` method returns a :term:`WSGI` application object
that can be used by any WSGI server to present an application to a
requestor.

The :mod:`repoze.bfg` application object, in particular, is an
instance of the ``repoze.bfg.router.Router`` class.  It has a
reference to the :term:`application registry` which resulted from
method calls to the configurator used to configure it.  The Router
consults the registry to obey the policy choices made by a single
application.  These policy choices were informed by method calls to
the ``Configurator`` made earlier; in our case, the only policy choice
made was a single call to the ``add_view`` method, telling our
application that it should unconditionally serve up the
``hello_world`` view callable to any requestor.

WSGI Application Serving
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :linenos:

       simple_server.make_server('', 8080, app).serve_forever()

Finally, we actually serve the application to requestors by starting
up a WSGI server.  We happen to use the ``wsgiref.simple_server`` WSGI
server implementation, telling it to serve the application on TCP port
8080, and we pass it the ``app`` object (an instance of
``repoze.bfg.router.Router``) as the application we wish to serve.  We
then call the ``serve_forever`` method of the result to
``simple_server.make_server``, causing the server to start listening
on the TCP port.  It will serve requests forever, or at least until we
stop it by killing the process which runs it.

Conclusion
~~~~~~~~~~

Our hello world application is the simplest possible :mod:`repoze.bfg`
application, configured "imperatively".  We can see a good deal of
what's going on "under the hood" when we configure a :mod:`repoze.bfg`
application imperatively.  However, another mode of configuration
exists named *declarative* configuration.

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
   from wsgiref import simple_server
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator(zcml_file='configure.zcml')
       app = config.make_wsgi_app()
       simple_server.make_server('', 8080, app).serve_forever()

In a file named ``configure.zcml`` in the same directory as the
previously created ``helloworld.py``:

.. code-block:: xml
   :linenos:

    <configure xmlns="http://namespaces.repoze.org/bfg">

      <include package="repoze.bfg.includes" />

      <view
         view="helloworld.hello_world"
         />

    </configure>

This pair of files forms an application functionally equivalent to the
application we created earlier.  Let's examine the differences between
the code described in :ref:`helloworld_imperative`" and the code
above.

In :ref:`helloworld_imperative_appconfig`, we had the following lines
within the ``if __name__ == '__main__'`` section of ``helloworld.py``:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.add_view(hello_world)
       app = config.make_wsgi_app()
       simple_server.make_server('', 8080, app).serve_forever()

In our "declarative" code, we've added a ``zcml_file`` argument to the
``Configurator`` constructor's argument list with the value
``configure.zcml``, and we've removed the line which reads
``config.add_view(hello_world)``, so that it now reads as:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator(zcml_file='configure.zcml')
       app = config.make_wsgi_app()
       simple_server.make_server('', 8080, app).serve_forever()

Everything else is much the same.

The ``zcml_file`` argument to the ``Configurator`` constructor tells
the configurator to load configuration declarations from the
``configure.zcml`` file which sits next to ``helloworld.py``.  Let's
take a look at the ``configure.zcml`` file now:

.. code-block:: xml
   :linenos:

    <configure xmlns="http://namespaces.repoze.org/bfg">

      <include package="repoze.bfg.includes" />

      <view
         view="helloworld.hello_world"
         />

    </configure>

The ``<configure>`` Tag
~~~~~~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains this bit of XML:

.. code-block:: xml
   :linenos:

    <configure xmlns="http://namespaces.repoze.org/bfg">
       ... body ...
    </configure>

Because :term:`ZCML` is XML, and because XML requires a single root
tag for each document, every ZCML file used by :mod:`repoze.bfg` must
contain a ``<configure>`` container tag, which acts as the root XML
tag.  Usually, the start tag of the ``<configure>`` container tag has
a default namespace associated with it. In the file above, the
``xmlns="http:/namepaces.repoze.org/bfg"`` attribute of the
``configure`` start tag names the default XML namespace, which is
``http://namespaces.repoze.org/bfg``.  See
:ref:`word_on_xml_namespaces` for more information about XML
namespaces.

The ``<include>`` Tag
~~~~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains this bit of XML within the
root tag:

.. code-block:: xml
   :linenos:

      <include package="repoze.bfg.includes" />

This singleton (self-closing) tag instructs ZCML to load a ZCML file
from the Python package with the :term:`dotted Python name`
``repoze.bfg.includes``, as specified by its ``package`` attribute.
This particular ``<include>`` declaration is required because it
actually allows subseqent declaration tags (such as ``<view>``, which
we'll see shortly) to be recognized.  The ``<include>`` tag
effectively just includes another ZCML file; this causes its
declarations to be executed.  In this case, we want to load the
declarations from the file named ``configure.zcml`` within the
``repoze.bfg.includes`` Python package.  We know we want to load the
``configure.zcml`` from this package because ``configure.zcml`` is the
default value for another attribute of the ``<include>`` tag named
``file``.  We could have spelled the include tag more verbosely, but
equivalently as:

.. code-block:: xml
   :linenos:

      <include package="repoze.bfg.includes" 
               file="configure.zcml"/>

The ``<include>`` tag that includes the ZCML statements implied by the
``configure.zcml`` file from the Python package named
``repoze.bfg.includes`` is basically required to come before any other
named declaration in an application's ``configure.zcml``.  If it is
not included, subsequent declaration tags will fail to be recognized,
and the configuration system will generate a traceback.  However, the
``<include package="repoze.bfg.includes"/>`` tag needs to exist only
in a "top-level" ZCML file, it needn't also exist in ZCML files
*included by* a top-level ZCML file.

The ``<view>`` Tag
~~~~~~~~~~~~~~~~~~

The ``configure.zcml`` ZCML file contains this bit of XML after the
``<include>`` tag, but within the root tag:

.. code-block:: xml
   :linenos:

      <view
         view="helloworld.hello_world"
         />

This ``<view>`` declaration tag directs :mod:`repoze.bfg` to create a
:term:`view configuration`.  This ``<view>`` tag has an attribute (the
attribute is also named ``view``), which points at a :term:`dotted
Python name`, referencing the ``hello_world`` function defined within
the ``helloworld`` package.  This tag is functionally equivalent to a
line we saw previously in our imperatively-configured application:

.. code-block:: python
   :linenos:

       config.add_view(hello_world)

The ``<view>`` declaration tag effectively invokes the ``add_view``
method of the ``Configurator`` object on your behalf.  Various
attributes can be specified on the ``<view>`` tag which influence the
:term:`view configuration` it creates.

The ``<view>`` tag is an example of a :mod:`repoze.bfg` declaration
tag.  Other such tags include ``<route>``, ``<scan>``, ``<notfound>``,
``<forbidden>``, and others.  All of these tags are effectively
"macros" which call methods on the ``Configurator`` object on your
behalf.

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
application, a ``ConfigurationError`` will be raised when you attempt
to start the application with information about which tags might have
conflicted.

.. _word_on_xml_namespaces:

A Word On XML Namespaces
~~~~~~~~~~~~~~~~~~~~~~~~

Using the ``http://namespaces.repoze.org/bfg`` namespace as the
default XML namespace isn't strictly necessary; you can use a
different default namespace as the default.  However, if you do, the
declaration tags which are defined by :mod:`repoze.bfg` such as the
``<view>`` declaration tag will need to be defined in such a way that
the XML parser that :mod:`repoze.bfg` uses knows which namespace the
:mod:`repoze.bfg` tags are associated with.  For example, the
following files are all completely equivalent:

.. topic:: Use of A Non-Default XML Namespace

  .. code-block:: xml
     :linenos:

      <configure xmlns="http://namespaces.zope.org/zope"
                 xmlns:bfg="http://namespaces.repoze.org/bfg">

        <include package="repoze.bfg.includes" />

        <bfg:view
           view="helloworld.hello_world"
           />

      </configure>

.. topic:: Use of A Per-Tag XML Namespace Without A Default XML Namespace

  .. code-block:: xml
     :linenos:

      <configure>

        <include package="repoze.bfg.includes" />

        <view xmlns="http://namespaces.repoze.org/bfg"
           view="helloworld.hello_world"
           />

      </configure>

For more information about XML namespaces, see `this older, but simple
XML.com article <http://www.xml.com/pub/a/1999/01/namespaces.html>`_.

Conclusions
-----------

:mod:`repoze.bfg` allows an application to perform configuration tasks
either imperatively or declaratively.  You can choose the mode that
best fits your brain as necessary.

For more information about the API of the ``Configurator`` object, see
:ref:`configuration_module`.  The equivalent ZCML declaration tags are
introduced in narrative documentation chapters as necessary.

