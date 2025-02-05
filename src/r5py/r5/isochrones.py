#!/usr/bin/env python3


"""Compute polygons of equal travel time from a destination."""


import datetime
import warnings

import geopandas
import pandas
import shapely

from .base_travel_time_matrix import BaseTravelTimeMatrix
from .travel_time_matrix import TravelTimeMatrix
from ..util import GoodEnoughEquidistantCrs


__all__ = ["Isochrones"]


CONCAVE_HULL_RATIO = 0.2
CONCAVE_HULL_BUFFER = 5.0  # metres
R5_CRS = "EPSG:4326"


class Isochrones(BaseTravelTimeMatrix):
    """Compute polygons of equal travel time from a destination."""

    _r5py_attributes = BaseTravelTimeMatrix._r5py_attributes + [
        "_isochrones",
        "isochrones",
        "_travel_times",
    ]

    def __init__(
        self,
        transport_network,
        origin=None,
        isochrones=pandas.timedelta_range(
            start=datetime.timedelta(minutes=0),
            end=datetime.timedelta(hours=1),
            freq=datetime.timedelta(minutes=15),
        ),
        snap_to_network=False,
        **kwargs,
    ):
        """
        Compute polygons of equal travel time from a destination.

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
        origin : geopandas.GeoDataFrame | shapely.geometry.Point
            Place to find a route _from_
            Has to be/have a point geometry
        isochrones : pandas.TimedeltaIndex | collections.abc.Iterable[int]
            For which interval to compute isochrone polygons. An iterable of
            integers is interpreted as minutes.
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
            origins=None,
            destinations=None,
            snap_to_network=snap_to_network,
            **kwargs,
        )

        if isinstance(origin, shapely.Geometry):
            origin = geopandas.GeoDataFrame(
                {
                    "id": ["origin"],
                    "geometry": [origin],
                },
                crs=R5_CRS,
            )
        self.origins = origin

        self.destinations = self.request.transport_network.nodes

        self.isochrones = isochrones

        # print(transport_network.nodes)
        # raise RuntimeError

        self._travel_times = TravelTimeMatrix(
            transport_network,
            origins=self.origins,
            destinations=self.destinations,
            snap_to_network=snap_to_network,
            max_time=self.isochrones.max(),
            **kwargs,
        )

        self.EQUIDISTANT_CRS = GoodEnoughEquidistantCrs(self.transport_network.extent)

        data = self._compute()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            for column in data.columns:
                self[column] = data[column]
            self.set_geometry("geometry")

    def _compute(self):
        """
        Compute TODO.

        Returns
        -------
        geopandas.GeoDataFrame

            TODO TODO TODO

            The resulting detailed routes. For each origin/destination pair,
            multiple route alternatives (‘options’) might be reported that each
            consist of one or more segments. Each segment represents one row.
            multiple route alternatives (‘options’) might be reported that each consist of
            one or more segments. Each segment represents one row.

            The data frame comprises of the following columns: `from_id`,
            `to_id`, `option` (`int`), `segment` (`int`), `transport_mode`
            (`r5py.TransportMode`), `departure_time` (`datetime.datetime`),
            `distance` (`float`, metres), `travel_time` (`datetime.timedelta`),
            `wait_time` (`datetime.timedelta`), `feed` (`str`, the feed name
            used), `agency_id` (`str` the public transport agency identifier),
            `route_id` (`str`, public transport route ID), `start_stop_id`
            (`str`, the GTFS stop_id for boarding), `end_stop_id` (`str`, the
            GTFS stop_id for alighting), `geometry` (`shapely.LineString`)
        """
        travel_times = self._travel_times.dropna()

        if self.request.percentiles == [50]:
            travel_time_column = "travel_time"
        else:
            travel_time_column = f"travel_time_p{self.request_percentile[0]:d}"

        isochrones = {
            "travel_time": [],
            "geometry": [],
        }

        for isochrone in self.isochrones:
            reached_nodes = self.destinations.set_index("id").join(
                travel_times[
                    travel_times[travel_time_column] <= (isochrone.total_seconds() / 60)
                ].set_index("to_id"),
                how="inner",
            )
            isochrones["travel_time"].append(isochrone)
            isochrones["geometry"].append(
                geopandas.GeoSeries([reached_nodes.geometry.union_all()])
                .concave_hull(ratio=CONCAVE_HULL_RATIO)
                .iat[0]
            )

        isochrones = geopandas.GeoDataFrame(isochrones, geometry="geometry", crs=R5_CRS)
        isochrones["geometry"] = (
            isochrones["geometry"]
            .to_crs(self.EQUIDISTANT_CRS)
            .buffer(CONCAVE_HULL_BUFFER)
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
