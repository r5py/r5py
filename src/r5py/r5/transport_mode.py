#!/usr/bin/env python3


"""The transport modes supported by R5 (Leg, Street, Transit, combined)."""


import enum

import jpype

from ..util import start_jvm

import com.conveyal.r5


__all__ = ["TransportMode"]


start_jvm()


TRANSIT_MODES = [
    "AIR",
    "BUS",
    "CABLE_CAR",
    "FERRY",
    "FUNICULAR",
    "GONDOLA",
    "RAIL",
    "SUBWAY",
    "TRAM",
    "TRANSIT",
]

STREET_MODES = [
    "BICYCLE",
    "CAR",
    "WALK",
]

LEG_MODES = STREET_MODES + [
    "BICYCLE_RENT",
    "CAR_PARK",
]


class TransportMode(enum.Enum):
    """
    Transport modes.

    TransportMode.AIR, TransportMode.TRAM, TransportMode.SUBWAY,
    TransportMode.RAIL, TransportMode.BUS, TransportMode.FERRY,
    TransportMode.CABLE_CAR, TransportMode.GONDOLA, TransportMode.FUNICULAR,
    TransportMode.TRANSIT (translate into R5’s TransitMode)

    TransportMode.WALK, TransportMode.BICYCLE, TransportMode.CAR (translate into
    R5’s StreetMode or LegMode)

    TransportMode.BICYCLE_RENT, TransportMode.CAR_PARK (translate into R5’s LegMode)
    """

    @classmethod
    def _missing_(cls, value):
        value = str(value).upper()
        for member in cls:
            if value == member.value:
                return member
        return None

    def __add__(self, other):
        """Combine two transport modes."""
        if isinstance(other, self.__class__):
            return [self, other]
        elif isinstance(other, list):
            return [self] + other
        else:
            raise TypeError(
                f"unsupported operand type(s) for '+': '{type(other)}' and '{type(self)}'"
            )

    def __radd__(self, other):
        """Combine two transport modes."""
        if other == 0:  # first iteration of sum()
            return self
        elif isinstance(other, list):
            return other + [self]
        else:
            return self.__add__(other)

    @property
    def is_leg_mode(self):
        """Can this TransportMode function as a LegMode?."""
        return self.name in LEG_MODES

    @property
    def is_street_mode(self):
        """Can this TransportMode function as a StreetMode?."""
        return self.name in STREET_MODES

    @property
    def is_transit_mode(self):
        """Can this TransportMode function as a TransitMode?."""
        return self.name in TRANSIT_MODES

    AIR = "AIR"
    BUS = "BUS"
    CABLE_CAR = "CABLE_CAR"
    FERRY = "FERRY"
    FUNICULAR = "FUNICULAR"
    GONDOLA = "GONDOLA"
    RAIL = "RAIL"
    SUBWAY = "SUBWAY"
    TRAM = "TRAM"
    TRANSIT = "TRANSIT"

    BICYCLE = "BICYCLE"
    CAR = "CAR"
    WALK = "WALK"

    BICYCLE_RENT = "BICYCLE_RENT"
    CAR_PARK = "CAR_PARK"


@jpype._jcustomizer.JConversion("com.conveyal.r5.api.util.LegMode", exact=TransportMode)
def _cast_LegMode(java_class, object_):
    if object_.name in LEG_MODES:
        return com.conveyal.r5.api.util.LegMode.valueOf(object_.name)
    else:
        raise ValueError(f"{object_.name} is not a valid R5 LegMode")


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.profile.StreetMode", exact=TransportMode
)
def _cast_StreetMode(java_class, object_):
    if object_.name in STREET_MODES:
        return com.conveyal.r5.profile.StreetMode.valueOf(object_.name)
    else:
        raise ValueError(f"{object_.name} is not a valid R5 StreetMode")


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.api.util.TransitModes", exact=TransportMode
)
def _cast_TransitMode(java_class, object_):
    if object_.name in TRANSIT_MODES:
        return com.conveyal.r5.api.util.TransitModes.valueOf(object_.name)
    else:
        raise ValueError(f"{object_.name} is not a valid R5 TransitModes")
