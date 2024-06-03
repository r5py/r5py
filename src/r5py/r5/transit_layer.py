#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransitLayer."""


import datetime
import functools

import jpype
import jpype.types

from ..util import parse_int_date


__all__ = ["TransitLayer"]


class TransitLayer:
    """Wrap a com.conveyal.r5.transit.TransitLayer."""

    @classmethod
    def from_r5_transit_layer(cls, transit_layer):
        """
        Create a TransitLayer from a com.conveyal.r5.transit.TransitLayer.

        Arguments
        ---------
        transit_layer : com.conveyal.r5.transit.TransitLayer
        """
        instance = cls()
        instance._transit_layer = transit_layer
        return instance

    @functools.cached_property
    def start_date(self):
        """The earliest date the loaded GTFS data covers."""
        try:
            start_date = min(
                [
                    parse_int_date(service.calendar.start_date)
                    for service in self._transit_layer.services
                ]
            )
        except (AttributeError, ValueError) as exception:
            raise ValueError("No GTFS data set loaded") from exception
        return start_date

    @functools.cached_property
    def end_date(self):
        """The latest date the loaded GTFS data covers."""
        try:
            end_date = max(
                [
                    parse_int_date(service.calendar.end_date)
                    for service in self._transit_layer.services
                ]
            )
            end_date += datetime.timedelta(
                hours=23, minutes=59, seconds=59
            )  # *end* of day
        except (AttributeError, ValueError) as exception:
            raise ValueError("No GTFS data set loaded") from exception
        return end_date

    def covers(self, point_in_time):
        """Check whether `point_in_time` is covered by GTFS data sets."""
        try:
            covers = self.start_date <= point_in_time <= self.end_date
        except ValueError:  # no GTFS data loaded
            covers = False
        return covers

    def get_street_vertex_for_stop(self, stop):
        """
        Get the street layer’s vertex corresponding to `stop`.

        Arguments
        ---------
        stop : int
            ID of the public transport stop for which to find a vertex

        Returns
        -------
        int
            ID of the vertex corresponding to the public transport stop
        """
        street_vertex = self._transit_layer.streetVertexForStop.get(stop)
        return street_vertex

    @functools.cached_property
    def routes(self):
        """Return a list of GTFS routes."""
        return list(self._transit_layer.routes)

    @functools.cached_property
    def trip_patterns(self):
        """Return a list of GTFS trip patterns."""
        return list(self._transit_layer.tripPatterns)


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransitLayer", exact=TransitLayer
)
def _cast_TransitLayer(java_class, object_):
    return object_._transit_layer
