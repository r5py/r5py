#!/usr/bin/env python3


"""Compute polygons of equal travel time from a destination."""


import datetime
import math
import warnings

import geopandas
import pandas
import pyproj
import shapely

from .base_travel_time_matrix import BaseTravelTimeMatrix
from .travel_time_matrix import TravelTimeMatrix
from ..util import GoodEnoughEquidistantCrs, SpatiallyClusteredGeoDataFrame


__all__ = ["Isochrones"]


CONCAVE_HULL_BUFFER_SIZE = 5.0  # metres
CONCAVE_HULL_RATIO = 1.0
POINT_GRID_RESOLUTION = 20  # metres
R5_CRS = "EPSG:4326"
SIMPLIFICATION_TOLERANCE = 50  # metres
VERY_SMALL_BUFFER_SIZE = 0.001  # turn points into polygons


class Isochrones(BaseTravelTimeMatrix):
    """Compute polygons of equal travel time from a destination."""

    _r5py_attributes = BaseTravelTimeMatrix._r5py_attributes + [
        "_isochrones",
        "isochrones",
    ]

    def __init__(
        self,
        transport_network,
        origins=None,
        isochrones=pandas.timedelta_range(
            start=datetime.timedelta(minutes=0),
            end=datetime.timedelta(hours=1),
            freq=datetime.timedelta(minutes=15),
        ),
        point_grid_resolution=POINT_GRID_RESOLUTION,
        snap_to_network=False,
        **kwargs,
    ):
        """
        Compute polygons of equal travel time from one or more destinations.

        ``r5py.Isochrones`` are child classes of ``geopandas.GeoDataFrame`` and
        support all of their methods and properties, see
        https://geopandas.org/en/stable/docs.html

        Arguments
        ---------
        transport_network : r5py.TransportNetwork | tuple(str, list(str), dict)
            The transport network to route on. This can either be a readily
            initialised r5py.TransportNetwork or a tuple of the parameters
            passed to ``TransportNetwork.__init__()``: the path to an OpenStreetMap
            extract in PBF format, a list of zero of more paths to GTFS transport
            schedule files, and a dict with ``build_config`` options.
        origins : geopandas.GeoDataFrame | shapely.geometry.Point
            Place(s) to find a route _from_
            Must be/have a point geometry. If multiple origin points are passed,
            isochrones will be computed as minimum travel time from any of them.
        isochrones : pandas.TimedeltaIndex | collections.abc.Iterable[int]
            For which interval to compute isochrone polygons. An iterable of
            integers is interpreted as minutes.
        point_grid_resolution : int
            Base the isochrone computation on a grid of points with this
            distance
        snap_to_network : bool or int, default False
            Should origin an destination points be snapped to the street network
            before routing? If `True`, the default search radius (defined in
            `com.conveyal.r5.streets.StreetLayer.LINK_RADIUS_METERS`) is used,
            if `int`, use `snap_to_network` meters as the search radius.
        **kwargs : mixed
            Any arguments than can be passed to r5py.RegionalTask:
            ``departure``, ``departure_time_window``, ``percentiles``, ``transport_modes``,
            ``access_modes``, ``egress_modes``, ``max_time``, ``max_time_walking``,
            ``max_time_cycling``, ``max_time_driving``, ``speed_cycling``, ``speed_walking``,
            ``max_public_transport_rides``, ``max_bicycle_traffic_stress``
            Note that not all arguments might make sense in this context, and the
            underlying R5 engine might ignore some of them.
            If percentiles are specified, the lowest one will be used for
            isochrone computation.
        """
        geopandas.GeoDataFrame.__init__(self)
        BaseTravelTimeMatrix.__init__(
            self,
            transport_network,
            snap_to_network=snap_to_network,
            **kwargs,
        )

        self.EQUIDISTANT_CRS = GoodEnoughEquidistantCrs(self.transport_network.extent)

        if isinstance(origins, shapely.Geometry):
            origins = geopandas.GeoDataFrame(
                {
                    "id": [
                        "origin",
                    ],
                    "geometry": [
                        origins,
                    ],
                },
                crs=R5_CRS,
            )
        self.origins = origins
        self.destinations = self._regular_point_grid(
            self.transport_network.extent,
            point_grid_resolution,
        )
        self.isochrones = isochrones

        travel_times = TravelTimeMatrix(
            transport_network,
            origins=self.origins,
            destinations=self.destinations,
            snap_to_network=snap_to_network,
            max_time=self.isochrones.max(),
            **kwargs,
        )
        data = self._compute_isochrones_from_travel_times(travel_times)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            for column in data.columns:
                self[column] = data[column]
            self.set_geometry("geometry")

    def _compute_isochrones_from_travel_times(self, travel_times):
        travel_times = travel_times.dropna().groupby("to_id").min().reset_index()

        if self.request.percentiles == [50]:
            travel_time_column = "travel_time"
        else:
            travel_time_column = f"travel_time_p{self.request.percentiles[0]:d}"

        isochrones = {
            "travel_time": [],
            "geometry": [],
        }

        for isochrone in self.isochrones:
            reached_nodes = (
                self.destinations.set_index("id")
                .join(
                    travel_times[
                        travel_times[travel_time_column]
                        <= (isochrone.total_seconds() / 60)
                    ].set_index("to_id"),
                    how="inner",
                )
                .reset_index()
            )

            # isochrone polygons might be disjoint (e.g., around metro stops)
            if not reached_nodes.empty:
                reached_nodes = SpatiallyClusteredGeoDataFrame(reached_nodes)
                isochrone_polygons = shapely.unary_union(
                    [
                        (
                            geopandas.GeoSeries([group.geometry.union_all()])
                            .concave_hull(ratio=CONCAVE_HULL_RATIO)
                            .iat[0]
                        )
                        for _, group in (
                            reached_nodes[reached_nodes["cluster"] != -1].groupby(
                                "cluster"
                            )
                        )
                    ]
                    + list(
                        reached_nodes[reached_nodes["cluster"] == -1]
                        .geometry.to_crs(self.EQUIDISTANT_CRS)
                        .buffer(VERY_SMALL_BUFFER_SIZE)
                        .to_crs(R5_CRS)
                        .values
                    )
                )

                reached_nodes.to_file(
                    f"/tmp/reached_nodes_{isochrone.total_seconds() / 60:03.0f}.gpkg"
                )

                isochrones["travel_time"].append(isochrone)
                isochrones["geometry"].append(isochrone_polygons)

        isochrones = geopandas.GeoDataFrame(isochrones, geometry="geometry", crs=R5_CRS)
        isochrones["geometry"] = (
            isochrones["geometry"]
            .to_crs(self.EQUIDISTANT_CRS)
            .apply(
                lambda geometry: shapely.simplify(geometry, SIMPLIFICATION_TOLERANCE)
            )
            .buffer(CONCAVE_HULL_BUFFER_SIZE)
            .apply(
                lambda geometry: (
                    geometry
                    if isinstance(geometry, shapely.MultiPolygon)
                    else shapely.MultiPolygon([geometry])
                )
            )
            .to_crs(R5_CRS)
        )

        return isochrones

    @property
    def isochrones(self):
        """
        Compute isochrones for these travel times.

        pandas.TimedeltaIndex | collections.abc.Iterable[int]
        An iterable of integers is interpreted as minutes.
        """
        try:
            return self._isochrones
        except AttributeError:
            raise

    @isochrones.setter
    def isochrones(self, isochrones):
        if not isinstance(isochrones, pandas.TimedeltaIndex):
            isochrones = pandas.to_timedelta(isochrones, unit="minutes")
        self._isochrones = isochrones

    def _regular_point_grid(self, extent, resolution):
        # print(extent)
        extent = shapely.ops.transform(
            pyproj.Transformer.from_crs(
                R5_CRS,
                self.EQUIDISTANT_CRS,
                always_xy=True,
            ).transform,
            extent,
        )
        minx, miny, maxx, maxy = extent.bounds
        # print([minx, miny, maxx, maxy], resolution)
        points = [
            shapely.Point([x, y])
            for x in range(math.floor(minx), math.ceil(maxx), round(resolution))
            for y in range(math.floor(miny), math.ceil(maxy), round(resolution))
        ]
        grid = geopandas.GeoDataFrame(
            {
                "geometry": points,
            },
            crs=self.EQUIDISTANT_CRS,
        ).to_crs(R5_CRS)
        grid["id"] = grid.index

        # print(self.EQUIDISTANT_CRS, R5_CRS)
        # grid.to_file("/tmp/destinations.gpkg")
        # raise RuntimeError

        return grid
