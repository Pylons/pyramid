Static Resources
================

:mod:`pyramid` makes it possible to serve up "static" (non-dynamic)
resources from a directory on a filesystem.  This chapter describes
how to configure :mod:`pyramid` to do so.

.. index::
   single: add_static_view

.. _static_resources_section:

Serving Static Resources
------------------------

Use the :meth:`pyramid.configuration.Configurator.add_static_view` to
instruct :mod:`pyramid` to serve static resources such as JavaScript and CSS
files. This mechanism makes static files available at a name relative to the
application root URL, e.g. ``/static``.

Note that the ``path`` provided to
:meth:`pyramid.configuration.Configurator.add_static_view` may be a fully
qualified :term:`resource specification` or an *absolute path*.  

Here's an example of a use of
:meth:`pyramid.configuration.Configurator.add_static_view` that will serve
files up under the ``/static`` URL from the ``/var/www/static`` directory of
the computer which runs the :mod:`pyramid` application using an absolute
path.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.configuration.Configurator
   config.add_static_view(name='static', path='/var/www/static')

Here's an example of
:meth:`pyramid.configuration.Configurator.add_static_view` that will serve
files up under the ``/static`` URL from the ``a/b/c/static`` directory of the
Python package named ``some_package`` using a fully qualified :term:`resource
specification`.

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.configuration.Configurator
   config.add_static_view(name='static', path='some_package:a/b/c/static')

Whether you use for ``path`` a fully qualified resource specification, or an
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
argument of the call to
:meth:`pyramid.configuration.Configurator.add_static_view` can also be one of
a number of things: a *view name* or a *URL*.  The above examples have shown
usage of the ``name`` argument as a view name.  When ``name`` is a *URL* (or
any string with a slash (``/``) in it), static resources can be served from
an external webserver.  In this mode, the ``name`` is used as the URL prefix
when generating a URL using :func:`pyramid.url.static_url`.

.. note::

   Using :func:`pyramid.url.static_url` in conjunction with a
   :meth:`pyramid.configuration.Configurator.add_static_view` makes
   it possible to put static media on a separate webserver during
   production (if the ``name`` argument to
   :meth:`pyramid.configuration.Configurator.add_static_view` is a
   URL), while keeping static media package-internal and served by the
   development webserver during development (if the ``name`` argument
   to :meth:`pyramid.configuration.Configurator.add_static_view` is
   a view name).  To create such a circumstance, we suggest using the
   :func:`pyramid.settings.get_settings` API in conjunction with a
   setting in the application ``.ini`` file named ``media_location``.
   Then set the value of ``media_location`` to either a view name or a
   URL depending on whether the application is being run in
   development or in production (use a different `.ini`` file for
   production than you do for development).  This is just a suggestion
   for a pattern; any setting name other than ``media_location`` could
   be used.

For example, :meth:`pyramid.configuration.Configurator.add_static_view` may
be fed a ``name`` argument which is ``http://example.com/images``:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.configuration.Configurator
   config.add_static_view(name='http://example.com/images', 
                          path='mypackage:images')

Because :meth:`pyramid.configuration.Configurator.add_static_view` is
provided with a ``name`` argument that is the URL prefix
``http://example.com/images``, subsequent calls to
:func:`pyramid.url.static_url` with paths that start with the ``path``
argument passed to :meth:`pyramid.configuration.Configurator.add_static_view`
will generate a URL something like ``http://example.com/logo.png``.  The
external webserver listening on ``example.com`` must be itself configured to
respond properly to such a request.  The :func:`pyramid.url.static_url` API
is discussed in more detail later in this chapter.

The :ref:`static_directive` ZCML directive offers an declarative equivalent
to :meth:`pyramid.configuration.Configurator.add_static_view`.  Use of the
:ref:`static_directive` ZCML directive is completely equivalent to using
imperative configuration for the same purpose.

.. index::
   single: generating static resource urls
   single: static resource urls

.. _generating_static_resource_urls:

Generating Static Resource URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a :meth:`pyramid.configuration.Configurator.add_static_view`` method is
used to register a static resource directory, a special helper API named
:func:`pyramid.static_url` can be used to generate the appropriate URL for a
package resource that lives in one of the directories named by the static
registration ``path`` attribute.

For example, let's assume you create a set of static declarations like so:

.. code-block:: python
   :linenos:

   config.add_static_view(name='static1', path='mypackage:resources/1')
   config.add_static_view(name='static2', path='mypackage:resources/2')

These declarations create URL-accessible directories which have URLs which
begin, respectively, with ``/static1`` and ``/static2``.  The resources in
the ``resources/1`` directory of the ``mypackage`` package are consulted when
a user visits a URL which begins with ``/static1``, and the resources in the
``resources/2`` directory of the ``mypackage`` package are consulted when a
user visits a URL which begins with ``/static2``.

You needn't generate the URLs to static resources "by hand" in such a
configuration.  Instead, use the :func:`pyramid.url.static_url` API
to generate them for you.  For example:

.. code-block:: python
   :linenos:

   from pyramid.url import static_url
   from pyramid.chameleon_zpt import render_template_to_response

   def my_view(request):
       css_url = static_url('mypackage:resources/1/foo.css', request)
       js_url = static_url('mypackage:resources/2/foo.js', request)
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

URLs may also be generated by :func:`pyramid.url.static_url` to static
resources that live *outside* the :mod:`pyramid` application.  This will
happen when the :meth:`pyramid.configuration.Configurator.add_static_view`
API associated with the path fed to :func:`pyramid.url.static_url` is a *URL*
instead of a view name.  For example, the ``name`` argument may be
``http://example.com`` while the the ``path`` given may be
``mypackage:images``:

.. code-block:: python
   :linenos:

   config.add_static_view(name='static1', path='mypackage:images')

Under such a configuration, the URL generated by ``static_url`` for
resources which begin with ``mypackage:images`` will be prefixed with
``http://example.com/images``:

.. code-block:: python

   static_url('mypackage:images/logo.png', request)
   # -> http://example.com/images/logo.png

.. index::
   single: static resource view

Advanced: Serving Static Resources Using a View Callable
--------------------------------------------------------

For more flexibility, static resources can be served by a :term:`view
callable` which you register manually.  For example, you may want
static resources to only be available when the :term:`context` of the
view is of a particular type, or when the request is of a particular
type.

The :class:`pyramid.view.static` helper class is used to perform
this task. This class creates an object that is capable acting as a
:mod:`pyramid` view callable which serves static resources from a
directory.  For instance, to serve files within a directory located on
your filesystem at ``/path/to/static/dir`` mounted at the URL path
``/static`` in your application, create an instance of the
:class:`pyramid.view.static` class inside a ``static.py`` file in
your application root as below.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from pyramid.view import static
   static_view = static('/path/to/static/dir')

.. note:: the argument to :class:`pyramid.view.static` can also be
   a relative pathname, e.g. ``my/static`` (meaning relative to the
   Python package of the module in which the view is being defined).
   It can also be a :term:`resource specification`
   (e.g. ``anotherpackage:some/subdirectory``) or it can be a
   "here-relative" path (e.g. ``some/subdirectory``).  If the path is
   "here-relative", it is relative to the package of the module in
   which the static view is defined.
 
Subsequently, you may wire this view up to be accessible as ``/static`` using
the :mod:`pyramid.configuration.Configurator.add_view` method in your
application's startup code against either the class or interface that
represents your root object.

.. code-block:: python
   :linenos:

   config.add_view('mypackage.static.static_view', name='static',
                   context='mypackage.models.Root')

In this case, ``mypackage.models.Root`` refers to the class of which your
:mod:`pyramid` application's root object is an instance.

You can also omit the ``context`` argument if you want the name ``static`` to
be accessible as the static view against any model.  This will also allow
``/static/foo.js`` to work, but it will allow for ``/anything/static/foo.js``
too, as long as ``anything`` itself is resolvable.

Note that you cannot use the :func:`pyramid.static_url` API to generate URLs
against resources made accessible by registering a custom static view.

.. warning::

   To ensure that model objects contained in the root don't "shadow"
   your static view (model objects take precedence during traversal),
   or to ensure that your root object's ``__getitem__`` is never
   called when a static resource is requested, you can refer to your
   static resources as registered above in URLs as,
   e.g. ``/@@static/foo.js``.  This is completely equivalent to
   ``/static/foo.js``.  See :ref:`traversal_chapter` for information
   about "goggles" (``@@``).

