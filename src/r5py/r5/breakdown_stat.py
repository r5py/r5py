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
    the departure time window. Its ride, access, egress, and transfer times are
    constant across those iterations, but the waiting time (and, hence, the
    total time) varies. ``BreakdownStat`` selects how to summarise them:
    ``BreakdownStat.MEAN`` reports each leg’s waiting time and the total time
    averaged over all of the template’s iterations, ``BreakdownStat.MINIMUM``
    reports the fastest iteration (an itinerary a rider could actually follow).
    This mirrors R5’s ``PathResult.summarizeIterations()``.
    """

    MEAN = com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf("MEAN")
    MINIMUM = com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf("MINIMUM")
