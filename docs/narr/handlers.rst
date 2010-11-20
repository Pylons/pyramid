.. _handlers_chapter:

View Handlers
=============

Along with normal view callables, :app:`Pyramid` provides the concept of a
:term:`view handler`.  Using a view handler instead of a plain :term:`view
callable` makes it unnecessary to call
:meth:`pyramid.configuration.Configurator.add_route` (and/or
:meth:`pyramid.configuration.Configurator.add_view`) "by hand" multiple
times, making it more pleasant to register a collection of views as a single
class when using :term:`url dispatch`.  The view handler machinery also
introduces the concept of an ``action``, which is used as a :term:`view
predicate` to control which method of the handler is called.

.. note:: 

   View handlers are not useful when using :term:`traversal`, only when using
   :term:`url dispatch`.  The concept of a view handler is analogous to a
   "controller" in Pylons 1.0.

The view handler class is initialized by :app:`Pyramid` in the same manner as
a view class.  Its ``__init__`` is called with a request object (see
:ref:`class_as_view`) when a request enters the system which corresponds with
a view handler registration made during configuration. A method of the view
handler class is then called. The method which is called depends on the view
handler configuration.

The :meth:`pyramid.configuration.Configurator.add_handler` method will scan
the handler class and automatically set up views for methods that are
auto-exposed or were decorated with :class:`~pyramid.view.action`. The
:class:`~pyramid.view.action` decorator is used to setup additional view
configuration information for individual class methods, and can be used
repeatedly for a single method to register multiple view configurations that
will call that view callable.

Here's an example view handler class:

.. code-block:: python
    
    from pyramid.response import Response
   
    from pyramid.view import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
       
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}

An accompanying call to the
:meth:`~pyramid.configuration.Configurator.add_handler` for the handler must
be performed in order to register it with the system:

.. code-block:: python

    config.add_handler('hello', '/hello/{action}', handler=Hello)

This example will result in a route being added for the pattern
``/hello/{action}``, each method of the ``Hello`` class will then be examined
to register the views. The value of ``{action}`` in the route pattern will be
used to determine which view should be called, and each view in the class will
be setup with a view predicate that requires a specific ``action`` name.

If the URL in the above example was ``/hello/index``, then the ``index``
method of the Hello class would be called.

Alternatively, the action can be declared specifically for a URL to go to a
specific ``action`` name:

.. code-block:: python
    
    config.add_handler('hello_index', '/hello/index', 
                       handler=Hello, action='index')

This will result one of the methods that are configured for the ``action`` of
'index' in the ``Hello`` handler class to be called. Other methods in the
handler class not named 'index' might be called if they were configured to be
called when the ``action`` name is 'index' as will be seen below.


Using :meth:`~pyramid.configuration.Configurator.add_handler`
-------------------------------------------------------------

When calling :meth:`~pyramid.configuration.Configurator.add_handler`, an
``action`` is required in either the route pattern or as a keyword argument,
but **cannot appear in both places**. A ``handler`` argument must also be
supplied, which can be either a :term:`resource specification` or a Python
reference to the handler class. Additional keyword arguments are passed
directly through to :meth:`pyramid.configuration.Configurator.add_route`.

For example:

.. code-block:: python
    
    config.add_handler('hello', '/hello/{action}',
                       handler='mypackage.handlers:MyHandler')

In larger applications, it is advised to use a :term:`resource specification`
with :meth:`~pyramid.configuration.Configurator.add_handler` to avoid having
to import every handler class.

Multiple :meth:`~pyramid.configuration.Configurator.add_handler` calls can
specify the same handler, to register specific route names for different
handler/action combinations. For example:

.. code-block:: python
    
    config.add_handler('hello_index', '/hello/index', 
                       handler=Hello, action='index')
    config.add_handler('bye_index', '/hello/bye', 
                       handler=Hello, action='bye')


View Setup in the Handler Class
-------------------------------

The handler class specified can have a single class level attribute called
``__autoexpose__`` which should be a regular expression or the value
``None``. It's used to determine which method names will result in additional
view configurations being registered.

When :meth:`~pyramid.configuration.Configurator.add_handler` runs, every
method in the handler class will be searched and a view registered if the
method name matches the ``__autoexpose__`` regular expression, or if the
method was decorated with :class:`~pyramid.view.action`.

Auto-exposed Views
------------------

Every method in the handler class that has a name meeting the
``_autoexpose__`` regular expression will have a view registered for an
``action`` name corresponding to the method name. This functionality can be
disabled by setting the ``__autoexpose__`` attribute to ``None``:

.. code-block:: python

    from pyramid.view import action
   
    class Hello(object):
        __autoexpose__ = None
        
        def __init__(self, request):
            self.request = request
        
        @action()
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}

With auto-expose effectively disabled, no views will be registered for a
method unless it is specifically decorated with :class:`~pyramid.view.action`.

Action Decorator
----------------

The :class:`~pyramid.view.action` decorator registers view configuration
information on the handler method which is used by
:meth:`~pyramid.configuration.Configurator.add_handler` to setup the view
configuration.

All keyword arguments are recorded, and passed to
:meth:`!pyramid.configuration.Configurator.add_view`. Any valid keyword
arguments for :meth:`!pyramid.configuration.Configurator.add_view` can thus be
used with the :class:`~pyramid.view.action` decorator to further restrict when
the view will be called.

One important difference is that a handler method can respond to an ``action``
name that is different from the method name by passing in a ``name`` argument.

Example:

.. code-block:: python
    
    from pyramid.view import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
        
        @action(name='index', renderer='created.mak', request_method='POST')
        def create(self):
            return {}

        @action(renderer="view_all.mak", request_method='GET')
        def index(self):
            return {}

This will register two views that require the ``action`` to be ``index``, with
the additional view predicate requiring a specific request method.

When a method is decorated multiple times with :class:`~pyramid.view.action`,
a view configuration will be registered for each call, with the view callable
being the method decorated. Used with a combination of ``name``, multiple
URL's can result in different template renderings with the same data.

Example:

.. code-block:: python
    
    from pyramid.view import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
        
        @action(name='home', renderer='home.mak')
        @action(name='about', renderer='about.mak')
        def show_template(self):
            # prep some template vars
            return {}

    # in the config
    config.add_handler('hello', '/hello/{action}', handler=Hello)

With this configuration, the url ``/hello/home`` will find a view configuration
that results in calling the ``show_template`` method, then rendering the
template with ``home.mak``, and the url ``/hello/about`` will call the same
method and render the ``about.mak`` template.
