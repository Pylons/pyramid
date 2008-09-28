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

"""Location support borrowed from ``zope.location``, but without
``zope.security`` support, which is not used by ``repoze.bfg``
"""

import zope.interface
from repoze.bfg.interfaces import ILocation
from zope.proxy import ProxyBase, getProxiedObject, non_overridable
from zope.proxy.decorator import DecoratorSpecificationDescriptor

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
    If ``model`` explicitly provides the
    ``repoze.bfg.interfaces.ILocation`` interface, locate ``model``
    directly set ``model`` 's ``__parent__`` attribute to the
    ``parent`` object (also a model), and its ``__name__`` to the
    supplied ``name`` argument.

    If ``model`` does *not* explicitly provide the
    ``repoze.bfg.interfaces.ILocation`` interface, return a
    ``LocationProxy`` object representing ``model`` with its
    ``__parent__`` attribute assigned to ``parent`` and a ``__name__``
    attribute assigned to ``__name__``.  A ``LocationProxy`` object is
    an unpickleable proxy that can 'stand in' for arbitrary object
    instances.
    """
    if ILocation.providedBy(model):
        if parent is not model.__parent__ or name != model.__name__:
            _locate(model, parent, name)
        return model
    return LocationProxy(model, parent, name)

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

def _locate(model, parent, name=None):
    model.__parent__ = parent
    model.__name__ = name

class ClassAndInstanceDescr(object):

    def __init__(self, *args):
        self.funcs = args

    def __get__(self, inst, cls):
        if inst is None:
            return self.funcs[1](cls)
        return self.funcs[0](inst)

class LocationProxy(ProxyBase):
    """Location-object proxy

    This is a non-picklable proxy that can be put around objects that
    don't implement `ILocation`.
    """

    zope.interface.implements(ILocation)

    __slots__ = '__parent__', '__name__'
    __safe_for_unpickling__ = True

    def __new__(self, ob, container=None, name=None):
        return ProxyBase.__new__(self, ob)

    def __init__(self, ob, container=None, name=None):
        ProxyBase.__init__(self, ob)
        self.__parent__ = container
        self.__name__ = name

    @non_overridable
    def __reduce__(self, proto=None):
        raise TypeError("Not picklable")

    __doc__ = ClassAndInstanceDescr(
        lambda inst: getProxiedObject(inst).__doc__,
        lambda cls, __doc__ = __doc__: __doc__,
        )

    __reduce_ex__ = __reduce__

    __providedBy__ = DecoratorSpecificationDescriptor()

