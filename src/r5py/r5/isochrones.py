#!/usr/bin/env python3


"""Compute polygons of equal travel time from a destination."""


import datetime
import warnings

import geohexgrid
import geopandas
import pandas
import pyproj
import shapely
import simplification.cutil

from .base_travel_time_matrix import BaseTravelTimeMatrix
from .transport_mode import TransportMode
from .travel_time_matrix import TravelTimeMatrix
from ..util import GoodEnoughEquidistantCrs, SpatiallyClusteredGeoDataFrame


__all__ = ["Isochrones"]


EMPTY_POINT = shapely.Point()
R5_CRS = "EPSG:4326"

CONCAVE_HULL_BUFFER_SIZE = 20.0  # metres
CONCAVE_HULL_RATIO = 0.3

VERY_SMALL_BUFFER_SIZE = 0.001  # turn points into polygons


class Isochrones(BaseTravelTimeMatrix):
    """Compute polygons of equal travel time from a destination."""

    _r5py_attributes = BaseTravelTimeMatrix._r5py_attributes + [
        "_isochrones",
        "isochrones",
        "point_grid_resolution",
        "point_grid_sample_ratio",
    ]

    def __init__(
        self,
        transport_network,
        origins,
        isochrones=pandas.timedelta_range(
            start=datetime.timedelta(minutes=0),
            end=datetime.timedelta(hours=1),
            freq=datetime.timedelta(minutes=15),
        ),
        point_grid_resolution=100,
        point_grid_sample_ratio=1.0,
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
        origins : geopandas.GeoDataFrame | shapely.Point
            Place(s) to find a route _from_
            Must be/have a point geometry. If multiple origin points are passed,
            isochrones will be computed as minimum travel time from any of them.
        isochrones : pandas.TimedeltaIndex | collections.abc.Iterable[int]
            For which interval to compute isochrone polygons. An iterable of
            integers is interpreted as minutes.
        point_grid_resolution : int
            Distance in meters between points in the regular grid of points laid over the
            transport network’s extent that is used to compute isochrones.
            Increase this value for performance, decrease it for precision.
        point_grid_sample_ratio : float
            Share of points of the point grid that are used in computation,
            ranging from 0.01 to 1.0.
            Increase this value for performance, decrease it for precision.
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
        self.isochrones = isochrones

        self.point_grid_resolution = point_grid_resolution
        self.point_grid_sample_ratio = max(0.01, min(1.0, point_grid_sample_ratio))

        travel_times = TravelTimeMatrix(
            transport_network,
            origins=self.origins,
            destinations=self.destinations,
            max_time=self.isochrones.max(),
            **kwargs,
        )

        data = self._compute_isochrones_from_travel_times(travel_times)

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=(
                    "You are adding a column named 'geometry' to a GeoDataFrame "
                    "constructed without an active geometry column"
                ),
                category=FutureWarning,
            )
            for column in data.columns:
                self[column] = data[column]
            self.set_geometry("geometry")

        del self.transport_network

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
                reached_nodes = SpatiallyClusteredGeoDataFrame(
                    reached_nodes, eps=(2.0 * self.point_grid_resolution)
                ).to_crs(self.EQUIDISTANT_CRS)
                isochrone_polygons = pandas.concat(
                    [
                        (
                            reached_nodes[reached_nodes["cluster"] != -1]
                            .dissolve(by="cluster")
                            .concave_hull(ratio=CONCAVE_HULL_RATIO)
                            .buffer(VERY_SMALL_BUFFER_SIZE)
                        ),
                        (
                            reached_nodes[reached_nodes["cluster"] == -1].buffer(
                                VERY_SMALL_BUFFER_SIZE
                            )
                        ),
                    ]
                ).union_all()

                isochrones["travel_time"].append(isochrone)
                isochrones["geometry"].append(isochrone_polygons)

        isochrones = geopandas.GeoDataFrame(
            isochrones, geometry="geometry", crs=self.EQUIDISTANT_CRS
        )

        # clip smaller isochrones by larger isochrones
        # (concave_hull’s ratio parameter depends on input shapes and does not
        # produce the same results, e.g., around bridges or at the coast line)
        for row in range(len(isochrones) - 2, 0, -1):
            isochrones.loc[row, "geometry"] = shapely.intersection(
                isochrones.loc[row, "geometry"], isochrones.loc[row + 1, "geometry"]
            )

        isochrones["geometry"] = (
            isochrones["geometry"]
            .buffer(CONCAVE_HULL_BUFFER_SIZE)
            .boundary.apply(
                lambda geometry: (
                    geometry
                    if isinstance(geometry, shapely.MultiLineString)
                    else shapely.MultiLineString([geometry])
                )
            )
            .apply(
                lambda multilinestring: (
                    shapely.MultiLineString(
                        [
                            simplification.cutil.simplify_coords_vwp(
                                linestring.coords,
                                self.point_grid_resolution * 5.0,
                            )
                            for linestring in multilinestring.geoms
                        ]
                    )
                )
            )
            .to_crs(R5_CRS)
        )

        return isochrones

    @property
    def destinations(self):
        """A regular grid of points covering the range of the chosen transport mode."""
        try:
            return self._destinations
        except AttributeError:
            destinations = self._regular_point_grid
            destinations["geometry"] = self.transport_network.snap_to_network(
                destinations["geometry"]
            )
            destinations = destinations[destinations["geometry"] != EMPTY_POINT]
            destinations["geometry"] = destinations["geometry"].normalize()
            destinations = destinations.drop_duplicates()

            # with snapping, sometimes we end up with clumps of points
            # below, we try to form clusters, from all clusters we retain
            # one geometry, only
            destinations = SpatiallyClusteredGeoDataFrame(
                destinations, eps=(0.5 * self.point_grid_resolution)
            )
            destinations = pandas.concat(
                [
                    (
                        destinations[destinations["cluster"] != -1]
                        .groupby("cluster")
                        .first()
                        .set_crs(R5_CRS)
                    ),
                    destinations[destinations["cluster"] == -1],
                ]
            )[["id", "geometry"]].copy()

            if self.point_grid_sample_ratio < 1.0:
                destinations = destinations.sample(frac=self.point_grid_sample_ratio)

            self._destinations = destinations

            return destinations

    @destinations.setter
    def destinations(self, destinations):
        # https://bugs.python.org/issue14965
        super(self.__class__, self.__class__).destinations.__set__(self, destinations)

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
        try:
            # do not compute for 0 travel time
            isochrones = isochrones.drop(datetime.timedelta(0))
        except KeyError:
            pass
        self._isochrones = isochrones

    @property
    def _regular_point_grid(self):
        extent = shapely.ops.transform(
            pyproj.Transformer.from_crs(
                R5_CRS,
                self.EQUIDISTANT_CRS,
                always_xy=True,
            ).transform,
            self.transport_network.extent,
        )

        grid = geohexgrid.make_grid_from_bounds(
            *extent.bounds,
            self.point_grid_resolution,
            crs=self.EQUIDISTANT_CRS,
        )
        grid["geometry"] = grid["geometry"].centroid
        grid["id"] = grid.index
        grid = grid[["id", "geometry"]].to_crs(R5_CRS)

        # for walking and cycling, we can clip the extent to an area reachable
        # by the (well-defined) travel speeds:
        if set(self.request.transport_modes) <= set(
            (TransportMode.WALK, TransportMode.BICYCLE)
        ):
            if TransportMode.WALK in self.request.transport_modes:
                speed = self.request.speed_walking
            if TransportMode.BICYCLE in self.request.transport_modes:
                speed = self.request.speed_cycling

            speed = speed * (1000.0 / 3600.0) * 1.1  # km/h -> m/s, plus a bit of buffer

            grid = grid.clip(
                (
                    pandas.concat([self.origins] * 2)  # workaround until
                    # https://github.com/pyproj4/pyproj/issues/1309 is fixed
                    .to_crs(self.EQUIDISTANT_CRS)
                    .buffer(speed * max(self.isochrones).total_seconds())
                    .to_crs(R5_CRS)
                )
            )

        return grid.copy()
