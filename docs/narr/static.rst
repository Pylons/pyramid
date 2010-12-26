Static Assets
=============

:app:`Pyramid` makes it possible to serve up static asset files from a
directory on a filesystem.  This chapter describes how to configure
:app:`Pyramid` to do so.

.. index::
   single: add_static_view

.. _static_assets_section:

Serving Static Assets
---------------------

Use the :meth:`pyramid.config.Configurator.add_static_view` to instruct
:app:`Pyramid` to serve static assets such as JavaScript and CSS files. This
mechanism makes a directory of static files available at a name relative to
the application root URL, e.g. ``/static`` or as an external URL.

.. note:: `~pyramid.config.Configurator.add_static_view` cannot serve a
   single file, nor can it serve a directory of static files directly
   relative to the root URL of a :app:`Pyramid` application.  For these
   features, see :ref:`advanced_static`.

Here's an example of a use of
:meth:`~pyramid.config.Configurator.add_static_view` that will serve files up
from the ``/var/www/static`` directory of the computer which runs the
:app:`Pyramid` application as URLs beneath the ``/static`` URL prefix.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='static', path='/var/www/static')

The ``name`` prepresents a URL *prefix*.  In order for files that live in the
``path`` directory to be served, a URL that requests one of them must begin
with that prefix.  In the example above, ``name`` is ``static``, and ``path``
is ``/var/www/static``.  In English, this means that you wish to serve the
files that live in ``/var/www/static`` as sub-URLs of the ``/static`` URL
prefix.  Therefore, the file ``/var/www/static/foo.css`` will be returned
when the user visits your application's URL ``/static/foo.css``.

A static directory named at ``path`` may contain subdirectories recursively,
and any subdirectories may hold files; these will be resolved by the static
view as you would expect.  The ``Content-Type`` header returned by the static
view for each particular type of file is dependent upon its file extension.

By default, all files made available via
:meth:`~pyramid.config.Configurator.add_static_view` are accessible by
completely anonymous users.  Simple authorization can be required, however.
To protect a set of static files using a permission, in addition to passing
the required ``name`` and ``path`` arguments, also pass the ``permission``
keyword argument to :meth:`~pyramid.config.Configurator.add_static_view`.
The value of the ``permission`` argument represents the :term:`permission`
that the user must have relative to the current :term:`context` when the
static view is invoked.  A user will be required to possess this permission
to view any of the files represented by ``path`` of the static view.  If your
static resources must be protected by a more complex authorization scheme,
see :ref:`advanced_static`.

Here's another example that uses an :term:`asset specification` instead of an
absolute path as the ``path`` argument.  To convince
:meth:`pyramid.config.Configurator.add_static_view` to serve files up under
the ``/static`` URL from the ``a/b/c/static`` directory of the Python package
named ``some_package``, we can use a fully qualified :term:`asset
specification` as the ``path``:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='static', path='some_package:a/b/c/static')

The ``path`` provided to :meth:`pyramid.config.Configurator.add_static_view`
may be a fully qualified :term:`asset specification`, or an *absolute path*.

Instead of representing a URL prefix, the ``name`` argument of a call to
:meth:`pyramid.config.Configurator.add_static_view` can alternately be a
*URL*.  Each of examples we've seen so far have shown usage of the ``name``
argument as a URL prefix.  However, when ``name`` is a *URL*, static assets
can be served from an external webserver.  In this mode, the ``name`` is used
as the URL prefix when generating a URL using :func:`pyramid.url.static_url`.

For example, :meth:`pyramid.config.Configurator.add_static_view` may
be fed a ``name`` argument which is ``http://example.com/images``:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='http://example.com/images', 
                          path='mypackage:images')

Because :meth:`pyramid.config.Configurator.add_static_view` is provided with
a ``name`` argument that is the URL ``http://example.com/images``, subsequent
calls to :func:`pyramid.url.static_url` with paths that start with the
``path`` argument passed to
:meth:`pyramid.config.Configurator.add_static_view` will generate a URL
something like ``http://example.com/images/logo.png``.  The external
webserver listening on ``example.com`` must be itself configured to respond
properly to such a request.  The :func:`pyramid.url.static_url` API is
discussed in more detail later in this chapter.

.. note::

   The :ref:`static_directive` ZCML directive offers an declarative
   equivalent to :meth:`pyramid.config.Configurator.add_static_view`.  Use of
   the :ref:`static_directive` ZCML directive is completely equivalent to
   using imperative configuration for the same purpose.

.. index::
   single: generating static asset urls
   single: static asset urls

.. _generating_static_asset_urls:

Generating Static Asset URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a :meth:`pyramid.config.Configurator.add_static_view` method is used to
register a static asset directory, a special helper API named
:func:`pyramid.url.static_url` can be used to generate the appropriate URL
for an asset that lives in one of the directories named by the static
registration ``path`` attribute.

For example, let's assume you create a set of static declarations like so:

.. code-block:: python
   :linenos:

   config.add_static_view(name='static1', path='mypackage:assets/1')
   config.add_static_view(name='static2', path='mypackage:assets/2')

These declarations create URL-accessible directories which have URLs that
begin with ``/static1`` and ``/static2``, respectively.  The assets in the
``assets/1`` directory of the ``mypackage`` package are consulted when a user
visits a URL which begins with ``/static1``, and the assets in the
``assets/2`` directory of the ``mypackage`` package are consulted when a user
visits a URL which begins with ``/static2``.

You needn't generate the URLs to static assets "by hand" in such a
configuration.  Instead, use the :func:`pyramid.url.static_url` API to
generate them for you.  For example:

.. code-block:: python
   :linenos:

   from pyramid.url import static_url
   from pyramid.chameleon_zpt import render_template_to_response

   def my_view(request):
       css_url = static_url('mypackage:assets/1/foo.css', request)
       js_url = static_url('mypackage:assets/2/foo.js', request)
       return render_template_to_response('templates/my_template.pt',
                                          css_url = css_url,
                                          js_url = js_url)

If the request "application URL" of the running system is
``http://example.com``, the ``css_url`` generated above would be:
``http://example.com/static1/foo.css``.  The ``js_url`` generated
above would be ``http://example.com/static2/foo.js``.

One benefit of using the :func:`pyramid.url.static_url` function rather than
constructing static URLs "by hand" is that if you need to change the ``name``
of a static URL declaration, the generated URLs will continue to resolve
properly after the rename.

URLs may also be generated by :func:`pyramid.url.static_url` to static assets
that live *outside* the :app:`Pyramid` application.  This will happen when
the :meth:`pyramid.config.Configurator.add_static_view` API associated with
the path fed to :func:`pyramid.url.static_url` is a *URL* instead of a view
name.  For example, the ``name`` argument may be ``http://example.com`` while
the the ``path`` given may be ``mypackage:images``:

.. code-block:: python
   :linenos:

   config.add_static_view(name='http://example.com/images', 
                          path='mypackage:images')

Under such a configuration, the URL generated by ``static_url`` for
assets which begin with ``mypackage:images`` will be prefixed with
``http://example.com/images``:

.. code-block:: python
   :linenos:

   static_url('mypackage:images/logo.png', request)
   # -> http://example.com/images/logo.png

Using :func:`pyramid.url.static_url` in conjunction with a
:meth:`pyramid.configuration.Configurator.add_static_view` makes it possible
to put static media on a separate webserver during production (if the
``name`` argument to :meth:`pyramid.config.Configurator.add_static_view` is a
URL), while keeping static media package-internal and served by the
development webserver during development (if the ``name`` argument to
:meth:`pyramid.config.Configurator.add_static_view` is a URL prefix).  To
create such a circumstance, we suggest using the
:attr:`pyramid.registry.Registry.settings` API in conjunction with a setting
in the application ``.ini`` file named ``media_location``.  Then set the
value of ``media_location`` to either a prefix or a URL depending on whether
the application is being run in development or in production (use a different
`.ini`` file for production than you do for development).  This is just a
suggestion for a pattern; any setting name other than ``media_location``
could be used.

.. index::
   single: static assets view

.. _advanced_static:

Advanced: Serving Static Assets Using a View Callable
-----------------------------------------------------

For more flexibility, static assets can be served by a :term:`view callable`
which you register manually.  For example, if you're using :term:`URL
dispatch`, you may want static assets to only be available as a fallback if
no previous route matches.  Alternately, you might like to serve a particular
static asset manually, because its download requires authentication.

Note that you cannot use the :func:`pyramid.url.static_url` API to generate
URLs against assets made accessible by registering a custom static view.

Root-Relative Custom Static View (URL Dispatch Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`pyramid.view.static` helper class generates a Pyramid view
callable.  This view callable can serve static assets from a directory.  An
instance of this class is actually used by the
:meth:`pyramid.config.Configurator.add_static_view` configuration method, so
its behavior is almost exactly the same once it's configured.

.. warning:: The following example *will not work* for applications that use
   :term:`traversal`, it will only work if you use :term:`URL dispatch`
   exclusively.  The root-relative route we'll be registering will always be
   matched before traversal takes place, subverting any views registered via
   ``add_view`` (at least those without a ``route_name``).  A
   :class:`pyramid.view.static` static view cannot be made root-relative when
   you use traversal.

To serve files within a directory located on your filesystem at
``/path/to/static/dir`` as the result of a "catchall" route hanging from the
root that exists at the end of your routing table, create an instance of the
:class:`pyramid.view.static` class inside a ``static.py`` file in your
application root as below.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from pyramid.view import static
   static_view = static('/path/to/static/dir')

.. note:: For better cross-system flexibility, use an :term:`asset
   specification` as the argument to :class:`pyramid.view.static` instead of
   a physical absolute filesystem path, e.g. ``mypackage:static`` instead of
   ``/path/to/mypackage/static``.

Subsequently, you may wire the files that are served by this view up to be
accessible as ``/<filename>`` using a configuration method in your
application's startup code.

.. code-block:: python
   :linenos:

   # .. every other add_route and/or add_handler declaration should come
   # before this one, as it will, by default, catch all requests

   config.add_route('catchall_static', '/*subpath', 'myapp.static.static_view')

The special name ``*subpath`` above is used by the
:class:`pyramid.view.static` view callable to signify the path of the file
relative to the directory you're serving.

Registering A View Callable to Serve a "Static" Asset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can register a simple view callable to serve a single static asset.  To
do so, do things "by hand".  First define the view callable.

.. code-block:: python
   :linenos:

   import os
   from webob import Response

   def favicon_view(request):
       here = os.path.dirname(__file__)
       icon = open(os.path.join(here, 'static', 'favicon.ico'))
       return Response(content_type='image/x-icon', app_iter=icon)

The above bit of code within ``favicon_view`` computes "here", which is a
path relative to the Python file in which the function is defined.  It then
uses the Python ``open`` function to obtain a file handle to a file within
"here" named ``static``, and returns a response using the open the file
handle as the response's ``app_iter``.  It makes sure to set the right
content_type too.

You might register such a view via configuration as a view callable that
should be called as the result of a traversal:

.. code-block:: python
   :linenos:

   config.add_view('myapp.views.favicon_view', name='favicon.ico')

Or you might register it to be the view callable for a particular route:

.. code-block:: python
   :linenos:

   config.add_route('favicon', '/favicon.ico', 
                    view='myapp.views.favicon_view')

Because this is a simple view callable, it can be protected with a
:term:`permission` or can be configured to respond under different
circumstances using :term:`view predicate` arguments.
