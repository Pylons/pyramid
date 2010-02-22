.. _modwsgi_tutorial:

Running a :mod:`repoze.bfg` Application under ``mod_wsgi``
==========================================================

:term:`mod_wsgi` is an Apache module developed by Graham Dumpleton.
It allows :term:`WSGI` programs to be served using the Apache web
server.

This guide will outline broad steps that can be used to get a
:mod:`repoze.bfg` application running under Apache via ``mod_wsgi``.
This particular tutorial was developed under Apple's Mac OS X platform
(Snow Leopard, on a 32-bit Mac), but the instructions should be
largely the same for all systems, delta specific path information for
commands and files.

.. note:: Unfortunately these instructions almost certainly won't work
   for deploying a :mod:`repoze.bfg` application on a Windows system
   using ``mod_wsgi``.  If you have experience with :mod:`repoze.bfg`
   and ``mod_wsgi`` on Windows systems, please help us document
   this experience by submitting documentation to the `mailing list
   <http://lists.repoze.org/listinfo/repoze-dev>`_.

#.  The tutorial assumes you have Apache already installed on your
    system.  If you do not, install Apache 2.X for your platform in
    whatever manner makes sense.

#.  Once you have Apache installed, install ``mod_wsgi``.  Use the
    (excellent) `installation instructions
    <http://code.google.com/p/modwsgi/wiki/InstallationInstructions>`_
    for your platform into your system's Apache installation.

#.  Install :term:`virtualenv` into the Python which mod_wsgi will
    run using the ``easy_install`` program.

    .. code-block:: text

       $ sudo /usr/bin/easy_install-2.6 virtualenv

    This command may need to be performed as the root user.

#.  Create a :term:`virtualenv` which we'll use to install our
    application.

    .. code-block:: text

       $ cd ~
       $ mkdir modwsgi
       $ cd modwsgi
       $ /usr/local/bin/virtualenv --no-site-packages env

#.  Install :mod:`repoze.bfg` into the newly created virtualenv:

    .. code-block:: text

       $ cd ~/modwsgi/env
       $ bin/easy_install -i http://dist.repoze.org/bfg/current/simple \
            repoze.bfg
    
#.  Create and install your :mod:`repoze.bfg` application.  For the
    purposes of this tutorial, we'll just be using the ``bfg_starter``
    application as a baseline application.  Substitute your existing
    :mod:`repoze.bfg` application as necessary if you already have
    one.

    .. code-block:: text

       $ cd ~/modwsgi/env
       $ bin/paster create -t bfg_starter myapp
       $ cd myapp
       $ ../bin/python setup.py install

#.  Within the virtualenv directory (``~/modwsgi/env``), create a
    script named ``bfg.wsgi``.  Give it these contents:

    .. code-block:: python

       from repoze.bfg.paster import get_app
       application = get_app(
         '/Users/chrism/modwsgi/env/myapp/myapp.ini', 'main')

    The first argument to ``get_app`` is the project Paste
    configuration file name.  The second is the name of the section
    within the .ini file that should be loaded by ``mod_wsgi``.  The
    assignment to the name ``application`` is important: mod_wsgi
    requires finding such an assignment when it opens the file.

#.  Make the ``bfg.wsgi`` script executable.

    .. code-block:: text

       $ cd ~/modwsgi/env
       $ chmod 755 bfg.wsgi

#.  Edit your Apache configuration and add some stuff.  I happened to
    create a file named ``/etc/apache2/other/modwsgi.conf`` on my own
    system while installing Apache, so this stuff went in there.

    .. code-block:: apache

       # Use only 1 Python sub-interpreter.  Multiple sub-interpreters
       # play badly with C extensions.
       WSGIApplicationGroup %{GLOBAL}
       WSGIPassAuthorization On
       WSGIDaemonProcess bfg user=chrism group=staff processes=1 threads=4 \
          python-path=/Users/chrism/modwsgi/env/lib/python2.6/site-packages
       WSGIScriptAlias /myapp /Users/chrism/modwsgi/env/bfg.wsgi

       <Directory /Users/chrism/modwsgi/env>
         WSGIProcessGroup bfg
         Order allow, deny
         Allow from all
       </Directory>
 
#.  Restart Apache

    .. code-block:: text

       $ sudo /usr/sbin/apachectl restart

#.  Visit ``http://localhost/myapp`` in a browser.  You should see the
    sample application rendered in your browser.

:term:`mod_wsgi` has many knobs and a great variety of deployment
modes.  This is just one representation of how you might use it to
serve up a :mod:`repoze.bfg` application.  See the `mod_wsgi
configuration documentation
<http://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines>`_ for
more in-depth configuration information.

