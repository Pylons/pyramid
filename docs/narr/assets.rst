.. index::
   single: assets
   single: static asssets

.. _assets_chapter:

Static Assets
=============

An :term:`asset` is any file contained within a Python :term:`package` which
is *not* a Python source code file.  For example, each of the following is an
asset:

- a GIF image file contained within a Python package or contained within any
  subdirectory of a Python package.

- a CSS file contained within a Python package or contained within any
  subdirectory of a Python package.

- a JavaScript source file contained within a Python package or contained
  within any subdirectory of a Python package.

- A directory within a package that does not have an ``__init__.py``
  in it (if it possessed an ``__init__.py`` it would *be* a package).

- a :term:`Chameleon` or :term:`Mako` template file contained within a Python
  package.

The use of assets is quite common in most web development projects.  For
example, when you create a :app:`Pyramid` application using one of the
available scaffolds, as described in :ref:`creating_a_project`, the
directory representing the application contains a Python :term:`package`.
Within that Python package, there are directories full of files which are
static assets.  For example, there's a ``static`` directory which contains
``.css``, ``.js``, and ``.gif`` files.  These asset files are delivered when
a user visits an application URL.

.. index::
   single: asset specifications

.. _asset_specifications:

Understanding Asset Specifications
----------------------------------

Let's imagine you've created a :app:`Pyramid` application that uses a
:term:`Chameleon` ZPT template via the
:func:`pyramid.renderers.render_to_response` API.  For example, the
application might address the asset using the :term:`asset specification`
``myapp:templates/some_template.pt`` using that API within a ``views.py``
file inside a ``myapp`` package:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from pyramid.renderers import render_to_response
   render_to_response('myapp:templates/some_template.pt', {}, request)

"Under the hood", when this API is called, :app:`Pyramid` attempts to make
sense out of the string ``myapp:templates/some_template.pt`` provided by the
developer.  This string is an :term:`asset specification`.  It is composed of
two parts:

- The *package name* (``myapp``)

- The *asset name* (``templates/some_template.pt``), relative to the package
  directory.

The two parts are separated by the colon character.

:app:`Pyramid` uses the Python :term:`pkg_resources` API to resolve the
package name and asset name to an absolute (operating-system-specific) file
name.  It eventually passes this resolved absolute filesystem path to the
Chameleon templating engine, which then uses it to load, parse, and execute
the template file.

There is a second form of asset specification: a *relative* asset
specification.  Instead of using an "absolute" asset specification which
includes the package name, in certain circumstances you can omit the package
name from the specification.  For example, you might be able to use
``templates/mytemplate.pt`` instead of ``myapp:templates/some_template.pt``.
Such asset specifications are usually relative to a "current package."  The
"current package" is usually the package which contains the code that *uses*
the asset specification.  :app:`Pyramid` APIs which accept relative asset
specifications typically describe what the asset is relative to in their
individual documentation.

.. index::
   single: add_static_view
   pair: assets; serving

.. _static_assets_section:

Serving Static Assets
---------------------

:app:`Pyramid` makes it possible to serve up static asset files from a
directory on a filesystem to an application user's browser.  Use the
:meth:`pyramid.config.Configurator.add_static_view` to instruct
:app:`Pyramid` to serve static assets such as JavaScript and CSS files. This
mechanism makes a directory of static files available at a name relative to
the application root URL, e.g. ``/static`` or as an external URL.

.. note::

   :meth:`~pyramid.config.Configurator.add_static_view` cannot serve a
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
static assets must be protected by a more complex authorization scheme,
see :ref:`advanced_static`.

Here's another example that uses an :term:`asset specification` instead of an
absolute path as the ``path`` argument.  To convince
:meth:`~pyramid.config.Configurator.add_static_view` to serve files up under
the ``/static`` URL from the ``a/b/c/static`` directory of the Python package
named ``some_package``, we can use a fully qualified :term:`asset
specification` as the ``path``:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='static', path='some_package:a/b/c/static')

The ``path`` provided to :meth:`~pyramid.config.Configurator.add_static_view`
may be a fully qualified :term:`asset specification` or an *absolute path*.

Instead of representing a URL prefix, the ``name`` argument of a call to
:meth:`~pyramid.config.Configurator.add_static_view` can alternately be a
*URL*.  Each of examples we've seen so far have shown usage of the ``name``
argument as a URL prefix.  However, when ``name`` is a *URL*, static assets
can be served from an external webserver.  In this mode, the ``name`` is used
as the URL prefix when generating a URL using
:meth:`pyramid.request.Request.static_url`.

For example, :meth:`~pyramid.config.Configurator.add_static_view` may
be fed a ``name`` argument which is ``http://example.com/images``:

.. code-block:: python
   :linenos:

   # config is an instance of pyramid.config.Configurator
   config.add_static_view(name='http://example.com/images', 
                          path='mypackage:images')

Because :meth:`~pyramid.config.Configurator.add_static_view` is provided with
a ``name`` argument that is the URL ``http://example.com/images``, subsequent
calls to :meth:`~pyramid.request.Request.static_url` with paths that start
with the ``path`` argument passed to
:meth:`~pyramid.config.Configurator.add_static_view` will generate a URL
something like ``http://example.com/images/logo.png``.  The external
webserver listening on ``example.com`` must be itself configured to respond
properly to such a request.  The :meth:`~pyramid.request.Request.static_url`
API is discussed in more detail later in this chapter.

.. index::
   single: generating static asset urls
   single: static asset urls
   pair:   assets; generating urls

.. _generating_static_asset_urls:

Generating Static Asset URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a :meth:`~pyramid.config.Configurator.add_static_view` method is used to
register a static asset directory, a special helper API named
:meth:`pyramid.request.Request.static_url` can be used to generate the
appropriate URL for an asset that lives in one of the directories named by
the static registration ``path`` attribute.

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
configuration.  Instead, use the :meth:`~pyramid.request.Request.static_url`
API to generate them for you.  For example:

.. code-block:: python
   :linenos:

   from pyramid.chameleon_zpt import render_template_to_response

   def my_view(request):
       css_url = request.static_url('mypackage:assets/1/foo.css')
       js_url = request.static_url('mypackage:assets/2/foo.js')
       return render_template_to_response('templates/my_template.pt',
                                          css_url = css_url,
                                          js_url = js_url)

If the request "application URL" of the running system is
``http://example.com``, the ``css_url`` generated above would be:
``http://example.com/static1/foo.css``.  The ``js_url`` generated
above would be ``http://example.com/static2/foo.js``.

One benefit of using the :meth:`~pyramid.request.Request.static_url` function
rather than constructing static URLs "by hand" is that if you need to change
the ``name`` of a static URL declaration, the generated URLs will continue to
resolve properly after the rename.

URLs may also be generated by :meth:`~pyramid.request.Request.static_url` to
static assets that live *outside* the :app:`Pyramid` application.  This will
happen when the :meth:`~pyramid.config.Configurator.add_static_view` API
associated with the path fed to :meth:`~pyramid.request.Request.static_url`
is a *URL* instead of a view name.  For example, the ``name`` argument may be
``http://example.com`` while the the ``path`` given may be
``mypackage:images``:

.. code-block:: python
   :linenos:

   config.add_static_view(name='http://example.com/images', 
                          path='mypackage:images')

Under such a configuration, the URL generated by ``static_url`` for
assets which begin with ``mypackage:images`` will be prefixed with
``http://example.com/images``:

.. code-block:: python
   :linenos:

   request.static_url('mypackage:images/logo.png')
   # -> http://example.com/images/logo.png

Using :meth:`~pyramid.request.Request.static_url` in conjunction with a
:meth:`~pyramid.configuration.Configurator.add_static_view` makes it possible
to put static media on a separate webserver during production (if the
``name`` argument to :meth:`~pyramid.config.Configurator.add_static_view` is
a URL), while keeping static media package-internal and served by the
development webserver during development (if the ``name`` argument to
:meth:`~pyramid.config.Configurator.add_static_view` is a URL prefix).  To
create such a circumstance, we suggest using the
:attr:`pyramid.registry.Registry.settings` API in conjunction with a setting
in the application ``.ini`` file named ``media_location``.  Then set the
value of ``media_location`` to either a prefix or a URL depending on whether
the application is being run in development or in production (use a different
``.ini`` file for production than you do for development).  This is just a
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

Note that you cannot use the :meth:`~pyramid.request.Request.static_url` API
to generate URLs against assets made accessible by registering a custom
static view.

Root-Relative Custom Static View (URL Dispatch Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`pyramid.static.static_view` helper class generates a Pyramid view
callable.  This view callable can serve static assets from a directory.  An
instance of this class is actually used by the
:meth:`~pyramid.config.Configurator.add_static_view` configuration method, so
its behavior is almost exactly the same once it's configured.

.. warning::

   The following example *will not work* for applications that use
   :term:`traversal`, it will only work if you use :term:`URL dispatch`
   exclusively.  The root-relative route we'll be registering will always be
   matched before traversal takes place, subverting any views registered via
   ``add_view`` (at least those without a ``route_name``).  A
   :class:`~pyramid.static.static_view` static view cannot be made
   root-relative when you use traversal unless it's registered as a
   :term:`Not Found view`.

To serve files within a directory located on your filesystem at
``/path/to/static/dir`` as the result of a "catchall" route hanging from the
root that exists at the end of your routing table, create an instance of the
:class:`~pyramid.static.static_view` class inside a ``static.py`` file in
your application root as below.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from pyramid.static import static_view
   static_view = static_view('/path/to/static/dir', use_subpath=True)

.. note:: For better cross-system flexibility, use an :term:`asset
   specification` as the argument to :class:`~pyramid.static.static_view`
   instead of a physical absolute filesystem path, e.g. ``mypackage:static``
   instead of ``/path/to/mypackage/static``.

Subsequently, you may wire the files that are served by this view up to be
accessible as ``/<filename>`` using a configuration method in your
application's startup code.

.. code-block:: python
   :linenos:

   # .. every other add_route declaration should come
   # before this one, as it will, by default, catch all requests

   config.add_route('catchall_static', '/*subpath')
   config.add_view('myapp.static.static_view', route_name='catchall_static')

The special name ``*subpath`` above is used by the
:class:`~pyramid.static.static_view` view callable to signify the path of the
file relative to the directory you're serving.

Registering A View Callable to Serve a "Static" Asset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can register a simple view callable to serve a single static asset.  To
do so, do things "by hand".  First define the view callable.

.. code-block:: python
   :linenos:

   import os
   from pyramid.response import FileResponse

   def favicon_view(request):
       here = os.path.dirname(__file__)
       icon = os.path.join(here, 'static', 'favicon.ico')
       return FileResponse(icon, request=request)

The above bit of code within ``favicon_view`` computes "here", which is a
path relative to the Python file in which the function is defined.  It then
creates a :class:`pyramid.response.FileResponse` using the file path as the
response's ``path`` argument and the request as the response's ``request``
argument.  :class:`pyramid.response.FileResponse` will serve the file as
quickly as possible when it's used this way.  It makes sure to set the right
content length and content_type too based on the file extension of the file
you pass.

You might register such a view via configuration as a view callable that
should be called as the result of a traversal:

.. code-block:: python
   :linenos:

   config.add_view('myapp.views.favicon_view', name='favicon.ico')

Or you might register it to be the view callable for a particular route:

.. code-block:: python
   :linenos:

   config.add_route('favicon', '/favicon.ico')
   config.add_view('myapp.views.favicon_view', route_name='favicon')

Because this is a simple view callable, it can be protected with a
:term:`permission` or can be configured to respond under different
circumstances using :term:`view predicate` arguments.


.. index::
   pair: overriding; assets

.. _overriding_assets_section:

Overriding Assets
-----------------

It can often be useful to override specific assets from "outside" a given
:app:`Pyramid` application.  For example, you may wish to reuse an existing
:app:`Pyramid` application more or less unchanged.  However, some specific
template file owned by the application might have inappropriate HTML, or some
static asset (such as a logo file or some CSS file) might not be appropriate.
You *could* just fork the application entirely, but it's often more
convenient to just override the assets that are inappropriate and reuse the
application "as is".  This is particularly true when you reuse some "core"
application over and over again for some set of customers (such as a CMS
application, or some bug tracking application), and you want to make
arbitrary visual modifications to a particular application deployment without
forking the underlying code.

To this end, :app:`Pyramid` contains a feature that makes it possible to
"override" one asset with one or more other assets.  In support of this
feature, a :term:`Configurator` API exists named
:meth:`pyramid.config.Configurator.override_asset`.  This API allows you to
*override* the following kinds of assets defined in any Python package:

- Individual :term:`Chameleon` templates.

- A directory containing multiple Chameleon templates.

- Individual static files served up by an instance of the
  ``pyramid.static.static_view`` helper class.

- A directory of static files served up by an instance of the
  ``pyramid.static.static_view`` helper class.

- Any other asset (or set of assets) addressed by code that uses the
  setuptools :term:`pkg_resources` API.

.. index::
   single: override_asset

.. _override_asset:

The ``override_asset`` API
~~~~~~~~~~~~~~~~~~~~~~~~~~

An individual call to :meth:`~pyramid.config.Configurator.override_asset`
can override a single asset.  For example:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_asset(
            to_override='some.package:templates/mytemplate.pt',
            override_with='another.package:othertemplates/anothertemplate.pt')

The string value passed to both ``to_override`` and ``override_with`` sent to
the ``override_asset`` API is called an :term:`asset specification`.  The
colon separator in a specification separates the *package name* from the
*asset name*.  The colon and the following asset name are optional.  If they
are not specified, the override attempts to resolve every lookup into a
package from the directory of another package.  For example:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_asset(to_override='some.package',
                         override_with='another.package')

Individual subdirectories within a package can also be overridden:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_asset(to_override='some.package:templates/',
                         override_with='another.package:othertemplates/')


If you wish to override a directory with another directory, you *must*
make sure to attach the slash to the end of both the ``to_override``
specification and the ``override_with`` specification.  If you fail to
attach a slash to the end of a specification that points to a directory,
you will get unexpected results.

You cannot override a directory specification with a file specification, and
vice versa: a startup error will occur if you try.  You cannot override an
asset with itself: a startup error will occur if you try.

Only individual *package* assets may be overridden.  Overrides will not
traverse through subpackages within an overridden package.  This means that
if you want to override assets for both ``some.package:templates``, and
``some.package.views:templates``, you will need to register two overrides.

The package name in a specification may start with a dot, meaning that
the package is relative to the package in which the configuration
construction file resides (or the ``package`` argument to the
:class:`~pyramid.config.Configurator` class construction).
For example:

.. ignore-next-block
.. code-block:: python
   :linenos:

   config.override_asset(to_override='.subpackage:templates/',
                         override_with='another.package:templates/')

Multiple calls to ``override_asset`` which name a shared ``to_override`` but
a different ``override_with`` specification can be "stacked" to form a search
path.  The first asset that exists in the search path will be used; if no
asset exists in the override path, the original asset is used.

Asset overrides can actually override assets other than templates and static
files.  Any software which uses the
:func:`pkg_resources.get_resource_filename`,
:func:`pkg_resources.get_resource_stream` or
:func:`pkg_resources.get_resource_string` APIs will obtain an overridden file
when an override is used.

