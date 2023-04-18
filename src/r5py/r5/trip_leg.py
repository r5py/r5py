#!/usr/bin/env python3


"""Represent one leg of a trip."""


__all__ = ["TripLeg"]


class TripLeg:
    """
    Represent one leg of a trip.

    This is a base class, use one the specific classes,
    e.g., TransitLeg, or DirectLeg
    """

    COLUMNS = [
        "transport_mode",
        "departure_time",
        "distance",
        "travel_time",
        "wait_time",
        "route",
        "geometry",
    ]

    def __init__(
        self,
        transport_mode=None,
        departure_time=None,
        distance=None,
        travel_time=None,
        wait_time=None,
        route=None,
        geometry=None,
    ):
        """
        Represent one leg of a trip.

        This is a base class, use one the specific classes,
        e.g., TransitLeg, or DirectLeg

        Arguments
        =========
        transport_mode : r5py.TransportMode
            mode of transport this trip leg was travelled
        departure_time : datetime.datetime,
        distance : float
            distance covered by this trip leg, in metres
        travel_time : datetime.timedelta
            time spent travelling on this trip leg
        wait_time : datetime.timedelta
            time spent waiting for a connection on this trip leg
        route : str
            public transport route used for this trip leg
        geometry : shapely.LineString
            spatial representation of this trip leg
        """
        self.transport_mode = transport_mode
        self.departure_time = departure_time
        self.distance = distance
        self.travel_time = travel_time
        self.wait_time = wait_time
        self.route = route
        self.geometry = geometry

    def __add__(self, other):
        from .trip import Trip

        if isinstance(other, self.__class__):
            trip = Trip([self, other])
            return trip
        else:
            raise NotImplementedError(
                f"Cannot use operator '+' on '{type(other)}' and '{type(self)}'"
            )

    def __radd__(self, other):
        from .trip import Trip

        if isinstance(other, Trip):
            other.legs.append(self)
            return other
        elif isinstance(other, self.__class__):
            trip = Trip([other, self])
            return trip
        else:
            raise NotImplementedError(
                f"Cannot use operator '+' on '{type(self)}' and '{type(other)}'"
            )

    def __str__(self):
        first_point = self.geometry.coords[0]
        last_point = self.geometry.coords[-1]
        return (
            "<"
            f"{self.__class__.__name__}: "
            f"{self.transport_mode}, "
            f"{self.distance}m, "
            f"{self.travel_time.total_seconds():0.1f}s, "
            f"{first_point} -> {last_point}"
            ">"
        )

    def as_table_row(self):
        """
        Return a table row (list) of this trip leg’s details.

        Returns
        =======
        list : detailed information about this trip leg: ``transport_mode``,
        ``departure_time``, ``distance``, ``travel_time``, ``wait_time``,
        ``route``, ``geometry``
        """
        return [getattr(self, column) for column in self.COLUMNS]
