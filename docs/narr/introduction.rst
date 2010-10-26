.. index::
   single: Agendaless Consulting
   single: Pylons
   single: Django
   single: Zope
   single: frameworks vs. libraries
   single: framework

:mod:`pyramid` Introduction
==============================

If they are judged only by differences in user interface, most web
applications seem to have very little in common with each other. For
example, a web page served by one web application might be a
representation of the contents of an accounting ledger, while a web
page served by another application might be a listing of songs.  These
applications probably won't serve the same set of customers.  However,
although they're not very similar on the surface, both a
ledger-serving application and a song-serving application can be
written using :mod:`pyramid`.

:mod:`pyramid` is a very general open source Python web
*framework*.  As a framework, its primary job is to make it easier for
a developer to create an arbitrary web application.  The type of
application being created isn't really important; it could be a
spreadsheet, a corporate intranet, or an "oh-so-Web-2.0" social
networking platform.  :mod:`pyramid` is general enough that it can
be used in a wide variety of circumstances.

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

The first release of the predecessor to :mod:`pyramid` (named
:mod:`repoze.bfg`) was made in July of 2008.  Since its first release,
we've tried to ensure that it maintains the following attributes:

Simplicity
  :mod:`pyramid` attempts to be a *"pay only for what you eat"*
  framework which delivers results even if you have only partial
  knowledge.  Other frameworks may expect you to understand many
  concepts and technologies fully before you can be truly productive.
  :mod:`pyramid` doesn't force you to use any particular technology
  to produce an application, and we try to keep the core set of
  concepts you need to understand to a minimum.

A Sense of Fun
  Developing a :mod:`pyramid` application should not feel
  "enterprisey".  We like to keep things down-to-earth.

Minimalism
  :mod:`pyramid` provides only the very basics: *URL to code
  mapping*, *templating*, *security*, and *resources*.  There is not
  much more to the framework than these pieces: you are expected to
  provide the rest.

Documentation
  Because :mod:`pyramid` is minimal, it's relatively easy to keep
  its documentation up-to-date, which is helpful to bring new
  developers up to speed.  It's our goal that nothing remain
  undocumented about :mod:`pyramid`.

Speed
  :mod:`pyramid` is faster than many other popular Python web
  frameworks for common tasks such as templating and simple response
  generation.  The "hardware is cheap" mantra has its limits when
  you're responsible for managing a great many machines: the fewer you
  need, the less pain you'll have.

Familiarity
  The :mod:`pyramid` framework is a canonization of practices that
  "fit the brains" of its authors.

Trustability
  :mod:`pyramid` is developed conservatively and tested
  exhaustively.  *If it ain't tested, it's broke.* Every release of
  :mod:`pyramid` has 100% statement coverage via unit tests.

Openness
  Like :term:`Python`, the :mod:`pyramid` software is distributed
  under a `permissive open source license
  <http://repoze.org/license.html>`_.

.. index::
   single: Repoze
   single: Agendaless Consulting
   single: repoze namespace package

What Is Pylons?
---------------

:mod:`pyramid` is a member of the collection of software published
under the :term:`Pylons` "brand".  :term:`Pylons` software is written
by a loose-knit community of contributors.  The `Pylons website
<http://pylonshq.com>`_ describes the Pylons brand in more detail.

.. index::
   single: pyramid and other frameworks
   single: Zope
   single: Pylons
   single: Django
   single: MVC

:mod:`pyramid` and Other Web Frameworks
------------------------------------------

Until the end of 2010, :mod:`pyramid` was known as :mod:`repoze.bfg`;
it was merged into the Pylons project at the end of 2010.

:mod:`pyramid` was inspired by :term:`Zope`, :term:`Pylons` (version
1.0) and :term:`Django`.  As a result, :mod:`pyramid` borrows several
concepts and features from each, combining them into a unique web
framework.

Many features of :mod:`pyramid` trace their origins back to
:term:`Zope`.  Like Zope applications, :mod:`pyramid` applications
can be configured via a set of declarative configuration files.  Like
Zope applications, :mod:`pyramid` applications can be easily
extended: if you obey certain constraints, the application you produce
can be reused, modified, re-integrated, or extended by third-party
developers without forking the original application.  The concepts of
:term:`traversal` and declarative security in :mod:`pyramid` were
pioneered first in Zope.

The :mod:`pyramid` concept of :term:`URL dispatch` is inspired by the
:term:`Routes` system used by :term:`Pylons` version 1.0.  Like Pylons
version 1.0, :mod:`pyramid` is mostly policy-free.  It makes no
assertions about which database you should use, and its built-in
templating facilities are included only for convenience.  In essence,
it only supplies a mechanism to map URLs to :term:`view` code, along
with a set of conventions for calling those views.  You are free to
use third-party components that fit your needs in your applications.

The concepts of :term:`view` and :term:`model` are used by
:mod:`pyramid` mostly as they would be by Django.
:mod:`pyramid` has a documentation culture more like Django's than
like Zope's.

Like :term:`Pylons` version 1.0, but unlike :term:`Zope`, a
:mod:`pyramid` application developer may use completely imperative
code to perform common framework configuration tasks such as adding a
view or a route.  In Zope, :term:`ZCML` is typically required for
similar purposes.  In :term:`Grok`, a Zope-based web framework,
:term:`decorator` objects and class-level declarations are used for
this purpose.  :mod:`pyramid` supports :term:`ZCML` and
decorator-based configuration, but does not require either. See
:ref:`configuration_narr` for more information.

Also unlike :term:`Zope` and unlike other "full-stack" frameworks such
as :term:`Django`, :mod:`pyramid` makes no assumptions about which
persistence mechanisms you should use to build an application.  Zope
applications are typically reliant on :term:`ZODB`; :mod:`pyramid`
allows you to build :term:`ZODB` applications, but it has no reliance
on the ZODB software.  Likewise, :term:`Django` tends to assume that
you want to store your application's data in a relational database.
:mod:`pyramid` makes no such assumption; it allows you to use a
relational database but doesn't encourage or discourage the decision.

Other Python web frameworks advertise themselves as members of a class
of web frameworks named `model-view-controller
<http://en.wikipedia.org/wiki/Model–view–controller>`_ frameworks.
Insofar as this term has been claimed to represent a class of web
frameworks, :mod:`pyramid` also generally fits into this class.

.. sidebar:: You Say :mod:`pyramid` is MVC, But Where's The Controller?

   The :mod:`pyramid` authors believe that the MVC pattern just
   doesn't really fit the web very well. In a :mod:`pyramid`
   application, there are models, which store data, and views, which
   present the data stored in models.  However, no facility provided
   by the framework actually maps to the concept of a "controller".
   So :mod:`pyramid` is actually an "MV" framework rather than an
   "MVC" framework.  "MVC", however, is close enough as a general
   classification moniker for purposes of comparison with other web
   frameworks.

