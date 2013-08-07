====================================
Starting New Projects With Scaffolds
====================================

So far we have done all of our *Quick Glance* as a single Python file.
No Python packages, no structure. Most Pyramid projects, though,
aren't developed this way.

To ease the process of getting started, Pyramid provides *scaffolds*
that generate sample projects. You run a command, perhaps answer some
questions, and a sample project is generated for you. Not just Pyramid
itself: add-ons such as ``pyramid_jinja2`` (or your own projects) can
register their own scaffolds.



Pyramid projects are organized using normal Python facilities for
projects. Normal, though, is in the eye of the beholder. This chapter
shows how to use scaffolds to automate the boilerplate and quickly
start development of a new project.

Topics: scaffolds, packaging, virtual environments

Pyramid's ``pcreate`` command is used to generate a starting point
from a scaffold. What does this command look like?

.. code-block:: bash

    $ pcreate --help
    Usage: pcreate [options] output_directory

    Render Pyramid scaffolding to an output directory

    Options:
      -h, --help            show this help message and exit
      -s SCAFFOLD_NAME, --scaffold=SCAFFOLD_NAME
                            Add a scaffold to the create process (multiple -s args
                            accepted)
      -t SCAFFOLD_NAME, --template=SCAFFOLD_NAME
                            A backwards compatibility alias for -s/--scaffold.
                            Add a scaffold to the create process (multiple -t args
                            accepted)
      -l, --list            List all available scaffold names
      --list-templates      A backwards compatibility alias for -l/--list.  List
                            all available scaffold names.
      --simulate            Simulate but do no work
      --overwrite           Always overwrite
      --interactive         When a file would be overwritten, interrogate

Let's see what our Pyramid install supports as starting-point scaffolds:

.. code-block:: bash

    $ pcreate --list
    Available scaffolds:
      alchemy:                 Pyramid SQLAlchemy project using url dispatch
      pyramid_jinja2_starter:  pyramid jinja2 starter project
      starter:                 Pyramid starter project
      zodb:                    Pyramid ZODB project using traversal

The ``pyramid_jinja2_starter`` looks interesting. From the parent
directory of where we want our Python package to be generated,
let's use that scaffold to make our project:

.. code-block:: bash

    $ pcreate --scaffold pyramid_jinja2_starter hello_world

After printing a bunch of lines about the files being generated,
we now have a Python package. As described in the *official
instructions*, we need to install this as a development package:

.. code-block:: bash

    $ cd hello_world
    $ python ./setup.py develop

What did we get? A top-level directory ``hello_world`` that includes
some packaging files and a subdirectory ``hello_world`` that has
sample files for our application:

.. code-block:: bash

    $ ls
    CHANGES.txt		development.ini		hello_world.egg-info
    MANIFEST.in		message-extraction.ini	setup.cfg
    README.txt		hello_world		setup.py

    $ ls hello_world
    __init__.py	locale		static		tests.py
    __pycache__	models.py	templates	views.py

We are moving in the direction of a full-featured Pyramid project,
with a proper setup for Python standards (packaging) and Pyramid
configuration. This includes a new way of running your application:

.. code-block:: bash

    $ pserve development.ini

With ``pserve``, your application isn't responsible for finding a WSGI
server and launching your WSGI app. Also, much of the wiring of your
application can be moved to a declarative ``.ini`` configuration file.

In your browser, visit
`http://localhost:6543/ <http://localhost:6543/>`_ and you'll see that
things look very different. In the next few sections we'll cover some
decisions made by this scaffold.

Let's look at ``pserve`` and configuration in more depth.