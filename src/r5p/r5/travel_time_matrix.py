#!/usr/bin/env python3

"""Calculate travel times between many origins and destinations."""

import math
import multiprocessing

import joblib
import numpy
import pandas

from .. import util  # noqa: F401
from .transport_network import TransportNetwork
from .regional_task import RegionalTask

import com.conveyal.r5


__all__ = ["TravelTimeMatrix"]


# R5 fills cut-off values with MAX_INT32
MAX_INT32 = (2 ** 31) - 1

# how many (Python) threads to start
# (they still run many Java threads, so be careful what you wish for ;) )
# TODO: benchmark the optimum
NUM_THREADS = math.ceil(multiprocessing.cpu_count() / 2)


class TravelTimeMatrix:
    """Calculate travel times between many origins and destinations."""

    def __init__(
            self,
            transport_network,
            origins,
            destinations=None,
            **kwargs
    ):
        """
        Load a transport network.

        Arguments
        ---------
        transport_network : r5p.r5.TransportNetwork | tuple(str, list(str), dict)
            The transport network to route on. This can either be a readily
            initialised `r5p.r5.TransportNetwork` or a tuple of the parameters
            passed to `TransportNetwork.__init__()`: the path to an OpenStreetMap
            extract in PBF format, a list of zero of more paths to GTFS transport
            schedule files, and a dict with `build_config` options.
        origins : geopandas.GeoDataFrame
            Points to route _from_
            Has to have a point geometry, and at least an `id` column
        destinations : geopandas.GeoDataFrame (optional)
            Points to route _to_
            Has to have a point geometry, and at least an `id` column
            If omitted, use same data set as for origins
        **kwargs : mixed
            Any arguments than can be passed to `r5p.r5.RegionalTask`,
            i.e., `departure`, `departure_time_window`, `transport_modes`,
            `access_modes`, `egress_modes`, `max_time`, `max_time_walking`,
            `max_time_cycling`, `max_time_driving`, `speed_walking`, `speed_cycling`,
            `speed_walking`, `max_public_transport_rides`, `max_bicycle_traffic_stress`
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
            origins.iloc[0].geometry,  # just one origin to pass through __init__
            destinations,
            **kwargs
        )

        self.verbose = util.config.arguments().verbose

    def compute_travel_times(self):
        """
        Compute travel times from all origins to all destinations.

        Returns
        -------
        pandas.DataFrame
            A data frame containing the columns `from_id`, `to_id`, and `travel_time`,
            where `travel_time` is the calculated travel time between `from_id` and
            `to_id` or `numpy.nan` if no connection with the given parameters (max_time!)
            was found.
        """
        # for this following section, there must exist a more elegant and
        # efficient way, such as groupby().apply() or something, but this
        # is quick and straightforward for now

        od_matrix = pandas.DataFrame({
            "from_id": pandas.Series(dtype=str),
            "to_id": pandas.Series(dtype=str),
            "travel_time": pandas.Series(dtype=float)
        })

        # loop over all origins, modify the request, and compute the times
        # to all destinations.
        with joblib.Parallel(
                prefer="threads",
                verbose=(10 * self.verbose),
                n_jobs=NUM_THREADS
        ) as parallel:
            od_matrix = pandas.concat(
                parallel(
                    joblib.delayed(self._travel_times_from_one_origin)(from_id)
                    for from_id in self.origins.id
                )
            )

        od_matrix = self.__class__._set_cutoff_travel_times_to_nan(od_matrix)
        return od_matrix

    def _travel_times_from_one_origin(self, from_id):
        self.request.origin = self.origins[self.origins.id == from_id].geometry

        travel_time_computer = com.conveyal.r5.analyst.TravelTimeComputer(
            self.request, self.transport_network
        )
        travel_times = travel_time_computer.computeTravelTimes().travelTimes.getValues()[0]

        od_matrix = pandas.DataFrame({
            "from_id": pandas.Series(dtype=str),
            "to_id": pandas.Series(dtype=str),
            "travel_time": pandas.Series(dtype=float)
        })
        od_matrix["to_id"] = self.destinations.id
        od_matrix["travel_time"] = travel_times
        od_matrix["from_id"] = from_id

        return od_matrix

    @staticmethod
    def _set_cutoff_travel_times_to_nan(od_matrix):
        od_matrix[od_matrix.travel_time == MAX_INT32] = (
            od_matrix[od_matrix.travel_time == MAX_INT32].assign(travel_time=numpy.nan)
        )
        return od_matrix
