.. _appengine_tutorial:

Running :app:`Pyramid` on Google's App Engine
================================================

It is possible to run a :app:`Pyramid` application on Google's `App
Engine <http://code.google.com/appengine/>`_.  Content from this
tutorial was contributed by YoungKing, based on the
`"appengine-monkey" tutorial for Pylons
<http://code.google.com/p/appengine-monkey/wiki/Pylons>`_.  This
tutorial is written in terms of using the command line on a UNIX
system; it should be possible to perform similar actions on a Windows
system.

#. Download Google's `App Engine SDK
   <http://code.google.com/appengine/downloads.html>`_ and install it
   on your system.

#. Use Subversion to check out the source code for
   ``appengine-monkey``.

   .. code-block:: text

      $ svn co http://appengine-monkey.googlecode.com/svn/trunk/ \
          appengine-monkey

#. Use ``appengine_homedir.py`` script in ``appengine-monkey`` to
   create a :term:`virtualenv` for your application.

   .. code-block:: text
 
      $ export GAE_PATH=/usr/local/google_appengine
      $ python2.5 /path/to/appengine-monkey/appengine-homedir.py --gae \
        $GAE_PATH pyramidapp

   Note that ``$GAE_PATH`` should be the path where you have unpacked
   the App Engine SDK.  (On Mac OS X at least,
   ``/usr/local/google_appengine`` is indeed where the installer puts
   it).

   This will set up an environment in ``pyramidapp/``, with some tools
   installed in ``pyramidapp/bin``. There will also be a directory
   ``pyramidapp/app/`` which is the directory you will upload to
   appengine.

#. Install :app:`Pyramid` into the virtualenv

   .. code-block:: text

      $ cd pyramidapp/
      $ bin/easy_install pyramid

   This will install :app:`Pyramid` in the environment.

#. Create your application

   We'll use the standard way to create a :app:`Pyramid`
   application, but we'll have to move some files around when we are
   done.  The below commands assume your current working directory is
   the ``pyramidapp`` virtualenv directory you created in the third step
   above:

   .. code-block:: text

      $ cd app
      $ rm -rf pyramidapp
      $ bin/paster create -t pyramid_starter pyramidapp
      $ mv pyramidapp aside
      $ mv aside/pyramidapp .
      $ rm -rf aside

#. Edit ``config.py``

   Edit the ``APP_NAME`` and ``APP_ARGS`` settings within
   ``config.py``.  The ``APP_NAME`` must be ``pyramidapp:main``, and
   the APP_ARGS must be ``({},)``.  Any other settings in
   ``config.py`` should remain the same.

   .. code-block:: python

      APP_NAME = 'pyramidapp:main'
      APP_ARGS = ({},)

#. Edit ``runner.py``

   To prevent errors for ``import site``, add this code stanza before
   ``import site`` in app/runner.py:

   .. code-block:: python

      import sys
      sys.path = [path for path in sys.path if 'site-packages' not in path]
      import site

   You will also need to comment out the line that starts with
   ``assert sys.path`` in the file.

   .. code-block:: python

      # comment the sys.path assertion out
      # assert sys.path[:len(cur_sys_path)] == cur_sys_path, (
      #   "addsitedir() caused entries to be prepended to sys.path")

   For GAE development environment 1.3.0 or better, you will also need
   the following somewhere near the top of the ``runner.py`` file to
   fix a compatibility issue with ``appengine-monkey``:

   .. code-block:: python

      import os
      os.mkdir = None

#. Run the application.  ``dev_appserver.py`` is typically installed
   by the SDK in the global path but you need to be sure to run it
   with Python 2.5 (or whatever version of Python your GAE SDK
   expects).

   .. code-block:: text
      :linenos:

      $ cd ../..
      $ python2.5 /usr/local/bin/dev_appserver.py pyramidapp/app/

   Startup success looks something like this:

   .. code-block:: text

      [chrism@vitaminf pyramid_gae]$ python2.5 \
                    /usr/local/bin/dev_appserver.py \
                    pyramidapp/app/
      INFO     2009-05-03 22:23:13,887 appengine_rpc.py:157] # ... more... 
      Running application pyramidapp on port 8080: http://localhost:8080

   You may need to run "Make Symlinks" from the Google App Engine
   Launcher GUI application if your system doesn't already have the
   ``dev_appserver.py`` script sitting around somewhere.

#. Hack on your pyramid application, using a normal run, debug, restart
   process.  For tips on how to use the ``pdb`` module within Google
   App Engine, `see this blog post
   <http://jjinux.blogspot.com/2008/05/python-debugging-google-app-engine-apps.html>`_.
   In particular, you can create a function like so and call it to
   drop your console into a pdb trace:

   .. code-block:: python
      :linenos:

      def set_trace():
          import pdb, sys
          debugger = pdb.Pdb(stdin=sys.__stdin__, 
              stdout=sys.__stdout__)
          debugger.set_trace(sys._getframe().f_back)

#. `Sign up for a GAE account <http://code.google.com/appengine/>`_
   and create an application.  You'll need a mobile phone to accept an
   SMS in order to receive authorization.

#. Edit the application's ID in ``app.yaml`` to match the application
   name you created during GAE account setup.

   .. code-block:: yaml

      application: mycoolpyramidapp

#. Upload the application

   .. code-block:: text

      $ python2.5 /usr/local/bin/appcfg.py update pyramidapp/app

   You almost certainly won't hit the 3000-file GAE file number limit
   when invoking this command.  If you do, however, it will look like
   so:

   .. code-block:: text

       HTTPError: HTTP Error 400: Bad Request
       Rolling back the update.
       Error 400: --- begin server output ---
       Max number of files and blobs is 3000.
       --- end server output ---

   If you do experience this error, you will be able to get around
   this by zipping libraries. You can use ``pip`` to create zipfiles
   from packages.  See :ref:`pip_zip` for more information about this.

   A successful upload looks like so:

   .. code-block:: text

      [chrism@vitaminf pyramidapp]$ python2.5 /usr/local/bin/appcfg.py \
                                    update ../pyramidapp/app/
      Scanning files on local disk.
      Scanned 500 files.
      # ... more output ...
      Will check again in 16 seconds.
      Checking if new version is ready to serve.
      Closing update: new version is ready to start serving.
      Uploading index definitions.

#. Visit ``http://<yourapp>.appspot.com`` in a browser.

.. _pip_zip:

Zipping Files Via Pip
---------------------

If you hit the Google App Engine 3000-file limit, you may need to
create zipfile archives out of some distributions installed in your
application's virtualenv.

First, see which packages are available for zipping:

.. code-block:: text

   $ bin/pip zip -l

This shows your zipped packages (by default, none) and your unzipped
packages. You can zip a package like so:

.. code-block:: text

   $ bin/pip zip pytz-2009g-py2.5.egg

Note that it requires the whole egg file name.  For a :app:`Pyramid` app, the
following packages are good candidates to be zipped.

- Chameleon
- zope.i18n

Once the zipping procedure is finished you can try uploading again.
