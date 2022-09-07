#!/usr/bin/env python3

"""Calculate travel times between many origins and destinations."""

import math
import multiprocessing

import joblib
import numpy
import pandas

from ..util import check_od_data_set, config
from ..util.exceptions import NonUniqueIDError, NoIDColumnError
from .breakdown_stat import BreakdownStat
from .regional_task import RegionalTask
from .transport_network import TransportNetwork

import com.conveyal.r5


__all__ = ["TravelTimeMatrixComputer"]


# R5 fills cut-off values with MAX_INT32
MAX_INT32 = (2**31) - 1

# how many (Python) threads to start
# (they still run many Java threads, so be careful what you wish for ;) )
# TODO: benchmark the optimal number of threads
NUM_THREADS = math.ceil(multiprocessing.cpu_count() * 0.75)

# Which columns (and types) are returned by
# com.conveyal.r5.analyst.cluster.PathResult.summarizeIterations?
# Note that these are already camel_case names and pandas/numpy (d)types.
DATA_COLUMNS = {
    "routes": pandas.SparseDtype(str),
    "board_stops": pandas.SparseDtype(str),
    "alight_stops": pandas.SparseDtype(str),
    "ride_times": pandas.SparseDtype(float),
    "access_time": float,
    "egress_time": float,
    "transfer_time": float,
    "wait_times": pandas.SparseDtype(float),
    "total_time": float,
    "n_iterations": int,
}


class TravelTimeMatrixComputer:
    """Compute travel times between many origins and destinations."""

    def __init__(
        self,
        transport_network,
        origins,
        destinations=None,
        breakdown=False,
        breakdown_stat=BreakdownStat.MEAN,
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
        breakdown : bool
            Return a more detailed breakdown of the routing results.
            Default: False
        breakdown_stat : r5py.BreakdownStat
            Summarise the values of the detailed breakdown using this statistical function.
            Default: r5py.BreakdownStat.MEAN
        **kwargs : mixed
            Any arguments than can be passed to r5py.RegionalTask:
            ``departure``, ``departure_time_window``, ``percentiles``, ``transport_modes``,
            ``access_modes``, ``egress_modes``, ``max_time``, ``max_time_walking``,
            ``max_time_cycling``, ``max_time_driving``, ``speed_cycling``, ``speed_walking``,
            ``max_public_transport_rides``, ``max_bicycle_traffic_stress``, ``breakdown``
        """
        if not isinstance(transport_network, TransportNetwork):
            transport_network = TransportNetwork(*transport_network)
        self.transport_network = transport_network

        check_od_data_set(origins)
        self.origins = origins

        if destinations is None:
            destinations = origins
        else:
            # only check destinations when it’s
            # different from origins (already checked)
            check_od_data_set(destinations)
        self.destinations = destinations

        self.breakdown = breakdown
        self.breakdown_stat = breakdown_stat

        # R5 has a maximum number of destinations for which
        # it returns detailed information, and it’s set
        # at 5000 by default. The value is a static property
        # of com.conveyal.r5.analyst.cluster.PathResult;
        # static properites of Java classes can be modified
        # in a singleton kind of way?)
        if breakdown:
            com.conveyal.r5.analyst.cluster.PathResult.maxDestinations = (
                len(destinations) + 1
            )

        self.request = RegionalTask(
            transport_network,
            origins.iloc[0].geometry,  # just one origin to pass through __init__
            destinations,
            breakdown=breakdown,
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
            If ``breakdown=True``: in addition to the columns above
            ``routes``, ``board_stops``, ``alight_stops``, ``ride_times``,
            ``access_time``, ``egress_time``, ``transfer_time``, ``wait_times``,
            ``total_time``, ``n_iterations``.

        """
        # for this following section, there must exist a more elegant and
        # efficient way, such as groupby().apply() or something, but this
        # is quick and straightforward for now

        # loop over all origins, modify the request, and compute the times
        # to all destinations.
        with joblib.Parallel(
            prefer="threads",
            verbose=(10 * self.verbose),  # joblib has a funny verbosity scale
            n_jobs=NUM_THREADS,
        ) as parallel:
            od_matrix = pandas.concat(
                parallel(
                    joblib.delayed(self._travel_times_from_one_origin)(from_id)
                    for from_id in self.origins.id
                )
            )

        return od_matrix

    def _parse_results_of_one_origin_details(self, from_id, results):
        od_matrix = pandas.DataFrame(
            {
                column_name: pandas.Series(dtype=column_type)
                for column_name, column_type in DATA_COLUMNS.items()
            }
        )

        # `details` is a ‘jagged’ Java array, i.e., can have incomplete/omitted/empty rows.
        # That’s why simply transposing the row-indexed data into columns using
        # `zip(*details)` does not work as expected
        # On top of that, non-empty rows seem to be wrapped in yet another array dimension.

        # Our strategy here is to first fill in empty rows with NULL values and
        # cast values to Python `str`, and only then transposing

        details = results.paths.summarizeIterations(self.breakdown_stat.value)

        _EMPTY_ROW = [None] * len(DATA_COLUMNS)
        details = [
            [str(value) if value else None for record in row for value in record]
            if row
            else _EMPTY_ROW
            for row in details
        ]

        for ((column_name, column_type), column_data) in zip(
            DATA_COLUMNS.items(), zip(*details)  # transpose data
        ):
            # split the array columns (they are pipe-separated strings)
            # also, cast to destination type

            # note, that `pandas.SparseDtype(str).subtype` defaults to dtype('O')
            # fortunately, we get str, which remains a character string when
            # cast to dtype('O')

            if isinstance(column_type, pandas.SparseDtype):
                column_data = [
                    [
                        column_type.subtype.type(value)  # cast
                        for value in row.split("|")
                    ]
                    if row is not None
                    else []
                    for row in column_data
                ]
            else:
                column_data = [
                    column_type(row) if row is not None else None  # cast
                    for row in column_data
                ]

            od_matrix[column_name] = column_data

        return od_matrix

    def _parse_results_of_one_origin_travel_times(self, from_id, results):
        # return travel times only

        # create the columns in order to force dtypes
        if self.request.percentiles == [50]:
            # if we’re only interested in the default (the median)
            travel_time_columns = {"travel_time": pandas.Series(dtype=float)}
        else:
            travel_time_columns = {
                f"travel_time_p{percentile:d}": pandas.Series(dtype=float)
                for percentile in self.request.percentiles
            }
        od_matrix = pandas.DataFrame(
            {
                "from_id": pandas.Series(dtype=str),
                "to_id": pandas.Series(dtype=str),
            }
            | travel_time_columns
        )

        # first assign columns with correct length (not the scalar `from_id`)
        od_matrix["to_id"] = self.destinations.id
        od_matrix["from_id"] = from_id

        if self.request.percentiles == [50]:
            # we name the column differently when it’s exactly the median
            travel_times = results.travelTimes.getValues()[0]
            od_matrix["travel_time"] = travel_times
        else:
            for (p, percentile) in enumerate(self.request.percentiles):
                travel_times = results.travelTimes.getValues()[p]
                od_matrix[f"travel_time_p{percentile:d}"] = travel_times

        # R5’s NULL value is MAX_INT32
        od_matrix = od_matrix.applymap(lambda x: numpy.nan if x == MAX_INT32 else x)

        # re-index (and don’t keep the old index as a new column)
        od_matrix = od_matrix.reset_index(drop=True)

        return od_matrix

    def _travel_times_from_one_origin(self, from_id):
        self.request.origin = self.origins[self.origins.id == from_id].geometry

        travel_time_computer = com.conveyal.r5.analyst.TravelTimeComputer(
            self.request, self.transport_network
        )
        results = travel_time_computer.computeTravelTimes()

        od_matrix = self._parse_results_of_one_origin_travel_times(from_id, results)

        if self.breakdown:
            od_matrix = od_matrix.join(
                self._parse_results_of_one_origin_details(from_id, results)
            )

        return od_matrix
