#!/usr/bin/env python3

"""Calculate travel times between many origins and destinations."""

import math
import multiprocessing
import warnings

import numpy
import shapely

from ..util import check_od_data_set, Config
from .regional_task import RegionalTask
from .transport_network import TransportNetwork


__all__ = ["BaseTravelTimeMatrixComputer"]


# R5 fills cut-off (NULL) values with MAX_INT32
MAX_INT32 = (2**31) - 1

# how many (Python) threads to start
# (they still run many Java threads, so be careful what you wish for ;) )
# TODO: benchmark the optimal number of threads
NUM_THREADS = math.ceil(multiprocessing.cpu_count() * 0.5)


class BaseTravelTimeMatrixComputer:
    """Base class for travel time computers between many origins and destinations."""

    MAX_INT32 = MAX_INT32

    NUM_THREADS = NUM_THREADS

    def __init__(
        self,
        transport_network,
        origins=None,
        destinations=None,
        snap_to_network=False,
        **kwargs,
    ):
        """
        Compute travel times between many origins and destinations.

        Arguments
        ---------
        transport_network : r5py.TransportNetwork | tuple(str, list(str), dict)
            The transport network to route on. This can either be a readily
            initialised r5py.TransportNetwork or a tuple of the parameters
            passed to ``TransportNetwork.__init__()``: the path to an OpenStreetMap
            extract in PBF format, a list of zero of more paths to GTFS transport
            schedule files, and a dict with ``build_config`` options.
        origins : geopandas.GeoDataFrame
            Places to find a route _from_
            Has to have a point geometry, and at least an `id` column
        destinations : geopandas.GeoDataFrame (optional)
            Places to find a route _to_
            Has to have a point geometry, and at least an `id` column
            If omitted, use same data set as for origins
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
        """
        if not isinstance(transport_network, TransportNetwork):
            transport_network = TransportNetwork(*transport_network)
        self.transport_network = transport_network

        self.snap_to_network = snap_to_network

        self.origins = origins
        self.destinations = destinations

        self.request = RegionalTask(
            transport_network,
            origin=None,
            destinations=None,
            **kwargs,
        )

        self.verbose = Config().arguments.verbose

    @property
    def destinations(self):
        """The destinations of this travel time matrix (`geopandas.GeoDataFrame`)."""
        return self._destinations

    @destinations.setter
    def destinations(self, destinations):
        if destinations is not None:
            check_od_data_set(destinations)
            self._destinations_crs = destinations.crs
            self._destinations = destinations.to_crs("EPSG:4326").copy()

    def _fill_nulls(self, data_set):
        """
        Fill NULL values in a data set returned from R5.

        R5 uses `MAX_INT32` as a marker for NULL values, this function
        replaces those values in `data_set` with `numpy.nan`

        Arguments
        ---------
        data_set : pandas.DataFrame
            Data frame in which NULLs are represented by MAX_INT32

        Returns
        -------
        pandas.DataFrame
            Data frame in which all MAX_INT32 have been replaced by `numpy.nan`.
        """
        return data_set.map(lambda x: numpy.nan if x == MAX_INT32 else x)

    def _prepare_origins_destinations(self):
        """Make sure we received enough information to route from origins to destinations."""
        try:
            self.origins
        except AttributeError as exception:
            raise ValueError("No routing origins defined") from exception

        try:
            self.destinations
            assert self.destinations is not None
        except (AssertionError, AttributeError):
            self.destinations = self.origins.copy()
            if self.verbose:
                warnings.warn(
                    "No routing destinations defined, using origins as destinations, too.",
                    RuntimeWarning,
                )

        if self.snap_to_network:
            for which_end in ("origins", "destinations"):
                points = getattr(self, f"_{which_end}")
                points.geometry = self.transport_network.snap_to_network(
                    points.geometry
                )
                if len(points[points.geometry == shapely.Point()]):
                    # if there are origins/destinations for which no snapped point could be found
                    points = points[points.geometry != shapely.Point()]
                    warnings.warn(
                        f"Some {which_end[:-1]} points could not be snapped to the street network",
                        RuntimeWarning,
                    )

                    if points.empty:
                        raise ValueError(
                            f"After snapping, no valid {which_end[:-1]} points remain"
                        )

                setattr(self, f"_{which_end}", points.copy())

            self.snap_to_network = False  # prevent repeated snapping on same point sets

    @property
    def origins(self):
        """The origins of this travel time matrix (`geopandas.GeoDataFrame`)."""
        return self._origins

    @origins.setter
    def origins(self, origins):
        if origins is not None:
            check_od_data_set(origins)
            self._origins_crs = origins.crs
            self._origins = origins.to_crs("EPSG:4326").copy()
