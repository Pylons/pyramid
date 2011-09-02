.. index::
   single: virtual hosting

.. _vhosting_chapter:

Virtual Hosting
===============

"Virtual hosting" is, loosely, the act of serving a :app:`Pyramid`
application or a portion of a :app:`Pyramid` application under a
URL space that it does not "naturally" inhabit.

:app:`Pyramid` provides facilities for serving an application under
a URL "prefix", as well as serving a *portion* of a :term:`traversal`
based application under a root URL.

.. index::
   single: hosting an app under a prefix

Hosting an Application Under a URL Prefix
-----------------------------------------

:app:`Pyramid` supports a common form of virtual hosting whereby you
can host a :app:`Pyramid` application as a "subset" of some other site
(e.g. under ``http://example.com/mypyramidapplication/`` as opposed to
under ``http://example.com/``).

If you use a "pure Python" environment, this functionality is provided
by Paste's `urlmap <http://pythonpaste.org/modules/urlmap.html>`_
"composite" WSGI application.  Alternately, you can use
:term:`mod_wsgi` to serve your application, which handles this virtual
hosting translation for you "under the hood".

If you use the ``urlmap`` composite application "in front" of a
:app:`Pyramid` application or if you use :term:`mod_wsgi` to serve
up a :app:`Pyramid` application, nothing special needs to be done
within the application for URLs to be generated that contain a
prefix. :mod:`paste.urlmap` and :term:`mod_wsgi` manipulate the
:term:`WSGI` environment in such a way that the ``PATH_INFO`` and
``SCRIPT_NAME`` variables are correct for some given prefix.

Here's an example of a PasteDeploy configuration snippet that includes
a ``urlmap`` composite.

.. code-block:: ini
  :linenos:

  [app:mypyramidapp]
  use = egg:mypyramidapp

  [composite:main]
  use = egg:Paste#urlmap
  /pyramidapp = mypyramidapp

This "roots" the :app:`Pyramid` application at the prefix
``/pyramidapp`` and serves up the composite as the "main" application
in the file.

.. note:: If you're using an Apache server to proxy to a Paste
   ``urlmap`` composite, you may have to use the `ProxyPreserveHost
   <http://httpd.apache.org/docs/2.2/mod/mod_proxy.html#proxypreservehost>`_
   directive to pass the original ``HTTP_HOST`` header along to the
   application, so URLs get generated properly.  As of this writing
   the ``urlmap`` composite does not seem to respect the
   ``HTTP_X_FORWARDED_HOST`` parameter, which will contain the
   original host header even if ``HTTP_HOST`` is incorrect.

If you use :term:`mod_wsgi`, you do not need to use a ``composite``
application in your ``.ini`` file.  The ``WSGIScriptAlias``
configuration setting in a :term:`mod_wsgi` configuration does the
work for you:

.. code-block:: apache
   :linenos:

   WSGIScriptAlias /pyramidapp /Users/chrism/projects/modwsgi/env/pyramid.wsgi

In the above configuration, we root a :app:`Pyramid` application at
``/pyramidapp`` within the Apache configuration.

.. index::
   single: virtual root

.. _virtual_root_support:

Virtual Root Support
--------------------

:app:`Pyramid` also supports "virtual roots", which can be used in
:term:`traversal` -based (but not :term:`URL dispatch` -based)
applications.

Virtual root support is useful when you'd like to host some resource in a
:app:`Pyramid` resource tree as an application under a URL pathname that does
not include the resource path itself.  For example, you might want to serve the
object at the traversal path ``/cms`` as an application reachable via
``http://example.com/`` (as opposed to ``http://example.com/cms``).

To specify a virtual root, cause an environment variable to be inserted into
the WSGI environ named ``HTTP_X_VHM_ROOT`` with a value that is the absolute
pathname to the resource object in the resource tree that should behave as
the "root" resource.  As a result, the traversal machinery will respect this
value during traversal (prepending it to the PATH_INFO before traversal
starts), and the :meth:`pyramid.request.Request.resource_url` API will
generate the "correct" virtually-rooted URLs.

An example of an Apache ``mod_proxy`` configuration that will host the
``/cms`` subobject as ``http://www.example.com/`` using this facility
is below:

.. code-block:: apache
   :linenos:

    NameVirtualHost *:80

    <VirtualHost *:80>
      ServerName www.example.com
      RewriteEngine On
      RewriteRule ^/(.*) http://127.0.0.1:6543/$1 [L,P]
      ProxyPreserveHost on
      RequestHeader add X-Vhm-Root /cms
    </VirtualHost>

.. note:: Use of the ``RequestHeader`` directive requires that the
   Apache `mod_headers
   <http://httpd.apache.org/docs/2.2/mod/mod_headers.html>`_ module be
   available in the Apache environment you're using.

For a :app:`Pyramid` application running under :term:`mod_wsgi`,
the same can be achieved using ``SetEnv``:

.. code-block:: apache
   :linenos:

    <Location />
      SetEnv HTTP_X_VHM_ROOT /cms
    </Location>

Setting a virtual root has no effect when using an application based
on :term:`URL dispatch`.

Fixing HTTP vs. HTTPS When Deploying Behind a Proxy
---------------------------------------------------

In a configuration where you have a :app:`Pyramid` server behind an Apache or
Nginx or Squid proxy which serves your website over SSL (as ``https``) as in
the above example in :ref:`virtual_root_support`, the request will be passed
by the proxy to an `http://`` URL that will be served by :app:`Pyramid`.
Because this is true, URLs generated by :app:`Pyramid` will be generated with
``http://`` instead of ``https://``; the SSL info has been "lost" during the
proxying.

To work around this, convert your application to use a "pipeline" instead of
a simple "app" in your PasteDeploy configuration, then add ``prefix``
middleware to the pipeline.  For example, if your ``production.ini`` file has
a ``main`` section that looks like this:

.. code-block:: ini

   [app:main]
   use = egg:MyProject

Convert it to look like this:

.. code-block:: ini

   [app:myapp]
   use = egg:MyProject

   [pipeline:main]
   pipeline =
       myapp

Then add the ``paste.prefix`` middleware with no options to the pipeline:

.. code-block:: ini

   [app:myapp]
   use = egg:MyProject

   [filter:paste_prefix]
   use = egg:PasteDeploy#prefix

   [pipeline:main]
   pipeline =
       paste_prefix
       myapp

This will have the side effect of retaining ``https`` URLs during generation.

Further Documentation and Examples
----------------------------------

The API documentation in :ref:`traversal_module` documents a
:func:`pyramid.traversal.virtual_root` API.  When called, it
returns the virtual root object (or the physical root object if no
virtual root has been specified).

:ref:`modwsgi_tutorial` has detailed information about using
:term:`mod_wsgi` to serve :app:`Pyramid` applications.

