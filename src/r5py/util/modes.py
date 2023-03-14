#!/usr/bin/env python3

"""Conversion of mode strings to proper mode enums"""


from ..r5.transit_mode import TransitMode
from ..r5.leg_mode import LegMode


MODE_STRING_TO_ENUM = {
    "WALK": LegMode.WALK,
    "BICYCLE": LegMode.BICYCLE,
    "CAR": LegMode.CAR,
    "AIR": TransitMode.AIR,
    "TRAM": TransitMode.TRAM,
    "SUBWAY": TransitMode.SUBWAY,
    "RAIL": TransitMode.RAIL,
    "BUS": TransitMode.BUS,
    "FERRY": TransitMode.FERRY,
    "CABLE_CAR": TransitMode.CABLE_CAR,
    "GONDOLA": TransitMode.GONDOLA,
    "FUNICULAR": TransitMode.FUNICULAR,
    "TRANSIT": TransitMode.TRANSIT,
    "BICYCLE_RENT": LegMode.BICYCLE_RENT,
    "CAR_PARK": LegMode.CAR_PARK,
}
