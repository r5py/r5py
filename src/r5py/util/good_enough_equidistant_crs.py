#!/usr/bin/env python3


"""Find the most appropriate equidistant (UTM) reference system for an extent."""


import pyproj
import shapely

from .exceptions import UnexpectedCrsError


class GoodEnoughEquidistantCrs(pyproj.CRS):
    """
    Find the most appropriate UTM reference system for the current extent.

    (We need this to be able to calculate lengths in meters.
    Results don’t have to be perfect, so also the neighbouring UTM grid will do.)
    """

    def __new__(cls, extent):
        """
        Find the most appropriate UTM reference system for the current extent.

        (We need this to be able to calculate lengths in meters.
        Results don’t have to be perfect, so also the neighbouring UTM grid will do.)

        Arguments
        ---------
        extent: shapely.Geometry
            The geographical extent for which to find an equidistant reference
            system, in `EPSG:4326`
        """
        if GoodEnoughEquidistantCrs._is_plausible_in_epsg4326(extent):
            # default CRS in case we do not find any better match
            crs = pyproj.CRS.from_epsg(3857)

            # buffer extent (so everything is a polygon)
            extent = extent.buffer(0.1)

            crsinfo = pyproj.database.query_utm_crs_info(
                datum_name="WGS 84",
                area_of_interest=pyproj.aoi.AreaOfInterest(*extent.bounds),
            )
            for candidate_crs in crsinfo:
                area_of_use = shapely.box(*candidate_crs.area_of_use.bounds)
                coverage = shapely.intersection(extent, area_of_use).area / extent.area

                if coverage > 0.5:
                    # more than half of extent covered by crs’ area of use
                    # -> good enough
                    crs = pyproj.CRS.from_authority(
                        candidate_crs.auth_name, candidate_crs.code
                    )
                    break

            return crs

        else:
            raise UnexpectedCrsError("`extent` does not seem to be in `EPSG:4326`")

    @staticmethod
    def _is_plausible_in_epsg4326(geometry):
        try:
            minx, miny, maxx, maxy = geometry.bounds
            assert -180 <= minx <= maxx <= 180
            assert -90 <= miny <= maxy <= 90
            return True
        except AssertionError:
            return False
