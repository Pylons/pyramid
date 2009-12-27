:mod:`repoze.bfg` Introduction
==============================

:mod:`repoze.bfg` is an open source Python web application framework.
It is inspired by :term:`Zope`, :term:`Pylons`, and :term:`Django`.
It uses the :term:`WSGI` protocol to handle requests and responses.

:mod:`repoze.bfg` is written by Agendaless Consulting and a community
of contributors.  It is developed primarily by people who come from
the world of :term:`Zope` but for whom Zope as a web application
development platform has lost some of its attraction.  Its authors
also have experience developing applications using many other web
frameworks.

The first release of :mod:`repoze.bfg` was made in July of 2008.
Since its first release, it has undergone many improvements, and has
gained features steadily.  Still, it strives to maintain the following
attributes:

Simplicity
  :mod:`repoze.bfg` attempts to be a *"pay only for what you eat"*
  framework in which you can be productive quickly with partial
  knowledge.  We contrast this with *"pay up front for what anyone
  might eventually want to eat"* frameworks, which tend to expect you
  to understand a great many concepts and technologies fully before
  you can be truly productive.  :mod:`repoze.bfg` doesn't force you to
  use any particular technology to produce an application, and we try
  to keep the core set of concepts you need to understand to a
  minimum.

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
  As web developers, we've become accustomed to working in very
  particular ways over the years.  This framework is a canonization of
  practices that "fit our brains".

Trustability
  :mod:`repoze.bfg` is developed conservatively and tested
  exhaustively.  *If it ain't tested, it's broke.* Every release of
  :mod:`repoze.bfg` has 100% unit test converage.

A Sense of Fun
  Developing a :mod:`repoze.bfg` application should not feel foreign
  or "enterprisey".  We like to keep things down-to-earth.

.. index::
   single: similarities to other frameworks

Similarities to Other Web Frameworks
------------------------------------

:mod:`repoze.bfg` was inspired by :term:`Zope`, :term:`Pylons` and
:term:`Django`.

.. sidebar:: Django's Authors Explain Why It Doesn't Use "MVC" Terminology

   Django appears to be a MVC framework, but you call the Controller
   the "view", and the View the "template". How come you don't use the
   standard names?  Well, the standard names are debatable.  In our
   interpretation of MVC, the "view" describes the data that gets
   presented to the user. It's not necessarily how the data looks, but
   which data is presented. The view describes which data you see, not
   how you see it. It's a subtle distinction.  So, in our case, a
   "view" is the Python callback function for a particular URL,
   because that callback function describes which data is presented.
   Furthermore, it's sensible to separate content from presentation -
   which is where templates come in. In Django, a "view" describes
   which data is presented, but a view normally delegates to a
   template, which describes how the data is presented.

The :mod:`repoze.bfg` concept of :term:`traversal` is inspired by
:term:`Zope`.  Additionally, :mod:`repoze.bfg` uses a :term:`Zope
Component Architecture` :term:`application registry` internally, as
does Zope 2, Zope 3, and :term:`Grok`.  Like Zope, :mod:`repoze.bfg`
allows you to create applications which do not need to be forked or
otherwise modified in order to be extended or overridden by a third
party developer.

The :mod:`repoze.bfg` concept of :term:`URL dispatch` is inspired by
the :term:`Routes` system used by :term:`Pylons`.  Like Pylons,
:mod:`repoze.bfg` is mostly policy-free.  It makes no assertions about
which database you should use, and its built-in templating facilities
are only for convenience.  In essence, it only supplies a mechanism to
map URLs to :term:`view` code, along with a convention for calling
those views.  You are free to use third-party components in your
application that fit your needs.  Also like Pylons, :mod:`repoze.bfg`
is dependent upon :term:`WSGI`.

The Django docs explain that Django is not an "MVC"
("model/view/controller") framework in their `FAQ
<http://www.djangoproject.com/documentation/faq/>`_.  The sidebar in
this section describes the Django authors' take on why "MVC"
terminology doesn't match the web very well.  The concepts of
:term:`view` and :term:`model` are used by :mod:`repoze.bfg` as they
would be by Django.

The skeleton code generator of :mod:`repoze.bfg` generates a directory
layout very similar to the directory layout suggested by the `Django
Book <http://www.djangobook.com/>`_ .  

.. index::
   single: differences from other frameworks

Differences from Other Web Frameworks
-------------------------------------

Like :term:`Zope`, the :mod:`repoze.bfg` framework imposes more
*control inversion* upon application developers than other Python
frameworks such as :term:`Pylons`.  For example :mod:`repoze.bfg`
allows you to explicitly resolve a URL to a :term:`context` object
before invoking a :term:`view`.  Pylons and other Python "MVC"
frameworks have no such intermediate step; they resolve a URL directly
to a "controller".  Another example: using the :mod:`repoze.bfg`
security subsystem assumes that you're willing to attach an
:term:`ACL` to a :term:`context` object; the ACL is checked by the
framework itself instead of by user code, and access is permitted or
denied by the framework itself rather than by user code.  Such a task
would typically be performed by user-space decorators in other Python
web frameworks.

Like Zope, but unlike :term:`Pylons` applications or most
:term:`Django` applications, when you build a :mod:`repoze.bfg`
application, if you obey certain constraints, the application you
produce can be reused, modified, re-integrated, or extended by
third-party developers without modification to the original
application itself.  See :ref:`extending_chapter` for more information
about extending or modifying an existing :mod:`repoze.bfg`
application.

:mod:`repoze.bfg` uses a :term:`Zope Component Architecture`
:term:`application registry` under the hood.  However, while a Zope
application developer tends to need to understand concepts such as
"adapters", "utilities", and "interfaces" to create a non-trivial
application, a :mod:`repoze.bfg` application developer isn't required
to understand any of these concepts.  :mod:`repoze.bfg` hides all
interaction with the component architecture registry behind
special-purpose API functions.

Like :term:`Pylons`, but unlike :term:`Zope`, a :mod:`repoze.bfg`
application developer may use completely imperative code to perform
common framework configuration tasks such as adding a view or a route.
In Zope, :term:`ZCML` is typically required for similar purposes.  In
:term:`Grok`, :term:`decorator` objects and class-level declarations
are used for this purpose.  :mod:`repoze.bfg` *supports* :term:`ZCML`
and supports decorator-based configuration, but does not require
either. See :ref:`configuration_narr` for more information.

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

