.. index::
   single: extending configuration

.. _extconfig_narr:

Extending Pyramid Configuration
===============================

Pyramid allows you to extend its Configurator with custom directives.  Custom
directives can use other directives, they can add a custom :term:`action`, they
can participate in :term:`conflict resolution`, and they can provide some
number of :term:`introspectable` objects.

.. index::
   single: add_directive
   pair: configurator; adding directives

.. _add_directive:

Adding Methods to the Configurator via ``add_directive``
--------------------------------------------------------

Framework extension writers can add arbitrary methods to a :term:`Configurator`
by using the :meth:`pyramid.config.Configurator.add_directive` method of the
configurator. Using :meth:`~pyramid.config.Configurator.add_directive` makes it
possible to extend a Pyramid configurator in arbitrary ways, and allows it to
perform application-specific tasks more succinctly.

The :meth:`~pyramid.config.Configurator.add_directive` method accepts two
positional arguments: a method name and a callable object.  The callable object
is usually a function that takes the configurator instance as its first
argument and accepts other arbitrary positional and keyword arguments. For
example:

.. code-block:: python
   :linenos:

   from pyramid.events import NewRequest
   from pyramid.config import Configurator

   def add_newrequest_subscriber(config, subscriber):
       config.add_subscriber(subscriber, NewRequest)

   if __name__ == '__main__':
       config = Configurator()
       config.add_directive('add_newrequest_subscriber',
                            add_newrequest_subscriber)

Once :meth:`~pyramid.config.Configurator.add_directive` is called, a user can
then call the added directive by its given name as if it were a built-in method
of the Configurator:

.. code-block:: python
   :linenos:

   def mysubscriber(event):
       print(event.request)

   config.add_newrequest_subscriber(mysubscriber)

A call to :meth:`~pyramid.config.Configurator.add_directive` is often "hidden"
within an ``includeme`` function within a "frameworky" package meant to be
included as per :ref:`including_configuration` via
:meth:`~pyramid.config.Configurator.include`.  For example, if you put this
code in a package named ``pyramid_subscriberhelpers``:

.. code-block:: python
   :linenos:

   def includeme(config):
       config.add_directive('add_newrequest_subscriber',
                            add_newrequest_subscriber)

The user of the add-on package ``pyramid_subscriberhelpers`` would then be able
to install it and subsequently do:

.. code-block:: python
   :linenos:

   def mysubscriber(event):
       print(event.request)

   from pyramid.config import Configurator
   config = Configurator()
   config.include('pyramid_subscriberhelpers')
   config.add_newrequest_subscriber(mysubscriber)

Using ``config.action`` in a Directive
--------------------------------------

If a custom directive can't do its work exclusively in terms of existing
configurator methods (such as
:meth:`pyramid.config.Configurator.add_subscriber` as above), the directive may
need to make use of the :meth:`pyramid.config.Configurator.action` method. This
method adds an entry to the list of "actions" that Pyramid will attempt to
process when :meth:`pyramid.config.Configurator.commit` is called. An action is
simply a dictionary that includes a :term:`discriminator`, possibly a callback
function, and possibly other metadata used by Pyramid's action system.

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
``jammyjam`` is passed as the first argument named ``discriminator``, and the
closure function named ``register`` is passed as the second argument named
``callable``.

When the :meth:`~pyramid.config.Configurator.action` method is called, it
appends an action to the list of pending configuration actions.  All pending
actions with the same discriminator value are potentially in conflict with one
another (see :ref:`conflict_detection`).  When the
:meth:`~pyramid.config.Configurator.commit` method of the Configurator is
called (either explicitly or as the result of calling
:meth:`~pyramid.config.Configurator.make_wsgi_app`), conflicting actions are
potentially automatically resolved as per :ref:`automatic_conflict_resolution`.
If a conflict cannot be automatically resolved, a
:exc:`pyramid.exceptions.ConfigurationConflictError` is raised and application
startup is prevented.

In our above example, therefore, if a consumer of our ``add_jammyjam``
directive did this:

.. code-block:: python

   config.add_jammyjam('first')
   config.add_jammyjam('second')

When the action list was committed resulting from the set of calls above, our
user's application would not start, because the discriminators of the actions
generated by the two calls are in direct conflict.  Automatic conflict
resolution cannot resolve the conflict (because no ``config.include`` is
involved), and the user provided no intermediate
:meth:`pyramid.config.Configurator.commit` call between the calls to
``add_jammyjam`` to ensure that the successive calls did not conflict with each
other.

This demonstrates the purpose of the discriminator argument to the action
method: it's used to indicate a uniqueness constraint for an action.  Two
actions with the same discriminator will conflict unless the conflict is
automatically or manually resolved. A discriminator can be any hashable object,
but it is generally a string or a tuple.  *You use a discriminator to
declaratively ensure that the user doesn't provide ambiguous configuration
statements.*

But let's imagine that a consumer of ``add_jammyjam`` used it in such a way
that no configuration conflicts are generated.

.. code-block:: python

   config.add_jammyjam('first')

What happens now?  When the ``add_jammyjam`` method is called, an action is
appended to the pending actions list.  When the pending configuration actions
are processed during :meth:`~pyramid.config.Configurator.commit`, and no
conflicts occur, the *callable* provided as the second argument to the
:meth:`~pyramid.config.Configurator.action` method within ``add_jammyjam`` is
called with no arguments.  The callable in ``add_jammyjam`` is the ``register``
closure function.  It simply sets the value ``config.registry.jammyjam`` to
whatever the user passed in as the ``jammyjam`` argument to the
``add_jammyjam`` function.  Therefore, the result of the user's call to our
directive will set the ``jammyjam`` attribute of the registry to the string
``first``.  *A callable is used by a directive to defer the result of a user's
call to the directive until conflict detection has had a chance to do its job*.

Other arguments exist to the :meth:`~pyramid.config.Configurator.action`
method, including ``args``, ``kw``, ``order``, and ``introspectables``.

``args`` and ``kw`` exist as values, which if passed will be used as arguments
to the ``callable`` function when it is called back.  For example, our
directive might use them like so:

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
``{'two':'two'}``.  ``args`` and ``kw`` are honestly not very useful when your
``callable`` is a closure function, because you already usually have access to
every local in the directive without needing them to be passed back.  They can
be useful, however, if you don't use a closure as a callable.

``order`` is a crude order control mechanism.  ``order`` defaults to the
integer ``0``; it can be set to any other integer.  All actions that share an
order will be called before other actions that share a higher order.  This
makes it possible to write a directive with callable logic that relies on the
execution of the callable of another directive being done first.  For example,
Pyramid's :meth:`pyramid.config.Configurator.add_view` directive registers an
action with a higher order than the
:meth:`pyramid.config.Configurator.add_route` method.  Due to this, the
``add_view`` method's callable can assume that, if a ``route_name`` was passed
to it, that a route by this name was already registered by ``add_route``, and
if such a route has not already been registered, it's a configuration error (a
view that names a nonexistent route via its ``route_name`` parameter will never
be called).

.. versionchanged:: 1.6
  As of Pyramid 1.6 it is possible for one action to invoke another. See
  :ref:`ordering_actions` for more information.

Finally, ``introspectables`` is a sequence of :term:`introspectable` objects.
You can pass a sequence of introspectables to the
:meth:`~pyramid.config.Configurator.action` method, which allows you to augment
Pyramid's configuration introspection system.

.. _ordering_actions:

Ordering Actions
----------------

In Pyramid every :term:`action` has an inherent ordering relative to other
actions. The logic within actions is deferred until a call to
:meth:`pyramid.config.Configurator.commit` (which is automatically invoked by
:meth:`pyramid.config.Configurator.make_wsgi_app`). This means you may call
``config.add_view(route_name='foo')`` **before** ``config.add_route('foo',
'/foo')`` because nothing actually happens until commit-time. During a commit
cycle, conflicts are resolved, and actions are ordered and executed.

By default, almost every action in Pyramid has an ``order`` of
:const:`pyramid.config.PHASE3_CONFIG`. Every action within the same order-level
will be executed in the order it was called. This means that if an action must
be reliably executed before or after another action, the ``order`` must be
defined explicitly to make this work. For example, views are dependent on
routes being defined. Thus the action created by
:meth:`pyramid.config.Configurator.add_route` has an ``order`` of
:const:`pyramid.config.PHASE2_CONFIG`.

Pre-defined Phases
~~~~~~~~~~~~~~~~~~

:const:`pyramid.config.PHASE0_CONFIG`

- This phase is reserved for developers who want to execute actions prior to
  Pyramid's core directives.

:const:`pyramid.config.PHASE1_CONFIG`

- :meth:`pyramid.config.Configurator.add_renderer`
- :meth:`pyramid.config.Configurator.add_route_predicate`
- :meth:`pyramid.config.Configurator.add_subscriber_predicate`
- :meth:`pyramid.config.Configurator.add_view_predicate`
- :meth:`pyramid.config.Configurator.add_view_deriver`
- :meth:`pyramid.config.Configurator.override_asset`
- :meth:`pyramid.config.Configurator.set_authorization_policy`
- :meth:`pyramid.config.Configurator.set_default_csrf_options`
- :meth:`pyramid.config.Configurator.set_default_permission`
- :meth:`pyramid.config.Configurator.set_view_mapper`

:const:`pyramid.config.PHASE2_CONFIG`

- :meth:`pyramid.config.Configurator.add_route`
- :meth:`pyramid.config.Configurator.set_authentication_policy`

:const:`pyramid.config.PHASE3_CONFIG`

- The default for all builtin or custom directives unless otherwise specified.

Calling Actions from Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionadded:: 1.6

Pyramid's configurator allows actions to be added during a commit-cycle as long
as they are added to the current or a later ``order`` phase. This means that
your custom action can defer decisions until commit-time and then do things
like invoke :meth:`pyramid.config.Configurator.add_route`. It can also provide
better conflict detection if your addon needs to call more than one other
action.

For example, let's make an addon that invokes ``add_route`` and ``add_view``,
but we want it to conflict with any other call to our addon:

.. code-block:: python
   :linenos:

   from pyramid.config import PHASE0_CONFIG

   def includeme(config):
       config.add_directive('add_auto_route', add_auto_route)

   def add_auto_route(config, name, view):
       def register():
           config.add_view(route_name=name, view=view)
           config.add_route(name, '/' + name)
       config.action(('auto route', name), register, order=PHASE0_CONFIG)

Now someone else can use your addon and be informed if there is a conflict
between this route and another, or two calls to ``add_auto_route``. Notice how
we had to invoke our action **before** ``add_view`` or ``add_route``. If we
tried to invoke this afterward, the subsequent calls to ``add_view`` and
``add_route`` would cause conflicts because that phase had already been
executed, and the configurator cannot go back in time to add more views during
that commit-cycle.

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def main(global_config, **settings):
       config = Configurator()
       config.include('auto_route_addon')
       config.add_auto_route('foo', my_view)

   def my_view(request):
       return request.response

.. _introspection:

Adding Configuration Introspection
----------------------------------

.. versionadded:: 1.3

Pyramid provides a configuration introspection system that can be used by
debugging tools to provide visibility into the configuration of a running
application.

All built-in Pyramid directives (such as
:meth:`pyramid.config.Configurator.add_view` and
:meth:`pyramid.config.Configurator.add_route`) register a set of
introspectables when called.  For example, when you register a view via
``add_view``, the directive registers at least one introspectable: an
introspectable about the view registration itself, providing human-consumable
values for the arguments passed into it.  You can later use the introspection
query system to determine whether a particular view uses a renderer, or whether
a particular view is limited to a particular request method, or against which
routes a particular view is registered.  The Pyramid "debug toolbar" makes use
of the introspection system in various ways to display information to Pyramid
developers.

Introspection values are set when a sequence of :term:`introspectable` objects
is passed to the :meth:`~pyramid.config.Configurator.action` method. Here's an
example of a directive which uses introspectables:

.. code-block:: python
   :linenos:

   def add_jammyjam(config, value):
       def register():
           config.registry.jammyjam = value
       intr = config.introspectable(category_name='jammyjams', 
                                    discriminator='jammyjam',
                                    title='a jammyjam',
                                    type_name=None)
       intr['value'] = value
       config.action('jammyjam', register, introspectables=(intr,))

   if __name__ == '__main__':
       config = Configurator()
       config.add_directive('add_jammyjam', add_jammyjam)

If you notice, the above directive uses the ``introspectable`` attribute of a
Configurator (:attr:`pyramid.config.Configurator.introspectable`) to create an
introspectable object.  The introspectable object's constructor requires at
least four arguments: the ``category_name``, the ``discriminator``, the
``title``, and the ``type_name``.

The ``category_name`` is a string representing the logical category for this
introspectable.  Usually the category_name is a pluralization of the type of
object being added via the action.

The ``discriminator`` is a value unique **within the category** (unlike the
action discriminator, which must be unique within the entire set of actions).
It is typically a string or tuple representing the values unique to this
introspectable within the category.  It is used to generate links and as part
of a relationship-forming target for other introspectables.

The ``title`` is a human-consumable string that can be used by introspection
system frontends to show a friendly summary of this introspectable.

The ``type_name`` is a value that can be used to subtype this introspectable
within its category for sorting and presentation purposes.  It can be any
value.

An introspectable is also dictionary-like.  It can contain any set of key/value
pairs, typically related to the arguments passed to its related directive.
While the ``category_name``, ``discriminator``, ``title``, and ``type_name``
are *metadata* about the introspectable, the values provided as key/value pairs
are the actual data provided by the introspectable.  In the above example, we
set the ``value`` key to the value of the ``value`` argument passed to the
directive.

Our directive above mutates the introspectable, and passes it in to the
``action`` method as the first element of a tuple as the value of the
``introspectable`` keyword argument.  This associates this introspectable with
the action.  Introspection tools will then display this introspectable in their
index.

Introspectable Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two introspectables may have relationships between each other.

.. code-block:: python
   :linenos:

   def add_jammyjam(config, value, template):
       def register():
           config.registry.jammyjam = (value, template)
       intr = config.introspectable(category_name='jammyjams', 
                                    discriminator='jammyjam',
                                    title='a jammyjam',
                                    type_name=None)
       intr['value'] = value
       tmpl_intr = config.introspectable(category_name='jammyjam templates',
                                         discriminator=template,
                                         title=template,
                                         type_name=None)
       tmpl_intr['value'] = template
       intr.relate('jammyjam templates', template)
       config.action('jammyjam', register, introspectables=(intr, tmpl_intr))

   if __name__ == '__main__':
       config = Configurator()
       config.add_directive('add_jammyjam', add_jammyjam)

In the above example, the ``add_jammyjam`` directive registers two
introspectables: the first is related to the ``value`` passed to the directive,
and the second is related to the ``template`` passed to the directive. If you
believe a concept within a directive is important enough to have its own
introspectable, you can cause the same directive to register more than one
introspectable, registering one introspectable for the "main idea" and another
for a related concept.

The call to ``intr.relate`` above
(:meth:`pyramid.interfaces.IIntrospectable.relate`) is passed two arguments: a
category name and a directive.  The example above effectively indicates that
the directive wishes to form a relationship between the ``intr`` introspectable
and the ``tmpl_intr`` introspectable; the arguments passed to ``relate`` are
the category name and discriminator of the ``tmpl_intr`` introspectable.

Relationships need not be made between two introspectables created by the same
directive.  Instead a relationship can be formed between an introspectable
created in one directive and another introspectable created in another by
calling ``relate`` on either side with the other directive's category name and
discriminator.  An error will be raised at configuration commit time if you
attempt to relate an introspectable with another nonexistent introspectable,
however.

Introspectable relationships will show up in frontend system renderings of
introspection values.  For example, if a view registration names a route name,
the introspectable related to the view callable will show a reference to the
route to which it relates and vice versa.
