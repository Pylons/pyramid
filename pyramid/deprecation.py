from zope.deprecation import deprecated  # noqa, internal api

class RemoveInPyramid19Warning(DeprecationWarning):
    pass

class RemoveInPyramid110Warning(DeprecationWarning):
    pass

RemovedInNextVersionWarning = RemoveInPyramid19Warning
