:mod:`repoze.bfg` Introduction
==============================

:mod:`repoze.bfg` is a Python web application framework.  It is
inspired by Zope, and uses :term:`Zope` libraries to do much of its
work.  However, it simpler than any than any released version of Zope.
:mod:`repoze.bfg` uses the :term:`WSGI` protocol to handle requests
and responses.

Similarities to Other Frameworks
--------------------------------

:mod:`repoze.bfg` was inspired by :term:`Zope`, :term:`Django`, and
:term:`Pylons`.

The :mod:`repoze.bfg` concept of traversal is inspired by
:term:`Zope`.  Additionally, :mod:`repoze.bfg` uses the Zope Component
Architecture ("CA") internally, as do Zope 2, Zope 3, and
:term:`Grok`.  Application :mod:`repoze.bfg` developers use either
:term:`ZCML` (an XML dialect, used in Zope) or decorators to perform
various configuration tasks.  The decorator support is provided by the
:term:`Grok` project.

Like :term:`Pylons`, :mod:`repoze.bfg` is mostly policy-free.  It
makes no assertions about which database you should use, and its
built-in templating facilities are only for convenience.  In essence,
it only supplies a mechanism to map URLs to :term:`view` code, along
with a convention for calling those views.  You are free to use
third-party components in your application that fit your needs.  Also
like Pylons, :mod:`repoze.bfg` is heavily dependent on WSGI.

The "Django docs state that Django is an "MTV" framework in their `FAQ
<http://www.djangoproject.com/documentation/faq/>`_.  This also
happens to be true for :mod:`repoze.bfg`::

  Django appears to be a MVC framework, but you call the Controller
  the "view", and the View the "template". How come you don't use the
  standard names?

  Well, the standard names are debatable.

  In our interpretation of MVC, the "view" describes the data that
  gets presented to the user. It's not necessarily how the data looks,
  but which data is presented. The view describes which data you see,
  not how you see it. It's a subtle distinction.

  So, in our case, a "view" is the Python callback function for a
  particular URL, because that callback function describes which data
  is presented.

  Furthermore, it's sensible to separate content from presentation -
  which is where templates come in. In Django, a "view" describes
  which data is presented, but a view normally delegates to a
  template, which describes how the data is presented.

  Where does the "controller" fit in, then? In Django's case, it's
  probably the framework itself: the machinery that sends a request to
  the appropriate view, according to the Django URL configuration.

  If you're hungry for acronyms, you might say that Django is a "MTV"
  framework - that is, "model", "template", and "view." That breakdown
  makes much more sense.

The skeleton code generator of :mod:`repoze.bfg` generates a directory
layout very simliar to the directory layout suggested by the `Django
Book <http://www.djangobook.com/>`_ .  Additionally, as suggested
above, the concepts of :term:`view`, :term:`model` and
:term:`template` are used by :mod:`repoze.bfg` as they would be by
Django.

To learn more about the concepts used by :mod:`repoze.bfg`, visit the
:ref:`glossary` for a listing of definitions.

Differences from Other Frameworks
---------------------------------

Like :term:`Zope`, the :mod:`repoze.bfg` framework imposes slightly
more `control inversion <http://plope.com/control_inversion>`_ upon
application developers than other Python frameworks such as
:term:`Pylons`.  For example :mod:`repoze.bfg` assumes that you're
wiling to resolve a URL to a :term:`context` object before passing it
to a :term:`view`.  Pylons and other Python "MVC" frameworks have no
such intermediate step; they resolve a URL directly to a controller.
Another example: using the :mod:`repoze.bfg` security subsystem
assumes that you're willing to attach an :term:`ACL` to a
:term:`context` object; the ACL is checked by the framework itself
instead of by user code, and access is permitted or denied by the
framework itself rather than by user code.  Such a task would
typically be performed by user-space decorators in other Python web
frameworks.

Unlike application development using Zope, application developers
don't interact with the Zope Component Architecture ("CA") very much
during :mod:`repoze.bfg` application development.  Instead, the
:mod:`repoze.bfg` framework tends to "hide" most interaction with the
CA behind special-purpose API functions.

Also unlike :term:`Zope` and unlike other "full-featured" frameworks
such as :term:`Django`, :mod:`repoze.bfg` makes no assumptions about
what persistence mechanisms you want to use to build an application.
Zope applications are typically reliant on :term:`ZODB`;
:mod:`repoze.bfg` allows you to build :term:`ZODB` applications, but
it has no reliance on the ZODB package.  Likewise, :term:`Django`
tends to make the assumption that you're going to want to store your
application's data in a relational database.  :mod:`repoze.bfg` makes
no such assumption; it allows you to use a relational database but
doesn't enourage or discourage an application developer about such a
decision.

Why?
----

*Familiarity*: As web developers, we've become accustomed to working
in very particular ways (primarily using Zope 2) over the years.  This
framework is a canonization of practices that "fit our brains".

*Simplicity*: :mod:`repoze.bfg` attempts to be a *"pay only for what
you eat"* framework in which you can be productive quickly with
partial knowledge, in contrast to *"pay up front for what anyone might
eventually want to eat"* frameworks, which tend to expect you to
understand a great many concepts and technologies fully before you can
be truly productive.  :mod:`repoze.bfg` doesn't force you to use any
particular technology to get your application written, and we try to
keep the core set of concepts you need to understand to a minimum.
We've thrown out all the cruft.

*Minimalism*: :mod:`repoze.bfg` provides only the very basics: *URL to
code mapping*, *templating*, and *security*.  There is not much more
to the framework than these pieces: you are expected to provide the
rest.

*Documentation*: Because :mod:`repoze.bfg` is so minimal, it's
relatively easy to keep its documentation up-to-date, which is helpful
to bring new developers up to speed.  It's our goal that nothing
remain undocumented about :mod:`repoze.bfg`.

*Speed*: :mod:`repoze.bfg` is meant to be fast, capable of serving on
the order of 100-1000 requests per second on today's commodity
hardware for views that do "real work" given proper application
implementation.  The *hardware is cheap* mantra has its limits when
you're responsible for managing a great many machines: the fewer you
need, the less pain you'll have.

It's Tested
-----------

*If it ain't tested, it's broke.* We strive to test :mod:`repoze.bfg`
completely.  Below a run of the ``nosetests`` command configured to
show code coverage information (run against the :mod:`repoze.bfg`
trunk just before the 0.6.3 release).

.. code-block:: bash

  [chrism@vitaminf trunk]$ python setup.py nosetests
  running nosetests
  running egg_info
  writing requirements to repoze.bfg.egg-info/requires.txt
  writing repoze.bfg.egg-info/PKG-INFO
  writing namespace_packages to repoze.bfg.egg-info/namespace_packages.txt
  writing top-level names to repoze.bfg.egg-info/top_level.txt
  writing dependency_links to repoze.bfg.egg-info/dependency_links.txt
  writing entry points to repoze.bfg.egg-info/entry_points.txt
  writing manifest file 'repoze.bfg.egg-info/SOURCES.txt'
  running build_ext
  .............................................................................
  .............................................................................
  .............................................................................
  .............................................................................
  .................................
  Name                                     Stmts   Exec  Cover   Missing
  ----------------------------------------------------------------------
  repoze.bfg                                   1      1   100%   
  repoze.bfg.chameleon_genshi                 44     44   100%   
  repoze.bfg.chameleon_text                   48     48   100%   
  repoze.bfg.chameleon_zpt                    44     44   100%   
  repoze.bfg.events                           18     18   100%   
  repoze.bfg.functional                       17     15    88%   99-100
  repoze.bfg.includes                          0      0   100%   
  repoze.bfg.interfaces                       66     66   100%   
  repoze.bfg.location                         42     42   100%   
  repoze.bfg.log                               9      9   100%   
  repoze.bfg.path                             12     12   100%   
  repoze.bfg.push                             16     16   100%   
  repoze.bfg.registry                         54     52    96%   95-97
  repoze.bfg.router                          107    107   100%   
  repoze.bfg.security                        163    163   100%   
  repoze.bfg.settings                         26     26   100%   
  repoze.bfg.template                         10     10   100%   
  repoze.bfg.templating                       17     17   100%   
  repoze.bfg.testing                         204    204   100%   
  repoze.bfg.tests                             0      0   100%   
  repoze.bfg.tests.fixtureapp                  0      0   100%   
  repoze.bfg.tests.fixtureapp.models           3      3   100%   
  repoze.bfg.tests.fixtureapp.views            4      4   100%   
  repoze.bfg.tests.grokkedapp                  5      5   100%   
  repoze.bfg.tests.routesapp                   0      0   100%   
  repoze.bfg.tests.routesapp.models            3      3   100%   
  repoze.bfg.tests.routesapp.views             4      4   100%   
  repoze.bfg.tests.test_chameleon_genshi     157    157   100%   
  repoze.bfg.tests.test_chameleon_text       172    172   100%   
  repoze.bfg.tests.test_chameleon_zpt        161    161   100%   
  repoze.bfg.tests.test_events                59     59   100%   
  repoze.bfg.tests.test_integration          127    127   100%   
  repoze.bfg.tests.test_location              83     83   100%   
  repoze.bfg.tests.test_log                   11     11   100%   
  repoze.bfg.tests.test_push                  29     29   100%   
  repoze.bfg.tests.test_registry              79     79   100%   
  repoze.bfg.tests.test_router               642    642   100%   
  repoze.bfg.tests.test_security             550    550   100%   
  repoze.bfg.tests.test_settings              98     98   100%   
  repoze.bfg.tests.test_template              73     73   100%   
  repoze.bfg.tests.test_templating            45     45   100%   
  repoze.bfg.tests.test_testing              365    365   100%   
  repoze.bfg.tests.test_traversal            371    371   100%   
  repoze.bfg.tests.test_url                  112    112   100%   
  repoze.bfg.tests.test_urldispatch          187    187   100%   
  repoze.bfg.tests.test_view                 458    458   100%   
  repoze.bfg.tests.test_wsgi                  20     20   100%   
  repoze.bfg.tests.test_xslt                 191    191   100%   
  repoze.bfg.tests.test_zcml                 603    603   100%   
  repoze.bfg.traversal                       108    108   100%   
  repoze.bfg.url                              65     65   100%   
  repoze.bfg.urldispatch                     108    108   100%   
  repoze.bfg.view                             75     75   100%   
  repoze.bfg.wsgi                              8      8   100%   
  repoze.bfg.xslt                             57     57   100%   
  repoze.bfg.zcml                            242    240    99%   168-169
  ----------------------------------------------------------------------
  TOTAL                                     6173   6167    99%   
  ----------------------------------------------------------------------
  Ran 341 tests in 10.093s

  OK
