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
user interface.  You *could* build a CMF-like layer on top of
:mod:`repoze.bfg` (as CMF is built on Zope) but none currently exists.
For those sorts of high-extensibility, highly-regularized-UI systems,
CMF is still the better choice.

:mod:`repoze.bfg` (and other more lightweight systems) is often a
better choice when you're building the a user interface from scratch,
which often happens when the paradigms of some CMF-provided user
interface don't match the requirements of an application very closely.
Even so, a good number of developers tend to use CMF even when they do
start an application for which they need to build a UI from scratch,
because CMF happens to provide other helpful services, such as types,
skins, and workflow; this tutorial is for those sorts of developers
and projects.

.. toctree::
   :maxdepth: 2

   content.rst
   catalog.rst
   skins.rst
   actions.rst
   workflow.rst
   missing.rst



