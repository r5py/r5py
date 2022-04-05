#!/usr/bin/env python3

"""Determine a reasonable memory footprint for the Java virtual machine."""

# This is obviously a very naive approach: we simply assume that we can hog
# up to 80% of RAM for Java alone, if that leaves a minimum of 2 GiB for
# the operating system, the Python part (potentially huge dataframes!), and
# everything else that happens to run on the same machine.
# TODO: figure out something smarter ;)

import math
import psutil


__all__ = ["EIGHTY_PERCENT_OF_RAM"]


def share_of_ram(share=0.8, leave_at_least=2):
    """
    Return a value in GiB that is close to `share` portion of total RAM.

    If that leaves less than `leave_at_least GiB, instead
    return total RAM minus `leave_at_least` GiB.
    """
    total_ram = psutil.virtual_memory().total / (1024 ** 3)
    if total_ram * (1.0 - share) > leave_at_least:
        share_of_ram = math.floor(share * total_ram)
    else:
        share_of_ram = math.floor(total_ram - leave_at_least)
    return share_of_ram


EIGHTY_PERCENT_OF_RAM = share_of_ram()
