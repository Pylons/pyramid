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

:mod:`repoze.bfg`'s traversal is inspired by Zope.  :mod:`repoze.bfg`
uses the Zope Component Architecture ("CA") internally, as do Zope 2,
Zope 3, and Grok.  Developers don't interact with the CA very much
during typical development, however; it's mostly used by the framework
developer rather than the application developer.

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

:mod:`repoze.bfg` 's skeleton code generator generates a directory
layout very simliar to the directory layout suggested by the `Django
Book <http://www.djangobook.com/>`_ .  Additionally, as suggested
above, the concepts of :term:`view`, :term:`model` and
:term:`template` are used by :module:`repoze.bfg` as they would be by
Django.

To learn more about the concepts used by :mod:`repoze.bfg`, visit the
:ref:`glossary` for a listing of definitions.
