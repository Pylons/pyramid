Static Resources
================

:mod:`repoze.bfg` makes it possible to serve up "static" (non-dynamic)
resources from a directory on a filesystem.  This chapter describes
how to configure :mod:`repoze.bfg` to do so.

.. index::
   triple: view; zcml; static resource
   single: add_static_view

.. _static_resources_section:

Serving Static Resources Using a ZCML Directive
-----------------------------------------------

Use of the ``static`` ZCML directive or the
:meth:`repoze.bfg.configuration.configurator.add_static_view` method
is the preferred way to instruct :mod:`repoze.bfg` to serve static
resources such as JavaScript and CSS files. This mechanism makes
static files available at a name relative to the application root URL,
e.g. ``/static``.

Here's an example of a ``static`` ZCML directive that will serve files
up under the ``/static`` URL from the ``/var/www/static`` directory of
the computer which runs the :mod:`repoze.bfg` application.

.. code-block:: xml
   :linenos:

   <static
      name="static"
      path="/var/www/static"
      />

Here's an example of a ``static`` directive that will serve files up
under the ``/static`` URL from the ``a/b/c/static`` directory of the
Python package named ``some_package``.

.. code-block:: xml
   :linenos:

   <static
      name="static"
      path="some_package:a/b/c/static"
      />

Here's an example of a ``static`` directive that will serve files up
under the ``/static`` URL from the ``static`` directory of the Python
package in which the ``configure.zcml`` file lives.

.. code-block:: xml
   :linenos:

   <static
      name="static"
      path="static"
      />

When you place your static files on the filesystem in the directory
represented as the ``path`` of the directive, you should be able
to view the static files in this directory via a browser at URLs
prefixed with the directive's ``name``.  For instance if the
``static`` directive's ``name`` is ``static`` and the static
directive's ``path`` is ``/path/to/static``,
``http://localhost:6543/static/foo.js`` will return the file
``/path/to/static/dir/foo.js``.  The static directory may contain
subdirectories recursively, and any subdirectories may hold files;
these will be resolved by the static view as you would expect.

See :ref:`static_directive` for detailed information about the
``static`` ZCML directive.

.. note:: The :ref:`static_directive` ZCML directive is new in
   :mod:`repoze.bfg` 1.1.

The :meth:`repoze.bfg.configuration.Configurator.add_static_view`
method offers an imperative equivalent to the ``static`` ZCML
directive.  Use of the ``add_static_view`` imperative configuration
method is completely equivalent to using ZCML for the same purpose.

.. index::
   single: generating static resource urls
   single: static resource urls

.. _generating_static_resource_urls:

Generating Static Resource URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a :ref:`static_directive` ZCML directive or a call to the
``add_static_view`` method of a
:class:`repoze.bfg.configuration.Configurator` is used to register a
static resource directory, a special helper API named
:func:`repoze.bfg.static_url` can be used to generate the appropriate
URL for a package resource that lives in one of the directories named
by the static registration ``path`` attribute.

For example, let's assume you create a set of ``static`` declarations
in ZCML like so:

.. code-block:: xml
   :linenos:

   <static
      name="static1"
      path="resources/1"
      />

   <static
      name="static2"
      path="resources/2"
      />

These declarations create URL-accessible directories which have URLs
which begin, respectively, with ``/static1`` and ``/static2``.  The
resources in the ``resources/1`` directory are consulted when a user
visits a URL which begins with ``/static1``, and the resources in the
``resources/2`` directory are consulted when a user visits a URL which
begins with ``/static2``.

You needn't generate the URLs to static resources "by hand" in such a
configuration.  Instead, use the :func:`repoze.bfg.url.static_url` API
to generate them for you.  For example, let's imagine that the
following code lives in a module that shares the same directory as the
above ZCML file:

.. code-block:: python
   :linenos:

   from repoze.bfg.url import static_url
   from repoze.bfg.chameleon_zpt import render_template_to_response

   def my_view(request):
       css_url = static_url('resources/1/foo.css', request)
       js_url = static_url('resources/2/foo.js', request)
       return render_template_to_response('templates/my_template.pt',
                                          css_url = css_url,
                                          js_url = js_url)

If the request "application URL" of the running system is
``http://example.com``, the ``css_url`` generated above would be:
``http://example.com/static1/foo.css``.  The ``js_url`` generated
above would be ``http://example.com/static2/foo.js``.

One benefit of using the :func:`repoze.bfg.url.static_url` function
rather than constructing static URLs "by hand" is that if you need to
change the ``name`` of a static URL declaration in ZCML, the generated
URLs will continue to resolve properly after the rename.

.. note:: The :func:`repoze.bfg.url.static_url` API is new in
   :mod:`repoze.bfg` 1.1.

.. index::
   single: static resource view

Advanced: Serving Static Resources Using a View Callable
--------------------------------------------------------

For more flexibility, static resources can be served by a :term:`view
callable` which you register manually.  For example, you may want
static resources to only be available when the :term:`context` of the
view is of a particular type, or when the request is of a particular
type.

The :class:`repoze.bfg.view.static` helper class is used to perform
this task. This class creates an object that is capable acting as a
:mod:`repoze.bfg` view callable which serves static resources from a
directory.  For instance, to serve files within a directory located on
your filesystem at ``/path/to/static/dir`` mounted at the URL path
``/static`` in your application, create an instance of the
:class:`repoze.bfg.view.static` class inside a ``static.py`` file in
your application root as below.

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg.view import static
   static_view = static('/path/to/static/dir')

.. note:: the argument to :class:`repoze.bfg.view.static` can also be
   a relative pathname, e.g. ``my/static`` (meaning relative to the
   Python package of the module in which the view is being defined).
   It can also be a :term:`resource specification`
   (e.g. ``anotherpackage:some/subdirectory``) or it can be a
   "here-relative" path (e.g. ``some/subdirectory``).  If the path is
   "here-relative", it is relative to the package of the module in
   which the static view is defined.
 
Subsequently, you may wire this view up to be accessible as
``/static`` using either the
:mod:`repoze.bfg.configuration.Configurator.add_view` method or the
``<view>`` ZCML directive in your application's ``configure.zcml``
against either the class or interface that represents your root
object.  For example (ZCML):

.. code-block:: xml
   :linenos:

    <view
      context=".models.Root"
      view=".static.static_view"
      name="static"
    />   

In this case, ``.models.Root`` refers to the class of which your
:mod:`repoze.bfg` application's root object is an instance.

You can also provide a ``context`` of ``*`` if you want the name
``static`` to be accessible as the static view against any model.
This will also allow ``/static/foo.js`` to work, but it will allow for
``/anything/static/foo.js`` too, as long as ``anything`` itself is
resolvable.

Note that you cannot use the :func:`repoze.bfg.static_url` API to
generate URLs against resources made accessible by registering a
custom static view.

.. warning::

   To ensure that model objects contained in the root don't "shadow"
   your static view (model objects take precedence during traversal),
   or to ensure that your root object's ``__getitem__`` is never
   called when a static resource is requested, you can refer to your
   static resources as registered above in URLs as,
   e.g. ``/@@static/foo.js``.  This is completely equivalent to
   ``/static/foo.js``.  See :ref:`traversal_chapter` for information
   about "goggles" (``@@``).

