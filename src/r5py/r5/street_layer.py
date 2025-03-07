#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.streets.StreetLayer."""


import functools

import jpype
import jpype.types
import shapely

from .transport_mode import TransportMode
from ..util import start_jvm

import com.conveyal.r5


__all__ = ["StreetLayer"]


start_jvm()


EMPTY_POINT = shapely.Point()


class StreetLayer:
    """Wrap a com.conveyal.r5.streets.StreetLayer."""

    @classmethod
    def from_r5_street_layer(cls, street_layer):
        """
        Create a StreetLayer from a com.conveyal.r5.streets.StreetLayer.

        Arguments
        ---------
        street_layer : com.conveyal.r5.streets.StreetLayer
        """
        instance = cls()
        instance._street_layer = street_layer
        return instance

    @functools.cached_property
    def extent(self):
        """The geographic area covered, as a `shapely.box`."""
        envelope = self._street_layer.envelope
        return shapely.box(
            envelope.getMinX(),
            envelope.getMinY(),
            envelope.getMaxX(),
            envelope.getMaxY(),
        )

    def find_split(
        self,
        point,
        radius=com.conveyal.r5.streets.StreetLayer.LINK_RADIUS_METERS,
        street_mode=TransportMode.WALK,
    ):
        """
        Find a location on an existing street near `point`.

        Arguments
        ---------
        point : shapely.Point
            Find a location close to this point
        radius : float
            Search radius around `point`
        street_mode : travel mode that the snapped-to street should allow

        Returns
        -------
        shapely.Point
            Closest location on the street network or `POINT EMPTY` if no
            such location could be found within `radius`
        """
        try:
            split = self._street_layer.findSplit(point.y, point.x, radius, street_mode)
            return shapely.Point(
                split.fixedLon / com.conveyal.r5.streets.VertexStore.FIXED_FACTOR,
                split.fixedLat / com.conveyal.r5.streets.VertexStore.FIXED_FACTOR,
            )
        except (AttributeError, TypeError):
            return EMPTY_POINT


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.streets.StreetLayer", exact=StreetLayer
)
def _cast_StreetLayer(java_class, object_):
    return object_._street_layer
