#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.api.util.TransitModes enum set."""

import enum

from .. import util  # noqa: F401

import com.conveyal.r5


__all__ = ["TransitMode"]


class TransitMode(enum.Enum):
    """
    Public transport modes.

    AIR, TRAM, SUBWAY, RAIL, BUS, FERRY, CABLE_CAR,
    GONDOLA, FUNICULAR, TRANSIT

    TRANSIT is a shorthand of all of the others combined.
    """

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
