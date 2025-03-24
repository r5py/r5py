#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransitLayer."""


import functools

import jpype
import jpype.types

import java.time


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

    def covers(self, date):
        """
        Check whether `date` is covered by GTFS data sets.

        Arguments:
        ----------
        date : datetime.date
            date for which to check whether a GTFS service exists.

        Returns:
        --------
        bool
            Whether or not any services exist on `date`.
        """
        date = java.time.LocalDate.of(date.year, date.month, date.day)
        return True in set(
            [service.activeOn(date) for service in self._transit_layer.services]
        )

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

    def get_stop_id_from_index(self, stop_index):
        """Get the GTFS stop id for the `stop_index`-th stop of this transit layer."""
        return self._transit_layer.stopIdForIndex[stop_index]


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransitLayer", exact=TransitLayer
)
def _cast_TransitLayer(java_class, object_):
    return object_._transit_layer
