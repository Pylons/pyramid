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
ZCML.

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
