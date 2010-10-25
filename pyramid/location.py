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

def inside(model1, model2):
    """Is ``model1`` 'inside' ``model2``?  Return ``True`` if so, else
    ``False``.

    ``model1`` is 'inside' ``model2`` if ``model2`` is a
    :term:`lineage` ancestor of ``model1``.  It is a lineage ancestor
    if its parent (or one of its parent's parents, etc.) is an
    ancestor.
    """
    while model1 is not None:
        if model1 is model2:
            return True
        model1 = model1.__parent__

    return False

def lineage(model):
    """
    Return a generator representing the :term:`lineage` of the
    :term:`model` object implied by the ``model`` argument.  The
    generator first returns ``model`` unconditionally.  Then, if
    ``model`` supplies a ``__parent__`` attribute, return the object
    represented by ``model.__parent__``.  If *that* object has a
    ``__parent__`` attribute, return that object's parent, and so on,
    until the object being inspected either has no ``__parent__``
    attribute or which has a ``__parent__`` attribute of ``None``.
    For example, if the object tree is::

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
        # The common case is that the AttributeError exception below
        # is exceptional as long as the developer is a "good citizen"
        # who has a root object with a __parent__ of None.  Using an
        # exception here instead of a getattr with a default is an
        # important micro-optimization, because this function is
        # called in any non-trivial application over and over again to
        # generate URLs and paths.
        try:
            model = model.__parent__
        except AttributeError:
            model = None

