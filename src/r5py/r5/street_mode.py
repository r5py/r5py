#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.profile.StreetMode enum set."""

import enum

import com.conveyal.r5


__all__ = ["StreetMode"]


class StreetMode(enum.Enum):
    """
    Transport modes (a subset of ``r5py.LegMode``).

    StreetMode.WALK, StreetMode.BICYCLE, StreetMode.CAR
    """

    WALK = com.conveyal.r5.profile.StreetMode.valueOf("WALK")
    BICYCLE = com.conveyal.r5.profile.StreetMode.valueOf("BICYCLE")
    CAR = com.conveyal.r5.profile.StreetMode.valueOf("CAR")
