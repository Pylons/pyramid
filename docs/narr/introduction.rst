:mod:`repoze.bfg` Introduction
==============================

:mod:`repoze.bfg` is a Python web application framework.  It is
inspired by Zope's publisher, and uses :term:`Zope` libraries to do
much of its work.  However, it is less ambitious and less featureful
than any released version of Zope's publisher.

:mod:`repoze.bfg` uses the :term:`WSGI` protocol to handle requests
and responses, and integrates :term:`Zope`, :term:`Paste`, and
:term:`WebOb` libraries to form the basis for a simple web object
publishing framework.

Similarities with Other Frameworks
----------------------------------

:mod:`repoze.bfg` was inspired by Zope, Django, and Pylons.

:mod:`repoze.bfg` traversal is inspired by Zope.  :mod:`repoze.bfg`
uses the Zope Component Architecture ("CA") internally, as do Zope 2,
Zope 3, and Grok.  Developers don't interact with the CA very much
during typical development, however; it's mostly used by the framework
developer rather than the application developer.  :mod:`repoze.bfg`
developers use :term:`ZCML` (an XML dialect) to perform various
configuration tasks; in particular, as in Zope3, one more more
:term:`view` functions is associated with a :term:`model` type via
ZCML.  It is also possible to configure :mod:`repoze.bfg` views
without :term:`ZCML` (instead configuration is done inside Python
decorators) by using an add-on package named
:term:`repoze.bfg.convention`.

Like Pylons, :mod:`repoze.bfg` is mostly policy-free.  It makes no
assertions about which database you should use, and its built-in
templating facilities are only for convenience.  In essence, it only
supplies a mechanism to map URLs to :term:`view` code, along with a
convention for calling those views.  You are free to use third-party
components in your application that fit your needs.  Also like Pylons,
:mod:`repoze.bfg` is heavily dependent on WSGI.

The Django docs state that Django is an "MTV" framework in their `FAQ
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
the order of 100+ requests per second on today's commodity hardware
for views that do "real work" given proper application implementation.
The *hardware is cheap* mantra has its limits when you're responsible
for managing a great many machines: the fewer you need, the less pain
you'll have.

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
  ............................................................................
  ............................................................................
  ............................................................................
  ........................................................................
  Name                                     Stmts   Exec  Cover   Missing
  ----------------------------------------------------------------------
  repoze.bfg                                   1      1   100%   
  repoze.bfg.chameleon_genshi                 44     44   100%   
  repoze.bfg.chameleon_text                   48     48   100%   
  repoze.bfg.chameleon_zpt                    44     44   100%   
  repoze.bfg.events                           18     18   100%   
  repoze.bfg.functional                       17     15    88%   99-100
  repoze.bfg.includes                          0      0   100%   
  repoze.bfg.interfaces                       64     64   100%   
  repoze.bfg.location                         42     42   100%   
  repoze.bfg.log                               9      9   100%   
  repoze.bfg.path                             12     12   100%   
  repoze.bfg.push                             14     14   100%   
  repoze.bfg.registry                         57     55    96%   98-100
  repoze.bfg.router                           95     95   100%   
  repoze.bfg.security                        163    163   100%   
  repoze.bfg.settings                         30     30   100%   
  repoze.bfg.template                         10     10   100%   
  repoze.bfg.templating                       17     17   100%   
  repoze.bfg.testing                         204    204   100%   
  repoze.bfg.tests                             0      0   100%   
  repoze.bfg.tests.fixtureapp                  0      0   100%   
  repoze.bfg.tests.fixtureapp.models           3      3   100%   
  repoze.bfg.tests.fixtureapp.views            5      4    80%   4
  repoze.bfg.tests.test_chameleon_genshi     157    157   100%   
  repoze.bfg.tests.test_chameleon_text       172    172   100%   
  repoze.bfg.tests.test_chameleon_zpt        161    161   100%   
  repoze.bfg.tests.test_events                59     59   100%   
  repoze.bfg.tests.test_location              83     83   100%   
  repoze.bfg.tests.test_log                   11     11   100%   
  repoze.bfg.tests.test_push                  29     29   100%   
  repoze.bfg.tests.test_registry              79     79   100%   
  repoze.bfg.tests.test_router               566    566   100%   
  repoze.bfg.tests.test_security             550    550   100%   
  repoze.bfg.tests.test_settings              98     98   100%   
  repoze.bfg.tests.test_template              73     73   100%   
  repoze.bfg.tests.test_templating            45     45   100%   
  repoze.bfg.tests.test_testing              365    365   100%   
  repoze.bfg.tests.test_traversal            324    324   100%   
  repoze.bfg.tests.test_url                  112    112   100%   
  repoze.bfg.tests.test_urldispatch           92     92   100%   
  repoze.bfg.tests.test_view                 424    424   100%   
  repoze.bfg.tests.test_wsgi                  58     58   100%   
  repoze.bfg.tests.test_xslt                 191    191   100%   
  repoze.bfg.tests.test_zcml                 393    393   100%   
  repoze.bfg.traversal                        96     96   100%   
  repoze.bfg.url                              65     65   100%   
  repoze.bfg.urldispatch                      51     51   100%   
  repoze.bfg.view                             64     64   100%   
  repoze.bfg.wsgi                             24     24   100%   
  repoze.bfg.xslt                             57     57   100%   
  repoze.bfg.zcml                            112    108    96%   160-161, 197, 207
  ----------------------------------------------------------------------
  TOTAL                                     5408   5399    99%   
  ----------------------------------------------------------------------
  Ran 300 tests in 9.523s

  OK
