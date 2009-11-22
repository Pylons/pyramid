:mod:`repoze.bfg` Introduction
==============================

:mod:`repoze.bfg` is a Python web framework.  It is inspired by
:term:`Zope`, :term:`Pylons`, and :term:`Django`.  :mod:`repoze.bfg`
uses the :term:`WSGI` protocol to handle requests and responses.

Similarities to Other Frameworks
--------------------------------

.. sidebar:: Django's Authors Explain Why It Doesn't Use "MVC" Terminology

  Django appears to be a MVC framework, but you call the Controller
  the "view", and the View the "template". How come you don't use the
  standard names?  Well, the standard names are debatable.

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

:mod:`repoze.bfg` was inspired by :term:`Zope`, :term:`Pylons` and
:term:`Django`.

The :mod:`repoze.bfg` concept of :term:`traversal` is inspired by
:term:`Zope`.  Additionally, :mod:`repoze.bfg` uses the :term:`Zope
Component Architecture` internally, as do Zope 2, Zope 3, and
:term:`Grok`.  :mod:`repoze.bfg` application developers may use either
:term:`ZCML` (an XML dialect, used in Zope) or decorators to perform
various application configuration tasks.  The decorator support is
provided by the :term:`Grok` project.  Like Zope, :mod:`repoze.bfg`
allows you to create applications which do not need to be forked or
otherwise modified to be extended or overridden by a third party
developer.

The :mod:`repoze.bfg` concept of :term:`URL dispatch` is inspired by
the :term:`Routes` system used by :term:`Pylons`.  Like Pylons,
:mod:`repoze.bfg` is mostly policy-free.  It makes no assertions about
which database you should use, and its built-in templating facilities
are only for convenience.  In essence, it only supplies a mechanism to
map URLs to :term:`view` code, along with a convention for calling
those views.  You are free to use third-party components in your
application that fit your needs.  Also like Pylons, :mod:`repoze.bfg`
is dependent upon WSGI.

The Django docs explain that Django is not an "MVC"
("model/view/controller") framework in their `FAQ
<http://www.djangoproject.com/documentation/faq/>`_.  The sidebar to
the right has the Django authors' take on why "MVC" terminology
doesn't match the web very well.  The concepts of :term:`view` and
:term:`model` are used by :mod:`repoze.bfg` as they would be by
Django.

The skeleton code generator of :mod:`repoze.bfg` generates a directory
layout very similar to the directory layout suggested by the `Django
Book <http://www.djangobook.com/>`_ .  

Differences from Other Frameworks
---------------------------------

Like :term:`Zope`, the :mod:`repoze.bfg` framework imposes more
`control inversion <http://plope.com/control_inversion>`_ upon
application developers than other Python frameworks such as
:term:`Pylons`.  For example :mod:`repoze.bfg` allows you to
explicitly resolve a URL to a :term:`context` object before invoking a
:term:`view`.  Pylons and other Python "MVC" frameworks have no such
intermediate step; they resolve a URL directly to a controller.
Another example: using the :mod:`repoze.bfg` security subsystem
assumes that you're willing to attach an :term:`ACL` to a
:term:`context` object; the ACL is checked by the framework itself
instead of by user code, and access is permitted or denied by the
framework itself rather than by user code.  Such a task would
typically be performed by user-space decorators in other Python web
frameworks.

Like Zope, but unlike :term:`Pylons` applications or most
:term:`Django` applications, when you build a :mod:`repoze.bfg`
application, if you obey certain constraints, the application you
produce can be reused, modified, re-integrated, or extended by
third-party developers without modification to the original
application itself.  See :ref:`extending_chapter` for more information
about extending or modifying an existing :mod:`repoze.bfg`
application.

:mod:`repoze.bfg` uses the :term:`Zope Component Architecture` under
the hood.  However, while a Zope application developer tends to need
to understand the component architecture (and concepts such as
adapters, utilities, and interfaces) to create a non-trivial
application, a :mod:`repoze.bfg` application developer isn't required
to interact with or understand the component architecture at all.
:mod:`repoze.bfg` tends to "hide" most interaction with the component
architecture behind special-purpose API functions and ZCML directives.

Also unlike :term:`Zope` and unlike other "full-featured" frameworks
such as :term:`Django`, :mod:`repoze.bfg` makes no assumptions about
which persistence mechanisms you should use to build an application.
Zope applications are typically reliant on :term:`ZODB`;
:mod:`repoze.bfg` allows you to build :term:`ZODB` applications, but
it has no reliance on the ZODB package.  Likewise, :term:`Django`
tends to assume that you want to store your application's data in a
relational database.  :mod:`repoze.bfg` makes no such assumption; it
allows you to use a relational database but doesn't encourage or
discourage an application developer about such a decision.

Why?
----

*Familiarity*: As web developers, we've become accustomed to working
in very particular ways over the years.  This framework is a
canonization of practices that "fit our brains".

*Simplicity*: :mod:`repoze.bfg` attempts to be a *"pay only for what
you eat"* framework in which you can be productive quickly with
partial knowledge.  We contrast this with *"pay up front for what
anyone might eventually want to eat"* frameworks, which tend to expect
you to understand a great many concepts and technologies fully before
you can be truly productive.  :mod:`repoze.bfg` doesn't force you to
use any particular technology to produce an application, and we try to
keep the core set of concepts you need to understand to a minimum.

*Minimalism*: :mod:`repoze.bfg` provides only the very basics: *URL to
code mapping*, *templating*, *security*, and *resources*.  There is
not much more to the framework than these pieces: you are expected to
provide the rest.

*Documentation*: Because :mod:`repoze.bfg` is minimal, it's relatively
easy to keep its documentation up-to-date, which is helpful to bring
new developers up to speed.  It's our goal that nothing remain
undocumented about :mod:`repoze.bfg`.

*Speed*: :mod:`repoze.bfg` is faster than many other popular Python
web frameworks for common tasks such as templating and simple response
generation.  The "hardware is cheap" mantra has its limits when you're
responsible for managing a great many machines: the fewer you need,
the less pain you'll have.

It's Tested
-----------

*If it ain't tested, it's broke.* We strive to test :mod:`repoze.bfg`
completely.  Below a run of the ``nosetests`` command configured to
show code coverage information (run against the :mod:`repoze.bfg`
trunk as of the 1.1b1 release).

.. code-block:: bash
   :linenos:

    [chrism@snowpro trunk]$ python setup.py nosetests --with-coverage
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
    ...........................................................................
    ...........................................................................
    ...........................................................................
    ...........................................................................
    ...........................................................................
    ...........................................................................
    ...........................................................................
    ...........................................................................
    ...........................................................................
    .................................................

    Name                                     Stmts   Exec  Cover   Missing
    ----------------------------------------------------------------------
    repoze.bfg                                   0      0   100%   
    repoze.bfg.authentication                  198    198   100%   
    repoze.bfg.authorization                    50     50   100%   
    repoze.bfg.chameleon_text                   45     45   100%   
    repoze.bfg.chameleon_zpt                    38     38   100%   
    repoze.bfg.compat                            6      6   100%   
    repoze.bfg.configuration                    80     80   100%   
    repoze.bfg.encode                           49     49   100%   
    repoze.bfg.events                           18     18   100%   
    repoze.bfg.exceptions                        2      2   100%   
    repoze.bfg.includes                          1      1   100%   
    repoze.bfg.interfaces                       66     66   100%   
    repoze.bfg.location                         14     14   100%   
    repoze.bfg.log                               9      9   100%   
    repoze.bfg.paster                           60     60   100%   
    repoze.bfg.path                             36     36   100%   
    repoze.bfg.registry                         14     14   100%   
    repoze.bfg.renderers                        54     54   100%   
    repoze.bfg.request                          57     57   100%   
    repoze.bfg.resource                        123    123   100%   
    repoze.bfg.router                           99     99   100%   
    repoze.bfg.scripting                        10     10   100%   
    repoze.bfg.security                         99     99   100%   
    repoze.bfg.settings                         35     35   100%   
    repoze.bfg.static                           53     53   100%   
    repoze.bfg.testing                         262    262   100%   
    repoze.bfg.tests                             1      1   100%   
    repoze.bfg.tests.fixtureapp                  1      1   100%   
    repoze.bfg.tests.fixtureapp.models           4      4   100%   
    repoze.bfg.tests.fixtureapp.subpackage       1      1   100%   
    repoze.bfg.tests.fixtureapp.views            4      4   100%   
    repoze.bfg.tests.grokkedapp                 53     53   100%   
    repoze.bfg.tests.grokkedapp.another         37     37   100%   
    repoze.bfg.tests.routesapp                   1      1   100%   
    repoze.bfg.tests.routesapp.views             4      4   100%   
    repoze.bfg.tests.test_authentication       487    487   100%   
    repoze.bfg.tests.test_authorization        124    124   100%   
    repoze.bfg.tests.test_chameleon_text       161    161   100%   
    repoze.bfg.tests.test_chameleon_zpt        146    146   100%   
    repoze.bfg.tests.test_compat                 7      7   100%   
    repoze.bfg.tests.test_configuration        208    208   100%   
    repoze.bfg.tests.test_encode                47     47   100%   
    repoze.bfg.tests.test_events                59     59   100%   
    repoze.bfg.tests.test_integration          153    153   100%   
    repoze.bfg.tests.test_location              34     34   100%   
    repoze.bfg.tests.test_log                   11     11   100%   
    repoze.bfg.tests.test_paster               110    110   100%   
    repoze.bfg.tests.test_path                 119    119   100%   
    repoze.bfg.tests.test_registry              34     34   100%   
    repoze.bfg.tests.test_renderers            174    174   100%   
    repoze.bfg.tests.test_request              141    141   100%   
    repoze.bfg.tests.test_resource             338    338   100%   
    repoze.bfg.tests.test_router               441    441   100%   
    repoze.bfg.tests.test_scripting             44     44   100%   
    repoze.bfg.tests.test_security             273    273   100%   
    repoze.bfg.tests.test_settings             138    138   100%   
    repoze.bfg.tests.test_static               126    126   100%   
    repoze.bfg.tests.test_testing              488    488   100%   
    repoze.bfg.tests.test_threadlocal           70     70   100%   
    repoze.bfg.tests.test_traversal            904    904   100%   
    repoze.bfg.tests.test_url                  206    206   100%   
    repoze.bfg.tests.test_urldispatch          290    290   100%   
    repoze.bfg.tests.test_view                1379   1379   100%   
    repoze.bfg.tests.test_wsgi                  99     99   100%   
    repoze.bfg.tests.test_zcml                2473   2473   100%   
    repoze.bfg.threadlocal                      27     27   100%   
    repoze.bfg.traversal                       179    179   100%   
    repoze.bfg.url                              65     65   100%   
    repoze.bfg.urldispatch                     117    117   100%   
    repoze.bfg.view                            368    368   100%   
    repoze.bfg.wsgi                             26     26   100%   
    repoze.bfg.zcml                            354    354   100%   
    ----------------------------------------------------------------------
    TOTAL                                    12004  12004   100%   
    ----------------------------------------------------------------------
    Ran 724 tests in 5.627s
    
    OK
