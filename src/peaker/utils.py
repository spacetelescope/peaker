"""Utility functions."""

import numpy as np


# bytes pretty-printing
UNITS_MAPPING = [
    (1<<50, "PB"),
    (1<<40, "TB"),
    (1<<30, "GB"),
    (1<<20, "MB"),
    (1<<10, "KB"),
    (1, "bytes"),
]


def convert_units(bytes_arr, desired_units=None):
    """
    Converts bytes into easily readable units or desired units.
    
    Parameters
    ----------
    bytes_arr : array or float
        Numbers in bytes to convert.
    desired_units : str or None
        Desired units to convert.

    Returns
    -------
    converted : array or float
        Converted bytes.
    units : str
        Units of converted bytes.
    """
    for factor, units in UNITS_MAPPING:
        converted = bytes_arr / factor
        if desired_units is not None:
            if units == desired_units:
                break
        else:
            median = np.median(converted)
            if median >= 1.0:
                break
    return converted, units
