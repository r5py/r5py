#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.analyst.cluster.PathResult.Stat enum set."""

import enum

import com.conveyal.r5


__all__ = ["BreakdownStat"]


class BreakdownStat(enum.Enum):
    """
    Statistical functions to apply to detailed routing results summary.

    BreakdownStat.MEAN, BreakdownStat.MINIMUM
    """

    MEAN = com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf("MEAN")
    MINIMUM = com.conveyal.r5.analyst.cluster.PathResult.Stat.valueOf("MINIMUM")
