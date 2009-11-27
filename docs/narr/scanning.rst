.. _scanning_chapter:

Configuration, Decorations And Code Scanning
============================================

:mod:`repoze.bfg` provides a number of "modes" for performing
application configuration.  These modes can be used interchangeably or
even combined, as necessary.

For example:

- A ``<view>`` :term:`ZCML declaration` adds a :term:`view
  configuration` to the current :term:`application registry`.

- A call to the ``add_view`` method of a :term:`Configurator` ZCML
  adds a :term:`view configuration` to the current :term:`application
  registry`.

- the ``@bfg_view`` :term:`decorator` adds :term:`configuration
  decoration` to the function or method it decorates.  This particular
  decoration can result in a :term:`view configuration` to be added to
  the current :term:`application registry` if the package the code
  lives in is run through a :term:`scan`.

Decorations and Code Scanning
-----------------------------

To lend more *locality of reference* to a :term:`configuration
declaration`, :mod:`repoze.bfg` allows you to insert
:term:`configuration decoration` statements very close to code that is
referred to by the declaration itself.

The mere existence of configuration decoration doesn't cause any
configuration registration to be made.  Before they have any effect on
the configuration of a :mod:`repoze.bfg` application, a configuration
decoration within application code must be found through a process
known as *scanning*.

:mod:`repoze.bfg` is willing to :term:`scan` a module or a package and
its subpackages for decorations when the ``scan`` method of a
:term:`Configurator` is invoked: scanning implies searching for
configuration declarations in a package and its subpackages.
:term:`ZCML` can also invoke a :term:`scan` via its ``<scan>``
directive.

The scanning machinery imports each module and subpackage in a package
or module recursively, looking for special attributes attached to
objects defined within a module.  These special attributes are
typically attached to code via the use of a :term:`decorator`.  For
example, the :class:`repoze.bfg.view.bfg_view` decorator can be
attached to a function or instance method:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from webob import Response

   @bfg_view(name='hello', request_method='GET')
   def hello(request):
       return Response('Hello')

The ``@bfg_view`` decorator above simply adds an attribute to the
``hello`` function, making it available for a :term:`scan` to find it
later.

Once scanning is invoked, and :term:`configuration decoration` is
found by the scanner, a set of calls are made to a :term:`Configurator`
on behalf of the developer: these calls represent the intent of the
configuration decoration.  In the example above, this is best
represented as the scanner translating the arguments to ``@bfg_view``
into a call to the ``add_view`` method of a :term:`Configurator`,
effectively:

.. code-block:: python
   :linenos:

   config.add_view(hello, name='hello', request_method='GET')

Scanning for :term:`configuration decoration` is performed via the
``scan`` method of a :term:`Configurator` or via a ``<scan>``
:term:`ZCML declaration`.  See :ref:`config_mode_equivalence` for
examples.

.. _config_mode_equivalence:

Configuration Mode Equivalence
------------------------------

A combination of imperative configuration, declarative configuration
via ZCML and scanning can be used to configure any application.  Each
of the below examples produces the same application configuration.

.. topic:: Completely Imperative Configuration

   .. code-block:: python
      :linenos:

      # helloworld.py

      from repoze.bfg.view import bfg_view
      from webob import Response
     
      def hello(request):
          return Response('Hello')

      if __name__ == '__main__':
          from repoze.bfg.configuration import Configurator
          config = Configurator()
          config.add_view(hello, name='hello', request_method='GET')

.. topic:: Configuration via ZCML

   .. code-block:: python
      :linenos:

      # helloworld.py

      from webob import Response
     
      def hello(request):
          return Response('Hello')

      if __name__ == '__main__':
          from repoze.bfg.configuration import Configurator
          config = Configurator()
          config.load_zcml('configure.zcml')

   .. code-block:: xml
      :linenos:

      <configure xmlns="http://namespaces.repoze.org">

        <!-- configure.zcml -->

        <include package="repoze.bfg.includes"/>

          <view name="hello"
                request_method="GET"/>

      </configure>

.. topic:: Using Decorations (Imperatively Starting a Scan)

   .. code-block:: python
      :linenos:

      from repoze.bfg.view import bfg_view
      from webob import Response
     
      @bfg_view(name='hello', request_method='GET')
      def hello(request):
          return Response('Hello')

      if __name__ == '__main__':
          from repoze.bfg.configuration import Configurator
          config = Configurator()
          config.scan()

.. topic:: Using Decorations (Starting a Scan via ZCML)

   .. code-block:: python
      :linenos:

      # helloworld.py

      from repoze.bfg.view import bfg_view
      from webob import Response
     
      @bfg_view(name='hello', request_method='GET')
      def hello(request):
          return Response('Hello')

      if __name__ == '__main__':
          from repoze.bfg.configuration import Configurator
          config = Configurator()
          config.load_zcml('configure.zcml')

   .. code-block:: xml
      :linenos:

      <configure xmlns="http://namespaces.repoze.org">

        <!-- configure.zcml -->

        <include package="repoze.bfg.includes"/>
        <scan package="."/>

      </configure>

