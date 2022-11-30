#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransitLayer."""


import datetime
import jpype
import jpype.types

from ..util import parse_int_date


__all__ = ["TransitLayer"]


class TransitLayer:
    """Wrap a com.conveyal.r5.transit.TransitLayer."""

    @classmethod
    def from_r5_transit_layer(self, transit_layer):
        """
        Create a TransitLayer from a com.conveyal.r5.transit.TransitLayer.

        Arguments
        ---------
        transit_layer : com.conveyal.r5.transit.TransitLayer
        """
        self._transit_layer = transit_layer

    @property
    def start_date(self):
        """The earliest date the loaded GTFS data covers."""
        try:
            self._start_date
        except AttributeError:
            try:
                self._start_date = min(
                    [
                        parse_int_date(service.calendar.start_date)
                        for service in self._transit_layer.services
                    ]
                )
            except ValueError as exception:
                raise ValueError("No GTFS data set loaded") from exception

    @property
    def end_date(self):
        """The earliest date the loaded GTFS data covers."""
        try:
            self._end_date
        except AttributeError:
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
                self._end_date = end_date
            except ValueError as exception:
                raise ValueError("No GTFS data set loaded") from exception

    def covers(self, point_in_time):
        """Check whether `point_in_time` is covered by GTFS data sets."""
        try:
            covers = self.start_date <= point_in_time <= self.end_date
        except ValueError:  # no GTFS data loaded
            covers = False
        return covers


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransitLayer", exact=TransitLayer
)
def _cast_TransitLayer(java_class, object_):
    return object_._transport_network
