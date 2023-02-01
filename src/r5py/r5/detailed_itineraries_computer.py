#!/usr/bin/env python3

"""Calculate detailed itineraries between many origins and destinations."""

import pandas

from .breakdown_stat import BreakdownStat
from .travel_time_matrix_computer import TravelTimeMatrixComputer


__all__ = ["DetailedItinerariesComputer"]


# Which columns (and types) are returned by
# com.conveyal.r5.analyst.cluster.PathResult.summarizeIterations?
# Note that these are already camel_case (Python) names and pandas/numpy (d)types.
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


class DetailedItinerariesComputer(TravelTimeMatrixComputer):
    """Compute detailed itineraries between many origins and destinations."""

    def __init__(
        self,
        transport_network,
        origins,
        destinations=None,
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
        breakdown_stat : r5py.BreakdownStat
            Summarise the values of the detailed breakdown using this statistical function.
            Default: r5py.BreakdownStat.MEAN
        **kwargs : mixed
            Any arguments than can be passed to r5py.RegionalTask:
            ``departure``, ``departure_time_window``, ``percentiles``, ``transport_modes``,
            ``access_modes``, ``egress_modes``, ``max_time``, ``max_time_walking``,
            ``max_time_cycling``, ``max_time_driving``, ``speed_cycling``, ``speed_walking``,
            ``max_public_transport_rides``, ``max_bicycle_traffic_stress``
        """
        super().__init__(transport_network, origins, destinations, **kwargs)

        self.request.breakdown = self.breakdown = True
        self.breakdown_stat = breakdown_stat

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
            Detailed information about the routes found is reported in the
            columns ``routes`` (route numbers of public transport lines),
            ``board_stops`` and ``alight_stops`` (public transport stops at
            which a vehicle/line is boarded or alighted), ``ride_times`` (times
            aboard a public transport vehicle or line), ``access_time`` (time
            to reach the road (when on car or bicycle) or the first public transport
            stop from ``from_id``), ``egress_time`` (time from road or last
            public transport stop to ``to_id``), ``total_time`` (overall travel
            time), and ``n_iterations`` (number of McRAPTOR iterations used).
            If non-default ``percentiles`` were requested: one or more columns
            ``travel_time_p{:02d}`` representing the particular percentile of
            travel time.

        """
        return super().compute_travel_times()

    def _parse_results(self, from_id, results):
        """
        Parse the *detailed* results of an R5 TravelTimeMatrix.

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
            detailed information about the routes, reported in the
            columns ``routes`` (route numbers of public transport lines),
            ``board_stops`` and ``alight_stops`` (public transport stops at
            which a vehicle/line is boarded or alighted), ``ride_times`` (times
            aboard a public transport vehicle or line), ``access_time`` (time
            to reach the road (when on car or bicycle) or the first public transport
            stop from ``from_id``), ``egress_time`` (time from road or last
            public transport stop to ``to_id``), ``total_time`` (overall travel
            time), and ``n_iterations`` (number of McRAPTOR iterations used).

            Results can contain more than one row per ``from_id``/``to_id`` pair.
        """
        # Let’s start with an empty DataFrame with the correct columns (and types)
        columns = {
            "from_id": [],
            "to_id": [],
        }
        columns.update(
            {
                column_name: pandas.Series(dtype=column_type)
                for column_name, column_type in DATA_COLUMNS.items()
            }
        )
        od_matrix = pandas.DataFrame(columns)

        # R5 returns multiple rows per O/D-pair, in a nested array
        # (first dimension == to_id, second dimension == different
        # routes for O/D pair, third dimension == data records)
        #
        # On top of that, some of the columns are arrays themselves,
        # and are represented as a pipe-separated string
        #
        # typically, data look something like this:
        #
        # [
        #   [
        #      ['1002|1003', '1020446|1090415', '1090415|1070417', '6.0|1.0', '7.3', '3.7', '0.0', '1.3|2.0', '21.3', '1']  # noqa: E501
        #       ...
        #   ],
        #    ...
        # ]

        # First, unnest the data, and add `from_id` and `to_id` to each row
        # (After this, we have a 2dim table of several rows per O/D pair)
        details = [
            [from_id, to_id] + list(row)
            for to_id, record in zip(
                self.destinations.id,
                results.paths.summarizeIterations(self.breakdown_stat.value),
            )
            for row in record
        ]

        # Because casting directly from jpype’s Java types does not always work
        # perfectly (probably because the Python types/‘cast function’ accept
        # mixed values, so jpype cannot decide), let’s just cast _everything_ to
        # ‘nullable’ `str` to be on the safe side
        details = [
            [None if value is None else str(value) for value in row] for row in details
        ]

        # Then, cast the data to Python types, and split the pipe-separated arrays
        #
        # We do this by column, because it should be fast in pandas, and because
        # more legible and comprehensible what we do.
        # (`zip(*details)` transposes rows and columns)
        details = list(zip(*details))
        od_matrix["from_id"] = details[0]
        od_matrix["to_id"] = details[1]

        for column_name, column_type, column_data in zip(
            DATA_COLUMNS.keys(),
            DATA_COLUMNS.values(),
            details[2:],
        ):
            # split the array columns (they are pipe-separated strings)
            # also, cast to destination type
            if isinstance(column_type, pandas.SparseDtype):
                column_data = [
                    [
                        column_type.subtype.type(array_member_value)  # cast
                        if array_member_value
                        else None  # if False-ish -> None
                        for array_member_value in value.split("|")
                    ]
                    if value is not None
                    else []
                    for value in column_data
                ]
            else:
                column_data = [
                    column_type(value) if value else None  # cast (nullable)
                    for value in column_data
                ]

            od_matrix[column_name] = column_data

        return od_matrix
