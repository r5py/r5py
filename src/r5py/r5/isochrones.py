#!/usr/bin/env python3


"""Compute polygons of equal travel time from a destination."""


import copy
import warnings

try:
    from warnings import deprecated
except ImportError:  # Python<=3.12
    from typing_extensions import deprecated

import geopandas
import joblib
import pandas

from .base_travel_time_matrix import BaseTravelTimeMatrix
from .trip import Trip
from .trip_planner import ACCURATE_GEOMETRIES, TripPlanner


__all__ = ["Isochrones"]


class Isochrones(BaseTravelTimeMatrix):
    """Compute polygons of equal travel time from a destination."""

    COLUMNS = ["from_id", "to_id", "option"] + Trip.COLUMNS

    _r5py_attributes = BaseTravelTimeMatrix._r5py_attributes + [
        "all_to_all",
        "od_pairs",
    ]

    def __init__(
        self,
        transport_network,
        origin=None,
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
            Not that not all arguments might make sense in this context, and the
            underlying R5 engine might ignore some of them.
        """
        super().__init__(
            transport_network,
            origin,
            snap_to_network,
            **kwargs,
        )

        data = self._compute()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            for column in data.columns:
                self[column] = data[column]
            self.set_geometry("geometry")

    def _compute(self):
        """
        Compute TODO

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
        return geopandas.GeoDataFrame({})
