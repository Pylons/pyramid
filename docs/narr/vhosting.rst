.. index::
   single: virtual hosting

.. _vhosting_chapter:

Virtual Hosting
===============

"Virtual hosting" is, loosely, the act of serving a :mod:`repoze.bfg`
application or a portion of a :mod:`repoze.bfg` application under a
URL space that it does not "naturally" inhabit.

:mod:`repoze.bfg` provides facilities for serving an application under
a URL "prefix", as well as serving a *portion* of a :term:`traversal`
based application under a root URL.

Hosting an Application Under a URL Prefix
-----------------------------------------

:mod:`repoze.bfg` supports a common form of virtual hosting whereby
you can host a :mod:`repoze.bfg` application as a "subset" of some
other site (e.g. under ``http://example.com/mybfgapplication/`` as
opposed to under ``http://example.com/``).

If you use a "pure Python" environment, this functionality is provided
by Paste's `urlmap <http://pythonpaste.org/modules/urlmap.html>`_
"composite" WSGI application.  Alternately, you can use
:term:`mod_wsgi` to serve your application, which handles this virtual
hosting translation for you "under the hood".

If you use the ``urlmap`` composite application "in front" of a
:mod:`repoze.bfg` application or if you use :term:`mod_wsgi` to serve
up a :mod:`repoze.bfg` application, nothing special needs to be done
within the application for URLs to be generated that contain a
prefix. :mod:`paste.urlmap` and :term:`mod_wsgi` manipulate the
:term:`WSGI` environment in such a way that the ``PATH_INFO`` and
``SCRIPT_NAME`` variables are correct for some given prefix.

Here's an example of a PasteDeploy configuration snippet that includes
a ``urlmap`` composite.

.. code-block:: ini

  [app:mybfgapp]
  use = egg:mybfgapp#app

  [composite:main]
  use = egg:Paste#urlmap
  /bfgapp =  bfgapp

This "roots" the :mod:`repoze.bfg` application at the prefix
``/bfgapp`` and serves up the composite as the "main" application in
the file.

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

   WSGIScriptAlias /bfgapp /Users/chrism/projects/modwsgi/env/bfg.wsgi

In the above configuration, we root a :mod:`repoze.bfg` application at
``/bfgapp`` within the Apache configuration.

.. index::
   single: virtual root

Virtual Root Support
--------------------

:mod:`repoze.bfg` also supports "virtual roots", which can be used in
:term:`traversal` -based (but not :term:`URL dispatch` -based)
applications.

Virtual root support is useful when you'd like to host some model in a
:mod:`repoze.bfg` object graph as an application under a URL pathname
that does not include the model path itself.  For example, you might
want to serve the object at the traversal path ``/cms`` as an
application reachable via ``http://example.com/`` (as opposed to
``http://example.com/cms``).

To specify a virtual root, cause an environment variable to be
inserted into the WSGI environ named ``HTTP_X_VHM_ROOT`` with a value
that is the absolute pathname to the model object in the traversal
graph that should behave as the "root" model.  As a result, the
traversal machinery will respect this value during traversal
(prepending it to the PATH_INFO before traversal starts), and the
:func:`repoze.bfg.url.model_url` API will generate the "correct"
virtually-rooted URLs.

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

For a :mod:`repoze.bfg` application running under :term:`mod_wsgi`,
the same can be achieved using ``SetEnv``:

.. code-block:: apache
   :linenos:

    <Location />
      SetEnv HTTP_X_VHM_ROOT /cms
    </Location>

Setting a virtual root has no effect when using an application based
on :term:`URL dispatch`.

Further Documentation and Examples
----------------------------------

The API documentation in :ref:`traversal_module` documents a
:func:`repoze.bfg.traversal.virtual_root` API.  When called, it
returns the virtual root object (or the physical root object if no
virtual root has been specified).

:ref:`modwsgi_tutorial` has detailed information about using
:term:`mod_wsgi` to serve :mod:`repoze.bfg` applications.

