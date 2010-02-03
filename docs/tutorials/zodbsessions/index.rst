.. _zodb_sessions:

Using ZODB-Based Sessions
=========================

Sessions are server-side namespaces which are associated with a site
user that expire automatically after some period of disuse.

If your application is ZODB-based (e.g. you've created an application
from the ``bfg_zodb`` paster template, or you've followed the
instructions in :ref:`zodb_with_zeo`), you can make use of the
``repoze.session`` and ``repoze.browserid`` packages to add
sessioning to your application.

.. note:: You can use the ``repoze.session`` package even if your
   application is not ZODB-based, but its backing store requires ZODB,
   so it makes the most sense to use this package if your application
   already uses ZODB.  This tutorial does not cover usage of
   ``repoze.session``-based sessions in applications that don't
   already use ZODB.  For this, see `the standalone repoze.session
   usage documentation <http://docs.repoze.org/session/usage.html>`_.
   If you don't want to use ZODB to do sessioning, you might choose to
   use a relational/filestorage sessioning system such as `Beaker
   <http://pypi.python.org/pypi/Beaker>`_.  :mod:`repoze.bfg` is fully
   compatible with this system too.

Installing Dependencies
-----------------------

#. Edit your :mod:`repoze.bfg` application's ``setup.py`` file, adding
   the following packages to the ``install_requires`` of the
   application:

   - ``repoze.session``

   - ``repoze.browserid``

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
                'repoze.session'
                'repoze.browserid',
                ],
          # ... other elements left out for brevity
           )

#. Rerun your application's ``setup.py`` file (e.g. using ``python
   setup.py develop``) to get these packages installed.

Configuration
-------------

#. Edit your application's Paste ``.ini`` file.

   If you already have an ``app`` section in the ``.ini`` file named
   ``main``, rename this section to ``myapp`` (e.g. ``app:main`` ->
   ``app:myapp``).  Add a key to it named ``zodb_uri``, e.g.

   .. code-block:: python
      :linenos:

      [app:myapp]
      use = egg:myapp#app
      zodb_uri = zeo://%(here)s/zeo.sock
      reload_templates = true
      debug_authorization = false
      debug_notfound = false

   Add a ``filter`` section to the ``.ini`` file named "browserid":

   .. code-block:: python
      :linenos:

      [filter:browserid]
      use = egg:repoze.browserid#browserid
      secret_key = my-secret-key

   Replace ``my-secret-key`` with any random string.  This string
   represents the value which the client-side "browser id" cookie is
   encrypted with, to prevent tampering.

   If a ``pipeline`` named ``main`` does not already exist in the
   paste ``.ini`` file , add a ``pipeline`` section named ``main``.
   Put the names ``connector``, ``egg:repoze.retry#retry``, and
   ``egg:repoze.tm2#tm`` to the top of the pipeline.

   .. code-block:: python
      :linenos:

      [pipeline:main]
      pipeline = 
             browserid
             egg:repoze.retry#retry
             egg:repoze.tm2#tm
             myapp

   When you're finished, your ``.ini`` file might look like so:

   .. code-block:: ini
      :linenos:

      [DEFAULT]
      debug = true

      [app:myapp]
      use = egg:myapp#app
      zodb_uri = zeo://%(here)s/zeo.sock
      reload_templates = true
      debug_authorization = false
      debug_notfound = false

      [filter:browserid]
      use = egg:repoze.browserid#browserid
      secret_key = my-secret-key

      [pipeline:main]
      pipeline = 
             browserid
             egg:repoze.retry#retry
             egg:repoze.tm2#tm
             myapp

      [server:main]
      use = egg:Paste#http
      host = 0.0.0.0
      port = 6543

   See :ref:`MyProject_ini` for more information about project Paste
   ``.ini`` files.

#.  Add a ``get_session`` API to your application.  I've chosen to add
    it directly to my ``views.py`` file, although it can live anywhere.

    .. code-block:: python
       :linenos:

       from repoze.session.manager import SessionDataManager
       from repoze.bfg.traversal import find_root

       def get_session(context, request):
           root = find_root(context)
           if not hasattr(root, '_sessions'):
               root._sessions = SessionDataManager(3600, 5)
           session = root._sessions.get(request.environ['repoze.browserid'])
           return session

    Note in the call to ``SessionDataManager`` that '3600' represents
    the disuse timeout (60 minutes == 3600 seconds), and '5' represents
    a write granularity time (the session will be marked as active at
    most every five seconds).  Vary these values as necessary.

#.  Whenever you want to use a session in your application, call this API:

    .. code-block:: python
       :linenos:

       from repoze.session.manager import SessionDataManager
       from repoze.bfg.traversal import find_root
       from repoze.bfg.chameleon_zpt import render_template_to_response

       def my_view(context, request):
           session = get_session(context, request)
           session['abc'] = '123'
           return render_template_to_response('templates/mytemplate.pt',
                                              request = request,
                                              project = 'sess')

       def get_session(context, request):
           root = find_root(context)
           if not hasattr(root, '_sessions'):
               root._sessions = SessionDataManager(3600, 5)
           session = root._sessions.get(request.environ['repoze.browserid'])
           return session

For more information, see the `repoze.session documentation
<http://docs.repoze.org/session/>`_ and the `repoze.browserid
documentation <http://pypi.python.org/pypi/repoze.browserid>`_.
