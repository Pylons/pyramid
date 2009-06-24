.. _appengine_tutorial:

Running :mod:`repoze.bfg` on Google's App Engine
================================================

As of :mod:`repoze.bfg` version 0.8, it is possible to run a
:mod:`repoze.bfg` application on Google's `App Engine
<http://code.google.com/appengine/>`_.  Content from this tutorial was
contributed by "YoungKing", based on the `"appengine-monkey" tutorial
for Pylons <http://code.google.com/p/appengine-monkey/wiki/Pylons>`_.
This tutorial is written in terms of using the command line on a UNIX
system; it should be possible to perform similar actions on a Windows
system.

.. note:: :term:`chameleon.zpt` cannot be used on Google App Engine
   due to GAE environment limitations, so the tutorial is presented in
   terms of using :term:`Jinja2` as the templating language in the
   generated BFG application.

#. Download Google's `App Engine SDK
   <http://code.google.com/appengine/downloads.html>`_ and install it
   on your system.

#. Use Subversion to check out the source code for
   ``appengine-monkey``.

   .. code-block:: bash

      $ svn co http://appengine-monkey.googlecode.com/svn/trunk/ appengine-monkey

#. Use ``appengine_homedir`` to create a :term:`virtualenv` for your
   application.

   .. code-block:: bash
   
      $ export GAE_PATH=/usr/local/google_appengine
      $ python2.5 appengine-homedir.py --gae $GAE_PATH bfgapp

   Note that ``$GAE_PATH`` should be the path where you have unpacked
   the App Engine SDK.  (On Mac OS X at least,
   ``/usr/local/google_appengine`` is indeed where the installer puts
   it).

   This will set up an environment in ``bfgapp/``, with some tools
   installed in ``bfgapp/bin``. There will also be a directory
   ``bfgapp/app/`` which is the directory you will upload to
   appengine.

#. Install :mod:`repoze.bfg.jinja2` into the virtualenv

   .. code-block:: bash

      $ cd bfgapp/
      $ bin/easy_install -i http://dist.repoze.org/bfg/dev/simple/ repoze.bfg.jinja2

   This will install :mod:`repoze.bfg` in the environment.

#. Create your application

   We'll use the standard way to create a :mod:`repoze.bfg`
   application, but we'll have to move some files around when we are
   done:

   .. code-block:: bash

      $ cd app
      $ rm -rf bfgapp
      $ bin/paster create -t bfg_jinja2_starter bfgapp
      $ mv bfgapp aside
      $ mv aside/bfgapp .
      $ rm -rf aside

#. Edit ``config.py``

   .. code-block:: python

    APP_NAME = 'bfgapp.run:app'
    APP_ARGS = ({},)

#.  Edit ``runner.py``

    To prevent errors for ``import site``, add this code stanza before
    ``import site`` in app/runner.py:

    .. code-block:: python

       import sys
       sys.path = [path for path in sys.path if "site-packages" not in path]
       import site

    You will also need to comment the ``assert`` in the file.

#. Run the application.  ``dev_appserver.py`` is typically installed
   by the SDK in the global path but you need to be sure to run it
   with Python 2.5 (or whatever version of Python your GAE SDK
   expects).

   .. code-block:: python

      $ cd ../..
      $ python2.5 /usr/local/bin/dev_appserver.py bfgapp/app/

   Startup success looks something like this::

      [chrism@vitaminf bfg_gae]$ python2.5 /usr/local/bin/dev_appserver.py bfgapp/app/INFO     2009-05-03 22:23:13,887 appengine_rpc.py:157] Server: appengine.google.com
      INFO     2009-05-03 22:23:13,898 appcfg.py:320] Checking for updates to the SDK.
      INFO     2009-05-03 22:23:14,034 appcfg.py:334] The SDK is up to date.
      WARNING  2009-05-03 22:23:14,035 datastore_file_stub.py:368] Could not read datastore data from /var/folders/dB/dByJ-qkiE6igZD4Yrm+nMk+++TI/-Tmp-/dev_appserver.datastore
      WARNING  2009-05-03 22:23:14,035 datastore_file_stub.py:368] Could not read datastore data from /var/folders/dB/dByJ-qkiE6igZD4Yrm+nMk+++TI/-Tmp-/dev_appserver.datastore.history
      WARNING  2009-05-03 22:23:14,045 dev_appserver.py:3240] Could not initialize images API; you are likely missing the Python "PIL" module. ImportError: No module named _imaging
      INFO     2009-05-03 22:23:14,050 dev_appserver_main.py:463] Running application bfgapp on port 8080: http://localhost:8080

#. Hack on your bfg application, using a normal run, debug, restart
   process.

#. `Sign up for a GAE account <http://code.google.com/appengine/>`_
   and create an application.  You'll need a mobile phone to accept an
   SMS in order to receive authorization.

#. Edit the application's ID in ``app.yaml`` to match the application
   name you created during GAE account setup.

   .. code-block:: python

      application: mycoolbfgapp

#. Upload the application

   .. code-block:: python

      $ python2.5 /usr/local/bin/appcfg.py update bfgapp/app

   You will almost certainly find that you hit the 1000-file GAE file
   limit.

   .. code-block:: python

       HTTPError: HTTP Error 400: Bad Request
       Rolling back the update.
       Error 400: --- begin server output ---
       Max number of files and blobs is 1000.
       --- end server output ---

   You will be able to get around this by zipping libraries. You can
   use ``pip`` to create zipfiles from packages.  For example:

   .. code-block:: python

     $ bin/pip zip -l

   This shows your zipped packages (by default, none) and your
   unzipped packages. You can zip a package like so:

   .. code-block:: python 

     $ bin/pip zip pytz-2009g-py2.5.egg

   Note that it requires the whole egg file name.  A the time of this
   tutorial's writing, the 1000 file limit can be subverted by causing
   the following packages to be zipped:

   - pytz
   - chameleon.core
   - chameleon.zpt
   - zope.i18n
   - zope.testing

   After zipping, a successful upload looks like so::

    [chrism@vitaminf bfgapp]$ python2.5 /usr/local/bin/appcfg.py update ../bfgapp/app/
    Scanning files on local disk.
    Scanned 500 files.
    Scanned 1000 files.
    Initiating update.
    Cloning 761 application files.
    Cloned 100 files.
    Cloned 200 files.
    Cloned 300 files.
    Cloned 400 files.
    Cloned 500 files.
    Cloned 600 files.
    Cloned 700 files.
    Uploading 12 files.
    Deploying new version.
    Checking if new version is ready to serve.
    Will check again in 1 seconds.
    Checking if new version is ready to serve.
    Will check again in 2 seconds.
    Checking if new version is ready to serve.
    Will check again in 4 seconds.
    Checking if new version is ready to serve.
    Will check again in 8 seconds.
    Checking if new version is ready to serve.
    Will check again in 16 seconds.
    Checking if new version is ready to serve.
    Closing update: new version is ready to start serving.
    Uploading index definitions.

#. Visit "<yourapp>.appspot.com" in a browser.





