#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.api.util.TransitModes enum set."""

import enum

from ..util import config  # noqa: F401

import com.conveyal.r5


__all__ = ["TransitMode"]


class TransitMode(enum.Enum):
    AIR = com.conveyal.r5.api.util.TransitModes.valueOf("AIR")
    TRAM = com.conveyal.r5.api.util.TransitModes.valueOf("TRAM")
    SUBWAY = com.conveyal.r5.api.util.TransitModes.valueOf("SUBWAY")
    RAIL = com.conveyal.r5.api.util.TransitModes.valueOf("RAIL")
    BUS = com.conveyal.r5.api.util.TransitModes.valueOf("BUS")
    FERRY = com.conveyal.r5.api.util.TransitModes.valueOf("FERRY")
    CABLE_CAR = com.conveyal.r5.api.util.TransitModes.valueOf("CABLE_CAR")
    GONDOLA = com.conveyal.r5.api.util.TransitModes.valueOf("GONDOLA")
    FUNICULAR = com.conveyal.r5.api.util.TransitModes.valueOf("FUNICULAR")
    TRANSIT = com.conveyal.r5.api.util.TransitModes.valueOf("TRANSIT")
