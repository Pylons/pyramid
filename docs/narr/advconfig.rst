.. index::
   pair: advanced; configuration

.. _advconfig_narr:

Advanced Configuration
======================

To support application extensibility, the :app:`Pyramid` :term:`Configurator`
by default detects configuration conflicts and allows you to include
configuration imperatively from other packages or modules.  It also by default
performs configuration in two separate phases.  This allows you to ignore
relative configuration statement ordering in some circumstances.

.. index::
   pair: configuration; conflict detection

.. _conflict_detection:

Conflict Detection
------------------

Here's a familiar example of one of the simplest :app:`Pyramid` applications,
configured imperatively:

.. code-block:: python
   :linenos:

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.response import Response

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.add_view(hello_world)
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

When you start this application, all will be OK.  However, what happens if we
try to add another view to the configuration with the same set of
:term:`predicate` arguments as one we've already added?

.. code-block:: python
   :linenos:

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.response import Response

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

   if __name__ == '__main__':
       config = Configurator()

       config.add_view(hello_world, name='hello')

       # conflicting view configuration
       config.add_view(goodbye_world, name='hello')

       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

The application now has two conflicting view configuration statements.  When we
try to start it again, it won't start.  Instead we'll receive a traceback that
ends something like this:

.. code-block:: text
   :linenos:

   Traceback (most recent call last):
     File "app.py", line 12, in <module>
       app = config.make_wsgi_app()
     File "pyramid/config.py", line 839, in make_wsgi_app
       self.commit()
     File "pyramid/pyramid/config.py", line 473, in commit
       self._ctx.execute_actions()
     ... more code ...
   pyramid.exceptions.ConfigurationConflictError:
           Conflicting configuration actions
     For: ('view', None, '', None, <InterfaceClass pyramid.interfaces.IView>,
           None, None, None, None, None, False, None, None, None)
     Line 14 of file app.py in <module>: 'config.add_view(hello_world)'
     Line 17 of file app.py in <module>: 'config.add_view(goodbye_world)'

This traceback is trying to tell us:

- We've got conflicting information for a set of view configuration statements
  (The ``For:`` line).

- There are two statements which conflict, shown beneath the ``For:`` line:
  ``config.add_view(hello_world. 'hello')`` on line 14 of ``app.py``, and
  ``config.add_view(goodbye_world, 'hello')`` on line 17 of ``app.py``.

These two configuration statements are in conflict because we've tried to tell
the system that the set of :term:`predicate` values for both view
configurations are exactly the same.  Both the ``hello_world`` and
``goodbye_world`` views are configured to respond under the same set of
circumstances.  This circumstance, the :term:`view name` represented by the
``name=`` predicate, is ``hello``.

This presents an ambiguity that :app:`Pyramid` cannot resolve. Rather than
allowing the circumstance to go unreported, by default Pyramid raises a
:exc:`ConfigurationConflictError` error and prevents the application from
running.

Conflict detection happens for any kind of configuration: imperative
configuration or configuration that results from the execution of a
:term:`scan`.

.. _manually_resolving_conflicts:

Manually Resolving Conflicts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a number of ways to manually resolve conflicts: by changing
registrations to not conflict, by strategically using
:meth:`pyramid.config.Configurator.commit`, or by using an "autocommitting"
configurator.

The Right Thing
+++++++++++++++

The most correct way to resolve conflicts is to "do the needful": change your
configuration code to not have conflicting configuration statements.  The
details of how this is done depends entirely on the configuration statements
made by your application.  Use the detail provided in the
:exc:`ConfigurationConflictError` to track down the offending conflicts and
modify your configuration code accordingly.

If you're getting a conflict while trying to extend an existing application,
and that application has a function which performs configuration like this one:

.. code-block:: python
   :linenos:

   def add_routes(config):
       config.add_route(...)

Don't call this function directly with ``config`` as an argument.  Instead, use
:meth:`pyramid.config.Configurator.include`:

.. code-block:: python
   :linenos:

   config.include(add_routes)

Using :meth:`~pyramid.config.Configurator.include` instead of calling the
function directly provides a modicum of automated conflict resolution, with the
configuration statements you define in the calling code overriding those of the
included function.

.. seealso::

    See also :ref:`automatic_conflict_resolution` and
    :ref:`including_configuration`.

Using ``config.commit()``
+++++++++++++++++++++++++

You can manually commit a configuration by using the
:meth:`~pyramid.config.Configurator.commit` method between configuration calls.
For example, we prevent conflicts from occurring in the application we examined
previously as the result of adding a ``commit``.  Here's the application that
generates conflicts:

.. code-block:: python
   :linenos:

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.response import Response

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

   if __name__ == '__main__':
       config = Configurator()

       config.add_view(hello_world, name='hello')

       # conflicting view configuration
       config.add_view(goodbye_world, name='hello')

       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

We can prevent the two ``add_view`` calls from conflicting by issuing a call to
:meth:`~pyramid.config.Configurator.commit` between them:

.. code-block:: python
   :linenos:
   :emphasize-lines: 16

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.response import Response

   def hello_world(request):
       return Response('Hello world!')

   def goodbye_world(request):
       return Response('Goodbye world!')

   if __name__ == '__main__':
       config = Configurator()

       config.add_view(hello_world, name='hello')

       config.commit() # commit any pending configuration actions

       # no-longer-conflicting view configuration
       config.add_view(goodbye_world, name='hello')

       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

In the above example we've issued a call to
:meth:`~pyramid.config.Configurator.commit` between the two ``add_view`` calls.
:meth:`~pyramid.config.Configurator.commit` will execute any pending
configuration statements.

Calling :meth:`~pyramid.config.Configurator.commit` is safe at any time.  It
executes all pending configuration actions and leaves the configuration action
list "clean".

Note that :meth:`~pyramid.config.Configurator.commit` has no effect when you're
using an *autocommitting* configurator (see :ref:`autocommitting_configurator`).

.. _autocommitting_configurator:

Using an Autocommitting Configurator
++++++++++++++++++++++++++++++++++++

You can also use a heavy hammer to circumvent conflict detection by using a
configurator constructor parameter: ``autocommit=True``.  For example:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   if __name__ == '__main__':
       config = Configurator(autocommit=True)

When the ``autocommit`` parameter passed to the Configurator is ``True``,
conflict detection (and :ref:`twophase_config`) is disabled.  Configuration
statements will be executed immediately, and succeeding statements will
override preceding ones.

:meth:`~pyramid.config.Configurator.commit` has no effect when ``autocommit``
is ``True``.

If you use a Configurator in code that performs unit testing, it's usually a
good idea to use an autocommitting Configurator, because you are usually
unconcerned about conflict detection or two-phase configuration in test code.

.. _automatic_conflict_resolution:

Automatic Conflict Resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your code uses the :meth:`~pyramid.config.Configurator.include` method to
include external configuration, some conflicts are automatically resolved.
Configuration statements that are made as the result of an "include" will be
overridden by configuration statements that happen within the caller of the
"include" method.

Automatic conflict resolution supports this goal.  If a user wants to reuse a
Pyramid application, and they want to customize the configuration of this
application without hacking its code "from outside", they can "include" a
configuration function from the package and override only some of its
configuration statements within the code that does the include.  No conflicts
will be generated by configuration statements within the code that does the
including, even if configuration statements in the included code would conflict
if it was moved "up" to the calling code.

Methods Which Provide Conflict Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are the methods of the configurator which provide conflict detection:

:meth:`~pyramid.config.Configurator.add_view`,
:meth:`~pyramid.config.Configurator.add_route`,
:meth:`~pyramid.config.Configurator.add_renderer`,
:meth:`~pyramid.config.Configurator.add_request_method`,
:meth:`~pyramid.config.Configurator.set_request_factory`,
:meth:`~pyramid.config.Configurator.set_session_factory`,
:meth:`~pyramid.config.Configurator.set_request_property`,
:meth:`~pyramid.config.Configurator.set_root_factory`,
:meth:`~pyramid.config.Configurator.set_view_mapper`,
:meth:`~pyramid.config.Configurator.set_authentication_policy`,
:meth:`~pyramid.config.Configurator.set_authorization_policy`,
:meth:`~pyramid.config.Configurator.set_locale_negotiator`,
:meth:`~pyramid.config.Configurator.set_default_permission`,
:meth:`~pyramid.config.Configurator.add_traverser`,
:meth:`~pyramid.config.Configurator.add_resource_url_adapter`,
and :meth:`~pyramid.config.Configurator.add_response_adapter`.

:meth:`~pyramid.config.Configurator.add_static_view` also indirectly provides
conflict detection, because it's implemented in terms of the conflict-aware
``add_route`` and ``add_view`` methods.

.. index::
   pair: configuration; including from external sources

.. _including_configuration:

Including Configuration from External Sources
---------------------------------------------

Some application programmers will factor their configuration code in such a way
that it is easy to reuse and override configuration statements.  For example,
such a developer might factor out a function used to add routes to their
application:

.. code-block:: python
   :linenos:

   def add_routes(config):
       config.add_route(...)

Rather than calling this function directly with ``config`` as an argument,
instead use :meth:`pyramid.config.Configurator.include`:

.. code-block:: python
   :linenos:

   config.include(add_routes)

Using ``include`` rather than calling the function directly will allow
:ref:`automatic_conflict_resolution` to work.

:meth:`~pyramid.config.Configurator.include` can also accept a :term:`module`
as an argument:

.. code-block:: python
   :linenos:

   import myapp

   config.include(myapp)

For this to work properly, the ``myapp`` module must contain a callable with
the special name ``includeme``, which should perform configuration (like the
``add_routes`` callable we showed above as an example).

:meth:`~pyramid.config.Configurator.include` can also accept a :term:`dotted
Python name` to a function or a module.

.. note:: See :ref:`the_include_tag` for a declarative alternative to the
   :meth:`~pyramid.config.Configurator.include` method.

.. _twophase_config:

Two-Phase Configuration
-----------------------

When a non-autocommitting :term:`Configurator` is used to do configuration (the
default), configuration execution happens in two phases.  In the first phase,
"eager" configuration actions (actions that must happen before all others, such
as registering a renderer) are executed, and *discriminators* are computed for
each of the actions that depend on the result of the eager actions.  In the
second phase, the discriminators of all actions are compared to do conflict
detection.

Due to this, for configuration methods that have no internal ordering
constraints, execution order of configuration method calls is not important.
For example, the relative ordering of
:meth:`~pyramid.config.Configurator.add_view` and
:meth:`~pyramid.config.Configurator.add_renderer` is unimportant when a
non-autocommitting configurator is used.  This code snippet:

.. code-block:: python
   :linenos:

   config.add_view('some.view', renderer='path_to_custom/renderer.rn')
   config.add_renderer('.rn', SomeCustomRendererFactory)

Has the same result as:

.. code-block:: python
   :linenos:

   config.add_renderer('.rn', SomeCustomRendererFactory)
   config.add_view('some.view', renderer='path_to_custom/renderer.rn')

Even though the view statement depends on the registration of a custom
renderer, due to two-phase configuration, the order in which the configuration
statements are issued is not important.  ``add_view`` will be able to find the
``.rn`` renderer even if ``add_renderer`` is called after ``add_view``.

The same is untrue when you use an *autocommitting* configurator (see
:ref:`autocommitting_configurator`).  When an autocommitting configurator is
used, two-phase configuration is disabled, and configuration statements must be
ordered in dependency order.

Some configuration methods, such as
:meth:`~pyramid.config.Configurator.add_route` have internal ordering
constraints: the routes they imply require relative ordering.  Such ordering
constraints are not absolved by two-phase configuration.  Routes are still
added in configuration execution order.

More Information
----------------

For more information, see the article :ref:`A Whirlwind Tour of Advanced
Configuration Tactics <cookbook:whirlwind-adv-conf>` in the Pyramid Community
Cookbook.
