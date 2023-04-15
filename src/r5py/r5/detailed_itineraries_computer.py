#!/usr/bin/env python3


"""Calculate detailed itineraries between many origins and destinations."""


import copy
import warnings

import joblib
import pandas

from .base_travel_time_matrix_computer import BaseTravelTimeMatrixComputer
from .trip import Trip
from .trip_planner import TripPlanner


__all__ = ["DetailedItinerariesComputer"]


class DetailedItinerariesComputer(BaseTravelTimeMatrixComputer):
    """Compute detailed itineraries between many origins and destinations."""

    COLUMNS = ["from_id", "to_id", "option"] + Trip.COLUMNS

    def __init__(
        self,
        transport_network,
        origins,
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
            Not that not all arguments might make sense in this context, and the
            underlying R5 engine might ignore some of them.
        """
        super().__init__(
            transport_network,
            origins,
            destinations,
            snap_to_network,
            **kwargs,
        )

        if destinations is None or len(origins) != len(destinations):
            # in case no destinations were specified, super().__init__() copied origins over to destinations

            # manually create a list of all all-to-all permutations
            self.od_pairs = self.origins[["id"]].join(
                self.destinations[["id"]],
                how="cross",
                lsuffix="_origin",
                rsuffix="_destination",
            )

            if destinations is not None and len(origins) != len(destinations):
                warnings.warn(
                    RuntimeWarning,
                    "Origins and destinations are of different length, computing an all-to-all matrix",
                )
        else:
            # origins and destinations are same length, run one-to-one routing
            self.od_pairs = pandas.DataFrame(
                {"id_origin": self.origins.id, "id_destination": self.destinations.id}
            )

    def compute_travel_details(self):
        """
        Compute travel times from all origins to all destinations.

        Returns
        -------
        pandas.DataFrame
            TODO: Add description of output data frame columns and format
        """
        # loop over all origin/destination pairs, modify the request, and
        # compute times, distance, and other details for each trip
        with joblib.Parallel(
            prefer="threads",
            verbose=(10 * self.verbose),  # joblib has a funny verbosity scale
            n_jobs=-1,
        ) as parallel:
            od_matrix = pandas.concat(
                parallel(
                    joblib.delayed(self._travel_details_per_od_pair)(from_id, to_id)
                    for _, (from_id, to_id) in self.od_pairs.iterrows()
                ),
                ignore_index=True,
            )

        try:
            od_matrix = od_matrix.to_crs(self._origins_crs)
        except AttributeError:  # (not a GeoDataFrame)
            pass
        return od_matrix

    def _travel_details_per_od_pair(self, from_id, to_id):
        origin = self.origins[self.origins.id == from_id]
        destination = self.destinations[self.destinations.id == to_id]

        request = copy.copy(self.request)
        request.fromLat = origin.geometry.item().y
        request.fromLon = origin.geometry.item().x
        request.toLat = destination.geometry.item().y
        request.toLon = destination.geometry.item().x

        trip_planner = TripPlanner(self.transport_network, request)
        trips = trip_planner.plan()

        # for option, trip in enumerate(trips):
        #     for segment in trip:
        #         [option] + segment

        # fmt: off
        trips = [
            [from_id, to_id, option] + segment
            for option, trip in enumerate(trips)
            for segment in trip.as_table()
        ]
        # fmt: on

        return pandas.DataFrame(trips, columns=self.COLUMNS)
