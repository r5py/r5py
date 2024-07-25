#!/usr/bin/env python3

"""Determine a reasonable memory footprint for the Java virtual machine."""


import psutil
import re
import warnings

from .config import Config
from .warnings import R5pyWarning


__all__ = ["MAX_JVM_MEMORY"]


ABSOLUTE_MINIMUM_MEMORY = 200 * 1024**2  # never grant less than 200 MiB to JVM


config = Config()
config.argparser.add(
    "-m",
    "--max-memory",
    help="""
        Memory limit for the JVM running R5.

        Use % as a suffix to specify a share of total RAM;
        K, M, G, T to specify KiB, MiB, GiB, or TiB, respectively.
        Values without suffix are interpreted as bytes.
    """,
    default="80%",
)


def _share_of_ram(share=0.8, leave_at_least=(2 * 1024**3)):
    """
    Calculate a share of total RAM.

    Arguments
    ---------
    share : float
        Which portion of total RAM to return.
        Default: 0.8
    leave_at_least : float
        How much RAM (in bytes) to leave (for other applications and system) in any case.
        If `total RAM - (total RAM ⨉ share)` is smaller than `leave_at_least`,
        return `total RAM - leave_at_least`, instead.
        Default: 2GiB

    Returns
    -------
    int
        A value in bytes that is close to `share` portion of total RAM.
    """
    total_ram = psutil.virtual_memory().total
    if total_ram * (1.0 - share) > leave_at_least:
        share_of_ram = round(share * total_ram)
    else:
        share_of_ram = round(total_ram - leave_at_least)
    return share_of_ram


def _parse_value_and_unit(value_and_unit, max_unit_length=1):
    """
    Extract value and unit from a string.

    The string is allowed to contain a (non-numeric) unit suffix.
    For instance, input values of `'1M'` or `3.732G` would yield return
    values `(1, 'M')` or `(3.732, 'G')`, respectively.

    Arguments
    ---------
    value_and_unit : str
        Input string (typically passed-through from config
        parameter `--max-memory`).
    max_unit_length : int
        Maximum length in characters of the unit suffix.
        Default: 1

    Returns
    -------
    tuple: a tuple containing
        - value (float): The value extracted from `value_and_unit`.
        - unit (str): The unit extracted from `value_and_unit`.
    """
    matches = re.match(
        (
            "^(?P<value>[0-9]+(\\.[0-9]+)?)"  # value
            f"(?P<unit>[^0-9]){{0,{max_unit_length}}}$"  # unit
        ),
        value_and_unit,
    )
    value = float(matches["value"])
    unit = matches["unit"]

    return value, unit


def _interpret_power_of_two_units(value, unit):
    """
    Convert a value given as value and power-of-two unit into a bytes value.

    Arguments
    ---------
    value : float
        Input value.
    unit : str
        Unit suffix, as specified in IEC 80000-13, e.g., 'K' for kibibyte.

    Returns
    -------
    int:
        interpreted value in bytes
    """
    # the position of each suffix in this string is the unit’s exponent
    # over 1024.
    # Compare https://en.wikipedia.org/wiki/ISO%2FIEC_80000#Part_13:_Information_science_and_technology
    SUFFIXES = " KMGTPEZY"

    if unit is None:
        unit = " "

    if unit not in SUFFIXES:
        raise ValueError(
            f"Could not interpret unit '{unit}'. "
            "Allowed suffixes are 'K', 'M', 'G', 'T', 'P', 'E', 'Z', and 'Y'."
        )

    exponent = SUFFIXES.find(unit)
    value *= 1024**exponent

    return value


def _get_max_memory(max_memory):
    """
    Interpret the config parameter --max-memory.

    Arguments
    ---------

    max_memory : str
        Memory limit for the JVM running R5.

        Use % as a suffix to specify a share of total RAM;
        K, M, G, T suffix specify KiB, MiB, GiB, or TiB, respectively.
        Values without suffix are interpreted as bytes.

    Returns
    -------
    int
        Maximum amount of memory allocated for R5 in bytes.
    """
    try:
        value, unit = _parse_value_and_unit(max_memory)
    except TypeError:
        raise ValueError(f"Could not interpret `--max-memory` ('{max_memory}').")

    if unit == "%":
        value = _share_of_ram(share=(value / 100.0))
    else:
        # convert to bytes
        value = _interpret_power_of_two_units(value, unit)

    max_memory = round(value)

    if max_memory < ABSOLUTE_MINIMUM_MEMORY:
        max_memory = ABSOLUTE_MINIMUM_MEMORY
        warnings.warn(
            f"Requested maximum JVM heap size is too low for R5, "
            f"setting to minimum value {ABSOLUTE_MINIMUM_MEMORY:d} bytes.",
            R5pyWarning,
        )

    return max_memory


MAX_JVM_MEMORY = _get_max_memory(config.arguments.max_memory)
