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
mechanism makes static files available at a name relative to the application
root URL, e.g. ``/static``.

Note that the ``path`` provided to
:meth:`pyramid.config.Configurator.add_static_view` may be a fully qualified
:term:`asset specification`, or an *absolute path*.

Here's an example of a use of
:meth:`pyramid.config.Configurator.add_static_view` that will serve
files up under the ``/static`` URL from the ``/var/www/static`` directory of
the computer which runs the :app:`Pyramid` application using an absolute
path.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='static', path='/var/www/static')

Here's an example of :meth:`pyramid.config.Configurator.add_static_view` that
will serve files up under the ``/static`` URL from the ``a/b/c/static``
directory of the Python package named ``some_package`` using a fully
qualified :term:`asset specification`.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='static', path='some_package:a/b/c/static')

Whether you use for ``path`` a fully qualified asset specification, or an
absolute path, when you place your static files on the filesystem in the
directory represented as the ``path`` of the directive, you will then be able
to view the static files in this directory via a browser at URLs prefixed
with the directive's ``name``.  For instance if the ``static`` directive's
``name`` is ``static`` and the static directive's ``path`` is
``/path/to/static``, ``http://localhost:6543/static/foo.js`` will return the
file ``/path/to/static/dir/foo.js``.  The static directory may contain
subdirectories recursively, and any subdirectories may hold files; these will
be resolved by the static view as you would expect.

While the ``path`` argument can be a number of different things, the ``name``
argument of the call to :meth:`pyramid.config.Configurator.add_static_view`
can also be one of a number of things: a *view name* or a *URL*.  The above
examples have shown usage of the ``name`` argument as a view name.  When
``name`` is a *URL* (or any string with a slash (``/``) in it), static assets
can be served from an external webserver.  In this mode, the ``name`` is used
as the URL prefix when generating a URL using :func:`pyramid.url.static_url`.

.. note::

   Using :func:`pyramid.url.static_url` in conjunction with a
   :meth:`pyramid.config.Configurator.add_static_view` makes it
   possible to put static media on a separate webserver during production (if
   the ``name`` argument to
   :meth:`pyramid.config.Configurator.add_static_view` is a URL),
   while keeping static media package-internal and served by the development
   webserver during development (if the ``name`` argument to
   :meth:`pyramid.config.Configurator.add_static_view` is a view
   name).  To create such a circumstance, we suggest using the
   :attr:`pyramid.registry.Registry.settings` API in conjunction with a
   setting in the application ``.ini`` file named ``media_location``.  Then
   set the value of ``media_location`` to either a view name or a URL
   depending on whether the application is being run in development or in
   production (use a different `.ini`` file for production than you do for
   development).  This is just a suggestion for a pattern; any setting name
   other than ``media_location`` could be used.

For example, :meth:`pyramid.config.Configurator.add_static_view` may
be fed a ``name`` argument which is ``http://example.com/images``:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='http://example.com/images', 
                          path='mypackage:images')

Because :meth:`pyramid.config.Configurator.add_static_view` is
provided with a ``name`` argument that is the URL prefix
``http://example.com/images``, subsequent calls to
:func:`pyramid.url.static_url` with paths that start with the ``path``
argument passed to :meth:`pyramid.config.Configurator.add_static_view`
will generate a URL something like ``http://example.com/images/logo.png``.  The
external webserver listening on ``example.com`` must be itself configured to
respond properly to such a request.  The :func:`pyramid.url.static_url` API
is discussed in more detail later in this chapter.

The :ref:`static_directive` ZCML directive offers an declarative equivalent
to :meth:`pyramid.config.Configurator.add_static_view`.  Use of the
:ref:`static_directive` ZCML directive is completely equivalent to using
imperative configuration for the same purpose.

.. note::

   Using :func:`pyramid.url.static_url` in conjunction with a
   :meth:`pyramid.configuration.Configurator.add_static_view` makes it
   possible to put static media on a separate webserver during production (if
   the ``name`` argument to
   :meth:`pyramid.configuration.Configurator.add_static_view` is a URL),
   while keeping static media package-internal and served by the development
   webserver during development (if the ``name`` argument to
   :meth:`pyramid.configuration.Configurator.add_static_view` is a view
   name).  To create such a circumstance, we suggest using the
   :attr:`pyramid.registry.Registry.settings` API in conjunction with a
   setting in the application ``.ini`` file named ``media_location``.  Then
   set the value of ``media_location`` to either a view name or a URL
   depending on whether the application is being run in development or in
   production (use a different `.ini`` file for production than you do for
   development).  This is just a suggestion for a pattern; any setting name
   other than ``media_location`` could be used.

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

   config.add_static_view(name='http://example.com/images', path='mypackage:images')

Under such a configuration, the URL generated by ``static_url`` for
assets which begin with ``mypackage:images`` will be prefixed with
``http://example.com/images``:

.. code-block:: python
   :linenos:

   static_url('mypackage:images/logo.png', request)
   # -> http://example.com/images/logo.png

.. index::
   single: static assets view

Advanced: Serving Static Assets Using a View Callable
-----------------------------------------------------

For more flexibility, static assets can be served by a :term:`view callable`
which you register manually.  For example, you may want static assets to only
be available when the :term:`context` is of a particular type, or when
certain request headers are present.

The :class:`pyramid.view.static` helper class is used to perform this
task. This class creates an object that is capable acting as a :app:`Pyramid`
view callable which serves static assets from a directory.  For instance, to
serve files within a directory located on your filesystem at
``/path/to/static/dir`` from the URL path ``/static`` in your application,
create an instance of the :class:`pyramid.view.static` class inside a
``static.py`` file in your application root as below.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from pyramid.view import static
   static_view = static('/path/to/static/dir')

.. note:: the argument to :class:`pyramid.view.static` can also be
   a "here-relative" pathname, e.g. ``my/static`` (meaning relative to the
   Python package of the module in which the view is being defined).
   It can also be a :term:`asset specification`
   (e.g. ``anotherpackage:some/subdirectory``).
 
Subsequently, you may wire this view up to be accessible as ``/static`` using
the :mod:`pyramid.config.Configurator.add_view` method in your application's
startup code against either the class or interface that represents your root
resource object.

.. code-block:: python
   :linenos:

   config.add_view('mypackage.static.static_view', name='static',
                   context='mypackage.resources.Root')

In this case, ``mypackage.resources.Root`` refers to the class of your
:app:`Pyramid` application's resource tree.

The context argument above limits where the static view is accessible to URL
paths directly under the root object.  If you omit the ``context`` argument,
then ``static`` will be accessible as the static view against any resource
object in the resource tree.  This will allow ``/static/foo.js`` to work, but
it will also allow for ``/anything/static/foo.js`` too, as long as
``anything`` can be resolved.

Note that you cannot use the :func:`pyramid.url.static_url` API to generate
URLs against assets made accessible by registering a custom static view.

.. warning::

   When adding a static view to your root object, you need to be careful that
   there are no resource objects contained in the root with the same key as
   the view name (e.g., ``static``).  Resource objects take precedence during
   traversal, thus such a name collision will cause the resource to "shadow"
   your static view. To avoid this issue, and ensure that your root
   resource's ``__getitem__`` is never called when a static asset is
   requested, you can refer to them unambiguously using the ``@@`` prefix
   (goggles) in their URLs.  For the above examples you could use
   '/@@static/foo.js' instead of '/static/foo.js' to avoid such shadowing.
   See :ref:`traversal_chapter` for information about "goggles" (``@@``).

