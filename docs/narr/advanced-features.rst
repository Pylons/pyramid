Advanced :app:`Pyramid` Design Features
=======================================

:app:`Pyramid` has been built from the ground up to avoid the problems that other frameworks can suffer.

You Don't Need Singletons
-------------------------

Have you ever struggled with parameterizing Django's ``settings.py`` file for multiple installations of the same Django application? Have you ever needed to monkey-patch a framework fixture to get it to behave properly for your use case? Have you ever tried to deploy your application using an asynchronous server and failed?

All these problems are symptoms of :term:`mutable` :term:`global state`, also known as :term:`import time` :term:`side effect`\ s and arise from the use of :term:`singleton` data structures.

:app:`Pyramid` is written so that you don't run into these types of problems. It is even possible to run multiple copies of the *same* :app:`Pyramid` application configured differently within a single Python process. This makes running :app:`Pyramid` in shared hosting environments a snap.

Simplify your View Code with Predicates
---------------------------------------

How many times have you found yourself beginning the logic of your view code with something like this:

.. code-block:: python
    :linenos:

    if request.user.is_authenticated:
        # do one thing
    else:
        # do something else

Unlike many other systems, :app:`Pyramid` allows you to associate more than one view with a single route. For example, you can create a route with the pattern ``/items`` and when the route is matched, you can send the request to one view if the request method is GET, another view if the request method is POST, and so on.

:app:`Pyramid` uses a system of :term:`view predicate`\ s to allow this. Matching the request method is one basic thing you can do with a :term:`view predicate`. You can also associate views with other request parameters, such as elements in the query string, the Accept header, whether the request is an AJAX (XHR) request or not, and lots of other things.

For our example above, you can do this instead:

.. code-block:: python
    :linenos:

    @view_config(route_name="items", effective_principals=pyramid.security.Authenticated)
    def auth_view(request):
        # do one thing

    @view_config(route_name="items")
    def anon_view(request):
        # do something else

This approach allows you to develop view code that is simpler, more easily understandable, and more directly testable.

.. seealso::

   See also :ref:`view_configuration_parameters`.

Stop Worrying About Transactions
--------------------------------

:app:`Pyramid`\ 's :term:`cookiecutter`\ s render projects that include a *transaction management* system.  When you use this system, you can stop worrying about when to commit your changes, :app:`Pyramid` handles it for you. The system will commit at the end of a request or abort if there was an exception.

Why is that a good thing? Imagine a situation where you manually commit a change to your persistence layer. It's very likely that other framework code will run *after* your changes are done. If an error happens in that other code, you can easily wind up with inconsistent data if you're not extremely careful.

Using transaction management saves you from needing to think about this. Either a request completes successfully and all changes are committed, or it does not and all changes are aborted.

:app:`Pyramid`\ 's transaction management is extendable, so you can synchronize commits between multiple databases or databases of different kinds. It also allows you to do things like conditionally send email if a transaction is committed, but otherwise keep quiet.

.. seealso::

   See also :ref:`bfg_sql_wiki_tutorial` (note the lack of commit statements anywhere in application code).

Stop Worrying About Configuration
---------------------------------

When a system is small, it's reasonably easy to keep it all in your head. But as systems grow large, configuration grows more complex. Your app may grow to have hundreds or even thousands of configuration statements.

:app:`Pyramid`\ 's configuration system keeps track of each of your statements. If you accidentally add two that are identical, or :app:`Pyramid` can't make sense out of what it would mean to have both statements active at the same time, it will complain loudly at startup time.

:app:`Pyramid`\ 's configuration system is not dumb though. If you use the :meth:`~pyramid.config.Configurator.include` system, it can automatically resolve conflicts on its own. More local statements are preferred over less local ones. So you can intelligently factor large systems into smaller ones.

.. seealso::

   See also :ref:`conflict_detection`.

Compose Powerful Apps From Simple Parts
----------------------------------------

Speaking of the :app:`Pyramid` structured :meth:`~pyramid.config.Configurator.include` mechanism, it allows you to compose complex applications from multiple, simple Python packages. All the configuration statements that can be performed in your main :app:`Pyramid` application can also be used in included packages. You can add views, routes, and subscribers, and even set authentication and authorization policies.

If you need, you can extend or override the configuration of an existing application by including its configuration in your own and then modifying it.


For example, if you want to reuse an existing application that already has a bunch of routes, you can just use the ``include`` statement with a ``route_prefix``. All the routes of that application will be availabe, prefixed as you requested:

.. code-block:: python
    :linenos:

    from pyramid.config import Configurator

    if __name__ == '__main__':
       config = Configurator()
       config.include('pyramid_jinja2')
       config.include('pyramid_exclog')
       config.include('some.other.package', route_prefix='/somethingelse')

.. seealso::

    See also :ref:`including_configuration` and :ref:`building_an_extensible_app`.

Authenticate Users Your Way
---------------------------

:app:`Pyramid` ships with prebuilt, well-tested authentication and authorization schemes out of the box. Using a scheme is a matter of configuration. So if you need to change approaches later, you need only update your configuration.

In addition, the system that handles authentication and authorization is flexible and pluggable. If you want to use another security add-on, or define your own, you can. And again, you need only update your application configuration to make the change.

.. seealso::

   See also :ref:`enabling_authorization_policy`.

Build Trees of Resources
------------------------

:app:`Pyramid` supports :term:`traversal`, a way of mapping URLs to a concrete :term:`resource tree`. If your application naturally consists of an arbitrary heirarchy of different types of content (like a CMS or a Document Management System), traversal is for you. If you have a requirement for a highly granular security model ("Jane can edit documents in *this* folder, but not *that* one"), traversal can be a powerful approach.

.. seealso::

   See also :ref:`hello_traversal_chapter` and :ref:`much_ado_about_traversal_chapter`.

Take Action on Each Request with Tweens
---------------------------------------

:app:`Pyramid` has a system for applying an arbitrary action to each request or response called a :term:`tween`. The system is similar in concept to WSGI :term:`middleware`, but can be more useful since :term:`tween`\ s run in the :app:`Pyramid` context, and have access to templates, request objects, and other niceties.

The :app:`Pyramid` debug toolbar is a :term:`tween`, as is the ``pyramid_tm`` transaction manager.

.. seealso::

   See also :ref:`registering_tweens`.

Return What You Want From Your Views
------------------------------------

We have shown elsewhere (in the :doc:`introduction`) how using a :term:`renderer` allows you to return simple Python dictionaries from your view code. But some frameworks allow you to return strings or tuples from view callables. When frameworks allow for this, code looks slightly prettier because there are fewer imports and less code. For example, compare this:

.. code-block:: python
    :linenos:

    from pyramid.response import Response

    def aview(request):
        return Response("Hello world!")

To this:

.. code-block:: python
    :linenos:

    def aview(request):
        return "Hello world!"

Nicer to look at, right?

Out of the box, :app:`Pyramid` will raise an exception if you try to run the second example above. After all, a view should return a response, and "explicit is better than implicit".

But if you're a developer who likes the aesthetics of simplicity, :app:`Pyramid` provides a way to support this sort of thing, the :term:`response adapter`\ :

.. code-block:: python
    :linenos:

    from pyramid.config import Configurator
    from pyramid.response import Response

    def string_response_adapter(s):
        response = Response(s)
        response.content_type = 'text/html'
        return response

A new response adapter is registered in configuration:

.. code-block:: python
    :linenos:

    if __name__ == '__main__':
        config = Configurator()
        config.add_response_adapter(string_response_adapter, str)

With that, you may return strings from any of your view callables, e.g.:

.. code-block:: python
    :linenos:

    def helloview(request):
        return "Hello world!"

    def goodbyeview(request):
        return "Goodbye world!"

You can even use a :term:`response adapter` to allow for custom content types and return codes:

.. code-block:: python
    :linenos:

    from pyramid.config import Configurator

    def tuple_response_adapter(val):
        status_int, content_type, body = val
        response = Response(body)
        response.content_type = content_type
        response.status_int = status_int
        return response

    def string_response_adapter(body):
        response = Response(body)
        response.content_type = 'text/html'
        response.status_int = 200
        return response

    if __name__ == '__main__':
        config = Configurator()
        config.add_response_adapter(string_response_adapter, str)
        config.add_response_adapter(tuple_response_adapter, tuple)

With this, both of these views will work as expected:

.. code-block:: python
    :linenos:

    def aview(request):
        return "Hello world!"

    def anotherview(request):
        return (403, 'text/plain', "Forbidden")

.. seealso::

   See also :ref:`using_iresponse`.

Use Global Response Objects
---------------------------

Views have to return responses. But constructing them in view code is a chore. And perhaps registering a :term:`response adapter` as shown above is just too much work. :app:`Pyramid` provides a global response object as well.  You can use it directly, if you prefer:

.. code-block:: python
    :linenos:

    def aview(request):
        response = request.response
        response.body = 'Hello world!'
        response.content_type = 'text/plain'
        return response

.. seealso::

   See also :ref:`request_response_attr`.

Extend Configuration
--------------------

Perhaps the :app:`Pyramid` configurator's syntax feels a bit verbose to you. Or possibly you would like to add a feature to configuration without asking the core developers to change :app:`Pyramid` itself?

You can extend :app:`Pyramid`\ 's :term:`configurator` with your own directives. For example, let's say you find yourself calling :meth:`pyramid.config.Configurator.add_view` repetitively. Usually you can get rid of the boring with existing shortcuts, but let's say that this is a case where there is no such shortcut:

.. code-block:: python
    :linenos:

    from pyramid.config import Configurator

    config = Configurator()
    config.add_route('xhr_route', '/xhr/{id}')
    config.add_view('my.package.GET_view', route_name='xhr_route',
                    xhr=True,  permission='view', request_method='GET')
    config.add_view('my.package.POST_view', route_name='xhr_route',
                    xhr=True, permission='view', request_method='POST')
    config.add_view('my.package.HEAD_view', route_name='xhr_route',
                    xhr=True, permission='view', request_method='HEAD')

Pretty tedious right? You can add a directive to the :app:`Pyramid` :term:`configurator` to automate some of the tedium away:

.. code-block:: python
    :linenos:

    from pyramid.config import Configurator

    def add_protected_xhr_views(config, module):
        module = config.maybe_dotted(module)
        for method in ('GET', 'POST', 'HEAD'):
            view = getattr(module, 'xhr_%s_view' % method, None)
            if view is not None:
                config.add_view(view, route_name='xhr_route', xhr=True,
                                permission='view', request_method=method)

    config = Configurator()
    config.add_directive('add_protected_xhr_views', add_protected_xhr_views)

Once that's done, you can call the directive you've just added as a method of the :term:`configurator` object:

.. code-block:: python
    :linenos:

    config.add_route('xhr_route', '/xhr/{id}')
    config.add_protected_xhr_views('my.package')

Much better!

You can share your configuration code with others, too. Add your code to a Python package. Put the call to :meth:`~pyramid.config.Configurator.add_directive` in a function. When other programmers install your package, they'll be able to use your configuration by passing your function to a call to :meth:`~pyramid.config.Configurator.include`.

.. seealso::

    See also :ref:`add_directive`.

Introspect Your Application
---------------------------

If you're building a large, pluggable system, it's useful to be able to get a list of what has been plugged in *at application runtime*. For example, you might want to show users a set of tabs at the top of the screen based on a list of the views they registered.

:app:`Pyramid` provides an :term:`introspector` for just this purpose.

Here's an example of using :app:`Pyramid`\ 's :term:`introspector` from within a view:

.. code-block:: python
    :linenos:

    from pyramid.view import view_config
    from pyramid.response import Response

    @view_config(route_name='bar')
    def show_current_route_pattern(request):
        introspector = request.registry.introspector
        route_name = request.matched_route.name
        route_intr = introspector.get('routes', route_name)
        return Response(str(route_intr['pattern']))

.. seealso::

    See also :ref:`using_introspection`.