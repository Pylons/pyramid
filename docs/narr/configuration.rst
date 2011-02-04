.. index::
   single: application configuration

.. _configuration_narr:

Application Configuration 
=========================

Each deployment of an application written using :app:`Pyramid` implies a
specific *configuration* of the framework itself.  For example, an
application which serves up MP3 files for your listening enjoyment might plug
code into the framework that manages song files, while an application that
manages corporate data might plug in code that manages accounting
information.  The way in which code is plugged in to :app:`Pyramid` for a
specific application is referred to as "configuration".

Most people understand "configuration" as coarse settings that inform the
high-level operation of a specific application deployment.  For instance,
it's easy to think of the values implied by a ``.ini`` file parsed at
application startup time as "configuration".  :app:`Pyramid` extends this
pattern to application development, using the term "configuration" to express
standardized ways that code gets plugged into a deployment of the framework
itself.  When you plug code into the :app:`Pyramid` framework, you are
"configuring" :app:`Pyramid` to create a particular application.

.. index::
   single: imperative configuration

.. _imperative_configuration:

Imperative Configuration
------------------------

Here's one of the simplest :app:`Pyramid` applications, configured
imperatively:

.. code-block:: python
   :linenos:

   from paste.httpserver import serve
   from pyramid.config import Configurator
   from pyramid.response import Response

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.add_view(hello_world)
       app = config.make_wsgi_app()
       serve(app, host='0.0.0.0')

We won't talk much about what this application does yet.  Just note that the
"configuration' statements take place underneath the ``if __name__ ==
'__main__':`` stanza in the form of method calls on a :term:`Configurator`
object (e.g. ``config.add_view(...)``).  These statements take place one
after the other, and are executed in order, so the full power of Python,
including conditionals, can be employed in this mode of configuration.

.. index::
   single: view_config
   single: configuration decoration
   single: code scanning

.. _decorations_and_code_scanning:

Configuration Decorations and Code Scanning
-------------------------------------------

A different mode of configuration gives more *locality of reference* to a
:term:`configuration declaration`.  It's sometimes painful to have all
configuration done in imperative code, because often the code for a single
application may live in many files.  If the configuration is centralized in
one place, you'll need to have at least two files open at once to see the
"big picture": the file that represents the configuration, and the file that
contains the implementation objects referenced by the configuration.  To
avoid this, :app:`Pyramid` allows you to insert :term:`configuration
decoration` statements very close to code that is referred to by the
declaration itself.  For example:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(name='hello', request_method='GET')
   def hello(request):
       return Response('Hello')

The mere existence of configuration decoration doesn't cause any
configuration registration to be performed.  Before it has any effect on the
configuration of a :app:`Pyramid` application, a configuration decoration
within application code must be found through a process known as a
:term:`scan`.

For example, the :class:`pyramid.view.view_config` decorator in the code
example above adds an attribute to the ``hello`` function, making it
available for a :term:`scan` to find it later.

A :term:`scan` of a :term:`module` or a :term:`package` and its subpackages
for decorations happens when the :meth:`pyramid.config.Configurator.scan`
method is invoked: scanning implies searching for configuration declarations
in a package and its subpackages.  For example:

.. topic:: Starting A Scan

   .. code-block:: python
      :linenos:

      from paste.httpserver import serve
      from pyramid.response import Response
      from pyramid.view import view_config
     
      @view_config()
      def hello(request):
          return Response('Hello')

      if __name__ == '__main__':
          from pyramid.config import Configurator
          config = Configurator()
          config.scan()
          app = config.make_wsgi_app()
          serve(app, host='0.0.0.0')

The scanning machinery imports each module and subpackage in a package or
module recursively, looking for special attributes attached to objects
defined within a module.  These special attributes are typically attached to
code via the use of a :term:`decorator`.  For example, the
:class:`~pyramid.view.view_config` decorator can be attached to a function or
instance method.

Once scanning is invoked, and :term:`configuration decoration` is found by
the scanner, a set of calls are made to a :term:`Configurator` on your
behalf: these calls replace the need to add imperative configuration
statements that don't live near the code being configured.

In the example above, the scanner translates the arguments to
:class:`~pyramid.view.view_config` into a call to the
:meth:`pyramid.config.Configurator.add_view` method, effectively:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.add_view(hello)

Declarative Configuration
-------------------------

A third mode of configuration can be employed when you create a
:app:`Pyramid` application named *declarative configuration*.  This mode uses
an XML language known as :term:`ZCML` to represent configuration statements
rather than Python.  ZCML is not built-in to Pyramid, but almost everything
that can be configured imperatively can also be configured via ZCML if you
install the :term:`pyramid_zcml` package.

