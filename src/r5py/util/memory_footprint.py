#!/usr/bin/env python3

"""Determine a reasonable memory footprint for the Java virtual machine."""


import psutil
import re
import warnings

from . import config


__all__ = ["MAX_JVM_MEMORY"]


ABSOLUTE_MINIMUM_MEMORY = 200 * 2**20  # never grant less than 200 MiB to JVM


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
arguments = config.arguments()


def _share_of_ram(share=0.8, leave_at_least=(2 * (2**30))):
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
    Extract value and unit from a string containing a possible
    (non-numeric) unit suffix.

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
        "^(?P<value>[0-9]+(\\.[0-9]+)?)"
        f"(?P<unit>[^0-9]){{0,{max_unit_length}}}$",
        value_and_unit
    )
    value = float(matches["value"])
    unit = matches["unit"]

    return value, unit


def _parse_max_memory(max_memory):
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
        raise ValueError(
            f"Could not interpret `--max-memory` ('{max_memory}')."
        )

    if unit is not None and unit not in "%KMGT":
        raise ValueError(
            f"Could not interpret unit '{unit}' (`--max-memory`)."
            "Allowed suffixes are '%', 'K', 'M', 'G', and 'T'."
        )

    if unit == "%":
        max_memory = _share_of_ram(share=(value / 100.0))
    else:
        # convert to bytes
        if unit is None:
            value *= 2**0
        elif unit == "K":
            value *= 2**10
        elif unit == "M":
            value *= 2**20
        elif unit == "G":
            value *= 2**30
        elif unit == "T":
            value *= 2**40

    max_memory = round(value)

    if max_memory < ABSOLUTE_MINIMUM_MEMORY:
        max_memory = ABSOLUTE_MINIMUM_MEMORY
        warnings.warn(
            f"Requested maximum JVM heap size is too low for R5, "
            f"setting to minimum value {ABSOLUTE_MINIMUM_MEMORY:d} MiB.",
            RuntimeWarning,
        )

    return max_memory


MAX_JVM_MEMORY = _parse_max_memory(arguments.max_memory)
