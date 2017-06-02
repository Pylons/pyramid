.. _qtut_cookiecutters:

=================================================
Prelude: Quick Project Startup with Cookiecutters
=================================================

To ease the process of getting started on a project, the Pylons Project provides :term:`cookiecutter`\ s that generate sample :app:`Pyramid` projects from project templates. These cookiecutters will install :app:`Pyramid` and its dependencies as well. We will still cover many topics of web application development using :app:`Pyramid`, but it's good to know of this facility. This prelude will demonstrate how to get a working :app:`Pyramid` web application running via ``cookiecutter``.


Objectives
==========

- Use a cookiecutter to make a new project.

- Start up a :app:`Pyramid` application and visit it in a web browser.


Steps
=====

#.  Install cookiecutter into your virtual environment.

    .. code-block:: bash

        $VENV/bin/pip install cookiecutter

#.  Let's use the cookiecutter ``pyramid-cookiecutter-starter`` to create a starter :app:`Pyramid` project in the current directory, entering values at the prompts as shown below for the following command.

    .. code-block:: bash

        $ $VENV/bin/cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout 1.9-branch

    If prompted for the first item, accept the default ``yes`` by hitting return.

    .. code-block:: text

        You've cloned ~/.cookiecutters/pyramid-cookiecutter-starter before.
        Is it okay to delete and re-clone it? [yes]: yes
        project_name [Pyramid Scaffold]: cc_starter
        repo_name [cc_starter]: cc_starter
        Select template_language:
        1 - jinja2
        2 - chameleon
        3 - mako
        Choose from 1, 2, 3 [1]: 1

#.  We then run through the following commands.

    .. code-block:: bash

        # Change directory into your newly created project.
        $ cd cc_starter
        # Create a new virtual environment...
        $ python3 -m venv env
        # ...where we upgrade packaging tools...
        $ env/bin/pip install --upgrade pip setuptools
        # ...and into which we install our project.
        $ env/bin/pip install -e .

#.  Start up the application by pointing :app:`Pyramid`'s ``pserve`` command at the
    project's (generated) configuration file:

    .. code-block:: bash

        $ env/bin/pserve development.ini --reload

    On start up, ``pserve`` logs some output:

    .. code-block:: text

        Starting subprocess with file monitor
        Starting server in PID 73732.
        Serving on http://localhost:6543
        Serving on http://localhost:6543

#. Open http://localhost:6543/ in your browser.

Analysis
========

Rather than starting from scratch, a cookiecutter can make it easy to get a Python
project containing a working :app:`Pyramid` application. The Pylons Project provides `several cookiecutters <https://github.com/Pylons?q=pyramid-cookiecutter>`_.

``pserve`` is :app:`Pyramid`'s application runner, separating operational details from
your code. When you install :app:`Pyramid`, a small command program called ``pserve``
is written to your ``bin`` directory. This program is an executable Python
module. It is passed a configuration file (in this case, ``development.ini``).
