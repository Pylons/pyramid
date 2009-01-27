.. _vhosting_chapter:

Virtual Hosting
===============

:mod:`repoze.bfg` supports a traditional form of virtual hosting
provided by packages like Paste's `urlmap
<http://pythonpaste.org/modules/urlmap.html>`_ middleware, where you
can host a :mod:`repoze.bfg` application as a "subset" of some other
site (e.g. ``http://example.com/mybfgapplication``).  Nothing special
needs to be done within a :mod:`repoze.bfg` application to make this
work.

However, :mod:`repoze.bfg` also supports "virtual roots", which can be
used in :term:`traversal` -based (but not :term:`URL-dispatch` -based)
applications.  These are explained below.

Virtual Root Support
--------------------

Virtual root support is useful when you'd like to host some model in a
:mod:`repoze.bfg` model graph as an application under a URL pathname
that does not include the model path itself.  For example, you might
want to serve the object at the traversal path ``/cms`` as an
application on reachable via ``http://example.com/`` (as opposed to
``http://example.com/cms``). To specify a virtual root, cause an
environment variable to be inserted into the WSGI environ named
``HTTP_X_VHM_ROOT`` with a value that is the absolute pathname to the
model object in the traversal graph that should behave as the "root"
model.  As a result, the traversal machinery will respect this value
during traversal (prepending it to the PATH_INFO before traversal
starts), and the ``repoze.bfg.url.model_url`` API will generate the
"correct" virtually-rooted URLs.

An example of an Apache ``mod_proxy`` configuration that will host the
``/cms`` subobject as ``http://www.example.com/`` using this facility
is below:

.. code-block:: xml

    NameVirtualHost *:80

    <VirtualHost *:80>
      ServerName www.example.com
      RewriteEngine On
      RewriteRule ^/(.*) http://127.0.0.1:6543/$1 [L,P]
      ProxyPreserveHost on
      RequestHeader add X-Vhm-Root /cms
    </VirtualHost>

For a :mod:`repoze.bfg` application running under ``mod_wsgi``, the
same can be achieved using ``SetEnv``:

.. code-block:: xml

    <Location />
       SetEnv HTTP_X_VHM_ROOT /cms
     </Location>

Setting a virtual root has no effect when using an application based
on :term:`URL dispatch`.

Further Documentation and Examples
----------------------------------

The API documentation in :ref:`traversal_module` documents a
``repoze.bfg.traversal.virtual_root`` API.  When called, it returns
the virtual root object (or the physical root object if no virtual
root has been specified).
