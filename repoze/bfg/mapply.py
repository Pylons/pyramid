##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Provide an apply-like facility that works with any mapping object
"""

def mapply(object,
           positional=(),
           keyword={},
           maybe=True,
           ):

    if hasattr(object,'__bases__'): # the object is a class
        raise TypeError('Cannot publish class %s' % object)

    f = object
    im = False

    if hasattr(f, 'im_func'):
        im = True
    elif not hasattr(f, 'func_defaults'):
        if hasattr(f, '__call__'):
            f = f.__call__
            if hasattr(f, 'im_func'):
                im = True
            elif not hasattr(f, 'func_defaults') and maybe:
                return object
        elif maybe:
            return object

    if im:
        f = f.im_func
        c = f.func_code
        defaults = f.func_defaults
        names = c.co_varnames[1:c.co_argcount]
    else:
        defaults = f.func_defaults
        c = f.func_code
        names = c.co_varnames[:c.co_argcount]

    nargs = len(names)
    if positional:
        positional = list(positional)
        if len(positional) > nargs:
            raise TypeError('too many arguments')
        args = positional
    else:
        args = []

    get = keyword.get
    nrequired = len(names) - (len(defaults or ()))
    for index in range(len(args), len(names)):
        name = names[index]
        v = get(name, args)
        if v is args:
            if index < nrequired:
                raise TypeError('Argument %s was omitted' % name)
            else:
                v = defaults[index-nrequired]
        args.append(v)

    args = tuple(args)
    return object(*args)
