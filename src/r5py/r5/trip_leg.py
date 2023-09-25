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
        "feed",
        "agency_id",
        "route_id",
        "start_stop_id",
        "end_stop_id",
        "geometry",
    ]

    def __init__(
        self,
        transport_mode=None,
        departure_time=None,
        distance=None,
        travel_time=None,
        wait_time=None,
        feed=None,
        agency_id=None,
        route_id=None,
        start_stop_id=None,
        end_stop_id=None,
        geometry=None,
    ):
        """
        Represent one leg of a trip.

        This is a base class, use one the specific classes, e.g., TransitLeg, or
        DirectLeg

        Arguments
        =========
        transport_mode : r5py.TransportMode
            mode of transport this trip leg was travelled
        departure_time : datetime.datetime, distance : float
            distance covered by this trip leg, in metres
        travel_time : datetime.timedelta
            time spent travelling on this trip leg
        wait_time : datetime.timedelta
            time spent waiting for a connection on this trip leg
        feed : str
            the GTFS feed identifier used for this trip leg
        agency_id : str
            the GTFS id the agency used for this trip leg
        route_id : str
            the GTFS id of the public transport route used for this trip leg
        start_stop_id : str
            the GTFS stop_id of the boarding stop used for this trip leg
        end_stop_id : str
            the GTFS stop_id of the aligning stop used for this trip leg
        geometry : shapely.LineString
            spatial representation of this trip leg
        """
        self.transport_mode = transport_mode
        self.departure_time = departure_time
        self.distance = distance
        self.travel_time = travel_time
        self.wait_time = wait_time
        self.feed = feed
        self.agency_id = agency_id
        self.route_id = route_id
        self.start_stop_id = start_stop_id
        self.end_stop_id = end_stop_id
        self.geometry = geometry

    def __add__(self, other):
        from .trip import Trip

        if isinstance(other, self.__class__):
            trip = Trip([self, other])
            return trip
        elif isinstance(other, Trip):
            other.legs = [self] + other.legs
            return other
        else:
            raise TypeError(
                f"unsupported operand type(s) for '+': '{type(other)}' and '{type(self)}'"
            )

    def __radd__(self, other):
        from .trip import Trip

        if other == 0:  # first iteration of sum()
            return self
        elif isinstance(other, Trip):
            other.legs.append(self)
            return other
        else:
            return self.__add__(other)

    def __gt__(self, other):
        if isinstance(other, TripLeg):
            return (self.travel_time + self.wait_time) > (
                other.travel_time + other.wait_time
            )

    def __ge__(self, other):
        if isinstance(other, TripLeg):
            return (self.travel_time + self.wait_time) >= (
                other.travel_time + other.wait_time
            )

    def __lt__(self, other):
        if isinstance(other, TripLeg):
            return (self.travel_time + self.wait_time) < (
                other.travel_time + other.wait_time
            )

    def __le__(self, other):
        if isinstance(other, TripLeg):
            return (self.travel_time + self.wait_time) <= (
                other.travel_time + other.wait_time
            )

    def __repr__(self):
        try:
            first_point = self.geometry.coords[0]
            last_point = self.geometry.coords[-1]
            _repr = (
                "<"
                f"{self.__class__.__name__}: "
                f"{self.transport_mode}, "
                f"{self.distance}m, "
                f"{self.travel_time.total_seconds():0.1f}s, "
                f"{first_point} -> {last_point}"
                ">"
            )
        except AttributeError:
            _repr = f"<{self.__class__.__name__}>"
        return _repr

    def as_table_row(self):
        """
        Return a table row (list) of this trip leg’s details.

        Returns
        =======
        list : detailed information about this trip leg: ``transport_mode``,
        ``departure_time``, ``distance``, ``travel_time``, ``wait_time``, ``feed``, ``agency_id``
        ``route_id``, ``start_stop_id``, ``end_stop_id``, ``geometry``
        """
        return [getattr(self, column) for column in self.COLUMNS]
