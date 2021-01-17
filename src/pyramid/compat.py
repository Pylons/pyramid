import warnings
from pyramid._compat import *


warnings.warn(
    '`pyramid._compat` is deprecated and will be removed in Pyramid 2.0.  The '
    'functionality is no longer necessary, as Pyramid 2.0 drops support for '
    'Python 2.',
    DeprecationWarning,
)
