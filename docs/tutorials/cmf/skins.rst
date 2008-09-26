.. _skins_chapter:

=====
Skins
=====

In CMF, a "skin layer" is defined as a collection of templates and
code (Python scripts, DTML methods, etc) that can be activated and
deactivated within a particular setup.  A collection of active "skin
layers" grouped in a particular order forms a "skin".  "Add-on" CMF
products often provide skin layers that are activated within a
particular skin to provide the site with additional features.

:mod:`repoze.bfg` itself has no such concept, and no package provides
a direct replacement, but bfg :term:`view` code combined with
differing :term:`request type` attributes can provide a good deal of
the same sort of behavior.  The `repoze.skins
<http://svn.repoze.org/repoze.skins/>`_ package is an attempt to allow
directories on disk to represent collections of templates, each of
which can be thought of as a minimal skin.


