.. _qtut_scaffolds:

=============================================
Prelude: Quick Project Startup with Scaffolds
=============================================

To ease the process of getting started, Pyramid provides *scaffolds* that
generate sample projects from templates in Pyramid and Pyramid add-ons.


Background
==========

We're going to cover a lot in this tutorial, focusing on one topic at a time
and writing everything from scratch. As a warm up, though, it sure would be
nice to see some pixels on a screen.

Like other web development frameworks, Pyramid provides a number of "scaffolds"
that generate working Python, template, and CSS code for sample applications.
In this step we'll use a built-in scaffold to let us preview a Pyramid
application, before starting from scratch on Step 1.


Objectives
==========

- Use Pyramid's ``pcreate`` command to list scaffolds and make a new project.

- Start up a Pyramid application and visit it in a web browser.


Steps
=====

#. Pyramid's ``pcreate`` command can list the available scaffolds:

    .. code-block:: bash

        $ $VENV/bin/pcreate --list
        Available scaffolds:
          alchemy:                 Pyramid SQLAlchemy project using url dispatch
          starter:                 Pyramid starter project
          zodb:                    Pyramid ZODB project using traversal

#. Tell ``pcreate`` to use the ``starter`` scaffold to make our project:

    .. code-block:: bash

        $ $VENV/bin/pcreate --scaffold starter scaffolds

#. Install our project in editable mode for development in the current
   directory:

    .. code-block:: bash

        $ cd scaffolds
        $ $VENV/bin/pip install -e .

#. Start up the application by pointing Pyramid's ``pserve`` command at the
   project's (generated) configuration file:

    .. code-block:: bash

        $ $VENV/bin/pserve development.ini --reload

   On start up, ``pserve`` logs some output:

    .. code-block:: bash

        Starting subprocess with file monitor
        Starting server in PID 72213.
        Starting HTTP server on http://0.0.0.0:6543

#. Open http://localhost:6543/ in your browser.

Analysis
========

Rather than starting from scratch, ``pcreate`` can make getting a Python
project containing a Pyramid application a quick matter. Pyramid ships with a
few scaffolds. But installing a Pyramid add-on can give you new scaffolds from
that add-on.

``pserve`` is Pyramid's application runner, separating operational details from
your code. When you install Pyramid, a small command program called ``pserve``
is written to your ``bin`` directory. This program is an executable Python
module. It is passed a configuration file (in this case, ``development.ini``).
