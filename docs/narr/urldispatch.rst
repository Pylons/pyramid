.. index::
   single: URL dispatch

.. _urldispatch_chapter:

URL Dispatch
============

:term:`URL dispatch` provides a simple way to map URLs to :term:`view` code
using a simple pattern matching language.  An ordered set of patterns is
checked one-by-one.  If one of the patterns matches the path information
associated with a request, a particular :term:`view callable` is invoked.  A
view callable is a specific bit of code, defined in your application, that
receives the :term:`request` and returns a :term:`response` object.

High-Level Operational Overview
-------------------------------

If route configuration is present in an application, the :app:`Pyramid`
:term:`Router` checks every incoming request against an ordered set of URL
matching patterns present in a *route map*.

If any route pattern matches the information in the :term:`request`,
:app:`Pyramid` will invoke :term:`view lookup` to find a matching view.

If no route pattern in the route map matches the information in the
:term:`request` provided in your application, :app:`Pyramid` will fail over
to using :term:`traversal` to perform resource location and view lookup.

.. index::
   single: route configuration

Route Configuration
-------------------

:term:`Route configuration` is the act of adding a new :term:`route` to an
application.  A route has a *name*, which acts as an identifier to be used
for URL generation.  The name also allows developers to associate a view
configuration with the route.  A route also has a *pattern*, meant to match
against the ``PATH_INFO`` portion of a URL (the portion following the scheme
and port, e.g. ``/foo/bar`` in the URL ``http://localhost:8080/foo/bar``). It
also optionally has a ``factory`` and a set of :term:`route predicate`
attributes.

.. index::
   single: add_route

.. _config-add-route:

Configuring a Route to Match a View
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :meth:`pyramid.config.Configurator.add_route` method adds a single
:term:`route configuration` to the :term:`application registry`.  Here's an
example:

.. ignore-next-block
.. code-block:: python

   # "config" below is presumed to be an instance of the
   # pyramid.config.Configurator class; "myview" is assumed
   # to be a "view callable" function
   from views import myview
   config.add_route('myroute', '/prefix/{one}/{two}')
   config.add_view(myview, route_name='myroute')

When a :term:`view callable` added to the configuration by way of
:meth:`~pyramid.config.Configurator.add_view` bcomes associated with a route
via its ``route_name`` predicate, that view callable will always be found and
invoked when the associated route pattern matches during a request.

More commonly, you will not use any ``add_view`` statements in your project's
"setup" code, instead only using ``add_route`` statements using a
:term:`scan` for to associate view callables with routes.  For example, if
this is a portion of your project's ``__init__.py``:

.. code-block:: python

   # in your project's __init__.py (mypackage.__init__)

   config.add_route('myroute', '/prefix/{one}/{two}')
   config.scan('mypackage')

Note that we don't call :meth:`~pyramid.config.Configurator.add_view` in this
setup code.  However, the above :term:`scan` execution
``config.scan('mypackage')`` will pick up all :term:`configuration
decoration`, including any objects decorated with the
:class:`pyramid.view.view_config` decorator in the ``mypackage`` Python
pakage.  For example, if you have a ``views.py`` in your package, a scan will
pick up any of its configuration decorators, so we can add one there that
that references ``myroute`` as a ``route_name`` parameter:

.. code-block:: python

   # in your project's views.py module (mypackage.views)

   from pyramid.view import view_config
   from pyramid.response import Response

   @view_config(route_name='myroute')
   def myview(request):
       return Response('OK')

THe above combination of ``add_route`` and ``scan`` is completely equivalent
to using the previous combination of ``add_route`` and ``add_view``.

.. index::
   single: route path pattern syntax

.. _route_pattern_syntax:

Route Pattern Syntax
~~~~~~~~~~~~~~~~~~~~

The syntax of the pattern matching language used by :app:`Pyramid` URL
dispatch in the *pattern* argument is straightforward; it is close to that of
the :term:`Routes` system used by :term:`Pylons`.

The *pattern* used in route configuration may start with a slash character.
If the pattern does not start with a slash character, an implicit slash will
be prepended to it at matching time.  For example, the following patterns are
equivalent:

.. code-block:: text

   {foo}/bar/baz

and:

.. code-block:: text

   /{foo}/bar/baz

A pattern segment (an individual item between ``/`` characters in the
pattern) may either be a literal string (e.g. ``foo``) *or* it may be a
replacement marker (e.g. ``{foo}``) or a certain combination of both. A
replacement marker does not need to be preceded by a ``/`` character.

A replacement marker is in the format ``{name}``, where this means "accept
any characters up to the next slash character and use this as the ``name``
:term:`matchdict` value."

A replacement marker in a pattern must begin with an uppercase or lowercase
ASCII letter or an underscore, and can be composed only of uppercase or
lowercase ASCII letters, underscores, and numbers.  For example: ``a``,
``a_b``, ``_b``, and ``b9`` are all valid replacement marker names, but
``0a`` is not.

.. note:: A replacement marker could not start with an underscore until
   Pyramid 1.2.  Previous versions required that the replacement marker start
   with an uppercase or lowercase letter.

A matchdict is the dictionary representing the dynamic parts extracted from a
URL based on the routing pattern.  It is available as ``request.matchdict``.
For example, the following pattern defines one literal segment (``foo``) and
two replacement markers (``baz``, and ``bar``):

.. code-block:: text

   foo/{baz}/{bar}

The above pattern will match these URLs, generating the following matchdicts:

.. code-block:: text

   foo/1/2        -> {'baz':u'1', 'bar':u'2'}
   foo/abc/def    -> {'baz':u'abc', 'bar':u'def'}

It will not match the following patterns however:

.. code-block:: text

   foo/1/2/        -> No match (trailing slash)
   bar/abc/def     -> First segment literal mismatch

The match for a segment replacement marker in a segment will be done only up
to the first non-alphanumeric character in the segment in the pattern.  So,
for instance, if this route pattern was used:

.. code-block:: text

   foo/{name}.html

The literal path ``/foo/biz.html`` will match the above route pattern, and
the match result will be ``{'name':u'biz'}``.  However, the literal path
``/foo/biz`` will not match, because it does not contain a literal ``.html``
at the end of the segment represented by ``{name}.html`` (it only contains
``biz``, not ``biz.html``).

To capture both segments, two replacement markers can be used:

.. code-block:: text

    foo/{name}.{ext}

The literal path ``/foo/biz.html`` will match the above route pattern, and
the match result will be ``{'name': 'biz', 'ext': 'html'}``. This occurs
because there is a literal part of ``.`` (period) between the two replacement
markers ``{name}`` and ``{ext}``.

Replacement markers can optionally specify a regular expression which will be
used to decide whether a path segment should match the marker.  To specify
that a replacement marker should match only a specific set of characters as
defined by a regular expression, you must use a slightly extended form of
replacement marker syntax.  Within braces, the replacement marker name must
be followed by a colon, then directly thereafter, the regular expression.
The *default* regular expression associated with a replacement marker
``[^/]+`` matches one or more characters which are not a slash.  For example,
under the hood, the replacement marker ``{foo}`` can more verbosely be
spelled as ``{foo:[^/]+}``.  You can change this to be an arbitrary regular
expression to match an arbitrary sequence of characters, such as
``{foo:\d+}`` to match only digits.

It is possible to use two replacement markers without any literal characters
between them, for instance ``/{foo}{bar}``. However, this would be a
nonsensical pattern without specifying a custom regular expression to
restrict what each marker captures.

Segments must contain at least one character in order to match a segment
replacement marker.  For example, for the URL ``/abc/``:

- ``/abc/{foo}`` will not match.

- ``/{foo}/`` will match.

Note that values representing matched path segments will be url-unquoted and
decoded from UTF-8 into Unicode within the matchdict.  So for instance, the
following pattern:

.. code-block:: text

   foo/{bar}

When matching the following URL:

 .. code-block:: text
 
   http://example.com/foo/La%20Pe%C3%B1a

The matchdict will look like so (the value is URL-decoded / UTF-8 decoded):

.. code-block:: text

   {'bar':u'La Pe\xf1a'}

Literal strings in the path segment should represent the *decoded* value of
the ``PATH_INFO`` provided to Pyramid.  You don't want to use a URL-encoded
value or a bytestring representing the literal's UTF-8 in the pattern.  For
example, rather than this:

.. code-block:: text

   /Foo%20Bar/{baz}

You'll want to use something like this:

.. code-block:: text

   /Foo Bar/{baz}

For patterns that contain "high-order" characters in its literals, you'll
want to use a Unicode value as the pattern as opposed to any URL-encoded or
UTF-8-encoded value.  For example, you might be tempted to use a bytestring
pattern like this:

.. code-block:: text

   /La Pe\xc3\xb1a/{x}

But this will either cause an error at startup time or it won't match
properly.  You'll want to use a Unicode value as the pattern instead rather
than raw bytestring escapes.  You can use a high-order Unicode value as the
pattern by using `Python source file encoding
<http://www.python.org/dev/peps/pep-0263/>`_ plus the "real" character in the
Unicode pattern in the source, like so:

.. code-block:: text

   /La Peña/{x}

Or you can ignore source file encoding and use equivalent Unicode escape
characters in the pattern.

.. code-block:: text

   /La Pe\xf1a/{x}

Dynamic segment names cannot contain high-order characters, so this applies
only to literals in the pattern.

If the pattern has a ``*`` in it, the name which follows it is considered a
"remainder match".  A remainder match *must* come at the end of the pattern.
Unlike segment replacement markers, it does not need to be preceded by a
slash.  For example:

.. code-block:: text

   foo/{baz}/{bar}*fizzle

The above pattern will match these URLs, generating the following matchdicts:

.. code-block:: text

   foo/1/2/           ->
            {'baz':u'1', 'bar':u'2', 'fizzle':()}

   foo/abc/def/a/b/c  ->
            {'baz':u'abc', 'bar':u'def', 'fizzle':(u'a', u'b', u'c')}

Note that when a ``*stararg`` remainder match is matched, the value put into
the matchdict is turned into a tuple of path segments representing the
remainder of the path.  These path segments are url-unquoted and decoded from
UTF-8 into Unicode.  For example, for the following pattern:

.. code-block:: text

   foo/*fizzle

When matching the following path:

.. code-block:: text

   /foo/La%20Pe%C3%B1a/a/b/c

Will generate the following matchdict:

.. code-block:: text

   {'fizzle':(u'La Pe\xf1a', u'a', u'b', u'c')}

By default, the ``*stararg`` will parse the remainder sections into a tuple
split by segment. Changing the regular expression used to match a marker can
also capture the remainder of the URL, for example:

.. code-block:: text

    foo/{baz}/{bar}{fizzle:.*}

The above pattern will match these URLs, generating the following matchdicts:

.. code-block:: text

   foo/1/2/           -> {'baz':u'1', 'bar':u'2', 'fizzle':()}
   foo/abc/def/a/b/c  -> {'baz':u'abc', 'bar':u'def', 'fizzle': u'a/b/c')}

This occurs because the default regular expression for a marker is ``[^/]+``
which will match everything up to the first ``/``, while ``{fizzle:.*}`` will
result in a regular expression match of ``.*`` capturing the remainder into a
single value.

.. index::
   single: route ordering

Route Declaration Ordering
~~~~~~~~~~~~~~~~~~~~~~~~~~

Route configuration declarations are evaluated in a specific order when a
request enters the system. As a result, the order of route configuration
declarations is very important.  The order that routes declarations are
evaluated is the order in which they are added to the application at startup
time.  (This is unlike a different way of mapping URLs to code that
:app:`Pyramid` provides, named :term:`traversal`, which does not depend on
pattern ordering).

For routes added via the :mod:`~pyramid.config.Configurator.add_route` method,
the order that routes are evaluated is the order in which they are added to
the configuration imperatively.

For example, route configuration statements with the following patterns might
be added in the following order:

.. code-block:: text

   members/{def}
   members/abc

In such a configuration, the ``members/abc`` pattern would *never* be
matched. This is because the match ordering will always match
``members/{def}`` first; the route configuration with ``members/abc`` will
never be evaluated.

.. index::
   single: route configuration arguments

Route Configuration Arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Route configuration ``add_route`` statements may specify a large number of
arguments.  They are documented as part of the API documentation at
:meth:`pyramid.config.Configurator.add_route`.

Many of these arguments are :term:`route predicate` arguments.  A route
predicate argument specifies that some aspect of the request must be true for
the associated route to be considered a match during the route matching
process.  Examples of route predicate arguments are ``pattern``, ``xhr``, and
``request_method``.

Other arguments are ``name`` and ``factory``.  These arguments represent
neither predicates nor view configuration information.

.. warning::

   Some arguments are view-configuration related arguments, such as
   ``view_renderer``.  These only have an effect when the route configuration
   names a ``view`` and these arguments have been deprecated as of
   :app:`Pyramid` 1.1.

.. index::
   single: route matching

Route Matching
--------------

The main purpose of route configuration is to match (or not match) the
``PATH_INFO`` present in the WSGI environment provided during a request
against a URL path pattern.  ``PATH_INFO`` represents the path portion of the
URL that was requested.

The way that :app:`Pyramid` does this is very simple.  When a request enters
the system, for each route configuration declaration present in the system,
:app:`Pyramid` checks the request's ``PATH_INFO`` against the pattern
declared.  This checking happens in the order that the routes were declared
via :meth:`pyramid.config.Configurator.add_route`.

When a route configuration is declared, it may contain :term:`route
predicate` arguments.  All route predicates associated with a route
declaration must be ``True`` for the route configuration to be used for a
given request during a check.  If any predicate in the set of :term:`route
predicate` arguments provided to a route configuration returns ``False``
during a check, that route is skipped and route matching continues through
the ordered set of routes.

If any route matches, the route matching process stops and the :term:`view
lookup` subsystem takes over to find the most reasonable view callable for
the matched route.  Most often, there's only one view that will match (a view
configured with a ``route_name`` argument matching the matched route).  To
gain a better understanding of how routes and views are associated in a real
application, you can use the ``paster pviews`` command, as documented in
:ref:`displaying_matching_views`.

If no route matches after all route patterns are exhausted, :app:`Pyramid`
falls back to :term:`traversal` to do :term:`resource location` and
:term:`view lookup`.

.. index::
   single: matchdict

.. _matchdict:

The Matchdict
~~~~~~~~~~~~~

When the URL pattern associated with a particular route configuration is
matched by a request, a dictionary named ``matchdict`` is added as an
attribute of the :term:`request` object.  Thus, ``request.matchdict`` will
contain the values that match replacement patterns in the ``pattern``
element.  The keys in a matchdict will be strings.  The values will be
Unicode objects.

.. note::

   If no route URL pattern matches, the ``matchdict`` object attached to the
   request will be ``None``.

.. index::
   single: matched_route

.. _matched_route:

The Matched Route
~~~~~~~~~~~~~~~~~

When the URL pattern associated with a particular route configuration is
matched by a request, an object named ``matched_route`` is added as an
attribute of the :term:`request` object.  Thus, ``request.matched_route``
will be an object implementing the :class:`~pyramid.interfaces.IRoute`
interface which matched the request.  The most useful attribute of the route
object is ``name``, which is the name of the route that matched.

.. note::

   If no route URL pattern matches, the ``matched_route`` object attached to
   the request will be ``None``.

Routing Examples
----------------

Let's check out some examples of how route configuration statements might be
commonly declared, and what will happen if they are matched by the
information present in a request.

.. _urldispatch_example1:

Example 1
~~~~~~~~~

The simplest route declaration which configures a route match to *directly*
result in a particular view callable being invoked:

.. code-block:: python
   :linenos:

    config.add_route('idea', 'site/{id}')
    config.add_view('mypackage.views.site_view', route_name='idea')

When a route configuration with a ``view`` attribute is added to the system,
and an incoming request matches the *pattern* of the route configuration, the
:term:`view callable` named as the ``view`` attribute of the route
configuration will be invoked.

In the case of the above example, when the URL of a request matches
``/site/{id}``, the view callable at the Python dotted path name
``mypackage.views.site_view`` will be called with the request.  In other
words, we've associated a view callable directly with a route pattern.

When the ``/site/{id}`` route pattern matches during a request, the
``site_view`` view callable is invoked with that request as its sole
argument.  When this route matches, a ``matchdict`` will be generated and
attached to the request as ``request.matchdict``.  If the specific URL
matched is ``/site/1``, the ``matchdict`` will be a dictionary with a single
key, ``id``; the value will be the string ``'1'``, ex.: ``{'id':'1'}``.

The ``mypackage.views`` module referred to above might look like so:

.. code-block:: python
   :linenos:

   from pyramid.response import Response

   def site_view(request):
       return Response(request.matchdict['id'])

The view has access to the matchdict directly via the request, and can access
variables within it that match keys present as a result of the route pattern.

See :ref:`views_chapter`, and :ref:`view_config_chapter` for more
information about views.

Example 2
~~~~~~~~~

Below is an example of a more complicated set of route statements you might
add to your application:

.. code-block:: python
   :linenos:

   config.add_route('idea', 'ideas/{idea}')
   config.add_route('user', 'users/{user}')
   config.add_route('tag', 'tags/{tags}')

   config.add_view('mypackage.views.idea_view', route_name='idea')
   config.add_view('mypackage.views.user_view', route_name='user')
   config.add_view('mypackage.views.tag_view', route_name='tag')

The above configuration will allow :app:`Pyramid` to service URLs in these
forms:

.. code-block:: text

   /ideas/{idea}
   /users/{user}
   /tags/{tag}

- When a URL matches the pattern ``/ideas/{idea}``, the view callable
  available at the dotted Python pathname ``mypackage.views.idea_view`` will
  be called.  For the specific URL ``/ideas/1``, the ``matchdict`` generated
  and attached to the :term:`request` will consist of ``{'idea':'1'}``.

- When a URL matches the pattern ``/users/{user}``, the view callable
  available at the dotted Python pathname ``mypackage.views.user_view`` will
  be called.  For the specific URL ``/users/1``, the ``matchdict`` generated
  and attached to the :term:`request` will consist of ``{'user':'1'}``.

- When a URL matches the pattern ``/tags/{tag}``, the view callable available
  at the dotted Python pathname ``mypackage.views.tag_view`` will be called.
  For the specific URL ``/tags/1``, the ``matchdict`` generated and attached
  to the :term:`request` will consist of ``{'tag':'1'}``.

In this example we've again associated each of our routes with a :term:`view
callable` directly.  In all cases, the request, which will have a
``matchdict`` attribute detailing the information found in the URL by the
process will be passed to the view callable.

Example 3
~~~~~~~~~

The :term:`context` resource object passed in to a view found as the result
of URL dispatch will, by default, be an instance of the object returned by
the :term:`root factory` configured at startup time (the ``root_factory``
argument to the :term:`Configurator` used to configure the application).

You can override this behavior by passing in a ``factory`` argument to the
:meth:`~pyramid.config.Configurator.add_route` method for a particular route.
The ``factory`` should be a callable that accepts a :term:`request` and
returns an instance of a class that will be the context resource used by the
view.

An example of using a route with a factory:

.. code-block:: python
   :linenos:

   config.add_route('idea', 'ideas/{idea}', factory='myproject.resources.Idea')
   config.add_view('myproject.views.idea_view', route_name='idea')

The above route will manufacture an ``Idea`` resource as a :term:`context`,
assuming that ``mypackage.resources.Idea`` resolves to a class that accepts a
request in its ``__init__``.  For example:

.. code-block:: python
   :linenos:

   class Idea(object):
       def __init__(self, request):
           pass

In a more complicated application, this root factory might be a class
representing a :term:`SQLAlchemy` model.

See :ref:`route_factories` for more details about how to use route factories.

.. index::
   single: matching the root URL
   single: root url (matching)
   pair: matching; root URL

Matching the Root URL
---------------------

It's not entirely obvious how to use a route pattern to match the root URL
("/").  To do so, give the empty string as a pattern in a call to
:meth:`~pyramid.config.Configurator.add_route`:

.. code-block:: python
   :linenos:

   config.add_route('root', '')

Or provide the literal string ``/`` as the pattern:

.. code-block:: python
   :linenos:

   config.add_route('root', '/')

.. index::
   single: generating route URLs
   single: route URLs

.. _generating_route_urls:

Generating Route URLs
---------------------

Use the :meth:`pyramid.request.Request.route_url` method to generate URLs
based on route patterns.  For example, if you've configured a route with the
``name`` "foo" and the ``pattern`` "{a}/{b}/{c}", you might do this.

.. code-block:: python
   :linenos:

   url = request.route_url('foo', a='1', b='2', c='3')

This would return something like the string ``http://example.com/1/2/3`` (at
least if the current protocol and hostname implied ``http://example.com``).


To generate only the *path* portion of a URL from a route, use the
:meth:`pyramid.request.Request.route_path` API instead of
:meth:`~pyramid.request.Request.route_url`.

.. code-block:: python

   url = request.route_path('foo', a='1', b='2', c='3')

This will return the string ``/1/2/3`` rather than a full URL.

Replacement values passed to ``route_url`` or ``route_path`` must be Unicode
or bytestrings encoded in UTF-8.  One exception to this rule exists: if
you're trying to replace a "remainder" match value (a ``*stararg``
replacement value), the value may be a tuple containing Unicode strings or
UTF-8 strings.

Note that URLs and paths generated by ``route_path`` and ``route_url`` are
always URL-quoted string types (they contain no non-ASCII characters).
Therefore, if you've added a route like so:

.. code-block:: python

   config.add_route('la', u'/La Peña/{city}')

And you later generate a URL using ``route_path`` or ``route_url`` like so:

.. code-block:: python

   url = request.route_path('la', city=u'Québec')

You will wind up with the path encoded to UTF-8 and URL quoted like so:

.. code-block:: text

   /La%20Pe%C3%B1a/Qu%C3%A9bec

If you have a ``*stararg`` remainder dynamic part of your route pattern:

.. code-block:: python

   config.add_route('abc', 'a/b/c/*foo')

And you later generate a URL using ``route_path`` or ``route_url`` using a
*string* as the replacement value:

.. code-block:: python

   url = request.route_path('abc', foo=u'Québec/biz')

The value you pass will be URL-quoted except for embedded slashes in the
result:

.. code-block:: text

   /a/b/c/Qu%C3%A9bec/biz

You can get a similar result by passing a tuple composed of path elements:

.. code-block:: python

   url = request.route_path('abc', foo=(u'Québec', u'biz'))

Each value in the tuple will be url-quoted and joined by slashes in this case:

.. code-block:: text

   /a/b/c/Qu%C3%A9bec/biz

.. index::
   single: static routes

.. _static_route_narr:

Static Routes
-------------

Routes may be added with a ``static`` keyword argument.  For example:

.. code-block:: python
   :linenos:

   config = Configurator()
   config.add_route('page', '/page/{action}', static=True)

Routes added with a ``True`` ``static`` keyword argument will never be
considered for matching at request time.  Static routes are useful for URL
generation purposes only.  As a result, it is usually nonsensical to provide
other non-``name`` and non-``pattern`` arguments to
:meth:`~pyramid.config.Configurator.add_route` when ``static`` is passed as
``True``, as none of the other arguments will ever be employed.  A single
exception to this rule is use of the ``pregenerator`` argument, which is not
ignored when ``static`` is ``True``.

.. note::

   the ``static`` argument to
   :meth:`~pyramid.config.Configurator.add_route` is new as of :app:`Pyramid`
   1.1.

.. index::
   single: redirecting to slash-appended routes

.. _redirecting_to_slash_appended_routes:

Redirecting to Slash-Appended Routes
------------------------------------

For behavior like Django's ``APPEND_SLASH=True``, use the
:func:`~pyramid.view.append_slash_notfound_view` view as the :term:`Not Found
view` in your application.  Defining this view as the :term:`Not Found view`
is a way to automatically redirect requests where the URL lacks a trailing
slash, but requires one to match the proper route.  When configured, along
with at least one other route in your application, this view will be invoked
if the value of ``PATH_INFO`` does not already end in a slash, and if the
value of ``PATH_INFO`` *plus* a slash matches any route's pattern.  In this
case it does an HTTP redirect to the slash-appended ``PATH_INFO``.

Let's use an example, because this behavior is a bit magical. If the
``append_slash_notfound_view`` is configured in your application and your
route configuration looks like so:

.. code-block:: python
   :linenos:

   config.add_route('noslash', 'no_slash')
   config.add_route('hasslash', 'has_slash/')

   config.add_view('myproject.views.no_slash', route_name='noslash')
   config.add_view('myproject.views.has_slash', route_name='hasslash')

If a request enters the application with the ``PATH_INFO`` value of
``/has_slash/``, the second route will match.  If a request enters the
application with the ``PATH_INFO`` value of ``/has_slash``, a route *will* be
found by the slash-appending not found view.  An HTTP redirect to
``/has_slash/`` will be returned to the user's browser.

If a request enters the application with the ``PATH_INFO`` value of
``/no_slash``, the first route will match.  However, if a request enters the
application with the ``PATH_INFO`` value of ``/no_slash/``, *no* route will
match, and the slash-appending not found view will *not* find a matching
route with an appended slash.

.. warning::

   You **should not** rely on this mechanism to redirect ``POST`` requests.
   The redirect  of the slash-appending not found view will turn a ``POST``
   request into a ``GET``, losing any ``POST`` data in the original
   request.

To configure the slash-appending not found view in your application, change
the application's startup configuration, adding the following stanza:

.. code-block:: python
   :linenos:

   config.add_view('pyramid.view.append_slash_notfound_view',
                   context='pyramid.httpexceptions.HTTPNotFound')

See :ref:`view_module` and :ref:`changing_the_notfound_view` for more
information about the slash-appending not found view and for a more general
description of how to configure a not found view.

Custom Not Found View With Slash Appended Routes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There can only be one :term:`Not Found view` in any :app:`Pyramid`
application.  Even if you use :func:`~pyramid.view.append_slash_notfound_view`
as the Not Found view, :app:`Pyramid` still must generate a ``404 Not Found``
response when it cannot redirect to a slash-appended URL; this not found
response will be visible to site users.

If you don't care what this 404 response looks like, and only you need
redirections to slash-appended route URLs, you may use the
:func:`~pyramid.view.append_slash_notfound_view` object as the Not Found view
as described above.  However, if you wish to use a *custom* notfound view
callable when a URL cannot be redirected to a slash-appended URL, you may
wish to use an instance of the
:class:`~pyramid.view.AppendSlashNotFoundViewFactory` class as the Not Found
view, supplying a :term:`view callable` to be used as the custom notfound
view as the first argument to its constructor.  For instance:

.. code-block:: python
     :linenos:

     from pyramid.httpexceptions import HTTPNotFound
     from pyramid.view import AppendSlashNotFoundViewFactory

     def notfound_view(context, request):
         return HTTPNotFound('It aint there, stop trying!')

     custom_append_slash = AppendSlashNotFoundViewFactory(notfound_view)
     config.add_view(custom_append_slash, context=HTTPNotFound)

The ``notfound_view`` supplied must adhere to the two-argument view callable
calling convention of ``(context, request)`` (``context`` will be the
exception object).

.. index::
   pair: debugging; route matching

.. _debug_routematch_section:

Debugging Route Matching
------------------------

It's useful to be able to take a peek under the hood when requests that enter
your application arent matching your routes as you expect them to.  To debug
route matching, use the ``PYRAMID_DEBUG_ROUTEMATCH`` environment variable or the
``pyramid.debug_routematch`` configuration file setting (set either to ``true``).
Details of the route matching decision for a particular request to the
:app:`Pyramid` application will be printed to the ``stderr`` of the console
which you started the application from.  For example:

.. code-block:: text
   :linenos:

    [chrism@thinko pylonsbasic]$ PYRAMID_DEBUG_ROUTEMATCH=true \
                                 bin/paster serve development.ini
    Starting server in PID 13586.
    serving on 0.0.0.0:6543 view at http://127.0.0.1:6543
    2010-12-16 14:45:19,956 no route matched for url \
                                        http://localhost:6543/wontmatch
    2010-12-16 14:45:20,010 no route matched for url \
                                http://localhost:6543/favicon.ico
    2010-12-16 14:41:52,084 route matched for url \
                                http://localhost:6543/static/logo.png; \
                                route_name: 'static/', ....

See :ref:`environment_chapter` for more information about how, and where to
set these values.

You can also use the ``paster proutes`` command to see a display of all the
routes configured in your application; for more information, see
:ref:`displaying_application_routes`.

.. _route_prefix:

Using a Route Prefix to Compose Applications
--------------------------------------------

.. note:: This feature is new as of :app:`Pyramid` 1.2.

The :meth:`pyramid.config.Configurator.include` method allows configuration
statements to be included from separate files.  See
:ref:`building_an_extensible_app` for information about this method.  Using
:meth:`pyramid.config.Configurator.include` allows you to build your
application from small and potentially reusable components.

The :meth:`pyramid.config.Configurator.include` method accepts an argument
named ``route_prefix`` which can be useful to authors of URL-dispatch-based
applications.  If ``route_prefix`` is supplied to the include method, it must
be a string.  This string represents a route prefix that will be prepended to
all route patterns added by the *included* configuration.  Any calls to
:meth:`pyramid.config.Configurator.add_route` within the included callable
will have their pattern prefixed with the value of ``route_prefix``. This can
be used to help mount a set of routes at a different location than the
included callable's author intended while still maintaining the same route
names.  For example:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def users_include(config):
       config.add_route('show_users', '/show')

   def main(global_config, **settings):
       config = Configurator()
       config.include(users_include, route_prefix='/users')

In the above configuration, the ``show_users`` route will have an effective
route pattern of ``/users/show``, instead of ``/show`` because the
``route_prefix`` argument will be prepended to the pattern.  The route will
then only match if the URL path is ``/users/show``, and when the
:meth:`pyramid.request.Request.route_url` function is called with the route
name ``show_users``, it will generate a URL with that same path.

Route prefixes are recursive, so if a callable executed via an include itself
turns around and includes another callable, the second-level route prefix
will be prepended with the first:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def timing_include(config):
       config.add_route('show_times', /times')

   def users_include(config):
       config.add_route('show_users', '/show')
       config.include(timing_include, route_prefix='/timing')

   def main(global_config, **settings):
       config = Configurator()
       config.include(users_include, route_prefix='/users')

In the above configuration, the ``show_users`` route will still have an
effective route pattern of ``/users/show``.  The ``show_times`` route
however, will have an effective pattern of ``/users/timing/show_times``.

Route prefixes have no impact on the requirement that the set of route
*names* in any given Pyramid configuration must be entirely unique.  If you
compose your URL dispatch application out of many small subapplications using
:meth:`pyramid.config.Configurator.include`, it's wise to use a dotted name
for your route names, so they'll be unlikely to conflict with other packages
that may be added in the future.  For example:

.. code-block:: python
   :linenos:

   from pyramid.config import Configurator

   def timing_include(config):
       config.add_route('timing.show_times', /times')

   def users_include(config):
       config.add_route('users.show_users', '/show')
       config.include(timing_include, route_prefix='/timing')

   def main(global_config, **settings):
       config = Configurator()
       config.include(users_include, route_prefix='/users')

.. index::
   single: route predicates (custom)

.. _custom_route_predicates:

Custom Route Predicates
-----------------------

Each of the predicate callables fed to the ``custom_predicates`` argument of
:meth:`~pyramid.config.Configurator.add_route` must be a callable accepting
two arguments.  The first argument passed to a custom predicate is a
dictionary conventionally named ``info``.  The second argument is the current
:term:`request` object.

The ``info`` dictionary has a number of contained values: ``match`` is a
dictionary: it represents the arguments matched in the URL by the route.
``route`` is an object representing the route which was matched (see
:class:`pyramid.interfaces.IRoute` for the API of such a route object).

``info['match']`` is useful when predicates need access to the route match.
For example:

.. code-block:: python
   :linenos:

   def any_of(segment_name, *allowed):
       def predicate(info, request):
           if info['match'][segment_name] in allowed:
               return True
       return predicate

   num_one_two_or_three = any_of('num', 'one', 'two', 'three')

   config.add_route('route_to_num', '/{num}',
                    custom_predicates=(num_one_two_or_three,))

The above ``any_of`` function generates a predicate which ensures that the
match value named ``segment_name`` is in the set of allowable values
represented by ``allowed``.  We use this ``any_of`` function to generate a
predicate function named ``num_one_two_or_three``, which ensures that the
``num`` segment is one of the values ``one``, ``two``, or ``three`` , and use
the result as a custom predicate by feeding it inside a tuple to the
``custom_predicates`` argument to
:meth:`~pyramid.config.Configurator.add_route`.

A custom route predicate may also *modify* the ``match`` dictionary.  For
instance, a predicate might do some type conversion of values:

.. code-block:: python
   :linenos:

    def integers(*segment_names):
        def predicate(info, request):
            match = info['match']
            for segment_name in segment_names:
                try:
                    match[segment_name] = int(match[segment_name])
                except (TypeError, ValueError):
                    pass
            return True
        return predicate

    ymd_to_int = integers('year', 'month', 'day')

    config.add_route('ymd', '/{year}/{month}/{day}',
                     custom_predicates=(ymd_to_int,))

Note that a conversion predicate is still a predicate so it must return
``True`` or ``False``; a predicate that does *only* conversion, such as the
one we demonstrate above should unconditionally return ``True``.

To avoid the try/except uncertainty, the route pattern can contain regular
expressions specifying requirements for that marker. For instance:

.. code-block:: python
   :linenos:

    def integers(*segment_names):
        def predicate(info, request):
            match = info['match']
            for segment_name in segment_names:
                match[segment_name] = int(match[segment_name])
            return True
        return predicate

    ymd_to_int = integers('year', 'month', 'day')

    config.add_route('ymd', '/{year:\d+}/{month:\d+}/{day:\d+}',
                     custom_predicates=(ymd_to_int,))

Now the try/except is no longer needed because the route will not match at
all unless these markers match ``\d+`` which requires them to be valid digits
for an ``int`` type conversion.

The ``match`` dictionary passed within ``info`` to each predicate attached to
a route will be the same dictionary.  Therefore, when registering a custom
predicate which modifies the ``match`` dict, the code registering the
predicate should usually arrange for the predicate to be the *last* custom
predicate in the custom predicate list.  Otherwise, custom predicates which
fire subsequent to the predicate which performs the ``match`` modification
will receive the *modified* match dictionary.

.. warning::

   It is a poor idea to rely on ordering of custom predicates to build a
   conversion pipeline, where one predicate depends on the side effect of
   another.  For instance, it's a poor idea to register two custom
   predicates, one which handles conversion of a value to an int, the next
   which handles conversion of that integer to some custom object.  Just do
   all that in a single custom predicate.

The ``route`` object in the ``info`` dict is an object that has two useful
attributes: ``name`` and ``pattern``.  The ``name`` attribute is the route
name.  The ``pattern`` attribute is the route pattern.  An example of using
the route in a set of route predicates:

.. code-block:: python
   :linenos:

    def twenty_ten(info, request):
        if info['route'].name in ('ymd', 'ym', 'y'):
            return info['match']['year'] == '2010'

    config.add_route('y', '/{year}', custom_predicates=(twenty_ten,))
    config.add_route('ym', '/{year}/{month}', custom_predicates=(twenty_ten,))
    config.add_route('ymd', '/{year}/{month}/{day}',
                     custom_predicates=(twenty_ten,))

The above predicate, when added to a number of route configurations ensures
that the year match argument is '2010' if and only if the route name is
'ymd', 'ym', or 'y'.

You can also caption the predicates by setting the ``__text__`` attribute. This
will help you with the ``paster pviews`` command (see
:ref:`displaying_application_routes`) and the ``pyramid_debugtoolbar``.

If a predicate is a class just add __text__ property in a standard manner.

.. code-block:: python
   :linenos:

   class DummyCustomPredicate1(object):
       def __init__(self):
           self.__text__ = 'my custom class predicate'

   class DummyCustomPredicate2(object):
       __text__ = 'my custom class predicate'

If a predicate is a method you'll need to assign it after method declaration
(see `PEP 232 <http://www.python.org/dev/peps/pep-0232/>`_)

.. code-block:: python
   :linenos:

   def custom_predicate():
       pass
   custom_predicate.__text__ = 'my custom method predicate'

If a predicate is a classmethod using @classmethod will not work, but you can
still easily do it by wrapping it in classmethod call.

.. code-block:: python
   :linenos:

   def classmethod_predicate():
       pass
   classmethod_predicate.__text__ = 'my classmethod predicate'
   classmethod_predicate = classmethod(classmethod_predicate)

Same will work with staticmethod, just use ``staticmethod`` instead of
``classmethod``.


See also :class:`pyramid.interfaces.IRoute` for more API documentation about
route objects.

.. index::
   single: route factory

.. _route_factories:

Route Factories
---------------

Although it is not a particular common need in basic applications, a "route"
configuration declaration can mention a "factory".  When that route matches a
request, and a factory is attached to a route, the :term:`root factory`
passed at startup time to the :term:`Configurator` is ignored; instead the
factory associated with the route is used to generate a :term:`root` object.
This object will usually be used as the :term:`context` resource of the view
callable ultimately found via :term:`view lookup`.

.. code-block:: python
   :linenos:

   config.add_route('abc', '/abc',
                    factory='myproject.resources.root_factory')
   config.add_view('myproject.views.theview', route_name='abc')

The factory can either be a Python object or a :term:`dotted Python name` (a
string) which points to such a Python object, as it is above.

In this way, each route can use a different factory, making it possible to
supply a different :term:`context` resource object to the view related to
each particular route.

A factory must be a callable which accepts a request and returns an arbitrary
Python object.  For example, the below class can be used as a factory:

.. code-block:: python
   :linenos:

   class Mine(object):
       def __init__(self, request):
           pass

A route factory is actually conceptually identical to the :term:`root
factory` described at :ref:`the_resource_tree`.

Supplying a different resource factory for each route is useful when you're
trying to use a :app:`Pyramid` :term:`authorization policy` to provide
declarative, "context sensitive" security checks; each resource can maintain
a separate :term:`ACL`, as documented in
:ref:`using_security_with_urldispatch`.  It is also useful when you wish to
combine URL dispatch with :term:`traversal` as documented within
:ref:`hybrid_chapter`.

.. index::
   pair: URL dispatch; security

.. _using_security_with_urldispatch:

Using :app:`Pyramid` Security With URL Dispatch
--------------------------------------------------

:app:`Pyramid` provides its own security framework which consults an
:term:`authorization policy` before allowing any application code to be
called.  This framework operates in terms of an access control list, which is
stored as an ``__acl__`` attribute of a resource object.  A common thing to
want to do is to attach an ``__acl__`` to the resource object dynamically for
declarative security purposes.  You can use the ``factory`` argument that
points at a factory which attaches a custom ``__acl__`` to an object at its
creation time.

Such a ``factory`` might look like so:

.. code-block:: python
   :linenos:

   class Article(object):
       def __init__(self, request):
          matchdict = request.matchdict
          article = matchdict.get('article', None)
          if article == '1':
              self.__acl__ = [ (Allow, 'editor', 'view') ]

If the route ``archives/{article}`` is matched, and the article number is
``1``, :app:`Pyramid` will generate an ``Article`` :term:`context` resource
with an ACL on it that allows the ``editor`` principal the ``view``
permission.  Obviously you can do more generic things than inspect the routes
match dict to see if the ``article`` argument matches a particular string;
our sample ``Article`` factory class is not very ambitious.

.. note::

   See :ref:`security_chapter` for more information about
   :app:`Pyramid` security and ACLs.

.. index::
   pair: route; view callable lookup details

Route View Callable Registration and Lookup Details
---------------------------------------------------

When a request enters the system which matches the pattern of the route, the
usual result is simple: the view callable associated with the route is
invoked with the request that caused the invocation.

For most usage, you needn't understand more than this; how it works is an
implementation detail.  In the interest of completeness, however, we'll
explain how it *does* work in the this section.  You can skip it if you're
uninterested.

When a view is associated with a route configuration, :app:`Pyramid` ensures
that a :term:`view configuration` is registered that will always be found
when the route pattern is matched during a request.  To do so:

- A special route-specific :term:`interface` is created at startup time for
  each route configuration declaration.

- When an ``add_view`` statement mentions a ``route name`` attribute, a
  :term:`view configuration` is registered at startup time.  This view
  configuration uses a route-specific interface as a :term:`request` type.

- At runtime, when a request causes any route to match, the :term:`request`
  object is decorated with the route-specific interface.

- The fact that the request is decorated with a route-specific interface
  causes the :term:`view lookup` machinery to always use the view callable
  registered using that interface by the route configuration to service
  requests that match the route pattern.

As we can see from the above description, technically, URL dispatch doesn't
actually map a URL pattern directly to a view callable.  Instead, URL
dispatch is a :term:`resource location` mechanism.  A :app:`Pyramid`
:term:`resource location` subsystem (i.e., :term:`URL dispatch` or
:term:`traversal`) finds a :term:`resource` object that is the
:term:`context` of a :term:`request`. Once the :term:`context` is determined,
a separate subsystem named :term:`view lookup` is then responsible for
finding and invoking a :term:`view callable` based on information available
in the context and the request.  When URL dispatch is used, the resource
location and view lookup subsystems provided by :app:`Pyramid` are still
being utilized, but in a way which does not require a developer to understand
either of them in detail.

If no route is matched using :term:`URL dispatch`, :app:`Pyramid` falls back
to :term:`traversal` to handle the :term:`request`.

References
----------

A tutorial showing how :term:`URL dispatch` can be used to create a
:app:`Pyramid` application exists in :ref:`bfg_sql_wiki_tutorial`.
