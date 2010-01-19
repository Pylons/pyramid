.. index::
   single: application configuration

.. _configuration_narr:

Application Configuration 
=========================

Each deployment of an application written using :mod:`repoze.bfg`
implies a specific *configuration* of the framework itself.  For
example, an application which serves up MP3s for user consumption
might plug code into the framework that manages songs, while an
application that manages corporate data might plug in code that
manages accounting information.  :mod:`repoze.bfg` refers to the way
in which code is plugged in to it for a specific application as
"configuration".

Most people understand "configuration" as coarse settings that inform
the high-level operation of a specific application deployment.  For
instance, it's easy to think of the values implied by a ``.ini`` file
parsed at application startup time as "configuration".
:mod:`repoze.bfg` extends this pattern to application development,
using the term "configuration" to express standardized ways that code
gets plugged into a deployment of the framework itself.  When you plug
code into the :mod:`repoze.bfg` framework, you are "configuring"
:mod:`repoze.bfg` for the purpose of creating a particular application
deployment.

There are two different mechanisms you may use to configure
:mod:`repoze.bfg` to create an application: *imperative* configuration
and *declarative* configuration.  We'll examine both modes in the
sections which follow.

.. index::
   single: imperative configuration

.. _imperative_configuration:

Imperative Configuration
------------------------

Experienced Python programmers might find that performing
configuration "imperatively" fits their brain best. This is the
configuration mode in which a developer cedes the least amount of
control to the framework; it's "imperative" because you express the
configuration directly in Python code, and you have the full power of
Python at your disposal as you issue configuration statements.

Here's one of the simplest :mod:`repoze.bfg` applications, configured
imperatively:

.. code-block:: python
   :linenos:

   from webob import Response
   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

We won't talk much about what this application does yet.  Just note
that the "configuration' statements take place underneath the ``if
__name__ == '__main__':`` stanza in the form of method calls on a
:term:`Configurator` object (e.g. ``config.begin()``,
``config.add_view(...)``, and ``config.end()``.  These statements take
place one after the other, and are executed in order, so the full
power of Python, including conditionals, can be employed in this mode
of configuration.

.. index::
   single: declarative configuration

.. _declarative_configuration:

Declarative Configuration
-------------------------

A :mod:`repoze.bfg` application can be alternately be configured
"declaratively", if so desired.  Declarative configuration relies on
*declarations* made external to the code in a configuration file
format named :term:`ZCML` (Zope Configuration Markup Language), an XML
dialect.

A :mod:`repoze.bfg` application configured declaratively requires not
one, but two files: a Python file and a :term:`ZCML` file.

In a file named ``helloworld.py``:

.. code-block:: python
   :linenos:

   from webob import Response
   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.load_zcml('configure.zcml')
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

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
application we created earlier in :ref:`imperative_configuration`.
Let's examine the differences between that code listing and the code
above.

In :ref:`imperative_configuration`, we had the following lines within
the ``if __name__ == '__main__'`` section of ``helloworld.py``:

.. code-block:: python
   :linenos:

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.end()
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

In our "declarative" code, we've removed the call to ``add_view`` and
replaced it with a call to the
:meth:`repoze.bfg.configuration.Configurator.load_zcml` method so that
it now reads as:

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
to load configuration declarations from the file named
``configure.zcml`` which sits next to ``helloworld.py`` on the
filesystem.  Let's take a look at that ``configure.zcml`` file again:

.. code-block:: xml
   :linenos:

   <configure xmlns="http://namespaces.repoze.org/bfg">

      <include package="repoze.bfg.includes" />

      <view
         view="helloworld.hello_world"
         />

   </configure>

Note that this file contains some XML, and that the XML contains a
``<view>`` :term:`configuration declaration` tag that references a
:term:`dotted Python name`.  This dotted name refers to the
``hello_world`` function that lives in our ``helloworld`` Python
module.

This ``<view>`` declaration tag performs the same function as the
``add_view`` method that was employed within
:ref:`imperative_configuration`.  In fact, the ``<view>`` tag is
effectively a "macro" which calls the
:meth:`repoze.bfg.configuration.Configurator.add_view` method on your
behalf.

The ``<view>`` tag is an example of a :mod:`repoze.bfg` declaration
tag.  Other such tags include ``<route>``, ``<scan>``, ``<notfound>``,
``<forbidden>``, and others.  Each of these tags is effectively a
"macro" which calls methods of a
:class:`repoze.bfg.configuration.Configurator` object on your behalf.

Essentially, using a :term:`ZCML` file and loading it from the
filesystem allows us to put our configuration statements within this
XML file rather as declarations, rather than representing them as
method calls to a :term:`Configurator` object.  Otherwise, declarative
and imperative configuration are functionally equivalent.

Using declarative configuration has a number of benefits, the primary
benefit being that applications configured declaratively can be
*overridden* and *extended* by third parties without requiring the
third party to change application code.  If you want to build a
framework or an extensible application, using declarative
configuration is a good idea.

Declarative configuration has an obvious downside: you can't use
plain-old-Python syntax you probably already know and understand to
configure your application; instead you need to use :term:`ZCML`.

.. index::
   single: ZCML conflict detection

ZCML Conflict Detection
~~~~~~~~~~~~~~~~~~~~~~~

A minor additional feature of ZCML is *conflict detection*.  If you
define two declaration tags within the same ZCML file which logically
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
application, an error will be raised when you attempt to start the
application.  This error will contain information about which tags
might have conflicted.

.. index::
   single: bfg_view
   single: ZCML view directive
   single: configuration decoration
   single: code scanning

.. _decorations_and_code_scanning:

Configuration Decorations and Code Scanning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alternate mode of declarative configuration lends more *locality of
reference* to a :term:`configuration declaration`.  It's sometimes
painful to have all configuration done in ZCML, or even in imperative
code, because you may need to have two files open at once to see the
"big picture": the file that represents the configuration, and the
file that contains the implementation objects referenced by the
configuration.  To avoid this, :mod:`repoze.bfg` allows you to insert
:term:`configuration decoration` statements very close to code that is
referred to by the declaration itself.  For example:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from webob import Response

   @bfg_view(name='hello', request_method='GET')
   def hello(request):
       return Response('Hello')

The mere existence of configuration decoration doesn't cause any
configuration registration to be made.  Before they have any effect on
the configuration of a :mod:`repoze.bfg` application, a configuration
decoration within application code must be found through a process
known as a :term:`scan`.

The :class:`repoze.bfg.view.bfg_view` decorator above adds an
attribute to the ``hello`` function, making it available for a
:term:`scan` to find it later.

:mod:`repoze.bfg` is willing to :term:`scan` a module or a package and
its subpackages for decorations when the
:meth:`repoze.bfg.configuration.Configurator.scan` method is invoked:
scanning implies searching for configuration declarations in a package
and its subpackages.  For example:

.. topic:: Imperatively Starting A Scan

   .. code-block:: python
      :linenos:

      from paste.httpserver import serve
      from repoze.bfg.view import bfg_view
      from webob import Response
     
      @bfg_view()
      def hello(request):
          return Response('Hello')

      if __name__ == '__main__':
          from repoze.bfg.configuration import Configurator
          config = Configurator()
          config.begin()
          config.scan()
          config.end()
          app = config.make_wsgi_app()
          serve(app, host='0.0.0.0')

:term:`ZCML` can also invoke a :term:`scan` via its ``<scan>``
directive.  If a ZCML file is processed that contains a scan
directive, the package the ZCML file points to is scanned.

.. topic:: Declaratively Starting a Scan

   .. code-block:: python
      :linenos:

      # helloworld.py

      from paste.httpserver import serve
      from repoze.bfg.view import bfg_view
      from webob import Response
     
      @bfg_view()
      def hello(request):
          return Response('Hello')

      if __name__ == '__main__':
          from repoze.bfg.configuration import Configurator
          config = Configurator()
          config.begin()
          config.load_zcml('configure.zcml')
          config.end()
          app = config.make_wsgi_app()
          serve(app, host='0.0.0.0')

   .. code-block:: xml
      :linenos:

      <configure xmlns="http://namespaces.repoze.org">

        <!-- configure.zcml -->

        <include package="repoze.bfg.includes"/>
        <scan package="."/>

      </configure>

The scanning machinery imports each module and subpackage in a package
or module recursively, looking for special attributes attached to
objects defined within a module.  These special attributes are
typically attached to code via the use of a :term:`decorator`.  For
example, the :class:`repoze.bfg.view.bfg_view` decorator can be
attached to a function or instance method.

Once scanning is invoked, and :term:`configuration decoration` is
found by the scanner, a set of calls are made to a
:term:`Configurator` on behalf of the developer: these calls represent
the intent of the configuration decoration.

In the example above, this is best represented as the scanner
translating the arguments to :class:`repoze.bfg.view.bfg_view` into a
call to the :meth:`repoze.bfg.configuration.Configurator.add_view`
method, effectively:

.. ignore-next-block
.. code-block:: python

   config.add_view(hello)

Which Mode Should I Use?
------------------------

A combination of imperative configuration, declarative configuration
via ZCML and scanning can be used to configure any application.  They
are not mutually exclusive.

The :mod:`repoze.bfg` authors often recommend using mostly declarative
configuration, because it's the more traditional form of configuration
used in :mod:`repoze.bfg` applications, it can be overridden and
extended by third party deployers, and there are more examples for it
"in the wild".

However, imperative mode configuration can be simpler to understand,
and the framework is not "opinionated" about the choice.  This book
presents examples in both styles, mostly interchangeably.  You can
choose the mode that best fits your brain as necessary.
