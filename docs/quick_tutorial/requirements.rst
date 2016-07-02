.. _qtut_requirements:

============
Requirements
============

Let's get our tutorial environment set up. Most of the set up work is in
standard Python development practices (install Python and make an isolated
virtual environment.)

.. note::

  Pyramid encourages standard Python development practices with packaging
  tools, virtual environments, logging, and so on. There are many variations,
  implementations, and opinions across the Python community.  For consistency,
  ease of documentation maintenance, and to minimize confusion, the Pyramid
  *documentation* has adopted specific conventions that are consistent with the
  :term:`Python Packaging Authority`.

This *Quick Tutorial* is based on:

* **Python 3.3**. Pyramid fully supports Python 3.2+ and Python 2.6+.
  This tutorial uses **Python 3.3** but runs fine under Python 2.7.

* **pyvenv**. We believe in virtual environments. For this tutorial,
  we use Python 3.3's built-in solution, the ``pyvenv`` command.
  For Python 2.7, you can install ``virtualenv``.

* **setuptools and easy_install**. We use `setuptools
  <https://pypi.python.org/pypi/setuptools/>`_ and its ``easy_install`` for
  package management.

* **Workspaces, projects, and packages.** Our home directory will contain a
  *tutorial workspace* with our Python virtual environment and *Python
  projects* (a directory with packaging information and *Python packages* of
  working code.)

* **Unix commands**. Commands in this tutorial use UNIX syntax and paths.
  Windows users should adjust commands accordingly.

.. note::
    Pyramid was one of the first web frameworks to fully support Python 3 in
    October 2011.

.. note::
    Windows commands use the plain old MSDOS shell. For PowerShell command
    syntax, see its documentation.

Steps
=====

#. :ref:`install-python-3.3-or-greater`
#. :ref:`create-a-project-directory-structure`
#. :ref:`set-an-environment-variable`
#. :ref:`create-a-virtual-environment`
#. :ref:`install-setuptools-(python-packaging-tools)`
#. :ref:`install-pyramid`

.. _install-python-3.3-or-greater:

Install Python 3.3 or greater
-----------------------------

Download the latest standard Python 3.3+ release (not development release)
from `python.org <https://www.python.org/downloads/>`_.

Windows and Mac OS X users can download and run an installer.

Windows users should also install the `Python for Windows extensions
<http://sourceforge.net/projects/pywin32/files/pywin32/>`_. Carefully read the
``README.txt`` file at the end of the list of builds, and follow its
directions. Make sure you get the proper 32- or 64-bit build and Python
version.

Linux users can either use their package manager to install Python 3.3
or may `build Python 3.3 from source
<http://pyramid.readthedocs.org/en/master/narr/install.html#package-manager-
method>`_.


.. _create-a-project-directory-structure:

Create a project directory structure
------------------------------------

We will arrive at a directory structure of ``workspace -> project -> package``,
where our workspace is named ``quick_tutorial``. The following tree diagram
shows how this will be structured, and where our :term:`virtual environment`
will reside as we proceed through the tutorial:

.. code-block:: text

    `── ~
        `── projects
            `── quick_tutorial
                │── env
                `── step_one
                    │── intro
                    │   │── __init__.py
                    │   `── app.py
                    `── setup.py

For Linux, the commands to do so are as follows:

.. code-block:: bash

    # Mac and Linux
    $ cd ~
    $ mkdir -p projects/quick_tutorial
    $ cd projects/quick_tutorial

For Windows:

.. code-block:: doscon

    # Windows
    c:\> cd \
    c:\> mkdir projects\quick_tutorial
    c:\> cd projects\quick_tutorial

In the above figure, your user home directory is represented by ``~``. In your
home directory, all of your projects are in the ``projects`` directory. This is
a general convention not specific to Pyramid that many developers use. Windows
users will do well to use ``c:\`` as the location for ``projects`` in order to
avoid spaces in any of the path names.

Next within ``projects`` is your workspace directory, here named
``quick_tutorial``. A workspace is a common term used by integrated
development environments (IDE), like PyCharm and PyDev, where virtual
environments, specific project files, and repositories are stored.


.. _set-an-environment-variable:

Set an environment variable
---------------------------

This tutorial will refer frequently to the location of the :term:`virtual
environment`. We set an environment variable to save typing later.

.. code-block:: bash

    # Mac and Linux
    $ export VENV=~/projects/quick_tutorial/env

.. code-block:: doscon

    # Windows
    c:\> set VENV=c:\projects\quick_tutorial\env


.. _create-a-virtual-environment:

Create a virtual environment
----------------------------

.. warning:: The current state of isolated Python environments using
    ``pyvenv`` on Windows is suboptimal in comparison to Mac and Linux.  See
    http://stackoverflow.com/q/15981111/95735 for a discussion of the issue
    and `PEP 453 <http://www.python.org/dev/peps/pep-0453/>`_ for a proposed
    resolution.

``pyvenv`` is a tool to create isolated Python 3.3 environments, each
with its own Python binary and independent set of installed Python
packages in its site directories. Let's create one, using the location
we just specified in the environment variable.

.. code-block:: bash

    # Mac and Linux
    $ pyvenv $VENV

.. code-block:: doscon

    # Windows
    c:\> c:\Python33\python -m venv %VENV%

.. seealso:: See also Python 3's :mod:`venv module <python3:venv>`,
   Python 2's `virtualenv <http://www.virtualenv.org/en/latest/>`_
   package,
   :ref:`Installing Pyramid on a Windows System <installing_windows>`


.. _install-setuptools-(python-packaging-tools):

Install ``setuptools`` (Python packaging tools)
-----------------------------------------------

The following command will download a script to install ``setuptools``, then
pipe it to your environment's version of Python.

.. code-block:: bash

    # Mac and Linux
    $ wget https://bootstrap.pypa.io/ez_setup.py -O - | $VENV/bin/python

.. code-block:: doscon

    # Windows
    #
    # Use your web browser to download this file:
    #   https://bootstrap.pypa.io/ez_setup.py
    #
    # ...and save it to:
    # c:\projects\quick_tutorial\ez_setup.py
    #
    # Then run the following command:

    c:\> %VENV%\Scripts\python ez_setup.py

If ``wget`` complains with a certificate error, then run this command instead:

.. code-block:: bash

    # Mac and Linux
    $ wget --no-check-certificate https://bootstrap.pypa.io/ez_setup.py -O - | $VENV/bin/python


.. _install-pyramid:

Install Pyramid
---------------

We have our Python standard prerequisites out of the way. The Pyramid
part is pretty easy.

.. parsed-literal::

    # Mac and Linux
    $ $VENV/bin/easy_install "pyramid==\ |release|\ "

    # Windows
    c:\\> %VENV%\\Scripts\\easy_install "pyramid==\ |release|\ "

Our Python virtual environment now has the Pyramid software available.

You can optionally install some of the extra Python packages used in this
tutorial.

.. code-block:: bash

    # Mac and Linux
    $ $VENV/bin/easy_install nose webtest deform sqlalchemy \
       pyramid_chameleon pyramid_debugtoolbar waitress \
       pyramid_tm zope.sqlalchemy

.. code-block:: doscon

    # Windows
    c:\> %VENV%\Scripts\easy_install nose webtest deform sqlalchemy pyramid_chameleon pyramid_debugtoolbar waitress pyramid_tm zope.sqlalchemy


.. note::

    Why ``easy_install`` and not ``pip``? Pyramid encourages use of namespace
    packages, for which ``pip``'s support is less-than-optimal. Also, Pyramid's
    dependencies use some optional C extensions for performance:   with
    ``easy_install``, Windows users can get these extensions without needing
    a C compiler (``pip`` does not support installing binary Windows
    distributions, except for ``wheels``, which are not yet available for
    all dependencies).

.. seealso:: See also :ref:`installing_unix`. For instructions to set up your
    Python environment for development using Windows or Python 2, see Pyramid's
    :ref:`Before You Install <installing_chapter>`.

    See also Python 3's :mod:`venv module <python3:venv>`, the `setuptools
    installation instructions
    <https://pypi.python.org/pypi/setuptools/0.9.8#installation-instructions>`_,
    and `easy_install help <https://pypi.python.org/pypi/setuptools/0.9.8#using-setuptools-and-easyinstall>`_.

