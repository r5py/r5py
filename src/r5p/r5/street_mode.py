#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.profile.StreetMode enum set."""

import enum

from ..util import config  # noqa: F401

import com.conveyal.r5


__all__ = ["StreetMode"]


class StreetMode(enum.Enum):
    WALK = com.conveyal.r5.profile.StreetMode.valueOf("WALK")
    BICYCLE = com.conveyal.r5.profile.StreetMode.valueOf("BICYCLE")
    CAR = com.conveyal.r5.profile.StreetMode.valueOf("CAR")
