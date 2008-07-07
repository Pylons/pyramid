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

import zope.interface
from zope.proxy import ProxyBase
from zope.proxy import getProxiedObject
from zope.proxy import non_overridable
from zope.proxy.decorator import DecoratorSpecificationDescriptor
from repoze.bfg.interfaces import ILocation

class Location(object):
    """Stupid mix-in that defines `__parent__` and `__name__` attributes."""

    zope.interface.implements(ILocation)

    __parent__ = __name__ = None

def locate(object, parent, name=None):
    """Locate an object in another

    This method should only be called from trusted code, because it
    sets attributes that are normally unsettable.
    """

    object.__parent__ = parent
    object.__name__ = name


def located(object, parent, name=None):
    """Locate an object in another and return it.

    If the object does not provide ILocation a LocationProxy is returned.

    """
    if ILocation.providedBy(object):
        if parent is not object.__parent__ or name != object.__name__:
            locate(object, parent, name)
        return object
    return LocationProxy(object, parent, name)


def LocationIterator(object):
    while object is not None:
        yield object
        object = getattr(object, '__parent__', None)


def inside(l1, l2):
    """Is l1 inside l2

    L1 is inside l2 if l2 is an ancestor of l1.

    """
    while l1 is not None:
        if l1 is l2:
            return True
        l1 = l1.__parent__

    return False


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

