.. _upgrading_chapter:

Upgrading Pyramid
=================

When a new version of Pyramid is released, it will sometimes deprecate a
feature or remove a feature that was deprecated in an older release.  When
features are removed from Pyramid, applications that depend on those features
will begin to break.  This chapter explains how to ensure your Pyramid
applications keep working when you upgrade the Pyramid version you're using.

.. sidebar::   About Release Numbering

   Conventionally, application version numbering in Python is described as
   ``major.minor.micro``.  If your Pyramid version is "1.2.3", it means you're
   running a version of Pyramid with the major version "1", the minor version
   "2" and the micro version "3".  A "major" release is one that increments the
   first-dot number; 2.X.X might follow 1.X.X.  A "minor" release is one that
   increments the second-dot number; 1.3.X might follow 1.2.X.  A "micro"
   release is one that increments the third-dot number; 1.2.3 might follow
   1.2.2.  In general, micro releases are "bugfix-only", and contain no new
   features, minor releases contain new features but are largely backwards
   compatible with older versions, and a major release indicates a large set of
   backwards incompatibilities.

The Pyramid core team is conservative when it comes to removing features.  We
don't remove features unnecessarily, but we're human and we make mistakes which
cause some features to be evolutionary dead ends.  Though we are willing to
support dead-end features for some amount of time, some eventually have to be
removed when the cost of supporting them outweighs the benefit of keeping them
around, because each feature in Pyramid represents a certain documentation and
maintenance burden.

Deprecation and removal policy
------------------------------

When a feature is scheduled for removal from Pyramid or any of its official
add-ons, the core development team takes these steps:

- Using the feature will begin to generate a `DeprecationWarning`, indicating
  the version in which the feature became deprecated.

- A note is added to the documentation indicating that the feature is
  deprecated.

- A note is added to the :ref:`changelog` about the deprecation.

When a deprecated feature is eventually removed:

- The feature is removed.

- A note is added to the :ref:`changelog` about the removal.

Features are never removed in *micro* releases.  They are only removed in minor
and major releases.  Deprecated features are kept around for at least *three*
minor releases from the time the feature became deprecated. Therefore, if a
feature is added in Pyramid 1.0, but it's deprecated in Pyramid 1.1, it will be
kept around through all 1.1.X releases, all 1.2.X releases and all 1.3.X
releases.  It will finally be removed in the first 1.4.X release.

Sometimes features are "docs-deprecated" instead of formally deprecated. This
means that the feature will be kept around indefinitely, but it will be removed
from the documentation or a note will be added to the documentation telling
folks to use some other newer feature.  This happens when the cost of keeping
an old feature around is very minimal and the support and documentation burden
is very low.  For example, we might rename a function that is an API without
changing the arguments it accepts.  In this case, we'll often rename the
function, and change the docs to point at the new function name, but leave
around a backwards compatibility alias to the old function name so older code
doesn't break.

"Docs deprecated" features tend to work "forever", meaning that they won't be
removed, and they'll never generate a deprecation warning.  However, such
changes are noted in the :ref:`changelog`, so it's possible to know that you
should change older spellings to newer ones to ensure that people reading your
code can find the APIs you're using in the Pyramid docs.


Python support policy
~~~~~~~~~~~~~~~~~~~~~

At the time of a Pyramid version release, each supports all versions of Python
through the end of their lifespans. The end-of-life for a given version of
Python is when security updates are no longer released.

- `Python 3.2 Lifespan <https://www.python.org/dev/peps/pep-0392/#lifespan>`_
  ends February 2016.
- `Python 3.3 Lifespan <https://www.python.org/dev/peps/pep-0392/#lifespan>`_
  ends September 2017.
- `Python 3.4 Lifespan <https://www.python.org/dev/peps/pep-0429/>`_ TBD.
- `Python 3.5 Lifespan <https://www.python.org/dev/peps/pep-0478/>`_ TBD.
- `Python 3.6 Lifespan <https://www.python.org/dev/peps/pep-0494/#id4>`_
  December 2021.

To determine the Python support for a specific release of Pyramid, view its
``tox.ini`` file at the root of the repository's version.


Consulting the change history
-----------------------------

Your first line of defense against application failures caused by upgrading to
a newer Pyramid release is always to read the :ref:`changelog` to find the
deprecations and removals for each release between the release you're currently
running and the one to which you wish to upgrade.  The change history notes
every deprecation within a ``Deprecation`` section and every removal within a
``Backwards Incompatibilies`` section for each release.

The change history often contains instructions for changing your code to avoid
deprecation warnings and how to change docs-deprecated spellings to newer ones.
You can follow along with each deprecation explanation in the change history,
simply doing a grep or other code search to your application, using the change
log examples to remediate each potential problem.

.. _testing_under_new_release:

Testing your application under a new Pyramid release
----------------------------------------------------

Once you've upgraded your application to a new Pyramid release and you've
remediated as much as possible by using the change history notes, you'll want
to run your application's tests (see :ref:`running_tests`) in such a way that
you can see DeprecationWarnings printed to the console when the tests run.

.. code-block:: bash

   $ python -Wd setup.py test -q

The ``-Wd`` argument tells Python to print deprecation warnings to the console.
See `the Python -W flag documentation
<https://docs.python.org/2/using/cmdline.html#cmdoption-W>`_ for more
information.

As your tests run, deprecation warnings will be printed to the console
explaining the deprecation and providing instructions about how to prevent the
deprecation warning from being issued.  For example:

.. code-block:: bash

   $ python -Wd setup.py test -q
   # .. elided ...
   running build_ext
   /home/chrism/projects/pyramid/env27/myproj/myproj/views.py:3:
   DeprecationWarning: static: The "pyramid.view.static" class is deprecated
   as of Pyramid 1.1; use the "pyramid.static.static_view" class instead with
   the "use_subpath" argument set to True.
     from pyramid.view import static
   .
   ----------------------------------------------------------------------
   Ran 1 test in 0.014s
   
   OK

In the above case, it's line #3 in the ``myproj.views`` module (``from
pyramid.view import static``) that is causing the problem:

.. code-block:: python
    :linenos:

    from pyramid.view import view_config

    from pyramid.view import static
    myview = static('static', 'static')

The deprecation warning tells me how to fix it, so I can change the code to do
things the newer way:

.. code-block:: python
    :linenos:

    from pyramid.view import view_config

    from pyramid.static import static_view
    myview = static_view('static', 'static', use_subpath=True)

When I run the tests again, the deprecation warning is no longer printed to my
console:

.. code-block:: bash

   $ python -Wd setup.py test -q
   # .. elided ...
   running build_ext
   .
   ----------------------------------------------------------------------
   Ran 1 test in 0.014s
   
   OK


My application doesn't have any tests or has few tests
------------------------------------------------------

If your application has no tests, or has only moderate test coverage, running
tests won't tell you very much, because the Pyramid codepaths that generate
deprecation warnings won't be executed.

In this circumstance, you can start your application interactively under a
server run with the ``PYTHONWARNINGS`` environment variable set to ``default``.
On UNIX, you can do that via:

.. code-block:: bash

   $ PYTHONWARNINGS=default $VENV/bin/pserve development.ini

On Windows, you need to issue two commands:

.. code-block:: bash

   C:\> set PYTHONWARNINGS=default
   C:\> Scripts/pserve.exe development.ini

At this point, it's ensured that deprecation warnings will be printed to the
console whenever a codepath is hit that generates one.  You can then click
around in your application interactively to try to generate them, and remediate
as explained in :ref:`testing_under_new_release`.

See `the PYTHONWARNINGS environment variable documentation
<https://docs.python.org/2/using/cmdline.html#envvar-PYTHONWARNINGS>`_ or `the
Python -W flag documentation
<https://docs.python.org/2/using/cmdline.html#cmdoption-W>`_ for more
information.

Upgrading to the very latest Pyramid release
--------------------------------------------

When you upgrade your application to the most recent Pyramid release,
it's advisable to upgrade step-wise through each most recent minor release,
beginning with the one that you know your application currently runs under,
and ending on the most recent release.  For example, if your application is
running in production on Pyramid 1.2.1, and the most recent Pyramid 1.3
release is Pyramid 1.3.3, and the most recent Pyramid release is 1.4.4, it's
advisable to do this:

- Upgrade your environment to the most recent 1.2 release.  For example, the
  most recent 1.2 release might be 1.2.3, so upgrade to it.  Then run your
  application's tests under 1.2.3 as described in
  :ref:`testing_under_new_release`.  Note any deprecation warnings and
  remediate.

- Upgrade to the most recent 1.3 release, 1.3.3.  Run your application's tests,
  note any deprecation warnings, and remediate.

- Upgrade to 1.4.4.  Run your application's tests, note any deprecation
  warnings, and remediate.

If you skip testing your application under each minor release (for example if
you upgrade directly from 1.2.1 to 1.4.4), you might miss a deprecation warning
and waste more time trying to figure out an error caused by a feature removal
than it would take to upgrade stepwise through each minor release.
