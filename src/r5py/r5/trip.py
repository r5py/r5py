#!/usr/bin/env python3


"""Represent one trip, consisting of one or more `TripLeg`s."""


import datetime

import shapely

from .trip_leg import TripLeg


__all__ = ["Trip"]


class Trip:
    """
    Represent one trip, consisting of one or more `TripLeg`s.
    """

    COLUMNS = [
        "segment",
    ] + TripLeg.COLUMNS

    def __init__(self, legs=[]):
        """
        Represent one trip, consisting of one of more `TripLeg`s.

        Arguments
        =========
        legs : collections.abc.Iterable
            optional list of trip legs with which to initialise this trip
        """
        self.legs = legs

    def __repr__(self):
        legs = ", ".join([str(leg) for leg in self.legs])
        return (
            f"<{self.__class__.__name__}: "
            f"{self.distance}m, "
            f"{self.duration.total_seconds()}s, "
            f"{legs}>"
        )

    def as_table(self):
        """
        Return a table (list of lists) of this trip’s legs.

        Returns
        =======
        list : detailed information about this trip and its legs (segments):
        ``segment``, ``transport_mode``, ``departure_time``, ``distance``,
        ``travel_time``, ``wait_time``, ``route``, ``geometry``
        """
        return [[segment] + leg.as_table_row() for segment, leg in enumerate(self.legs)]

    @property
    def distance(self):
        """Overall distance of this trip in metres (float)."""
        return sum([leg.distance for leg in self.legs])

    @property
    def geometry(self):
        """Joined geometries of all legs of this trip (shapely.MultiLineString)."""
        return shapely.MultiLineString([leg.geometry for leg in self.legs])

    @property
    def routes(self):
        """The public transport route(s) used on this trip."""
        return set([leg.route for leg in self.legs])

    @property
    def transport_modes(self):
        """The transport mode(s) used on this trip."""
        return set([leg.transport_mode for leg in self.legs])

    @property
    def travel_time(self):
        """Overall travel_time of this trip (datetime.timedelta)."""
        return sum(
            [leg.travel_time for leg in self.legs], datetime.timedelta(seconds=0)
        )

    @property
    def wait_time(self):
        """Overall wait_time of this trip (datetime.timedelta)."""
        return sum([leg.wait_time for leg in self.legs], datetime.timedelta(seconds=0))
