=================
Tutorial Approach
=================

In summary:

- Tutorial broken into topics with quick working examples

- Each step is a Python *package* with working code in the repo

- Setup each step with ``python setup.py develop``

This "Getting Started" tutorial is broken into independent steps,
starting with the smallest possible "single file WSGI app" example.
Each of these steps introduce a topic and a very small set of concepts
via working code. The steps each correspond to a directory in this
repo, where each step/topic/directory is a Python package.

To successfully run each step::

  $ cd request_response
  $ python setup.py develop

...and repeat for each step you would like to work on. In most cases we
will start with the results of an earlier step.

Directory Tree
==============

As we develop our tutorial our directory tree will resemble the
structure below::

  request_response/
    development.ini
    setup.py
    tutorial/
      __init__.py
      home.pt
      tests.py
      views.py

Each of the first-level directories are a *Python project*
(except, as noted, the first.) The ``tutorial`` directory is a *Python
package*. At the end of each step, we copy the old directory into a new
directory to use as a starting point.