.. index::
   single: Agendaless Consulting
   single: Pylons
   single: Django
   single: Zope
   single: frameworks vs. libraries
   single: framework

:app:`Pyramid` Introduction
==============================

:app:`Pyramid` is a general, open source, Python web application development
*framework*. Its primary goal is to make it easier for a Python developer to
create web applications.

.. sidebar:: Frameworks vs. Libraries

   A *framework* differs from a *library* in one very important way:
   library code is always *called* by code that you write, while a
   framework always *calls* code that you write.  Using a set of
   libraries to create an application is usually easier than using a
   framework initially, because you can choose to cede control to
   library code you have not authored very selectively. But when you
   use a framework, you are required to cede a greater portion of
   control to code you have not authored: code that resides in the
   framework itself.  You needn't use a framework at all to create a
   web application using Python.  A rich set of libraries already
   exists for the platform.  In practice, however, using a framework
   to create an application is often more practical than rolling your
   own via a set of libraries if the framework provides a set of
   facilities that fits your application requirements.

Pyramid attempts to follow these design and engineering principles:

Simplicity
  :app:`Pyramid` takes a *"pay only for what you eat"* approach.  You can get
  results even if you have only a partial understanding of :app:`Pyramid`.
  It doesn’t force you to use any particular technology to produce an
  application, and we try to keep the core set of concepts that you need to
  understand to a minimum.

Minimalism
  :app:`Pyramid` tries to solve only the fundamental problems of creating
  a web application: the mapping of URLs to code, templating, security and
  serving static assets. We consider these to be the core activities that are
  common to nearly all web applications.

Documentation
  Pyramid's minimalism means that it is easier for us to maintain complete
  and up-to-date documentation. It is our goal that no aspect of Pyramid
  is undocumented.

Speed
  :app:`Pyramid` is designed to provide noticeably fast execution for common
  tasks such as templating and simple response generation. Although "hardware
  is cheap", the limits of this approach become painfully evident when one
  finds him or herself responsible for managing a great many machines.

Reliability
  :app:`Pyramid` is developed conservatively and tested exhaustively. Where
  Pyramid source code is concerned, our motto is: "If it ain’t tested, it’s
  broke".

Openness
  As with Python, the Pyramid software is distributed under a `permissive
  open source license <http://repoze.org/license.html>`_.

.. _what_makes_pyramid_unique:

What Makes Pyramid Unique
-------------------------

Understandably, people don't usually want to hear about squishy engineering
principles, they want to hear about concrete stuff that solves their
problems.  With that in mind, what would make someone want to use Pyramid
instead of one of the many other web frameworks available today?  What makes
Pyramid unique?

This is a hard question to answer, because there are lots of excellent
choices, and it's actually quite hard to make a wrong choice, particularly in
the Python web framework market.  But one reasonable answer is this: you can
write very small applications in Pyramid without needing to know a lot.
"What?", you say, "that can't possibly be a unique feature, lots of other web
frameworks let you do that!"  Well, you're right.  But unlike many other
systems, you can also write very large applications in Pyramid if you learn a
little more about it.  Pyramid will allow you to become productive quickly,
and will grow with you; it won't hold you back when your application is small
and it won't get in your way when your application becomes large.  "Well
that's fine," you say, "lots of other frameworks let me write large apps
too."  Absolutely.  But other Python web frameworks don't seamlessly let you
do both.  They seem to fall into two non-overlapping categories: frameworks
for "small apps" and frameworks for "big apps".  The "small app" frameworks
typically sacrifice "big app" features, and vice versa.

We don't think it's a universally reasonable suggestion to write "small apps"
in a "small framework" and "big apps" in a "big framework".  You can't really
know to what size every application will eventually grow.  We don't really
want to have to rewrite a previously small application in another framework
when it gets "too big".  We believe the current binary distinction between
frameworks for small and large applications is just false; a well-designed
framework should be able to be good at both.  Pyramid strives to be that kind
of framework.

To this end, Pyramid provides a set of features, that, combined, are unique
amongst Python web frameworks.  Lots of other frameworks contain some
combination of these features; Pyramid of course actually stole many of them
from those other frameworks.  But Pyramid is the only one that has all of
them in one place, documented appropriately, and useful a la carte without
necessarily paying for the entire banquet.  These are detailed below.

Single-file applications
~~~~~~~~~~~~~~~~~~~~~~~~

You can write a Pyramid application that lives entirely in one Python file,
not unlike existing Python microframeworks.  This is beneficial for one-off
prototyping, bug reproduction, and very small applications.  These
applications are easy to understand because all the information about the
application lives in a single place, and you can deploy them without needing
to understand much about Python distributions and packaging.  Pyramid isn't
really marketed as a microframework, but it allows you to do almost
everything that frameworks that are marketed as micro offer in very similar
ways.

.. literalinclude:: helloworld.py

See also :ref:`firstapp_chapter`.

Decorator-based configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you like the idea of framework configuration statements living next to the
code it configures, so you don't have to constantly switch between files to
refer to framework configuration when adding new code, you can use Pyramid
decorators to localize the configuration.  For example:

.. code-block:: python

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(route_name='fred')
   def fred_view(request):
       return Response('fred')

However, unlike some other systems, using decorators for Pyramid
configuration does not make your application difficult to extend, test or
reuse.  The :class:`~pyramid.view.view_config` decorator, for example, does
not actually *change* the input or output of the function it decorates, so
testing it is a "WYSIWYG" operation; you don't need to understand the
framework to test your own code, you just behave as if the decorator is not
there.  You can also instruct Pyramid to ignore some decorators, or use
completely imperative configuration instead of decorators to add views.
Pyramid decorators are inert instead of eager: you detect and activate them
with a :term:`scan`.

Example: :ref:`mapping_views_using_a_decorator_section`.

URL generation
~~~~~~~~~~~~~~

Pyramid is capable of generating URLs for resources, routes, and static
assets.  Its URL generation APIs are easy to use and flexible.  If you use
Pyramid's various APIs for generating URLs, you can change your configuration
around arbitrarily without fear of breaking a link on one of your web pages.

Example: :ref:`generating_route_urls`.

Static file serving
~~~~~~~~~~~~~~~~~~~

Pyramid is perfectly willing to serve static files itself.  It won't make you
use some external web server to do that.  You can even serve more than one
set of static files in a single Pyramid web application (e.g. ``/static`` and
``/static2``).  You can also, optionally, place your files on an external web
server and ask Pyramid to help you generate URLs to those files, so you can
use Pyramid's internal fileserving while doing development, and a faster
static file server in production without changing any code.

Example: :ref:`static_assets_section`.

Debug Toolbar
~~~~~~~~~~~~~

Pyramid's debug toolbar comes activated when you use a Pyramid scaffold to
render a project.  This toolbar overlays your application in the browser, and
allows you access to framework data such as the routes configured, the last
renderings performed, the current set of packages installed, SQLAlchemy
queries run, logging data, and various other facts.  When an exception
occurs, you can use its interactive debugger to poke around right in your
browser to try to determine the cause of the exception.  It's handy.

Example: :ref:`debug_toolbar`.

Debugging settings
~~~~~~~~~~~~~~~~~~

Pyramid has debugging settings that allow you to print Pyramid runtime
information to the console when things aren't behaving as you're expecting.
For example, you can turn on "debug_notfound", which prints an informative
message to the console every time a URL does not match any view.  You can
turn on "debug_authorization", which lets you know why a view execution was
allowed or denied by printing a message to the console.  These features are
useful for those WTF moments.

There are also a number of commands that you can invoke within a Pyramid
environment that allow you to introspect the configuration of your system:
``proutes`` shows all configured routes for an application in the order
they'll be evaluated for matching; ``pviews`` shows all configured views for
any given URL.  These are also WTF-crushers in some circumstances.

Examples: :ref:`debug_authorization_section` and :ref:`command_line_chapter`.

Add-ons
~~~~~~~~

Pyramid has an extensive set of add-ons held to the same quality standards as
the Pyramid core itself.  Add-ons are packages which provide functionality
that the Pyramid core doesn't.  Add-on packages already exist which let you
easily send email, let you use the Jinja2 templating system, let you use
XML-RPC or JSON-RPC, let you integrate with jQuery Mobile, etc.

Examples: http://docs.pylonsproject.org/docs/pyramid.html#pyramid-add-on-documentation

Class-based and function-based views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyramid has a structured, unified concept of a :term:`view callable`.
View callables can be functions, methods of classes, or even instances.  When
you add a new view callable, you can choose to make it a function or a method
of a class; in either case, Pyramid treats it largely the same way.  You can
change your mind later, and move code between methods of classes and
functions.  A collection of similar view callables can be attached to a
single class as methods, if that floats your boat, and they can share
initialization code as necessary.  All kinds of views are easy to understand
and use and operate similarly.  There is no phony distinction between them;
they can be used for the same purposes.

Here's a view callable defined as a function:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   @view_config(route_name='aview')
   def aview(request):
       return Response('one')

Here's a few views defined as methods of a class instead:

.. code-block:: python
   :linenos:

   from pyramid.response import Response
   from pyramid.view import view_config

   class AView(object):
       def __init__(self, request):
           self.request = request

       @view_config(route_name='view_one')
       def view_one(request):
           return Response('one')

       @view_config(route_name='view_two')
       def view_two(request):
           return Response('two')

See also :ref:`view_config_placement`.

.. _intro_asset_specs:

Asset specifications
~~~~~~~~~~~~~~~~~~~~

Asset specifications are strings that contain both a Python package name and
a file or directory name, e.g. ``MyPackage:static/index.html``.  Use of these
specifications is omnipresent in Pyramid.  An asset specification can refer
to a template, a translation directory, or any other package-bound static
resource.  This makes a system built on Pyramid extensible, because you don't
have to rely on globals ("*the* static directory") or lookup schemes ("*the*
ordered set of template directories") to address your files.  You can move
files around as necessary, and include other packages that may not share your
system's templates or static files without encountering conflicts.

Because asset specifications are used heavily in Pyramid, we've also provided
a way to allow users to override assets.  Say you love a system that someone
else has created with Pyramid but you just need to change "that one template"
to make it all better.  No need to fork the application.  Just override the
asset specification for that template with your own inside a wrapper, and
you're good to go.

Examples: :ref:`asset_specifications` and :ref:`overriding_assets_section`.

Extensible templating
~~~~~~~~~~~~~~~~~~~~~

Pyramid has a structured API that allows for pluggability of "renderers".
Templating systems such as Mako, Genshi, Chameleon, and Jinja2 can be treated
as renderers.  Renderer bindings for all of these templating systems already
exist for use in Pyramid.  But if you'd rather use another, it's not a big
deal.  Just copy the code from an existing renderer package, and plug in your
favorite templating system.  You'll then be able to use that templating
system from within Pyramid just as you'd use one of the "built-in" templating
systems.

Pyramid does not make you use a single templating system exclusively.  You
can use multiple templating systems, even in the same project.

Example: :ref:`templates_used_directly`.

Rendered views can return dictionaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you use a :term:`renderer`, you don't have to return a special kind of
"webby" ``Response`` object from a view.  Instead, you can return a
dictionary instead, and Pyramid will take care of converting that dictionary
to a Response using a template on your behalf.  This makes the view easier to
test, because you don't have to parse HTML in your tests; just make an
assertion instead that the view returns "the right stuff" in the dictionary
it returns.  You can write "real" unit tests instead of functionally testing
all of your views.

For example, instead of:

.. code-block:: python
   :linenos:

    from pyramid.renderers import render_to_response

    def myview(request):
        return render_to_response('myapp:templates/mytemplate.pt', {'a':1},
                                  request=request)

You can do this:

.. code-block:: python
   :linenos:

    from pyramid.view import view_config

    @view_config(renderer='myapp:templates/mytemplate.pt')
    def myview(request):
        return {'a':1}

When this view callable is called by Pyramid, the ``{'a':1}`` dictionary will
be rendered to a response on your behalf.  The string passed as ``renderer=``
above is an :term:`asset specification`.  It is in the form
``packagename:directoryname/filename.ext``.  In this case, it names the
``mytemplate.pt`` file in the ``templates`` directory within the ``myapp``
Python package.  Asset specifications are omnipresent in Pyramid: see
:ref:`intro_asset_specs` for more information.

Example: :ref:`renderers_chapter`.

Event system
~~~~~~~~~~~~

Pyramid emits *events* during its request processing lifecycle.  You can
subscribe any number of listeners to these events.  For example, to be
notified of a new request, you can subscribe to the ``NewRequest`` event.  To
be notified that a template is about to be rendered, you can subscribe to the
``BeforeRender`` event, and so forth.  Using an event publishing system as a
framework notification feature instead of hardcoded hook points tends to make
systems based on that framework less brittle.

You can also use Pyramid's event system to send your *own* events.  For
example, if you'd like to create a system that is itself a framework, and may
want to notify subscribers that a document has just been indexed, you can
create your own event type (``DocumentIndexed`` perhaps) and send the event
via Pyramid.  Users of this framework can then subscribe to your event like
they'd subscribe to the events that are normally sent by Pyramid itself.

Example: :ref:`events_chapter` and :ref:`event_types`.

Built-in internationalization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyramid ships with internationalization-related features in its core:
localization, pluralization, and creating message catalogs from source files
and templates.  Pyramid allows for a plurality of message catalog via the use
of translation domains: you can create a system that has its own translations
without conflict with other translations in other domains.

Example: :ref:`i18n_chapter`.

HTTP caching
~~~~~~~~~~~~

Pyramid provides an easy way to associate views with HTTP caching policies.
You can just tell Pyramid to configure your view with an ``http_cache``
statement, and it will take care of the rest::

   @view_config(http_cache=3600) # 60 minutes
   def myview(request): ....

Pyramid will add appropriate ``Cache-Control`` and ``Expires`` headers to
responses generated when this view is invoked.

See the :meth:`~pyramid.config.Configurator.add_view` method's
``http_cache`` documentation for more information.

Sessions
~~~~~~~~

Pyramid has built-in HTTP sessioning.  This allows you to associate data with
otherwise anonymous users between requests.  Lots of systems do this.  But
Pyramid also allows you to plug in your own sessioning system by creating
some code that adheres to a documented interface.  Currently there is a
binding package for the third-party Beaker sessioning system that does exactly
this.  But if you have a specialized need (perhaps you want to store your
session data in MongoDB), you can.  You can even switch between
implementations without changing your application code.

Example: :ref:`sessions_chapter`.

Speed
~~~~~

The Pyramid core is, as far as we can tell, at least marginally faster than
any other existing Python web framework.  It has been engineered from the
ground up for speed.  It only does as much work as absolutely necessary when
you ask it to get a job done.  Extraneous function calls and suboptimal
algorithms in its core codepaths are avoided.  It is feasible to get, for
example, between 3500 and 4000 requests per second from a simple Pyramid view
on commodity dual-core laptop hardware and an appropriate WSGI server
(mod_wsgi or gunicorn).  In any case, performance statistics are largely
useless without requirements and goals, but if you need speed, Pyramid will
almost certainly never be your application's bottleneck; at least no more
than Python will be a bottleneck.

Example: http://blog.curiasolutions.com/the-great-web-framework-shootout/

Exception views
~~~~~~~~~~~~~~~

Exceptions happen.  Rather than deal with exceptions that might present
themselves to a user in production in an ad-hoc way, Pyramid allows you to
register an :term:`exception view`.  Exception views are like regular Pyramid
views, but they're only invoked when an exception "bubbles up" to Pyramid
itself.  For example, you might register an exception view for the
:exc:`Exception` exception, which will catch *all* exceptions, and present a
pretty "well, this is embarrassing" page.  Or you might choose to register an
exception view for only specific kinds of application-specific exceptions,
such as an exception that happens when a file is not found, or an exception
that happens when an action cannot be performed because the user doesn't have
permission to do something.  In the former case, you can show a pretty "Not
Found" page; in the latter case you might show a login form.

Example: :ref:`exception_views`.

No singletons
~~~~~~~~~~~~~

Pyramid is written in such a way that it requires your application to have
exactly zero "singleton" data structures.  Or, put another way, Pyramid
doesn't require you to construct any "mutable globals".  Or put even a
different way, an import of a Pyramid application needn't have any
"import-time side effects".  This is esoteric-sounding, but if you've ever
tried to cope with parameterizing a Django "settings.py" file for multiple
installations of the same application, or if you've ever needed to
monkey-patch some framework fixture so that it behaves properly for your use
case, or if you've ever wanted to deploy your system using an asynchronous
server, you'll end up appreciating this feature.  It just won't be a problem.
You can even run multiple copies of a similar but not identically configured
Pyramid application within the same Python process.  This is good for shared
hosting environments, where RAM is at a premium.

View predicates and many views per route
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike many other systems, Pyramid allows you to associate more than one view
per route.  For example, you can create a route with the pattern ``/items``
and when the route is matched, you can shuffle off the request to one view if
the request method is GET, another view if the request method is POST, etc.
A system known as "view predicates" allows for this.  Request method matching
is the very most basic thing you can do with a view predicate.  You can also
associate views with other request parameters such as the elements in the
query string, the Accept header, whether the request is an XHR request or
not, and lots of other things.  This feature allows you to keep your
individual views "clean"; they won't need much conditional logic, so they'll
be easier to test.

Example: :ref:`view_configuration_parameters`.

Transaction management
~~~~~~~~~~~~~~~~~~~~~~

Pyramid's :term:`scaffold` system renders projects that include a
*transaction management* system, stolen from Zope.  When you use this
transaction management system, you cease being responsible for committing
your data anymore.  Instead, Pyramid takes care of committing: it commits at
the end of a request or aborts if there's an exception.  Why is that a good
thing?  Having a centralized place for transaction management is a great
thing.  If, instead of managing your transactions in a centralized place, you
sprinkle ``session.commit`` calls in your application logic itself, you can
wind up in a bad place.  Wherever you manually commit data to your database,
it's likely that some of your other code is going to run *after* your commit.
If that code goes on to do other important things after that commit, and an
error happens in the later code, you can easily wind up with inconsistent
data if you're not extremely careful.  Some data will have been written to
the database that probably should not have.  Having a centralized commit
point saves you from needing to think about this; it's great for lazy people
who also care about data integrity.  Either the request completes
successfully, and all changes are committed, or it does not, and all changes
are aborted.

Also, Pyramid's transaction management system allows you to synchronize
commits between multiple databases, and allows you to do things like
conditionally send email if a transaction commits, but otherwise keep quiet.

Example: :ref:`bfg_sql_wiki_tutorial` (note the lack of commit statements
anywhere in application code).

Configuration conflict detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a system is small, it's reasonably easy to keep it all in your head.
But when systems grow large, you may have hundreds or thousands of
configuration statements which add a view, add a route, and so forth.
Pyramid's configuration system keeps track of your configuration statements,
and if you accidentally add two that are identical, or Pyramid can't make
sense out of what it would mean to have both statements active at the same
time, it will complain loudly at startup time.  It's not dumb though: it will
automatically resolve conflicting configuration statements on its own if you
use the configuration :meth:`~pyramid.config.Configurator.include` system:
"more local" statements are preferred over "less local" ones.  This allows
you to intelligently factor large systems into smaller ones.

Example: :ref:`conflict_detection`.

Configuration extensibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike other systems, Pyramid provides a structured "include" mechanism (see
:meth:`~pyramid.config.Configurator.include`) that allows you to compose
applications from multiple Python packages.  All the configuration statements
that can be performed in your "main" Pyramid application can also be
performed by included packages including the addition of views, routes,
subscribers, and even authentication and authorization policies. You can even
extend or override an existing application by including another application's
configuration in your own, overriding or adding new views and routes to
it.  This has the potential to allow you to compose a big application out of
many other smaller ones.  For example, if you want to reuse an existing
application that already has a bunch of routes, you can just use the
``include`` statement with a ``route_prefix``; the new application will live
within your application at a URL prefix.  It's not a big deal, and requires
little up-front engineering effort.

For example:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   if __name__ == '__main__':
      config = Configurator()
      config.include('pyramid_jinja2')
      config.include('pyramid_exclog')
      config.include('some.other.guys.package', route_prefix='/someotherguy')

See also :ref:`including_configuration` and :ref:`building_an_extensible_app`

Flexible authentication and authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyramid includes a flexible, pluggable authentication and authorization
system.  No matter where your user data is stored, or what scheme you'd like
to use to permit your users to access your data, you can use a predefined
Pyramid plugpoint to plug in your custom authentication and authorization
code.  If you want to change these schemes later, you can just change it in
one place rather than everywhere in your code.  It also ships with prebuilt
well-tested authentication and authorization schemes out of the box.  But
what if you don't want to use Pyramid's built-in system?  You don't have to.
You can just write your own bespoke security code as you would in any other
system.

Example: :ref:`enabling_authorization_policy`.

Traversal
~~~~~~~~~

:term:`Traversal` is a concept stolen from :term:`Zope`.  It allows you to
create a tree of resources, each of which can be addressed by one or more
URLs.  Each of those resources can have one or more *views* associated with
it. If your data isn't naturally treelike (or you're unwilling to create a
treelike representation of your data), you aren't going to find traversal
very useful.  However, traversal is absolutely fantastic for sites that need
to be arbitrarily extensible: it's a lot easier to add a node to a tree than
it is to shoehorn a route into an ordered list of other routes, or to create
another entire instance of an application to service a department and glue
code to allow disparate apps to share data.  It's a great fit for sites that
naturally lend themselves to changing departmental hierarchies, such as
content management systems and document management systems.  Traversal also lends itself well to
systems that require very granular security ("Bob can edit *this* document"
as opposed to "Bob can edit documents").

Example: :ref:`much_ado_about_traversal_chapter`.

Tweens
~~~~~~

Pyramid has a sort of internal WSGI-middleware-ish pipeline that can be
hooked by arbitrary add-ons named "tweens".  The debug toolbar is a "tween",
and the ``pyramid_tm`` transaction manager is also.  Tweens are more useful
than WSGI middleware in some circumstances because they run in the context of
Pyramid itself, meaning you have access to templates and other renderers, a
"real" request object, and other niceties.

Example: :ref:`registering_tweens`.

View response adapters
~~~~~~~~~~~~~~~~~~~~~~

A lot is made of the aesthetics of what *kinds* of objects you're allowed to
return from view callables in various frameworks.  In a previous section in
this document we showed you that, if you use a :term:`renderer`, you can
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
exception.  This is because "explicit is better than implicit", in most
cases, and by default, Pyramid wants you to return a :term:`Response` object
from a view callable.  This is because there's usually a heck of a lot more
to a response object than just its body.  But if you're the kind of person
who values such aesthetics, we have an easy way to allow for this sort of
thing:

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

Pyramid defaults to explicit behavior, because it's the most generally
useful, but provides hooks that allow you to adapt the framework to localized
aesthetic desires.

See also :ref:`using_iresponse`.

"Global" response object
~~~~~~~~~~~~~~~~~~~~~~~~

"Constructing these response objects in my view callables is such a chore!
And I'm way too lazy to register a response adapter, as per the prior
section," you say.  Fine.  Be that way:

.. code-block:: python
   :linenos:

   def aview(request):
       response = request.response
       response.body = 'Hello world!'
       response.content_type = 'text/plain'
       return response

See also :ref:`request_response_attr`.

Automating repetitive configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Does Pyramid's configurator allow you to do something, but you're a little
adventurous and just want it a little less verbose?  Or you'd like to offer
up some handy configuration feature to other Pyramid users without requiring
that we change Pyramid?  You can extend Pyramid's :term:`Configurator` with
your own directives.  For example, let's say you find yourself calling
:meth:`pyramid.config.Configurator.add_view` repetitively.  Usually you can
take the boring away by using existing shortcuts, but let's say that this is
a case such a way that no existing shortcut works to take the boring away:

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

You can share your configuration code with others this way too by packaging
it up and calling :meth:`~pyramid.config.Configurator.add_directive` from
within a function called when another user uses the
:meth:`~pyramid.config.Configurator.include` method against your code.

See also :ref:`add_directive`.

Testing
~~~~~~~

Every release of Pyramid has 100% statement coverage via unit and integration
tests, as measured by the ``coverage`` tool available on PyPI.  It also has
greater than 95% decision/condition coverage as measured by the
``instrumental`` tool available on PyPI.  It is automatically tested by the
Jenkins tool on Python 2.6, Python 2.7, Python 3.2 and PyPy after each commit
to its GitHub repository.  Official Pyramid add-ons are held to a similar
testing standard.  We still find bugs in Pyramid and its official add-ons,
but we've noticed we find a lot more of them while working on other projects
that don't have a good testing regime.

Example: http://jenkins.pylonsproject.org/

Support
~~~~~~~

It's our goal that no Pyramid question go unanswered.  Whether you ask a
question on IRC, on the Pylons-discuss maillist, or on StackOverflow, you're
likely to get a reasonably prompt response.  We don't tolerate "support
trolls" or other people who seem to get their rocks off by berating fellow
users in our various offical support channels.  We try to keep it well-lit
and new-user-friendly.

Example: Visit irc\://freenode.net#pyramid (the ``#pyramid`` channel on
irc.freenode.net in an IRC client) or the pylons-discuss maillist at
http://groups.google.com/group/pylons-discuss/ .

Documentation
~~~~~~~~~~~~~

It's a constant struggle, but we try to maintain a balance between
completeness and new-user-friendliness in the official narrative Pyramid
documentation (concrete suggestions for improvement are always appreciated,
by the way).  We also maintain a "cookbook" of recipes, which are usually
demonstrations of common integration scenarios, too specific to add to the
official narrative docs.  In any case, the Pyramid documentation is
comprehensive.

Example: The rest of this documentation and the cookbook at
http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/ .

.. index::
   single: Pylons Project

What Is The Pylons Project?
---------------------------

:app:`Pyramid` is a member of the collection of software published under the
Pylons Project.  Pylons software is written by a loose-knit community of
contributors.  The `Pylons Project website <http://pylonsproject.org>`_
includes details about how :app:`Pyramid` relates to the Pylons Project.

.. index::
   single: pyramid and other frameworks
   single: Zope
   single: Pylons
   single: Django
   single: MVC

:app:`Pyramid` and Other Web Frameworks
------------------------------------------

The first release of Pyramid's predecessor (named :mod:`repoze.bfg`) was made
in July of 2008.  At the end of 2010, we changed the name of
:mod:`repoze.bfg` to :app:`Pyramid`.  It was merged into the Pylons project
as :app:`Pyramid` in November of that year.

:app:`Pyramid` was inspired by :term:`Zope`, :term:`Pylons` (version
1.0) and :term:`Django`.  As a result, :app:`Pyramid` borrows several
concepts and features from each, combining them into a unique web
framework.

Many features of :app:`Pyramid` trace their origins back to :term:`Zope`.
Like Zope applications, :app:`Pyramid` applications can be easily extended:
if you obey certain constraints, the application you produce can be reused,
modified, re-integrated, or extended by third-party developers without
forking the original application.  The concepts of :term:`traversal` and
declarative security in :app:`Pyramid` were pioneered first in Zope.

The :app:`Pyramid` concept of :term:`URL dispatch` is inspired by the
:term:`Routes` system used by :term:`Pylons` version 1.0.  Like Pylons
version 1.0, :app:`Pyramid` is mostly policy-free.  It makes no
assertions about which database you should use, and its built-in
templating facilities are included only for convenience.  In essence,
it only supplies a mechanism to map URLs to :term:`view` code, along
with a set of conventions for calling those views.  You are free to
use third-party components that fit your needs in your applications.

The concept of :term:`view` is used by :app:`Pyramid` mostly as it would be
by Django.  :app:`Pyramid` has a documentation culture more like Django's
than like Zope's.

Like :term:`Pylons` version 1.0, but unlike :term:`Zope`, a :app:`Pyramid`
application developer may use completely imperative code to perform common
framework configuration tasks such as adding a view or a route.  In Zope,
:term:`ZCML` is typically required for similar purposes.  In :term:`Grok`, a
Zope-based web framework, :term:`decorator` objects and class-level
declarations are used for this purpose.  Out of the box, Pyramid supports
imperative and decorator-based configuration; :term:`ZCML` may be used via an
add-on package named ``pyramid_zcml``.

Also unlike :term:`Zope` and unlike other "full-stack" frameworks such
as :term:`Django`, :app:`Pyramid` makes no assumptions about which
persistence mechanisms you should use to build an application.  Zope
applications are typically reliant on :term:`ZODB`; :app:`Pyramid`
allows you to build :term:`ZODB` applications, but it has no reliance
on the ZODB software.  Likewise, :term:`Django` tends to assume that
you want to store your application's data in a relational database.
:app:`Pyramid` makes no such assumption; it allows you to use a
relational database but doesn't encourage or discourage the decision.

Other Python web frameworks advertise themselves as members of a class
of web frameworks named `model-view-controller
<http://en.wikipedia.org/wiki/Model–view–controller>`_ frameworks.
Insofar as this term has been claimed to represent a class of web
frameworks, :app:`Pyramid` also generally fits into this class.

.. sidebar:: You Say :app:`Pyramid` is MVC, But Where's The Controller?

   The :app:`Pyramid` authors believe that the MVC pattern just doesn't
   really fit the web very well. In a :app:`Pyramid` application, there is a
   resource tree, which represents the site structure, and views, which tend
   to present the data stored in the resource tree and a user-defined "domain
   model".  However, no facility provided *by the framework* actually
   necessarily maps to the concept of a "controller" or "model".  So if you
   had to give it some acronym, I guess you'd say :app:`Pyramid` is actually
   an "RV" framework rather than an "MVC" framework.  "MVC", however, is
   close enough as a general classification moniker for purposes of
   comparison with other web frameworks.
