#!/usr/bin/env python3

"""A less complex representation of com.conveyal.r5.api.util.StreetSegment."""


import datetime

import shapely


__all__ = ["StreetSegment"]


class StreetSegment:
    """A less complex representation of com.conveyal.r5.api.util.StreetSegment."""

    distance = 0
    duration = datetime.timedelta()
    geometry = shapely.LineString()

    def __init__(self, street_path):
        """
        Initialise a less complex representation of com.conveyal.r5.api.util.StreetSegment.

        Arguments
        ---------
        street_path : com.conveyal.r5.profile.StreetPath
            StreetPath, obtained, e.g., from StreetRouter state
        """
        self.distance = street_path.getDistance()
        self.duration = street_path.getDuration()
        self.geometry = shapely.line_merge(
            shapely.MultiLineString(
                [
                    shapely.from_wkt(
                        str(street_path.getEdge(edge).getGeometry().toText())
                    )
                    for edge in street_path.getEdges()
                ]
            )
        )
