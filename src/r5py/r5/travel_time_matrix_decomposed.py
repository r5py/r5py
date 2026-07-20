#!/usr/bin/env python3

"""Decompose transit travel times into their in- and out-of-vehicle components."""

import copy

import numpy
import pandas

from .breakdown_stat import BreakdownStat
from .travel_time_matrix import TravelTimeMatrix
from ..util import start_jvm

import com.conveyal.r5

__all__ = ["TravelTimeMatrixDecomposed"]


start_jvm()


# R5 refuses to record path results for more than this many destinations
# (com.conveyal.r5.analyst.cluster.PathResult.MAX_PATH_DESTINATIONS, which is
# `final`, so we cannot raise it from here).
MAX_PATH_DESTINATIONS = 5_000


class TravelTimeMatrixDecomposed(TravelTimeMatrix):
    """
    Compute travel times broken down into their components.

    In addition to the total travel time (as reported by
    ``r5py.TravelTimeMatrix``), this reports how that time splits into
    in-vehicle, waiting, access (to the first stop), egress (from the last
    stop), and transfer time, together with the routes and stops that make up
    each path.
    """

    COLUMNS = [
        "from_id",
        "to_id",
        "routes",
        "board_stops",
        "alight_stops",
        "feed_ids",
        "in_vehicle_time",
        "wait_time",
        "access_time",
        "egress_time",
        "transfer_time",
        "total_time",
        "n_rides",
        "n_iterations",
    ]

    _r5py_attributes = TravelTimeMatrix._r5py_attributes + ["breakdown_stat"]

    def __init__(
        self,
        transport_network,
        origins=None,
        destinations=None,
        snap_to_network=False,
        breakdown_stat=BreakdownStat.MEAN,
        **kwargs,
    ):
        """
        Compute travel times broken down into their components.

        ``r5py.TravelTimeMatrixDecomposed`` is a child class of
        ``pandas.DataFrame`` and supports all of its methods and properties, see
        https://pandas.pydata.org/docs/ . Unlike ``r5py.TravelTimeMatrix``,
        which reports one row per origin/destination pair, this reports one row
        per origin, destination, and *path template* — a distinct sequence of
        routes and stops that R5 found between the pair. An origin/destination
        pair can therefore appear in more than one row, or in none (if it is not
        reachable).

        The reported component times do **not**, in general, add up to the
        ``travel_time`` of the corresponding ``r5py.TravelTimeMatrix``: the
        latter is a percentile (by default the median) over the departure time
        window, while the components summarise the iterations of a single path
        template (see ``breakdown_stat``). The components of one row, however,
        reconcile exactly: ``total_time`` equals the sum of ``in_vehicle_time``,
        ``wait_time``, ``access_time``, ``egress_time``, and ``transfer_time``.

        Arguments
        ---------
        transport_network : r5py.TransportNetwork | tuple(
        pathlib.Paths | str, list(pathlib.Path | str))
            The transport network to route on. This can either be a readily
            initialised r5py.TransportNetwork or a tuple of the parameters
            passed to ``TransportNetwork.__init__()``: the path to an
            OpenStreetMap extract in PBF format, and a list of zero of more
            paths to GTFS transport schedule files.
        origins : geopandas.GeoDataFrame
            Places to find a route _from_
            Has to have a point geometry, and at least an `id` column
        destinations : geopandas.GeoDataFrame (optional)
            Places to find a route _to_
            Has to have a point geometry, and at least an `id` column
            If omitted, use same data set as for origins. R5 records path
            details for at most 5000 destinations; a larger set raises a
            ``ValueError``.
        snap_to_network : bool or int, default False
            Should origin an destination points be snapped to the street network
            before routing? If `True`, the default search radius (defined in
            `com.conveyal.r5.streets.StreetLayer.LINK_RADIUS_METERS`) is used,
            if `int`, use `snap_to_network` meters as the search radius.
        breakdown_stat : r5py.BreakdownStat, default r5py.BreakdownStat.MEAN
            How to summarise the departure-minute iterations of a path template.
            A template’s in-vehicle, access, and egress times are constant
            across its iterations, but its waiting time (and, hence, its
            transfer and total times) varies. The reported iteration is the one
            whose total waiting time is closest to the ``MEAN`` or ``MINIMUM``
            total waiting time across the template’s iterations.
        **kwargs : mixed
            Any arguments than can be passed to r5py.RegionalTask:
            ``departure``, ``departure_time_window``, ``percentiles``,
            ``transport_modes``, ``access_modes``, ``egress_modes``,
            ``max_time``, ``max_time_walking``, ``max_time_cycling``,
            ``max_time_driving``, ``speed_cycling``, ``speed_walking``,
            ``max_public_transport_rides``, ``max_bicycle_traffic_stress``.
            Note that ``percentiles`` has no effect on the reported components.
        """
        self.breakdown_stat = breakdown_stat
        super().__init__(
            transport_network,
            origins,
            destinations,
            snap_to_network,
            **kwargs,
        )

    def _compute(self):
        """
        Compute the travel time breakdown from all origins to all destinations.

        Returns
        -------
        pandas.DataFrame
            One row per origin, destination, and path template, with the columns
            listed in ``TravelTimeMatrixDecomposed.COLUMNS``.
        """
        self._prepare_origins_destinations()
        if len(self.destinations) > MAX_PATH_DESTINATIONS:
            raise ValueError(
                "R5 records path details for at most "
                f"{MAX_PATH_DESTINATIONS} destinations, but "
                f"{len(self.destinations)} were requested. Split the "
                "destinations into smaller batches and concatenate the results."
            )
        self.request.destinations = self.destinations
        self.request._regional_task.includePathResults = True

        breakdown = pandas.concat(
            [self._breakdown_per_origin(from_id) for from_id in self.origins.id],
            ignore_index=True,
        )
        return breakdown

    def _breakdown_per_origin(self, from_id):
        request = copy.copy(self.request)
        request.origin = self.origins[self.origins.id == from_id].geometry.item()
        request._regional_task.includePathResults = True

        travel_time_computer = com.conveyal.r5.analyst.TravelTimeComputer(
            request, self.transport_network
        )
        results = travel_time_computer.computeTravelTimes()

        return self._parse_results(from_id, results)

    def _parse_results(self, from_id, results):
        """
        Parse the ``PathResult`` of routing from one origin to many destinations.

        Reads R5’s public ``PathResult.iterationsForPathTemplates`` array
        directly (rather than the string-formatting ``summarizeIterations()``
        path), and pulls the numeric components off the ``RouteSequence`` /
        ``StopSequence`` / ``Iteration`` objects.

        Arguments
        ---------
        from_id : str
            The value of the ID column of the origin record to report on.
        results : com.conveyal.r5.OneOriginResult (Java object)

        Returns
        -------
        pandas.DataFrame
            One row per (``from_id``, destination, path template).
        """
        transit_layer = self.transport_network._transport_network.transitLayer
        id_only = com.conveyal.r5.transit.TransitLayer.EntityRepresentation.ID_ONLY

        rows = []
        paths = results.paths
        if paths is not None:
            destination_ids = list(self.destinations.id)
            templates_per_destination = paths.iterationsForPathTemplates
            for d, to_id in enumerate(destination_ids):
                iteration_map = templates_per_destination[d]
                if iteration_map is None:
                    continue
                for route_sequence in iteration_map.keySet():
                    iterations = list(iteration_map.get(route_sequence))
                    rows.append(
                        self._summarise_template(
                            from_id,
                            to_id,
                            route_sequence,
                            iterations,
                            transit_layer,
                            id_only,
                        )
                    )

        breakdown = pandas.DataFrame(rows, columns=self.COLUMNS)
        breakdown = breakdown.astype(
            {
                "from_id": str,
                "to_id": str,
                "routes": str,
                "board_stops": str,
                "alight_stops": str,
                "feed_ids": str,
                "access_time": float,
                "egress_time": float,
                "transfer_time": float,
                "total_time": float,
                "n_rides": int,
                "n_iterations": int,
            }
        )
        return breakdown

    def _summarise_template(
        self, from_id, to_id, route_sequence, iterations, transit_layer, id_only
    ):
        """Summarise one path template into a single result row (times in minutes)."""
        stop_sequence = route_sequence.stopSequence
        routes = route_sequence.routes
        n_rides = routes.size()

        # per-template components: constant across the template’s iterations
        if stop_sequence.rideTimesSeconds is not None:
            in_vehicle_time = [
                seconds / 60.0 for seconds in stop_sequence.rideTimesSeconds.toArray()
            ]
        else:
            in_vehicle_time = []
        access_time = (
            stop_sequence.access.time / 60.0
            if stop_sequence.access is not None
            else numpy.nan
        )
        egress_time = (
            stop_sequence.egress.time / 60.0
            if stop_sequence.egress is not None
            else numpy.nan
        )

        # path identity, as R5 reports it (GTFS ids, one entry per transit leg)
        routes_str = "|".join(
            str(transit_layer.routeString(routes.get(i), id_only))
            for i in range(n_rides)
        )
        board_stops_str = "|".join(
            str(transit_layer.stopString(stop_sequence.boardStops.get(i), id_only))
            for i in range(n_rides)
        )
        alight_stops_str = "|".join(
            str(transit_layer.stopString(stop_sequence.alightStops.get(i), id_only))
            for i in range(n_rides)
        )
        feed_ids_str = "|".join(
            str(transit_layer.feedFromStop(stop_sequence.boardStops.get(i)))
            for i in range(n_rides)
        )

        # pick the representative iteration (mirrors R5’s
        # PathResult.summarizeIterations(): the iteration whose total waiting
        # time is closest to the requested statistic of all iterations’)
        total_waits = [iteration.waitTimes.sum() for iteration in iterations]
        if self.breakdown_stat == BreakdownStat.MINIMUM:
            target = min(total_waits)
        else:
            target = sum(total_waits) / len(total_waits)
        representative = min(
            iterations, key=lambda iteration: abs(target - iteration.waitTimes.sum())
        )

        wait_time = [seconds / 60.0 for seconds in representative.waitTimes.toArray()]
        transfer_time = stop_sequence.transferTime(representative) / 60.0
        total_time = representative.totalTime / 60.0

        return [
            from_id,
            to_id,
            routes_str,
            board_stops_str,
            alight_stops_str,
            feed_ids_str,
            in_vehicle_time,
            wait_time,
            access_time,
            egress_time,
            transfer_time,
            total_time,
            n_rides,
            len(iterations),
        ]
