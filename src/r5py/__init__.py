#!/usr/bin/env python3

"""Python wrapper for the R5 routing analysis engine."""

__version__ = "0.1.1"

from .util import start_jvm

start_jvm()

from .r5 import (  # noqa: E402
    DetailedItinerariesComputer,
    RegionalTask,
    TransportMode,
    TransportNetwork,
    TravelTimeMatrixComputer,
)

__all__ = [
    "DetailedItinerariesComputer",
    "RegionalTask",
    "TransportMode",
    "TransportNetwork",
    "TravelTimeMatrixComputer",
    "__version__",
]
