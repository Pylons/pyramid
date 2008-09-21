Converting an Existing Zope/CMF Application to :mod:`repoze.bfg`
================================================================

The Zope `Content Management Framework
<http://www.zope.org/Products/CMF/>`_ (aka CMF) is a layer on top of
:term:`Zope` 2 that provides facilities for creating content-driven
websites.  It's reasonably easy to convert a modern Zope/CMF
application to :mod:`repoze.bfg`.

The main difference between CMF and :mod:`repoze.bfg` is that
:mod:`repoze.bfg` does not advertise itself as a system into which you
can plug arbitrary "packages" that extend a system-supplied management
user interface.  For those sorts of high-extensibility,
highly-regularized-UI systems, CMF is still the better choice.

:mod:`repoze.bfg` (and other more lightweight systems) are often a
better choice when you're building the a user interface from scratch,
which often happens when the paradigms of the system-provided user
interface don't match the requirements of an application very closely.
Despite the mismatch, a good number of developers tend to use CMF even
when the UI requirements aren't a very good fit, because it happens to
provide other helpful services, such as types and skins; this tutorial
is for those sorts of developers.

Missing:

   templates.rst
   forms.rst
   workflow.rst
   membership.rst
   discussions.rst
   syndication.rst
   dublincore.rst

.. toctree::
   :maxdepth: 2

   content.rst
   catalog.rst
   skins.rst
   actions.rst


