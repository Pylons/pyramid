.. index::
   single: Agendaless Consulting
   single: Pylons
   single: Django
   single: Zope
   single: frameworks vs. libraries
   single: framework

:mod:`repoze.bfg` Introduction
==============================

If they are judged only by differences in user interface, most web
applications seem to have very little in common with each other. For
example, a web page served by one web application might be a
representation of the contents of an accounting ledger, while a web
page served by another application might be a listing of songs.  These
applications probably won't serve the same set of customers.  However,
although they're not very similar on the surface, both a
ledger-serving application and a song-serving application can be
written using :mod:`repoze.bfg`.

:mod:`repoze.bfg` is a very general open source Python web
*framework*.  As a framework, its primary job is to make it easier for
a developer to create an arbitrary web application.  The type of
application being created isn't really important; it could be a
spreadsheet, a corporate intranet, or an "oh-so-Web-2.0" social
networking platform.  :mod:`repoze.bfg` is general enough that it can
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

The first release of :mod:`repoze.bfg` was made in July of 2008.
Since its first release, we've tried to ensure that it maintains the
following attributes:

Simplicity
  :mod:`repoze.bfg` attempts to be a *"pay only for what you eat"*
  framework which delivers results even if you have only partial
  knowledge.  Other frameworks may expect you to understand many
  concepts and technologies fully before you can be truly productive.
  :mod:`repoze.bfg` doesn't force you to use any particular technology
  to produce an application, and we try to keep the core set of
  concepts you need to understand to a minimum.

A Sense of Fun
  Developing a :mod:`repoze.bfg` application should not feel
  "enterprisey".  We like to keep things down-to-earth.

Minimalism
  :mod:`repoze.bfg` provides only the very basics: *URL to code
  mapping*, *templating*, *security*, and *resources*.  There is not
  much more to the framework than these pieces: you are expected to
  provide the rest.

Documentation
  Because :mod:`repoze.bfg` is minimal, it's relatively easy to keep
  its documentation up-to-date, which is helpful to bring new
  developers up to speed.  It's our goal that nothing remain
  undocumented about :mod:`repoze.bfg`.

Speed
  :mod:`repoze.bfg` is faster than many other popular Python web
  frameworks for common tasks such as templating and simple response
  generation.  The "hardware is cheap" mantra has its limits when
  you're responsible for managing a great many machines: the fewer you
  need, the less pain you'll have.

Familiarity
  The :mod:`repoze.bfg` framework is a canonization of practices that
  "fit the brains" of its authors.

Trustability
  :mod:`repoze.bfg` is developed conservatively and tested
  exhaustively.  *If it ain't tested, it's broke.* Every release of
  :mod:`repoze.bfg` has 100% statement coverage via unit tests.

Openness
  Like :term:`Python`, the :mod:`repoze.bfg` software is distributed
  under a `permissive open source license
  <http://repoze.org/license.html>`_.

This book usually refers to the framework by its full package name,
:mod:`repoze.bfg`.  However, it is often referred to as just "BFG"
(the "repoze-dot" dropped) in conversation.

.. index::
   single: Repoze
   single: Agendaless Consulting
   single: repoze namespace package

What Is Repoze?
---------------

:mod:`repoze.bfg` is a member of the collection of software published
under the :term:`Repoze` "brand".  :term:`Repoze` software is written
by :term:`Agendaless Consulting` and a community of contributors.  The
`Repoze website <http://repoze.org>`_ describes the Repoze brand in
more detail.  Software authored that uses this brand is usually placed
into a ``repoze`` namespace package.  This namespace consists of a
number of packages.  Each package is useful in isolation.  The
``repoze`` namespace package represents that the software is written
by a notional community rather than representing a collection of
software that is meant to be used as a unit.  For example, even though
``repoze.bfg`` shares the same namespace as another popular Repoze
package, ``repoze.who``, these two packages are otherwise unrelated
and can be used separately.

.. index::
   single: repoze.bfg and other frameworks
   single: Zope
   single: Pylons
   single: Django
   single: MVC

:mod:`repoze.bfg` and Other Web Frameworks
------------------------------------------

:mod:`repoze.bfg` was inspired by :term:`Zope`, :term:`Pylons` and
:term:`Django`.  As a result, :mod:`repoze.bfg` borrows several
concepts and features from each, combining them into a unique web
framework.

Many features of :mod:`repoze.bfg` trace their origins back to
:term:`Zope`.  Like Zope applications, :mod:`repoze.bfg` applications
can be configured via a set of declarative configuration files.  Like
Zope applications, :mod:`repoze.bfg` applications can be easily
extended: if you obey certain constraints, the application you produce
can be reused, modified, re-integrated, or extended by third-party
developers without forking the original application.  The concepts of
:term:`traversal` and declarative security in :mod:`repoze.bfg` were
pioneered first in Zope.

The :mod:`repoze.bfg` concept of :term:`URL dispatch` is inspired by
the :term:`Routes` system used by :term:`Pylons`.  Like Pylons,
:mod:`repoze.bfg` is mostly policy-free.  It makes no assertions about
which database you should use, and its built-in templating facilities
are included only for convenience.  In essence, it only supplies a
mechanism to map URLs to :term:`view` code, along with a set of
conventions for calling those views.  You are free to use third-party
components that fit your needs in your applications.

The concepts of :term:`view` and :term:`model` are used by
:mod:`repoze.bfg` mostly as they would be by Django.
:mod:`repoze.bfg` has a documentation culture more like Django's than
like Zope's.

Like :term:`Pylons`, but unlike :term:`Zope`, a :mod:`repoze.bfg`
application developer may use completely imperative code to perform
common framework configuration tasks such as adding a view or a route.
In Zope, :term:`ZCML` is typically required for similar purposes.  In
:term:`Grok`, a Zope-based web framework, :term:`decorator` objects
and class-level declarations are used for this purpose.
:mod:`repoze.bfg` supports :term:`ZCML` and decorator-based
configuration, but does not require either. See
:ref:`configuration_narr` for more information.

Also unlike :term:`Zope` and unlike other "full-stack" frameworks such
as :term:`Django`, :mod:`repoze.bfg` makes no assumptions about which
persistence mechanisms you should use to build an application.  Zope
applications are typically reliant on :term:`ZODB`; :mod:`repoze.bfg`
allows you to build :term:`ZODB` applications, but it has no reliance
on the ZODB software.  Likewise, :term:`Django` tends to assume that
you want to store your application's data in a relational database.
:mod:`repoze.bfg` makes no such assumption; it allows you to use a
relational database but doesn't encourage or discourage the decision.

Other Python web frameworks advertise themselves as members of a class
of web frameworks named `model-view-controller
<http://en.wikipedia.org/wiki/Model–view–controller>`_ frameworks.
Insofar as this term has been claimed to represent a class of web
frameworks, :mod:`repoze.bfg` also generally fits into this class.

.. sidebar:: You Say BFG is MVC, But Where's The Controller?

   The :mod:`repoze.bfg` authors believe that the MVC pattern just
   doesn't really fit the web very well. In a :mod:`repoze.bfg`
   application, there are models, which store data, and views, which
   present the data stored in models.  However, no facility provided
   by the framework actually maps to the concept of a "controller".
   So :mod:`repoze.bfg` is actually an "MV" framework rather than an
   "MVC" framework.  "MVC", however, is close enough as a general
   classification moniker for purposes of comparison with other web
   frameworks.

