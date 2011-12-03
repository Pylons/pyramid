.. index::
   single: extending configuration

.. _extconfig_narr:

Extending Pyramid Configuration
===============================

Pyramid allows you to extend its Configurator with custom directives.  These
directives can add an :term:`action`, participate in :term:`conflict
resolution`, and can provide some number of :term:`introspectable` objects.

.. index::
   single: add_directive
   pair: configurator; adding directives

.. _add_directive:

Adding Methods to the Configurator via ``add_directive``
--------------------------------------------------------

Framework extension writers can add arbitrary methods to a
:term:`Configurator` by using the
:meth:`pyramid.config.Configurator.add_directive` method of the configurator.
Using :meth:`~pyramid.config.Configurator.add_directive` makes it possible to
extend a Pyramid configurator in arbitrary ways, and allows it to perform
application-specific tasks more succinctly.

The :meth:`~pyramid.config.Configurator.add_directive` method accepts two
positional arguments: a method name and a callable object.  The callable
object is usually a function that takes the configurator instance as its
first argument and accepts other arbitrary positional and keyword arguments.
For example:

.. code-block:: python
   :linenos:

   from pyramid.events import NewRequest
   from pyramid.config import Configurator

   def add_newrequest_subscriber(config, subscriber):
       config.add_subscriber(subscriber, NewRequest).

   if __name__ == '__main__':
       config = Configurator()
       config.add_directive('add_newrequest_subscriber',
                            add_newrequest_subscriber)

Once :meth:`~pyramid.config.Configurator.add_directive` is called, a user can
then call the added directive by its given name as if it were a built-in
method of the Configurator:

.. code-block:: python
   :linenos:

   def mysubscriber(event):
       print event.request

   config.add_newrequest_subscriber(mysubscriber)

A call to :meth:`~pyramid.config.Configurator.add_directive` is often
"hidden" within an ``includeme`` function within a "frameworky" package meant
to be included as per :ref:`including_configuration` via
:meth:`~pyramid.config.Configurator.include`.  For example, if you put this
code in a package named ``pyramid_subscriberhelpers``:

.. code-block:: python
   :linenos:

   def includeme(config)
       config.add_directive('add_newrequest_subscriber',
                            add_newrequest_subscriber)

The user of the add-on package ``pyramid_subscriberhelpers`` would then be
able to install it and subsequently do:

.. code-block:: python
   :linenos:

   def mysubscriber(event):
       print event.request

   from pyramid.config import Configurator
   config = Configurator()
   config.include('pyramid_subscriberhelpers')
   config.add_newrequest_subscriber(mysubscriber)

Using ``config.action`` in a Directive
--------------------------------------

If a custom directive can't do its work exclusively in terms of existing
configurator methods (such as
:meth:`pyramid.config.Configurator.add_subscriber`, as above), the directive
may need to make use of the :meth:`pyramid.config.Configurator.action`
method.  This method adds an entry to the list of "actions" that Pyramid will
attempt to process when :meth:`pyramid.config.Configurator.commit` is called.
An action is simply a dictionary that includes a :term:`discriminator`,
possibly a callback function, and possibly other metadata used by Pyramid's
action system.

Here's an example directive which uses the "action" method:

.. code-block:: python
   :linenos:

   def add_jammyjam(config, jammyjam):
       def register():
           config.registry.jammyjam = jammyjam
       config.action('jammyjam', register)

   if __name__ == '__main__':
       config = Configurator()
       config.add_directive('add_jammyjam', add_jammyjam)

Fancy, but what does it do?  The action method accepts a number of arguments.
In the above directive named ``add_jammyjam``, we call
:meth:`~pyramid.config.Configurator.action` with two arguments: the string
``jammyjam`` is passed as the first argument, ``discriminator`` and the
closure function named ``register`` is passed as the second argument,
named ``callable``.

When the :meth:`~pyramid.config.Configurator.action` method is called, it
appends an action to the list of pending configuration actions.  All pending
actions with the same discriminator value are potentially in conflict with
one another (see :ref:`conflict_detection`).  When the
:meth:`~pyramid.config.Configurator.commit` method of the Configurator is
called (either explicitly or as the result of calling
:meth:`~pyramid.config.Configurator.make_wsgi_app`), conflicting actions are
potentially automatically resolved as per
:ref:`automatic_conflict_resolution`.  If a conflict cannot be automatically
resolved, a ConfigurationConflictError is raised and application startup is
prevented.

In our above example, therefore, if a consumer of our ``add_jammyjam``
directive did this:

.. code-block:: python
   :linenos:

   config.add_jammyjam('first')
   config.add_jammyjam('second')

When the action list was committed, the user's application would not start,
because the discriminators of the actions generated by the two calls are in
direct conflict.  Automatic conflict resolution cannot resolve the conflict,
and the user provided no intermediate
:meth:`pyramid.config.Configurator.commit` call between the calls to
``add_jammyjam`` to ensure that the successive calls did not conflict with
each other.  This is the purpose of the discriminator argument to the action
method: it's used to indicate a uniqueness constraint for an action.  Two
actions with the same discriminator will conflict unless the conflict is
automatically or manually resolved. A discriminator can be any hashable
object, but it is generally a string or a tuple.

But let's imagine that a consumer of ``add_jammyjam`` used it in such a way
that no configuration conflicts are generated.

.. code-block:: python
   :linenos:

   config.add_jammyjam('first')

What happens then?  When the ``add_jammyjam`` method is called, an action is
appended to the pending actions list.  When the pending configuration actions
are processed during :meth:`~pyramid.config.Configurator.commit`, and no
conflicts occur, the *callable* provided as the second argument to the
:meth:`~pyramid.config.Configurator.action` method within ``add_jammyjam`` is
called with no arguments.  The callable in ``add_jammyjam`` is the
``register`` closure function.  It simply sets the value
``config.registry.jammyjam`` to whatever the user passed in as the
``jammyjam`` argument to the ``add_jammyjam`` function.  Therefore, the
result of the user's call to our directive will set the ``jammyjam``
attribute of the registry to the string ``first``.  A callable is used by a
directive to defer the result of a user's call to a directive until conflict
detection has had a chance to do its job.

Other arguments exist to the :meth:`~pyramid.config.Configurator.action`
method, including ``args``, ``kw``, ``order``, and ``introspectables``.  

``args`` and ``kw`` exist as values, which, if passed, will be used as
arguments to the ``callable`` function when it is called back.  For example
our directive might use them like so:

.. code-block:: python
   :linenos:

   def add_jammyjam(config, jammyjam):
       def register(*arg, **kw):
           config.registry.jammyjam_args = arg
           config.registry.jammyjam_kw = kw
           config.registry.jammyjam = jammyjam
       config.action('jammyjam', register, args=('one',), kw={'two':'two'})

In the above example, when this directive is used to generate an action, and
that action is committed, ``config.registry.jammyjam_args`` will be set to
``('one',)`` and ``config.registry.jammyjam_kw`` will be set to
``{'two':'two'}``.  ``args`` and ``kw`` are honestly not very useful when
your ``callable`` is a closure function, because you already usually have
access to every local in the directive without needing them to be passed
back.  They can be useful, however, if you don't use a closure as a callable.

``order`` is a crude order control mechanism.  ``order`` defaults to the
integer ``0``; it can be set to any other integer.  All actions that share an
order will be called before other actions that share a higher order.  This
makes it possible to write a directive with callable logic that relies on the
execution of the callable of another directive being done first.  For
example, Pyramid's :meth:`pyramid.config.Configurator.add_view` directive
registers an action with a higher order than the
:meth:`pyramid.config.Configurator.add_route` method.  Due to this, the
``add_view`` method's callable can assume that, if a ``route_name`` was
passed to it, that a route by this name was already registered by
``add_route``, and if such a route has not already been registered, it's a
configuration error (a view that names a nonexistent route via its
``route_name`` parameter will never be called).

``introspectables`` is a sequence of :term:`introspectable` objects.  Using
``introspectables`` allows you to plug into Pyramid's configuration
introspection system.

