.. _handlers_chapter:

View Handlers
=============

View Handlers tie together
:meth:`pyramid.configuration.Configurator.add_route` and
:meth:`pyramid.configuration.Configurator.add_view` to register a collection
of views in a single class. The View Handler also introduces the concept
of an ``action``, which is used as a view predicate to control which method of
the handler is called.

The handler class is initialized by :mod:`pyramid` in the same manner as a
view class with its ``__init__`` called with a request object. A method of
the class is then called depending on its configuration. The
:meth:`pyramid.configuration.Configurator.add_handler` method will scan the
handler class and automatically setup views for methods that are auto-exposed
or have an ``__exposed__`` attribute. The :class:`~pyramid.view.action`
decorator is used to setup additional view configuration information for
individual class methods, and can be used repeatedly for a single method
to register multiple view configurations that will call that view callable.

Here's an example handler class:

.. code-block:: python
    
    from webob import Response
   
    from pyramid.view import action
   
    class Hello(object):
        def __init__(self, request):
            self.request = request
       
        def index(self):
            return Response('Hello world!')

        @action(renderer="mytemplate.mak")
        def bye(self):
            return {}

A :meth:`~pyramid.configuration.Configurator.add_handler` setup for the
handler:

.. code-block:: python

    config.add_handler('hello', '/hello/:action', handler=Hello)

This example will result in a route being added for the pattern
``/hello/:action``, each method of the ``Hello`` class will then be examined
to register the views. The value of ``:action`` in the route pattern will be
used to determine which view should be called, and each view in the class will
be setup with a view predicate that requires a specific ``action`` name.

If the URL in the above example was ``/hello/index``, then the ``index``
method of the Hello class would be called.

Alternatively, the action can be declared specifically for a URL to go to a
specific ``action`` name:

.. code-block:: python
    
    config.add_handler('hello_index', '/hello/index', handler=Hello, action='index')

This will result one of the methods that are configured for the ``action`` of
'index' in the ``Hello`` handler class to be called. Other methods in the
handler class not named 'index' might be called if they were configured to be
called when the ``action`` name is 'index' as will be seen below.


Using :meth:`~pyramid.configuration.Configurator.add_handler`
-------------------------------------------------------------

When calling :meth:`~pyramid.configuration.Configurator.add_handler`, an
``action`` is required in either the route pattern or as a keyword argument,
but **cannot appear in both places**. Additional keyword arguments are passed
directly through to :meth:`pyramid.configuration.Configurator.add_route`.

Multiple :meth:`~pyramid.configuration.Configurator.add_handler` calls can
specify the same handler, to register specific route name's for different
handler/action combinations. For example:

.. code-block:: python
    
    config.add_handler('hello_index', '/hello/index', handler=Hello, action='index')
    config.add_handler('bye_index', '/hello/bye', handler=Hello, action='bye')


View Setup in the Handler Class
-------------------------------

The handler class specified can have a single class level attribute called
``__autoexpose__`` which should be a regular expression. It's used to
determine which method names will result in additional view configurations
being registered.

When :meth:`~pyramid.configuration.Configurator.add_handler` runs, every
method in the handler class will be searched and a view registered if the
method name matches the ``__autoexpose__`` regular expression, or if the
method has a ``__exposed__`` attribute. The ``__exposed__`` attribute for a
function should never be set manually, the :class:`~pyramid.view.action`
decorator will configure it.

Auto-exposed Views
------------------

Every method in the handler class that has a name meeting the
``_autoexpose__`` regular expression will have a view registered for an
``action`` name corresponding to the method name. This functionality can be
disabled by setting an ``__autoexpose__`` regular expression to begin with a
number:

.. code-block:: python

    from pyramid.view import action
   
    class Hello(object):
        __autoexpose__ = r'^\d+'
        
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
information on the method's ``__exposed__`` attribute, which is used by
:meth:`~pyramid.configuration.Configurator.add_handler` to setup the view
configuration.

All keyword arguments are recorded, and passed to
:meth:`pyramid.configuration.Configurator.add_view`. Any valid keyword
arguments for :meth:`pyramid.configuration.Configurator.add_view` can thus be
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
