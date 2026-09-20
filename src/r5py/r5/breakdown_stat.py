#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.analyst.cluster.PathResult.Stat enum set."""

import enum

from ..util import start_jvm

import com.conveyal.r5

__all__ = ["BreakdownStat"]


start_jvm()


class BreakdownStat(enum.Enum):
    """
    Statistical function to summarise a path template’s iterations.

    A transit path template (a distinct sequence of routes and stops) can be
    found in more than one of the departure-minute iterations R5 computes over
    the departure time window. Its in-vehicle, access, and egress times are
    constant across those iterations, but the waiting time (and, hence, the
    transfer and total times) varies. ``BreakdownStat`` selects which iteration
    represents the template in the results: the one whose total waiting time is
    closest to the minimum (``BreakdownStat.MINIMUM``) or the mean
    (``BreakdownStat.MEAN``) total waiting time across all of the template’s
    iterations.
    """

    MEAN = com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf("MEAN")
    MINIMUM = com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf("MINIMUM")
