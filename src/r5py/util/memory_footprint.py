#!/usr/bin/env python3

"""Determine a reasonable memory footprint for the Java virtual machine."""


import psutil
import re

from . import config


__all__ = ["MAX_JVM_MEMORY"]


config.argparser.add(
    "-m",
    "--max-memory",
    help="""
        Memory limit for the JVM running R5.

        Use % as a suffix to specify a share of total RAM;
        M, G, T to specify MiB, GiB, or TiB, respectively.
        Values without suffix are interpreted as bytes.
        Values are rounded to the closest MiB.
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


def max_memory(max_memory):
    """Interpret the config parameter --max-memory."""
    try:
        matches = re.match(r"(?P<value>[0-9]+(\.[0-9]+)?)(?P<unit>[%MGT])?", max_memory)
        value = float(matches["value"])
        unit = matches["unit"]
        if unit == "%":
            max_memory = share_of_ram(share=(value / 100.0))
        else:
            # convert to MiB
            if unit is None:
                value *= 2**-10
                if value < 1:
                    value = 1
            # elif unit == "M":
            #    value *= 2 ** 1
            elif unit == "G":
                value *= 2**10
            elif unit == "T":
                value *= 2**20
            max_memory = round(value)
    except TypeError:
        raise ValueError("Could not interpret --max-memory: {}".format(max_memory))
    return max_memory


MAX_JVM_MEMORY = max_memory(arguments.max_memory)
