#!/usr/bin/env python3


"""The elevation cost functions supported by R5 (Tobler, Minetti)."""


import enum

import jpype

from ..util import start_jvm

import com.conveyal.r5


__all__ = ["ElevationCostFunction"]


start_jvm()


class ElevationCostFunction(enum.Enum):
    """
    Elevation cost functions.

    TOBLER: Waldo Tobler’s hiking function, cf. https://en.wikipedia.org/wiki/Tobler%27s_hiking_function
    MINETTI: Minetti et al.’s perceived effort/energy consumption, cf.
    https://doi.org/10.1152/japplphysiol.01177.2001
    """

    @classmethod
    def _missing_(cls, value):
        value = str(value).upper()
        for member in cls:
            if value == member.value:
                return member
        return None

    TOBLER = "TOBLER"
    MINETTI = "MINETTI"


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.analyst.scenario.RasterCost.CostFunction",
    exact=ElevationCostFunction,
)
def _cast_LegMode(java_class, object_):
    return com.conveyal.r5.analyst.scenario.RasterCost.CostFunction.valueOf(
        object_.name
    )
