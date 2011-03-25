.. index::
   single: converting a BFG app
   single: bfg2pyramid

.. _converting_a_bfg_app:

Converting a :mod:`repoze.bfg` Application to :app:`Pyramid`
============================================================

Prior iterations of :app:`Pyramid` were released as a package named
:mod:`repoze.bfg`.  :mod:`repoze.bfg` users are encouraged to upgrade
their deployments to :app:`Pyramid`, as, after the first final release
of :app:`Pyramid`, further feature development on :mod:`repoze.bfg`
will cease.

Most existing :mod:`repoze.bfg` applications can be converted to a
:app:`Pyramid` application in a completely automated fashion.
However, if your application depends on packages which are not "core"
parts of :mod:`repoze.bfg` but which nonetheless have ``repoze.bfg``
in their names (e.g. ``repoze.bfg.skins``,
``repoze.bfg.traversalwrapper``, ``repoze.bfg.jinja2``), you will need
to find an analogue for each.  For example, by the time you read this,
there will be a ``pyramid_jinja2`` package, which can be used instead
of ``repoze.bfg.jinja2``.  If an analogue does not seem to exist for a
``repoze.bfg`` add-on package that your application uses, please email
the `Pylons-devel <http://groups.google.com/group/pylons-devel>`_
maillist; we'll convert the package to a :app:`Pyramid` analogue for
you.

Here's how to convert a :mod:`repoze.bfg` application to a
:app:`Pyramid` application:

#. Ensure that your application works under :mod:`repoze.bfg` *version
   1.3 or better*.  See
   `http://docs.repoze.org/bfg/1.3/narr/install.html
   <http://docs.repoze.org/bfg/1.3/narr/install.html>`_ for
   :mod:`repoze.bfg` 1.3 installation instructions.  If your
   application has an automated test suite, run it while your
   application is using :mod:`repoze.bfg` 1.3+.  Otherwise, test it
   manually.  It is only safe to proceed to the next step once your
   application works under :mod:`repoze.bfg` 1.3+.

   If your application has a proper set of dependencies, and a
   standard automated test suite, you might test your
   :mod:`repoze.bfg` application against :mod:`repoze.bfg` 1.3 like
   so:

   .. code-block:: bash

     $ bfgenv/bin/python setup.py test

   ``bfgenv`` above will be the virtualenv into which you've installed
   :mod:`repoze.bfg` 1.3.

#. Install :app:`Pyramid` into a *separate* virtualenv as per the
   instructions in :ref:`installing_chapter`.  The :app:`Pyramid`
   virtualenv should be separate from the one you've used to install
   :mod:`repoze.bfg`.  A quick way to do this:

   .. code-block:: bash

      $ cd ~
      $ virtualenv --no-site-packages pyramidenv
      $ cd pyramidenv
      $ bin/easy_install pyramid

#. Put a *copy* of your :mod:`repoze.bfg` application into a temporary
   location (perhaps by checking a fresh copy of the application out
   of a version control repository).  For example:

   .. code-block:: bash

      $ cd /tmp
      $ svn co http://my.server/my/bfg/application/trunk bfgapp

#. Use the ``bfg2pyramid`` script present in the ``bin`` directory of
   the :app:`Pyramid` virtualenv to convert all :mod:`repoze.bfg`
   Python import statements into compatible :app:`Pyramid` import
   statements. ``bfg2pyramid`` will also fix ZCML directive usages of
   common :mod:`repoze.bfg` directives. You invoke ``bfg2pyramid`` by
   passing it the *path* of the copy of your application.  The path
   passed should contain a "setup.py" file, representing your
   :mod:`repoze.bfg` application's setup script.  ``bfg2pyramid`` will
   change the copy of the application *in place*.

   .. code-block:: bash
 
      $ ~/pyramidenv/bfg2pyramid /tmp/bfgapp

   ``bfg2pyramid`` will convert the following :mod:`repoze.bfg`
   application aspects to :app:`Pyramid` compatible analogues:

   - Python ``import`` statements naming :mod:`repoze.bfg` APIs will
     be converted to :app:`Pyramid` compatible ``import`` statements.
     Every Python file beneath the top-level path will be visited and
     converted recursively, except Python files which live in
     directories which start with a ``.`` (dot).

   - Each ZCML file found (recursively) within the path will have the
     default ``xmlns`` attribute attached to the ``configure`` tag
     changed from ``http://namespaces.repoze.org/bfg`` to
     ``http://pylonshq.com/pyramid``.  Every ZCML file beneath the
     top-level path (files ending with ``.zcml``) will be visited and
     converted recursively, except ZCML files which live in
     directories which start with a ``.`` (dot).

   - ZCML files which contain directives that have attributes which
     name a ``repoze.bfg`` API module or attribute of an API module
     (e.g. ``context="repoze.bfg.exceptions.NotFound"``) will be
     converted to :app:`Pyramid` compatible ZCML attributes
     (e.g. ``context="pyramid.exceptions.NotFound``).  Every ZCML file
     beneath the top-level path (files ending with ``.zcml``) will be
     visited and converted recursively, except ZCML files which live
     in directories which start with a ``.`` (dot).

#. Edit the ``setup.py`` file of the application you've just converted
   (if you've been using the example paths, this will be
   ``/tmp/bfgapp/setup.py``) to depend on the ``pyramid`` distribution
   instead the of ``repoze.bfg`` distribution in its
   ``install_requires`` list.  If you used a scaffold to
   create the :mod:`repoze.bfg` application, you can do so by changing
   the ``requires`` line near the top of the ``setup.py`` file.  The
   original may look like this:

   .. code-block:: text

     requires = ['repoze.bfg', ... other dependencies ...]

   Edit the ``setup.py`` so it has:

   .. code-block:: text

     requires = ['pyramid', ... other dependencies ...]

   All other install-requires and tests-requires dependencies save for
   the one on ``repoze.bfg`` can remain the same.

#. Convert any ``install_requires`` dependencies your application has
   on other add-on packages which have ``repoze.bfg`` in their names
   to :app:`Pyramid` compatible analogues (e.g. ``repoze.bfg.jinja2``
   should be replaced with ``pyramid_jinja2``).  You may need to
   adjust configuration options and/or imports in your
   :mod:`repoze.bfg` application after replacing these add-ons.  Read
   the documentation of the :app:`Pyramid` add-on package for
   information.

#. *Only if you use ZCML and add-ons which use ZCML*: The default
   ``xmlns`` of the ``configure`` tag in ZCML has changed.  The
   ``bfg2pyramid`` script effects the default namespace change (it
   changes the ``configure`` tag default ``xmlns`` from
   ``http://namespaces.repoze.org/bfg`` to
   ``http://pylonshq.com/pyramid``).

   This means that uses of add-ons which define ZCML directives in the
   ``http://namespaces.repoze.org/bfg`` namespace will begin to "fail"
   (they're actually not really failing, but your ZCML assumes that
   they will always be used within a ``configure`` tag which names the
   ``http://namespaces.repoze.org/bfg`` namespace as its default
   ``xmlns``). Symptom: when you attempt to start the application, an
   error such as ``ConfigurationError: ('Unknown directive',
   u'http://namespaces.repoze.org/bfg', u'workflow')`` is printed to
   the console and the application fails to start.  In such a case,
   either add an ``xmlns="http://namespaces.repoze.org/bfg"``
   attribute to each tag which causes a failure, or define a namespace
   alias in the configure tag and prefix each failing tag.  For
   example, change this "failing" tag instance::

     <configure xmlns="http://pylonshq.com/pyramid">
         <failingtag attr="foo"/>
     </configure>
 
   To this, which will begin to succeed::

     <configure xmlns="http://pylonshq.com/pyramid"
                xmlns:bfg="http://namespaces.repoze.org/bfg">
         <bfg:failingtag attr="foo"/>
     </configure>

   You will also need to add the ``pyramid_zcml`` package to your
   ``setup.py`` ``install_requires`` list.  In Pyramid, ZCML configuration
   became an optional add-on supported by the ``pyramid_zcml`` package.

#. Retest your application using :app:`Pyramid`.  This might be as
   easy as:

   .. code-block:: bash

     $ cd /tmp/bfgapp
     $ ~/pyramidenv/bin/python setup.py test

#. Fix any test failures.

#. Fix any code which generates deprecation warnings.

#. Start using the converted version of your application.  Celebrate.

Two terminological changes have been made to Pyramid which make its
documentation and newer APIs different than those of ``repoze.bfg``.  The
concept that BFG called ``model`` is called ``resource`` in Pyramid and the
concept that BFG called ``resource`` is called ``asset`` in Pyramid.  Various
APIs have changed as a result (although all have backwards compatible shims).
Additionally, the environment variables that influenced server behavior which
used to be prefixed with ``BFG_`` (such as ``BFG_DEBUG_NOTFOUND``) must now
be prefixed with ``PYRAMID_``.
