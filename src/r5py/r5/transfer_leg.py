#!/usr/bin/env python3


"""Represent one leg of a trip, specifically transfers between public transport
vehicles."""


from .direct_leg import DirectLeg


__all__ = ["TransferLeg"]


class TransferLeg(DirectLeg):
    """
    Represent one leg of a trip, specifically transfers between public transport
    vehicles.
    """

    def __init__(self, transport_mode, street_segment, travel_time=None):
        """
        Represent one leg of a trip, specifically transfers between public
        transport vehicles.

        Arguments
        =========
        transport_mode : r5py.TransportMode
            mode of transport this trip leg was travelled
        street_segment : com.conveyal.r5.profile.StreetSegment
            the leg’s data as output by R5’s `StreetRouter`
        travel_time : datetime.timedelta
            travel time for this leg, if not specified (default),
            use `street_segment.duration`
        """
        super().__init__(transport_mode, street_segment)
        if travel_time is not None:
            self.travel_time = travel_time
