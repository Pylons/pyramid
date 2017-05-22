Advanced :app:`Pyramid` Design Features
=======================================

Pyramid has been built from the ground up to avoid the problems that other
frameworks can suffer.


No singletons
~~~~~~~~~~~~~

Pyramid is written in such a way that it requires your application to have
exactly zero "singleton" data structures.  Or put another way, Pyramid doesn't
require you to construct any "mutable globals".  Or put even another different
way, an import of a Pyramid application needn't have any "import-time side
effects".  This is esoteric-sounding, but if you've ever tried to cope with
parameterizing a Django ``settings.py`` file for multiple installations of the
same application, or if you've ever needed to monkey-patch some framework
fixture so that it behaves properly for your use case, or if you've ever wanted
to deploy your system using an asynchronous server, you'll end up appreciating
this feature.  It just won't be a problem. You can even run multiple copies of
a similar but not identically configured Pyramid application within the same
Python process.  This is good for shared hosting environments, where RAM is at
a premium.

View predicates and many views per route
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike many other systems, Pyramid allows you to associate more than one view
per route.  For example, you can create a route with the pattern ``/items`` and
when the route is matched, you can shuffle off the request to one view if the
request method is GET, another view if the request method is POST, etc. A
system known as "view predicates" allows for this.  Request method matching is
the most basic thing you can do with a view predicate.  You can also associate
views with other request parameters, such as the elements in the query string,
the Accept header, whether the request is an XHR request or not, and lots of
other things.  This feature allows you to keep your individual views clean.
They won't need much conditional logic, so they'll be easier to test.

Example: :ref:`view_configuration_parameters`.

Transaction management
~~~~~~~~~~~~~~~~~~~~~~

Pyramid's :term:`scaffold` system renders projects that include a *transaction
management* system, stolen from Zope.  When you use this transaction management
system, you cease being responsible for committing your data anymore.  Instead
Pyramid takes care of committing: it commits at the end of a request or aborts
if there's an exception.  Why is that a good thing?  Having a centralized place
for transaction management is a great thing.  If, instead of managing your
transactions in a centralized place, you sprinkle ``session.commit`` calls in
your application logic itself, you can wind up in a bad place.  Wherever you
manually commit data to your database, it's likely that some of your other code
is going to run *after* your commit. If that code goes on to do other important
things after that commit, and an error happens in the later code, you can
easily wind up with inconsistent data if you're not extremely careful.  Some
data will have been written to the database that probably should not have. 
Having a centralized commit point saves you from needing to think about this;
it's great for lazy people who also care about data integrity.  Either the
request completes successfully, and all changes are committed, or it does not,
and all changes are aborted.

Pyramid's transaction management system allows you to synchronize commits
between multiple databases. It also allows you to do things like conditionally
send email if a transaction commits, but otherwise keep quiet.

Example: :ref:`bfg_sql_wiki_tutorial` (note the lack of commit statements
anywhere in application code).

Configuration conflict detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a system is small, it's reasonably easy to keep it all in your head. But
when systems grow large, you may have hundreds or thousands of configuration
statements which add a view, add a route, and so forth.

Pyramid's configuration system keeps track of your configuration statements. If
you accidentally add two that are identical, or Pyramid can't make sense out of
what it would mean to have both statements active at the same time, it will
complain loudly at startup time.  It's not dumb though. It will automatically
resolve conflicting configuration statements on its own if you use the
configuration :meth:`~pyramid.config.Configurator.include` system. "More local"
statements are preferred over "less local" ones.  This allows you to
intelligently factor large systems into smaller ones.

Example: :ref:`conflict_detection`.

Configuration extensibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike other systems, Pyramid provides a structured "include" mechanism (see
:meth:`~pyramid.config.Configurator.include`) that allows you to combine
applications from multiple Python packages.  All the configuration statements
that can be performed in your "main" Pyramid application can also be performed
by included packages, including the addition of views, routes, subscribers, and
even authentication and authorization policies. You can even extend or override
an existing application by including another application's configuration in
your own, overriding or adding new views and routes to it.  This has the
potential to allow you to create a big application out of many other smaller
ones.  For example, if you want to reuse an existing application that already
has a bunch of routes, you can just use the ``include`` statement with a
``route_prefix``. The new application will live within your application at an
URL prefix.  It's not a big deal, and requires little up-front engineering
effort.

For example:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   if __name__ == '__main__':
      config = Configurator()
      config.include('pyramid_jinja2')
      config.include('pyramid_exclog')
      config.include('some.other.package', route_prefix='/somethingelse')

.. seealso::

    See also :ref:`including_configuration` and
    :ref:`building_an_extensible_app`.

Flexible authentication and authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyramid includes a flexible, pluggable authentication and authorization system.
No matter where your user data is stored, or what scheme you'd like to use to
permit your users to access your data, you can use a predefined Pyramid
plugpoint to plug in your custom authentication and authorization code.  If you
want to change these schemes later, you can just change it in one place rather
than everywhere in your code.  It also ships with prebuilt well-tested
authentication and authorization schemes out of the box.  But what if you don't
want to use Pyramid's built-in system?  You don't have to. You can just write
your own bespoke security code as you would in any other system.

Example: :ref:`enabling_authorization_policy`.

Traversal
~~~~~~~~~

:term:`Traversal` is a concept stolen from :term:`Zope`.  It allows you to
create a tree of resources, each of which can be addressed by one or more URLs.
Each of those resources can have one or more *views* associated with it. If
your data isn't naturally treelike, or you're unwilling to create a treelike
representation of your data, you aren't going to find traversal very useful. 
However, traversal is absolutely fantastic for sites that need to be
arbitrarily extensible. It's a lot easier to add a node to a tree than it is to
shoehorn a route into an ordered list of other routes, or to create another
entire instance of an application to service a department and glue code to
allow disparate apps to share data.  It's a great fit for sites that naturally
lend themselves to changing departmental hierarchies, such as content
management systems and document management systems.  Traversal also lends
itself well to systems that require very granular security ("Bob can edit
*this* document" as opposed to "Bob can edit documents").

Examples: :ref:`hello_traversal_chapter` and
:ref:`much_ado_about_traversal_chapter`.

Tweens
~~~~~~

Pyramid has a sort of internal WSGI-middleware-ish pipeline that can be hooked
by arbitrary add-ons named "tweens".  The debug toolbar is a "tween", and the
``pyramid_tm`` transaction manager is also.  Tweens are more useful than WSGI
:term:`middleware` in some circumstances because they run in the context of
Pyramid itself, meaning you have access to templates and other renderers, a
"real" request object, and other niceties.

Example: :ref:`registering_tweens`.

View response adapters
~~~~~~~~~~~~~~~~~~~~~~

A lot is made of the aesthetics of what *kinds* of objects you're allowed to
return from view callables in various frameworks.  In a previous section in
this document, we showed you that, if you use a :term:`renderer`, you can
usually return a dictionary from a view callable instead of a full-on
:term:`Response` object.  But some frameworks allow you to return strings or
tuples from view callables.  When frameworks allow for this, code looks
slightly prettier, because fewer imports need to be done, and there is less
code.  For example, compare this:

.. code-block:: python
   :linenos:

   def aview(request):
       return "Hello world!"

To this:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def aview(request):
       return Response("Hello world!")

The former is "prettier", right?

Out of the box, if you define the former view callable (the one that simply
returns a string) in Pyramid, when it is executed, Pyramid will raise an
exception.  This is because "explicit is better than implicit", in most cases,
and by default Pyramid wants you to return a :term:`Response` object from a
view callable.  This is because there's usually a heck of a lot more to a
response object than just its body.  But if you're the kind of person who
values such aesthetics, we have an easy way to allow for this sort of thing:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator
   from pyramid.response import Response

   def string_response_adapter(s):
       response = Response(s)
       response.content_type = 'text/html'
       return response

   if __name__ == '__main__':
       config = Configurator()
       config.add_response_adapter(string_response_adapter, basestring)

Do that once in your Pyramid application at startup.  Now you can return
strings from any of your view callables, e.g.:

.. code-block:: python
   :linenos:

   def helloview(request):
       return "Hello world!"

   def goodbyeview(request):
       return "Goodbye world!"

Oh noes!  What if you want to indicate a custom content type?  And a custom
status code?  No fear:

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
       config.add_response_adapter(string_response_adapter, basestring)
       config.add_response_adapter(tuple_response_adapter, tuple)

Once this is done, both of these view callables will work:

.. code-block:: python
   :linenos:

   def aview(request):
       return "Hello world!"

   def anotherview(request):
       return (403, 'text/plain', "Forbidden")

Pyramid defaults to explicit behavior, because it's the most generally useful,
but provides hooks that allow you to adapt the framework to localized aesthetic
desires.

.. seealso::

    See also :ref:`using_iresponse`.

"Global" response object
~~~~~~~~~~~~~~~~~~~~~~~~

"Constructing these response objects in my view callables is such a chore! And
I'm way too lazy to register a response adapter, as per the prior section," you
say.  Fine.  Be that way:

.. code-block:: python
   :linenos:

   def aview(request):
       response = request.response
       response.body = 'Hello world!'
       response.content_type = 'text/plain'
       return response

.. seealso::

    See also :ref:`request_response_attr`.

Automating repetitive configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Does Pyramid's configurator allow you to do something, but you're a little
adventurous and just want it a little less verbose?  Or you'd like to offer up
some handy configuration feature to other Pyramid users without requiring that
we change Pyramid?  You can extend Pyramid's :term:`Configurator` with your own
directives.  For example, let's say you find yourself calling
:meth:`pyramid.config.Configurator.add_view` repetitively.  Usually you can
take the boring away by using existing shortcuts, but let's say that this is a
case where there is no such shortcut:

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

Pretty tedious right?  You can add a directive to the Pyramid configurator to
automate some of the tedium away:

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

Once that's done, you can call the directive you've just added as a method of
the Configurator object:

.. code-block:: python
   :linenos:

   config.add_route('xhr_route', '/xhr/{id}')
   config.add_protected_xhr_views('my.package')

Your previously repetitive configuration lines have now morphed into one line.

You can share your configuration code with others this way, too, by packaging
it up and calling :meth:`~pyramid.config.Configurator.add_directive` from
within a function called when another user uses the
:meth:`~pyramid.config.Configurator.include` method against your code.

.. seealso::

    See also :ref:`add_directive`.

Programmatic introspection
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're building a large system that other users may plug code into, it's
useful to be able to get an enumeration of what code they plugged in *at
application runtime*.  For example, you might want to show them a set of tabs
at the top of the screen based on an enumeration of views they registered.

This is possible using Pyramid's :term:`introspector`.

Here's an example of using Pyramid's introspector from within a view callable:

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