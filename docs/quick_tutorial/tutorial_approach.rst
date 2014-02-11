=================
Tutorial Approach
=================

This tutorial uses conventions to keep the introduction focused and
concise. Details, references, and deeper discussions are mentioned in
"See also" notes.

.. seealso:: This is an example "See also" note.

This "Getting Started" tutorial is broken into independent steps,
starting with the smallest possible "single file WSGI app" example.
Each of these steps introduce a topic and a very small set of concepts
via working code. The steps each correspond to a directory in this
repo, where each step/topic/directory is a Python package.

To successfully run each step::

  $ cd request_response
  $ $VENV/bin/python setup.py develop

...and repeat for each step you would like to work on. In most cases we
will start with the results of an earlier step.

Directory Tree
==============

As we develop our tutorial our directory tree will resemble the
structure below::

  quicktutorial/
    request_response/
      development.ini
      setup.py
      tutorial/
        __init__.py
        home.pt
        tests.py
        views.py

Each of the first-level directories (e.g. ``request_response``) is a
*Python project* (except, as noted, the ``hello_world`` step.) The
``tutorial`` directory is a *Python package*. At the end of each step,
we copy a previous directory into a new directory to use as a starting
point.
