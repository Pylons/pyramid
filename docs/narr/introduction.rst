.. index::
   single: Agendaless Consulting
   single: Pylons
   single: Django
   single: Zope
   single: frameworks vs. libraries
   single: framework

:app:`Pyramid` Introduction
==============================

:app:`Pyramid` is a general, open source, Python web application development
*framework*. Its primary goal is to make it easier for a developer to create
web applications. The type of application being created could be a
spreadsheet, a corporate intranet, or a social networking platform; Pyramid's
generality enables it to be used to build an unconstrained variety of web
applications.

.. sidebar:: Frameworks vs. Libraries

   A *framework* differs from a *library* in one very important way:
   library code is always *called* by code that you write, while a
   framework always *calls* code that you write.  Using a set of
   libraries to create an application is usually easier than using a
   framework initially, because you can choose to cede control to
   library code you have not authored very selectively. But when you
   use a framework, you are required to cede a greater portion of
   control to code you have not authored: code that resides in the
   framework itself.  You needn't use a framework at all to create a
   web application using Python.  A rich set of libraries already
   exists for the platform.  In practice, however, using a framework
   to create an application is often more practical than rolling your
   own via a set of libraries if the framework provides a set of
   facilities that fits your application requirements.

The first release of Pyramid's predecessor (named :mod:`repoze.bfg`) was made
in July of 2008. We have worked hard to ensure that Pyramid continues to
follow the design and engineering principles that we consider to be the core
characteristics of a successful framework:

Simplicity
  :app:`Pyramid` takes a *"pay only for what you eat"* approach.  This means
  that you can get results even if you have only a partial understanding of
  :app:`Pyramid`.  It doesn’t force you to use any particular technology to
  produce an application, and we try to keep the core set of concepts that
  you need to understand to a minimum.

Minimalism
  :app:`Pyramid` concentrates on providing fast, high-quality solutions to
  the fundamental problems of creating a web application: the mapping of URLs
  to code, templating, security and serving static assets. We consider these
  to be the core activities that are common to nearly all web applications.

Documentation
  Pyramid's minimalism means that it is relatively easy for us to maintain
  extensive and up-to-date documentation. It is our goal that no aspect of
  Pyramid remains undocumented.

Speed
  :app:`Pyramid` is designed to provide noticeably fast execution for common
  tasks such as templating and simple response generation. Although the
  “hardware is cheap” mantra may appear to offer a ready solution to speed
  problems, the limits of this approach become painfully evident when one
  finds him or herself responsible for managing a great many machines.

Reliability
  :app:`Pyramid` is developed conservatively and tested exhaustively. Where
  Pyramid source code is concerned, our motto is: "If it ain’t tested, it’s
  broke". Every release of Pyramid has 100% statement coverage via unit
  tests.

Openness
  As with Python, the Pyramid software is distributed under a `permissive
  open source license <http://repoze.org/license.html>`_.

.. index::
   single: Pylons
   single: Agendaless Consulting
   single: repoze namespace package

What Is The Pylons Project?
---------------------------

:app:`Pyramid` is a member of the collection of software published under the
Pylons Project.  Pylons software is written by a loose-knit community of
contributors.  The `Pylons Project website <http://docs.pylonsproject.org>`_
includes details about how :app:`Pyramid` relates to the Pylons Project.

.. index::
   single: pyramid and other frameworks
   single: Zope
   single: Pylons
   single: Django
   single: MVC

:app:`Pyramid` and Other Web Frameworks
------------------------------------------

Until the end of 2010, :app:`Pyramid` was known as :mod:`repoze.bfg`; it was
merged into the Pylons project as :app:`Pyramid` in November of that year.

:app:`Pyramid` was inspired by :term:`Zope`, :term:`Pylons` (version
1.0) and :term:`Django`.  As a result, :app:`Pyramid` borrows several
concepts and features from each, combining them into a unique web
framework.

Many features of :app:`Pyramid` trace their origins back to
:term:`Zope`.  Like Zope applications, :app:`Pyramid` applications
can be configured via a set of declarative configuration files.  Like
Zope applications, :app:`Pyramid` applications can be easily
extended: if you obey certain constraints, the application you produce
can be reused, modified, re-integrated, or extended by third-party
developers without forking the original application.  The concepts of
:term:`traversal` and declarative security in :app:`Pyramid` were
pioneered first in Zope.

The :app:`Pyramid` concept of :term:`URL dispatch` is inspired by the
:term:`Routes` system used by :term:`Pylons` version 1.0.  Like Pylons
version 1.0, :app:`Pyramid` is mostly policy-free.  It makes no
assertions about which database you should use, and its built-in
templating facilities are included only for convenience.  In essence,
it only supplies a mechanism to map URLs to :term:`view` code, along
with a set of conventions for calling those views.  You are free to
use third-party components that fit your needs in your applications.

The concept of :term:`view` is used by :app:`Pyramid` mostly as it would be
by Django.  :app:`Pyramid` has a documentation culture more like Django's
than like Zope's.

Like :term:`Pylons` version 1.0, but unlike :term:`Zope`, a
:app:`Pyramid` application developer may use completely imperative
code to perform common framework configuration tasks such as adding a
view or a route.  In Zope, :term:`ZCML` is typically required for
similar purposes.  In :term:`Grok`, a Zope-based web framework,
:term:`decorator` objects and class-level declarations are used for
this purpose.  :app:`Pyramid` supports :term:`ZCML` and
decorator-based configuration, but does not require either. See
:ref:`configuration_narr` for more information.

Also unlike :term:`Zope` and unlike other "full-stack" frameworks such
as :term:`Django`, :app:`Pyramid` makes no assumptions about which
persistence mechanisms you should use to build an application.  Zope
applications are typically reliant on :term:`ZODB`; :app:`Pyramid`
allows you to build :term:`ZODB` applications, but it has no reliance
on the ZODB software.  Likewise, :term:`Django` tends to assume that
you want to store your application's data in a relational database.
:app:`Pyramid` makes no such assumption; it allows you to use a
relational database but doesn't encourage or discourage the decision.

Other Python web frameworks advertise themselves as members of a class
of web frameworks named `model-view-controller
<http://en.wikipedia.org/wiki/Model–view–controller>`_ frameworks.
Insofar as this term has been claimed to represent a class of web
frameworks, :app:`Pyramid` also generally fits into this class.

.. sidebar:: You Say :app:`Pyramid` is MVC, But Where's The Controller?

   The :app:`Pyramid` authors believe that the MVC pattern just doesn't
   really fit the web very well. In a :app:`Pyramid` application, there is a
   resource tree, which represents the site structure, and views, which tend
   to present the data stored in the resource tree and a user-defined "domain
   model".  However, no facility provided *by the framework* actually
   necessarily maps to the concept of a "controller" or "model".  So if you
   had to give it some acronym, I guess you'd say :app:`Pyramid` is actually
   an "RV" framework rather than an "MVC" framework.  "MVC", however, is
   close enough as a general classification moniker for purposes of
   comparison with other web frameworks.
