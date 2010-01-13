.. _zodb_with_zeo:

Using ZODB with ZEO
===================

:term:`ZODB` is a Python object persistence mechanism.  :term:`ZODB`
works well as a storage mechanism for :mod:`repoze.bfg` applications,
especially in applications that use :term:`traversal`.

:term:`ZEO` is an extension to ZODB which allows more than one process
to simultaneously communicate with a ZODB storage.  Making a ZODB
database accessible to more than one process means that you can debug
your application objects at the same time that a :mod:`repoze.bfg`
server that accesses the database is running, and will also allow your
application to run under multiprocess configurations, such as those
exposed by :term:`mod_wsgi`.

The easiest way to get started with ZODB in a :mod:`repoze.bfg`
application is to use the ZODB ``bfg_zodb`` paster template.  See
:ref:`additional_paster_templates` for more information about using
this template.  However, the Paster template does not set up a
ZEO-capable application.  This chapter shows you how to do that "from
scratch".

Installing Dependencies
-----------------------

#. Edit your :mod:`repoze.bfg` application's ``setup.py`` file, adding
   the following packages to the ``install_requires`` of the
   application:

   - ``repoze.folder``

   - ``repoze.retry``

   - ``repoze.tm2``

   - ``repoze.zodbconn``

   For example, the relevant portion of your application's
   ``setup.py`` file might look like so when you're finished adding
   the dependencies.

   .. code-block:: python
      :linenos:

      setup(
          # ... other elements left out for brevity
          install_requires=[
                'repoze.bfg',
                'repoze.folder',
                'repoze.retry',
                'repoze.tm2',
                'repoze.zodbconn',
                ],
          # ... other elements left out for brevity
           )

#. Rerun your application's ``setup.py`` file (e.g. using ``python
   setup.py develop``) to get these packages installed.  A number of
   packages will be installed, including ``ZODB``.  For the purposes
   of this tutorial, we'll assume that your "application" is actually
   just the result of the ``bfg_starter`` Paster template.

Configuration
-------------

#. Edit your application's Paste ``.ini`` file.

   If you already have an ``app`` section in the ``.ini`` file named
   ``main``, rename this section to ``myapp`` (e.g. ``app:main`` ->
   ``app:myapp``).  Add a key to it named ``zodb_uri``, e.g.

   .. code-block:: ini

      [app:myapp]
      use = egg:myapp#app
      zodb_uri = zeo://%(here)s/zeo.sock
      reload_templates = true
      debug_authorization = false
      debug_notfound = false

   If a ``pipeline`` named ``main`` does not already exist in the
   paste ``.ini`` file , add a ``pipeline`` section named ``main``.
   Put the names ``connector``, ``egg:repoze.retry#retry``, and
   ``egg:repoze.tm2#tm`` to the top of the pipeline.

   .. code-block:: ini

      [pipeline:main]
      pipeline = 
             egg:repoze.retry#retry
             egg:repoze.tm2#tm
             myapp

   When you're finished, your ``.ini`` file might look like so:

   .. code-block:: ini

      [DEFAULT]
      debug = true

      [app:myapp]
      use = egg:myapp#app
      zodb_uri = zeo://%(here)s/zeo.sock
      reload_templates = true
      debug_authorization = false
      debug_notfound = false

      [pipeline:main]
      pipeline = 
             egg:repoze.retry#retry
             egg:repoze.tm2#tm
             myapp

      [server:main]
      use = egg:Paste#http
      host = 0.0.0.0
      port = 6543

   See :ref:`MyProject_ini` for more information about project Paste
   ``.ini`` files.

#. Add a ``zeo.conf`` file to your package with the following
   contents:

   .. code-block:: text

      %define INSTANCE .

      <zeo>
        address $INSTANCE/zeo.sock
        read-only false
        invalidation-queue-size 100
        pid-filename $INSTANCE/zeo.pid
      </zeo>

      <blobstorage 1>
        <filestorage>
          path $INSTANCE/myapp.db
        </filestorage>
        blob-dir $INSTANCE/blobs
      </blobstorage>

#.  For the purposes of this tutorial we'll assume that you want your
    :mod:`repoze.bfg` application's :term:`root` object to be a
    "folderish" object.  To achieve this, change your application's
    ``models.py`` file to look like the below:

    .. code-block:: python

       from repoze.folder import Folder

       class MyModel(Folder):
           pass

       def appmaker(root):
           if not 'myapp' in root:
               root['myapp'] = MyModel()
               transaction.commit()
           return root['myapp']

#.  Change your application's ``run.py`` to look something like the
    below:

    .. code-block:: python

       from repoze.bfg.configuration import Configurator
       from repoze.zodbconn.finder import PersistentApplicationFinder
       from myapp.models import appmaker
       import transaction

       def app(global_config, **settings):
           """ This function returns a ``repoze.bfg`` WSGI 
           application.

           It is usually called by the PasteDeploy framework during
           ``paster serve``"""
           # paster app config callback
           zodb_uri = settings['zodb_uri']
           finder = PersistentApplicationFinder(zodb_uri, appmaker)
           def get_root(request):
               return finder(request.environ)
           config = Configurator(root_factory=get_root, settings=settings)
           return config.make_wsgi_app()

Running
-------
    
#.  Start the ZEO server in a terminal with the current directory set
    to the package directory:

    .. code-block:: text

       ../bin/runzeo -C zeo.conf

    You should see something like this, as a result:

    .. code-block:: text
       :linenos:

       [chrism@snowpro myapp]$ ../bin/runzeo -C zeo.conf 
       ------
       2009-09-19T13:48:41 INFO ZEO.runzeo (9910) created PID file './zeo.pid'
       # ... more output ...
       2009-09-19T13:48:41 INFO ZEO.zrpc (9910) listening on ./zeo.sock

#.  While the ZEO server is running, start the application server:

    .. code-block:: text
       :linenos:

       [chrism@snowpro myapp]$ ../bin/paster serve myapp.ini 
       Starting server in PID 10177.
       serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

#.  The root object is now a "folderish" ZODB object.  Nothing else
    about the application has changed.  

#.  You can manipulate the database directly (even when the
    application's HTTP server is running) by using the ``bfgshell``
    command in a third terminal window:

    .. code-block:: text
       :linenos:

       [chrism@snowpro sess]$ ../bin/paster --plugin=repoze.bfg bfgshell \
              myapp.ini myapp
       Python 2.5.4 (r254:67916, Sep  4 2009, 02:12:16) 
       [GCC 4.2.1 (Apple Inc. build 5646)] on darwin
       Type "help" for more information. "root" is the BFG app root object.
       >>> root
       <sess.models.MyModel object None at 0x16438f0>
       >>> root.foo = 'bar'
       >>> import transaction
       >>> transaction.commit()


