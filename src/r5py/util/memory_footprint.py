#!/usr/bin/env python3

"""Determine a reasonable memory footprint for the Java virtual machine."""


import psutil
import re
import warnings

from . import config


__all__ = ["MAX_JVM_MEMORY"]


ABSOLUTE_MINIMUM_MEMORY = 200  # never grant less than 200 MiB to JVM


config.argparser.add(
    "-m",
    "--max-memory",
    help="""
        Memory limit for the JVM running R5.

        Use % as a suffix to specify a share of total RAM;
        K, M, G, T to specify KiB, MiB, GiB, or TiB, respectively.
        Values are rounded to the closest MiB.
        Values without suffix will raise an error.
    """,
    default="80%",
)
arguments = config.arguments()


def share_of_ram(share=0.8, leave_at_least=(2 * (2**10))):
    """
    Calculate a share of total RAM.

    Arguments
    ---------
    share : float
        Which share of total RAM to calculate.
        Default: 0.8
    leave_at_least : float
        How much RAM in MiB to leave in any case.
        If `total RAM - (total RAM ⨉ share)` is smaller than `leave_at_least`,
        return `total RAM - leave_at_least`, instead.
        Default: 2GiB

    Returns
    -------
    float
        A value in MiB that is close to `share` portion of total RAM.
    """
    total_ram = psutil.virtual_memory().total / (2**20)
    if total_ram * (1.0 - share) > leave_at_least:
        share_of_ram = round(share * total_ram)
    else:
        share_of_ram = round(total_ram - leave_at_least)
    return share_of_ram


def parse_max_memory_string(max_memory):
    """
    Extract maximum memory value and unit from text input.
    """
    try:
        matches = re.match(
            r"(?P<value>[0-9]+(\.[0-9]+)?)(?P<unit>[%KMGT])?", max_memory
        )
        value = float(matches["value"])
        unit = matches["unit"]

        if unit is None:
            raise ValueError(
                f"Could not interpret the memory unit from --max-memory."
                f"The suffix for --max-memory should be '%', 'K', 'M', 'G' or 'T'."
                f"For example to allocate five gigabytes of memory, use: '5G'"
            )
        return value, unit
    except TypeError:
        raise ValueError(
            f"Could not interpret --max-memory: {max_memory}."
            f"To allocate memory, use e.g. '5G' for five gigabytes of memory."
        )


def get_max_memory(max_memory):
    """
    Interpret the config parameter --max-memory.

    Arguments
    ---------

    max_memory : str
        Memory limit for the JVM running R5.

        Use % as a suffix to specify a share of total RAM;
        K, M, G, T suffix specify KiB, MiB, GiB, or TiB, respectively.
        Values without suffix are interpreted as bytes.
        Values are rounded to the closest MiB.
    """

    value, unit = parse_max_memory_string(max_memory)

    if unit == "%":
        max_memory = share_of_ram(share=(value / 100.0))
    else:
        # convert to MiB
        if unit == "K":
            value *= 2**-20
            if value < 1:
                value = 1
        elif unit == "M":
            value *= 2**1
        elif unit == "G":
            value *= 2**10
        elif unit == "T":
            value *= 2**20
        max_memory = round(value)

    if max_memory < ABSOLUTE_MINIMUM_MEMORY:
        max_memory = ABSOLUTE_MINIMUM_MEMORY
        warnings.warn(
            f"Requested maximum JVM heap size is too low for R5, "
            f"setting to minimum value {ABSOLUTE_MINIMUM_MEMORY:d} MiB.",
            RuntimeWarning,
        )

    return max_memory


MAX_JVM_MEMORY = get_max_memory(arguments.max_memory)
