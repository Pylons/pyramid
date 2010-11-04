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

To override static resources using a "search path" much like a set of
skin layers, :mod:`pyramid` provides the concept of
:term:`resource` overrides.  See :ref:`overriding_resources_section`
for more information about resource overrides.

While there is no analogue to a skin layer search path for locating
Python code (as opposed to resources), :term:`view` code combined with
differing :term:`predicate` arguments can provide a good deal of
the same sort of behavior.

