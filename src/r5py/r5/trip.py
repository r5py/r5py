#!/usr/bin/env python3


"""Represent one trip, consisting of one or more `TripLeg`s."""


import datetime

import shapely

from .trip_leg import TripLeg


__all__ = ["Trip"]


class Trip:
    """Represent one trip, consisting of one or more `r5py.r5.TripLeg`."""

    COLUMNS = [
        "segment",
    ] + TripLeg.COLUMNS

    def __init__(self, legs=[]):
        """
        Represent one trip, consisting of one of more `r5py.r5.TripLeg`.

        Arguments
        =========
        legs : collections.abc.Iterable
            optional list of trip legs with which to initialise this trip
        """
        self.legs = legs

    def __eq__(self, other):
        """Check whether `self` and `other` are equal."""
        if isinstance(other, self.__class__):
            return self.legs == other.legs

    def __repr__(self):
        """Return a string representation of `self`."""
        legs = ", ".join([str(leg) for leg in self.legs])
        return (
            f"<{self.__class__.__name__}: "
            f"{self.distance}m, "
            f"{self.travel_time.total_seconds()}s, "
            f"{legs}>"
        )

    def as_table(self):
        """
        Return a table (list of lists) of this trip’s legs.

        Returns
        =======
        list : detailed information about this trip and its legs (segments):
            ``segment``, ``transport_mode``, ``departure_time``, ``distance``,
            ``travel_time``, ``wait_time``, ``feed``, ``agency_id``, ``route_id``,
            ``start_stop_id``, ``end_stop_id``, ``geometry``
        """
        return [[segment] + leg.as_table_row() for segment, leg in enumerate(self.legs)]

    @property
    def distance(self):
        """Overall distance of this trip in metres (float)."""
        try:
            distance = sum([leg.distance for leg in self.legs])
        except TypeError:  # distance of a leg can be None
            distance = None
        return distance

    @property
    def geometry(self):
        """Joined geometries of all legs of this trip (shapely.LineString or shapely.MultiLineString)."""
        return shapely.line_merge(
            shapely.MultiLineString([leg.geometry for leg in self.legs])
        )

    @property
    def route_ids(self):
        """The public transport route(s) used on this trip."""
        return [leg.route_id for leg in self.legs]

    @property
    def transport_modes(self):
        """The transport mode(s) used on this trip."""
        return [leg.transport_mode for leg in self.legs]

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
