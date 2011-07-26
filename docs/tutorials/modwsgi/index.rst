.. _modwsgi_tutorial:

Running a :app:`Pyramid` Application under ``mod_wsgi``
==========================================================

:term:`mod_wsgi` is an Apache module developed by Graham Dumpleton.
It allows :term:`WSGI` programs to be served using the Apache web
server.

This guide will outline broad steps that can be used to get a
:app:`Pyramid` application running under Apache via ``mod_wsgi``.
This particular tutorial was developed under Apple's Mac OS X platform
(Snow Leopard, on a 32-bit Mac), but the instructions should be
largely the same for all systems, delta specific path information for
commands and files.

.. note:: Unfortunately these instructions almost certainly won't work for
   deploying a :app:`Pyramid` application on a Windows system using
   ``mod_wsgi``.  If you have experience with :app:`Pyramid` and ``mod_wsgi``
   on Windows systems, please help us document this experience by submitting
   documentation to the `Pylons-devel maillist
   <http://groups.google.com/group/pylons-devel>`_.

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

#.  Install :app:`Pyramid` into the newly created virtualenv:

    .. code-block:: text

       $ cd ~/modwsgi/env
       $ bin/easy_install pyramid
    
#.  Create and install your :app:`Pyramid` application.  For the purposes of
    this tutorial, we'll just be using the ``pyramid_starter`` application as
    a baseline application.  Substitute your existing :app:`Pyramid`
    application as necessary if you already have one.

    .. code-block:: text

       $ cd ~/modwsgi/env
       $ bin/paster create -t pyramid_starter myapp
       $ cd myapp
       $ ../bin/python setup.py install

#.  Within the virtualenv directory (``~/modwsgi/env``), create a
    script named ``pyramid.wsgi``.  Give it these contents:

    .. code-block:: python

       from pyramid.paster import get_app
       application = get_app(
         '/Users/chrism/modwsgi/env/myapp/production.ini', 'main')

    The first argument to ``get_app`` is the project Paste configuration file
    name.  It's best to use the ``production.ini`` file provided by your
    scaffold, as it contains settings appropriate for
    production.  The second is the name of the section within the .ini file
    that should be loaded by ``mod_wsgi``.  The assignment to the name
    ``application`` is important: mod_wsgi requires finding such an
    assignment when it opens the file.

#.  Make the ``pyramid.wsgi`` script executable.

    .. code-block:: text

       $ cd ~/modwsgi/env
       $ chmod 755 pyramid.wsgi

#.  Edit your Apache configuration and add some stuff.  I happened to
    create a file named ``/etc/apache2/other/modwsgi.conf`` on my own
    system while installing Apache, so this stuff went in there.

    .. code-block:: apache

       # Use only 1 Python sub-interpreter.  Multiple sub-interpreters
       # play badly with C extensions.
       WSGIApplicationGroup %{GLOBAL}
       WSGIPassAuthorization On
       WSGIDaemonProcess pyramid user=chrism group=staff threads=4 \
          python-path=/Users/chrism/modwsgi/env/lib/python2.6/site-packages
       WSGIScriptAlias /myapp /Users/chrism/modwsgi/env/pyramid.wsgi

       <Directory /Users/chrism/modwsgi/env>
         WSGIProcessGroup pyramid
         Order allow,deny
         Allow from all
       </Directory>
 
#.  Restart Apache

    .. code-block:: text

       $ sudo /usr/sbin/apachectl restart

#.  Visit ``http://localhost/myapp`` in a browser.  You should see the
    sample application rendered in your browser.

:term:`mod_wsgi` has many knobs and a great variety of deployment
modes.  This is just one representation of how you might use it to
serve up a :app:`Pyramid` application.  See the `mod_wsgi
configuration documentation
<http://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines>`_ for
more in-depth configuration information.

