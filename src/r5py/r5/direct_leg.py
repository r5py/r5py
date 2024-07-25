#!/usr/bin/env python3


"""Represent one leg of a direct mode (walk, cycle, car) trip."""


import datetime

import shapely

from .trip_leg import TripLeg


__all__ = ["DirectLeg"]


class DirectLeg(TripLeg):
    """Represent one leg of a public transport trip."""

    def __init__(self, transport_mode, street_segment):
        """
        Represent one leg of a public transport trip.

        Arguments
        =========
        transport_mode : r5py.TransportMode
            mode of transport this trip leg was travelled
        street_segment : com.conveyal.r5.profile.StreetSegment
            the leg’s data as output by R5’s `StreetRouter`
        """
        distance = street_segment.distance / 1000.0  # millimetres!
        travel_time = datetime.timedelta(seconds=street_segment.duration)
        geometry = shapely.from_wkt(str(street_segment.geometry))
        osm_ids = []

        if hasattr(street_segment, "streetEdges"):
            for edge_info in street_segment.streetEdges:
                if hasattr(edge_info, "edgeOsmId"):
                    osm_ids.append(edge_info.edgeOsmId)

        super().__init__(
            transport_mode=transport_mode,
            distance=distance,
            travel_time=travel_time,
            geometry=geometry,
            osm_ids=osm_ids,
        )
