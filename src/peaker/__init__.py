# Licensed under a 3-clause BSD style license - see LICENSE.rst

try:
    from ._version import *
except ImportError:
    __version__ = ''

# Expose subpackage API at package level.
from .peaker import *  # noqa
