.. _index:

=========================
The Pyramid Web Framework
=========================

:app:`Pyramid` is a small, fast, down-to-earth Python web framework.  It is
developed as part of the `Pylons Project <https://pylonsproject.org>`_.
It is licensed under a `BSD-like license <https://web.archive.org/web/20190401024809/http://repoze.org/license.html>`_.

Here is one of the simplest :app:`Pyramid` applications you can make:

.. literalinclude:: narr/helloworld.py

After you install :app:`Pyramid` and run this application, when you visit
`<http://localhost:6543/>`_ in a browser, you will see the text
``Hello World!`` See :ref:`firstapp_chapter` for a full explanation of how
this application works.


.. _getting_started:

Getting Started
===============

If you are new to Pyramid, we have a few resources that can help you get up to
speed right away.

.. toctree::
   :hidden:

   quick_tour
   quick_tutorial/index

* :doc:`quick_tour` gives an overview of the major features in Pyramid,
  covering a little about a lot.

* Like learning by example? Visit the official :ref:`html_tutorials` as well as
  the community-contributed :ref:`Pyramid Tutorials
  <tutorials:pyramid-tutorials>` and :ref:`Pyramid Community Cookbook
  <cookbook:pyramid-cookbook>`.

* For help getting Pyramid set up, try :ref:`installing_chapter`.

* Need help?  See :ref:`Support and Development <support-and-development>`.


.. _html_tutorials:

Tutorials
=========

Official tutorials provide a quick overview of :app:`Pyramid`'s features in more depth than the Quick Tour and with working code, explain how to use :app:`Pyramid` to build various types of applications, and how to deploy :app:`Pyramid` applications to various platforms.

.. toctree::
   :maxdepth: 1

   quick_tutorial/index
   tutorials/wiki2/index
   tutorials/wiki/index
   tutorials/modwsgi/index


.. _support-and-development:

Support and Development
=======================

The `Pyramid website <https://trypyramid.com/documentation.html>`_ is the main
entry point to :app:`Pyramid` web framework resources for support and
development information.

To report bugs, use the `issue tracker
<https://github.com/Pylons/pyramid/issues>`_.

If you've got questions that aren't answered by this documentation, contact the
`Pylons-discuss maillist
<https://groups.google.com/forum/#!forum/pylons-discuss>`_ or join the
`#pyramid IRC channel
<https://web.libera.chat/#pyramid>`_.

Browse and check out tagged and trunk versions of :app:`Pyramid` via the
`Pyramid GitHub repository <https://github.com/Pylons/pyramid/>`_. To check out
the trunk via ``git``, use either command:

.. code-block:: text

    # If you have SSH keys configured on GitHub:
    git clone git@github.com:Pylons/pyramid.git

    # Otherwise, HTTPS will work, using your GitHub login:
    git clone https://github.com/Pylons/pyramid.git

To find out how to become a contributor to :app:`Pyramid`, please see `How to Contribute Source Code and Documentation <https://pylonsproject.org/community-how-to-contribute.html>`_.


.. _html_narrative_documentation:

Narrative Documentation
=======================

Narrative documentation in chapter form explaining how to use :app:`Pyramid`.

.. toctree::
   :maxdepth: 2

   narr/introduction
   narr/install
   narr/firstapp
   narr/configuration
   narr/project
   narr/startup
   narr/router
   narr/urldispatch
   narr/views
   narr/renderers
   narr/templates
   narr/viewconfig
   narr/assets
   narr/webob
   narr/sessions
   narr/events
   narr/environment
   narr/logging
   narr/paste
   narr/commandline
   narr/i18n
   narr/vhosting
   narr/testing
   narr/resources
   narr/hellotraversal
   narr/muchadoabouttraversal
   narr/traversal
   narr/security
   narr/hybrid
   narr/subrequest
   narr/hooks
   narr/introspector
   narr/extending
   narr/advconfig
   narr/extconfig
   narr/cookiecutters
   narr/upgrading
   narr/threadlocals
   narr/zca


API Documentation
=================

Comprehensive reference material for every public API exposed by
:app:`Pyramid`:

.. toctree::
   :maxdepth: 2

   api/index


``p*`` Scripts Documentation
============================

``p*`` scripts included with :app:`Pyramid`.

.. toctree::
   :maxdepth: 2

   pscripts/index


Change History
==============

.. toctree::
   :maxdepth: 1

   whatsnew-2.0
   whatsnew-1.10
   whatsnew-1.9
   whatsnew-1.8
   whatsnew-1.7
   whatsnew-1.6
   whatsnew-1.5
   whatsnew-1.4
   whatsnew-1.3
   whatsnew-1.2
   whatsnew-1.1
   whatsnew-1.0
   changes


Design Documents
================

.. toctree::
   :maxdepth: 1

   designdefense


Copyright, Trademarks, and Attributions
=======================================

.. toctree::
   :maxdepth: 1

   copyright


Typographical Conventions and Style Guide
=========================================

.. toctree::
   :maxdepth: 1

   typographical-conventions


Index and Glossary
==================

* :ref:`glossary`
* :ref:`genindex`
* :ref:`search`


.. toctree::
   :hidden:

   glossary

