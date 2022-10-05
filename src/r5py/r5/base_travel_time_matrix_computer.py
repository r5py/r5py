#!/usr/bin/env python3

"""Calculate travel times between many origins and destinations."""

import math
import multiprocessing

import joblib
import numpy
import pandas

from ..util import check_od_data_set, config
from .regional_task import RegionalTask
from .transport_network import TransportNetwork

import com.conveyal.r5


__all__ = ["BaseTravelTimeMatrixComputer"]


# R5 fills cut-off (NULL) values with MAX_INT32
MAX_INT32 = (2**31) - 1

# how many (Python) threads to start
# (they still run many Java threads, so be careful what you wish for ;) )
# TODO: benchmark the optimal number of threads
NUM_THREADS = math.ceil(multiprocessing.cpu_count() * 0.75)


class BaseTravelTimeMatrixComputer:
    """Base class for travel time computers between many origins and destinations."""

    def __init__(
        self,
        transport_network,
        origins,
        destinations=None,
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

        self.origins = origins
        if destinations is None:
            destinations = origins
        self.destinations = destinations

        self.request = RegionalTask(
            transport_network,
            origins.iloc[0].geometry,  # any one origin (potentially overriden later)
            destinations,
            **kwargs,
        )

        self.verbose = config.arguments().verbose

    def compute_travel_times(self):
        """
        Compute travel times from all origins to all destinations.

        Returns
        -------
        pandas.DataFrame
            A data frame containing the columns ``from_id``, ``to_id``, and
            ``travel_time``, where ``travel_time`` is the median calculated
            travel time between ``from_id`` and ``to_id`` or ``numpy.nan``
            if no connection with the given parameters was found.
            If non-default ``percentiles`` were requested: one or more columns
            ``travel_time_p{:02d}`` representing the particular percentile of
            travel time.
        """
        # loop over all origins, modify the request, and compute the times
        # to all destinations.
        with joblib.Parallel(
            prefer="threads",
            verbose=(10 * self.verbose),  # joblib has a funny verbosity scale
            n_jobs=NUM_THREADS,
        ) as parallel:
            od_matrix = pandas.concat(
                parallel(
                    joblib.delayed(self._travel_times_per_origin)(from_id)
                    for from_id in self.origins.id
                )
            )

        try:
            od_matrix = od_matrix.to_crs(self._origins_crs)
        except AttributeError:  # (not a GeoDataFrame)
            pass
        return od_matrix

    @property
    def destinations(self):
        return self._destinations

    @destinations.setter
    def destinations(self, destinations):
        check_od_data_set(destinations)
        self._destinations = destinations.to_crs("EPSG:4326")

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
        return data_set.applymap(lambda x: numpy.nan if x == MAX_INT32 else x)

    @property
    def origins(self):
        return self._origins

    @origins.setter
    def origins(self, origins):
        check_od_data_set(origins)
        self._origins_crs = origins.crs
        self._origins = origins.to_crs("EPSG:4326")

    def _travel_times_per_origin(self, from_id):
        # TODO: check whether this following line could cause race conditions
        self.request.origin = self.origins[self.origins.id == from_id].geometry

        travel_time_computer = com.conveyal.r5.analyst.TravelTimeComputer(
            self.request, self.transport_network
        )
        results = travel_time_computer.computeTravelTimes()

        od_matrix = self._parse_results(from_id, results)

        return od_matrix
