#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.point_to_point.builder.SpeedUnit enum set."""

import enum

from ..util import config  # noqa: F401

import com.conveyal.r5


__all__ = ["SpeedUnit"]


class SpeedUnit(enum.Enum):
    KMH = com.conveyal.r5.point_to_point.builder.SpeedUnit.valueOf("KMH")
    MPH = com.conveyal.r5.point_to_point.builder.SpeedUnit.valueOf("MPH")
    KNOTS = com.conveyal.r5.point_to_point.builder.SpeedUnit.valueOf("KNOTS")

    @staticmethod
    def from_string(unit):
        if unit in (
                "km/h",
                "kmh",
                "kmph",
                "kph"
        ):
            return SpeedUnit.KMH
        elif unit == "mph":
            return SpeedUnit.MPH
        elif unit == "knots":
            return SpeedUnit.KNOTS
        else:
            raise KeyError("SpeedUnit does not have a value for '{}'".format(unit))
