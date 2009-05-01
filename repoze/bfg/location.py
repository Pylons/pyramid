##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""Location support loosely based from ``zope.location``, but without
``zope.security`` support or proxy support, neither of which is used
by ``repoze.bfg``
"""

def inside(model1, model2):
    """Is ``model1`` 'inside' ``model2``?  Return ``True`` if so, else
    ``False``.

    ``model1`` is 'inside' ``model2`` if ``model2`` is a `location
    ancestor` of ``model1``.  It is a location ancestor if its parent
    (or one of its parent's parents, etc.) is an ancestor.
    """
    while model1 is not None:
        if model1 is model2:
            return True
        model1 = model1.__parent__

    return False

def locate(model, parent, name=None):
    """
    Directly set ``model`` 's ``__parent__`` attribute to the
    ``parent`` object (also a model), and its ``__name__`` to the
    supplied ``name`` argument, and return the model.
    """
    model.__parent__ = parent
    model.__name__ = name
    return model

def lineage(model):
    """
    Return a generator representing the model lineage.  The generator
    first returns ``model`` unconditionally.  Then, if ``model``
    supplies a ``__parent__`` attribute, return the object represented
    by ``model.__parent__``.  If *that* object has a ``__parent__``
    attribute, return that object's parent, and so on, until the
    object being inspected either has no ``__parent__`` attribute or
    which has a ``__parent__`` attribute of ``None``.  For example, if
    the object tree is::

      thing1 = Thing()
      thing2 = Thing()
      thing2.__parent__ = thing1

    Calling ``lineage(thing2)`` will return a generator.  When we turn
    it into a list, we will get::
    
      list(lineage(thing2))
      [ <Thing object at thing2>, <Thing object at thing1> ]
    """
    while model is not None:
        yield model
        model = getattr(model, '__parent__', None)

