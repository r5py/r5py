#!/usr/bin/env python3

"""Calculate travel times between many origins and destinations."""

import copy

import pandas

from .base_travel_time_matrix_computer import BaseTravelTimeMatrixComputer
from ..util import start_jvm

import com.conveyal.r5


__all__ = ["TravelTimeMatrixComputer"]


start_jvm()


class TravelTimeMatrixComputer(BaseTravelTimeMatrixComputer):
    """Compute travel times between many origins and destinations."""

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
        self._prepare_origins_destinations()
        self.request.destinations = self.destinations

        od_matrix = pandas.concat(
            [self._travel_times_per_origin(from_id) for from_id in self.origins.id],
            ignore_index=True,
        )

        try:
            od_matrix = od_matrix.to_crs(self._origins_crs)
        except AttributeError:  # (not a GeoDataFrame)
            pass
        return od_matrix

    def _parse_results(self, from_id, results):
        """
        Parse the results of an R5 TravelTimeMatrix.

        Parse data as returned from `com.conveyal.r5.analyst.TravelTimeComputer.computeTravelTimes()`,
        cast data to Python types, and return as a `pandas.Dataframe`. Because of the way r5py
        and R5 interact, this parses the results of routing from one origin to many (all) destinations.

        Arguments
        ---------
        from_id : mixed
            The value of the ID column of the origin record to report on.
        results : `com.conveyal.r5.OneOriginResult` (Java object)

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
        # First, create an empty DataFrame (this forces column types)
        travel_time_columns = {
            "from_id": pandas.Series(dtype=str),
            "to_id": pandas.Series(dtype=str),
        }
        travel_time_columns.update(
            {
                f"travel_time_p{percentile:d}": pandas.Series(dtype=float)
                for percentile in self.request.percentiles
            }
        )
        od_matrix = pandas.DataFrame(travel_time_columns)

        # first assign columns with correct length (`to_id`),
        # only then fill `from_id` (it’s a scalar)
        od_matrix["to_id"] = self.destinations.id
        od_matrix["from_id"] = from_id

        for p, percentile in enumerate(self.request.percentiles):
            travel_times = results.travelTimes.getValues()[p]
            od_matrix[f"travel_time_p{percentile:d}"] = travel_times

        # rename percentile column if only median requested (the default)
        if self.request.percentiles == [50]:
            od_matrix = od_matrix.rename(columns={"travel_time_p50": "travel_time"})

        # R5’s NULL value is MAX_INT32
        od_matrix = self._fill_nulls(od_matrix)

        # re-index (and don’t keep the old index as a new column)
        od_matrix = od_matrix.reset_index(drop=True)

        return od_matrix

    def _travel_times_per_origin(self, from_id):
        request = copy.copy(self.request)
        request.origin = self.origins[self.origins.id == from_id].geometry.item()

        travel_time_computer = com.conveyal.r5.analyst.TravelTimeComputer(
            request, self.transport_network
        )
        results = travel_time_computer.computeTravelTimes()

        od_matrix = self._parse_results(from_id, results)

        return od_matrix
