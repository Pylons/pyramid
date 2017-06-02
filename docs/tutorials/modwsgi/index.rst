.. _modwsgi_tutorial:

Running a :app:`Pyramid` Application under ``mod_wsgi``
=======================================================

:term:`mod_wsgi` is an Apache module developed by Graham Dumpleton.
It allows :term:`WSGI` programs to be served using the Apache web
server.

This guide will outline broad steps that can be used to get a :app:`Pyramid`
application running under Apache via ``mod_wsgi``.  This particular tutorial
was developed under Apple's Mac OS X platform (Snow Leopard, on a 32-bit
Mac), but the instructions should be largely the same for all systems, delta
specific path information for commands and files.

.. note:: Unfortunately these instructions almost certainly won't work for
   deploying a :app:`Pyramid` application on a Windows system using
   ``mod_wsgi``.  If you have experience with :app:`Pyramid` and ``mod_wsgi``
   on Windows systems, please help us document this experience by submitting
   documentation to the `Pylons-devel maillist
   <https://groups.google.com/forum/#!forum/pylons-devel>`_.

#.  The tutorial assumes you have Apache already installed on your
    system.  If you do not, install Apache 2.X for your platform in
    whatever manner makes sense.

#.  It is also assumed that you have satisfied the
    :ref:`requirements-for-installing-packages`.

#.  Once you have Apache installed, install ``mod_wsgi``.  Use the
    (excellent) `installation instructions
    <https://code.google.com/archive/p/modwsgi/wikis/InstallationInstructions.wiki>`_
    for your platform into your system's Apache installation.

#.  Create a :app:`Pyramid` application. For this tutorial we'll use the
    ``starter`` :term:`cookiecutter`. See :ref:`project_narr` for more
    in-depth information about creating a new project.

    .. code-block:: bash

       $ cd ~
       $ cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout 1.9-branch

    If prompted for the first item, accept the default ``yes`` by hitting return.

    .. code-block:: text

        You've cloned ~/.cookiecutters/pyramid-cookiecutter-starter before.
        Is it okay to delete and re-clone it? [yes]: yes
        project_name [Pyramid Scaffold]: myproject
        repo_name [myproject]: myproject
        Select template_language:
        1 - jinja2
        2 - chameleon
        3 - mako
        Choose from 1, 2, 3 [1]: 1

#.  Create a :term:`virtual environment` which we'll use to install our
    application. It is important to use the same base Python interpreter
    that was used to build ``mod_wsgi``. For example, if ``mod_wsgi`` was
    built against the system Python 3.x, then your project should use a
    virtual environment created from that same system Python 3.x.

    .. code-block:: bash

       $ cd myproject
       $ python3 -m venv env

#.  Install your :app:`Pyramid` application and its dependencies.

    .. code-block:: bash

       $ env/bin/pip install -e .

#.  Within the project directory (``~/myproject``), create a script
    named ``pyramid.wsgi``.  Give it these contents:

    .. code-block:: python

       from pyramid.paster import get_app, setup_logging
       ini_path = '/Users/chrism/myproject/production.ini'
       setup_logging(ini_path)
       application = get_app(ini_path, 'main')

    The first argument to :func:`pyramid.paster.get_app` is the project
    configuration file name.  It's best to use the ``production.ini`` file
    provided by your cookiecutter, as it contains settings appropriate for
    production.  The second is the name of the section within the ``.ini``
    file that should be loaded by ``mod_wsgi``.  The assignment to the name
    ``application`` is important: mod_wsgi requires finding such an
    assignment when it opens the file.

    The call to :func:`pyramid.paster.setup_logging` initializes the standard
    library's `logging` module to allow logging within your application.
    See :ref:`logging_config`.

    There is no need to make the ``pyramid.wsgi`` script executable.
    However, you'll need to make sure that *two* users have access to change
    into the ``~/myproject`` directory: your current user (mine is
    ``chrism`` and the user that Apache will run as often named ``apache`` or
    ``httpd``).  Make sure both of these users can "cd" into that directory.

#.  Edit your Apache configuration and add some stuff.  I happened to
    create a file named ``/etc/apache2/other/modwsgi.conf`` on my own
    system while installing Apache, so this stuff went in there.

    .. code-block:: apache

       # Use only 1 Python sub-interpreter.  Multiple sub-interpreters
       # play badly with C extensions.  See
       # http://stackoverflow.com/a/10558360/209039
       WSGIApplicationGroup %{GLOBAL}
       WSGIPassAuthorization On
       WSGIDaemonProcess pyramid user=chrism group=staff threads=4 \
          python-path=/Users/chrism/myproject/env/lib/python3.5/site-packages
       WSGIScriptAlias /myapp /Users/chrism/myproject/pyramid.wsgi

       <Directory /Users/chrism/myproject>
         WSGIProcessGroup pyramid
         Require all granted
       </Directory>
 
#.  Restart Apache

    .. code-block:: bash

       $ sudo /usr/sbin/apachectl restart

#.  Visit ``http://localhost/myapp`` in a browser.  You should see the
    sample application rendered in your browser.

:term:`mod_wsgi` has many knobs and a great variety of deployment modes. This
is just one representation of how you might use it to serve up a :app:`Pyramid`
application.  See the `mod_wsgi configuration documentation
<https://modwsgi.readthedocs.io/en/develop/configuration.html>`_
for more in-depth configuration information.
