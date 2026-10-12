#!/usr/bin/env python3

"""Break transit travel times down into their in- and out-of-vehicle components."""

import copy

import numpy
import pandas

from .breakdown_stat import BreakdownStat
from .travel_time_matrix import TravelTimeMatrix
from ..util import start_jvm

import com.conveyal.r5

__all__ = ["ExpandedTravelTimeMatrix"]


start_jvm()


# R5 refuses to record path results for more than this many destinations
# (com.conveyal.r5.analyst.cluster.PathResult.MAX_PATH_DESTINATIONS, which is
# `final`, so we cannot raise it from here).
MAX_PATH_DESTINATIONS = 5_000


class ExpandedTravelTimeMatrix(TravelTimeMatrix):
    """
    Compute travel times broken down into their components.

    In addition to the total travel time (as reported by
    ``r5py.TravelTimeMatrix``), this reports how that time splits into
    in-vehicle, waiting, access (to the first stop), egress (from the last
    stop), and transfer time, together with the routes, their GTFS
    ``route_type``s, and the stops that make up each path.
    """

    COLUMNS = [
        "from_id",
        "to_id",
        "routes",
        "route_types",
        "board_stops",
        "alight_stops",
        "feed_ids",
        "ride_time",
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

        ``r5py.ExpandedTravelTimeMatrix`` is a child class of
        ``pandas.DataFrame`` and supports all of its methods and properties, see
        https://pandas.pydata.org/docs/ . Unlike ``r5py.TravelTimeMatrix``,
        which reports one row per origin/destination pair, this reports one row
        per origin, destination, and *path template* — a distinct sequence of
        routes and stops that R5 found between the pair. An origin/destination
        pair can therefore appear in more than one row, or in none (if it is not
        reachable). (This differs from r5r’s ``expanded_travel_time_matrix()``,
        which reports one row per departure minute and draw.)

        The reported component times do **not**, in general, add up to the
        ``travel_time`` of the corresponding ``r5py.TravelTimeMatrix``: the
        latter is a percentile (by default the median) over the departure time
        window, while the components summarise the iterations of a single path
        template (see ``breakdown_stat``). The components of one row, however,
        reconcile exactly: ``total_time`` equals the sum of ``ride_time``,
        ``wait_time``, ``access_time``, ``egress_time``, and ``transfer_time``.
        Moreover, where ``from_id`` equals ``to_id``, ``total_time`` is the
        (non-zero) time R5 reports for routing from and to the nearest street
        segment, whereas ``r5py.TravelTimeMatrix`` sets such pairs to 0.

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
            A template’s ride, access, egress, and transfer times are constant
            across its iterations, but its waiting time (and, hence, its total
            time) varies. ``MEAN`` reports each leg’s waiting time and the total
            time averaged over the template’s iterations, ``MINIMUM`` reports
            the fastest iteration. This mirrors R5’s
            ``PathResult.summarizeIterations()``.
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
            listed in ``ExpandedTravelTimeMatrix.COLUMNS``.
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
        gtfs_ids = _GtfsIds(self.transport_network._transport_network.transitLayer)

        rows = []
        paths = results.paths
        if paths is not None:
            destination_ids = list(self.destinations.id)
            templates_per_destination = paths.iterationsForPathTemplates
            # street-only travel times (in whole minutes), constant across
            # percentiles when no transit is ridden
            direct_travel_times = results.travelTimes.getValues()[0]
            for d, to_id in enumerate(destination_ids):
                iteration_map = templates_per_destination[d]
                if iteration_map is None:
                    # R5 records path details only in its transit search, which
                    # it skips if no transit modes are requested or no stop can
                    # be reached from the origin; report a direct path instead
                    if direct_travel_times[d] < self.MAX_INT32:
                        rows.append(
                            self._direct_path(from_id, to_id, direct_travel_times[d])
                        )
                    continue
                for route_sequence in iteration_map.keySet():
                    iterations = list(iteration_map.get(route_sequence).toArray())
                    rows.append(
                        self._summarise_template(
                            from_id,
                            to_id,
                            route_sequence,
                            iterations,
                            gtfs_ids,
                        )
                    )

        breakdown = pandas.DataFrame(rows, columns=self.COLUMNS)
        breakdown = breakdown.astype(
            {
                # keep the ids’ original types, as r5py.TravelTimeMatrix does
                "from_id": self.origins.id.dtype,
                "to_id": self.destinations.id.dtype,
                "routes": str,
                "route_types": str,
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

    def _summarise_template(self, from_id, to_id, route_sequence, iterations, gtfs_ids):
        """Summarise one path template into a single result row (times in minutes)."""
        stop_sequence = route_sequence.stopSequence
        # copy R5’s int lists to Python in one call each, rather than one
        # Java call per element
        routes = _to_list(route_sequence.routes)
        n_rides = len(routes)
        if n_rides > 0:
            board_stops = _to_list(stop_sequence.boardStops)[:n_rides]
            alight_stops = _to_list(stop_sequence.alightStops)[:n_rides]
        else:
            # without transit legs, R5 may leave the stop lists unset
            board_stops = alight_stops = []

        # per-template components: constant across the template’s iterations
        if stop_sequence.rideTimesSeconds is not None:
            ride_time = (_to_array(stop_sequence.rideTimesSeconds) / 60.0).tolist()
        else:
            ride_time = []
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

        # path identity, as R5 reports it (GTFS ids, one entry per transit
        # leg); ``route_types`` is aligned index-by-index with ``routes`` (and
        # hence with the per-leg ``ride_time`` list)
        routes_str = "|".join(gtfs_ids.route(route) for route in routes)
        route_types_str = "|".join(gtfs_ids.route_type(route) for route in routes)
        board_stops_str = "|".join(gtfs_ids.stop(stop) for stop in board_stops)
        alight_stops_str = "|".join(gtfs_ids.stop(stop) for stop in alight_stops)
        feed_ids_str = "|".join(gtfs_ids.feed(stop) for stop in board_stops)

        # summarise the iterations (mirrors R5’s
        # PathResult.summarizeIterations()): MINIMUM reports the fastest
        # iteration (ties broken by earliest departure), MEAN averages each
        # leg’s waiting time and the total time over all iterations
        if self.breakdown_stat == BreakdownStat.MINIMUM:
            fastest = min(
                iterations,
                key=lambda iteration: (iteration.totalTime, iteration.departureTime),
            )
            wait_time = (_to_array(fastest.waitTimes) / 60.0).tolist()
            total_time = fastest.totalTime / 60.0
        else:
            n_iterations = len(iterations)
            # one row per iteration, one column per leg; integer sums are
            # exact, so this matches summing leg by leg
            wait_times = numpy.array(
                [_to_array(iteration.waitTimes)[:n_rides] for iteration in iterations],
                dtype=numpy.int64,
            ).reshape(n_iterations, n_rides)
            wait_time = (wait_times.sum(axis=0) / n_iterations / 60.0).tolist()
            total_time = (
                sum(iteration.totalTime for iteration in iterations)
                / n_iterations
                / 60.0
            )

        # R5 ≥ 7.6 precomputes transfer walking time on the path template
        # (``StopSequence.transferTimesSeconds``); it no longer varies by
        # iteration
        transfer_time = stop_sequence.totalTransferTimeSeconds() / 60.0

        return [
            from_id,
            to_id,
            routes_str,
            route_types_str,
            board_stops_str,
            alight_stops_str,
            feed_ids_str,
            ride_time,
            wait_time,
            access_time,
            egress_time,
            transfer_time,
            total_time,
            n_rides,
            len(iterations),
        ]

    def _direct_path(self, from_id, to_id, travel_time):
        """Report a direct (street-only) path, with no transit, as a result row."""
        n_departure_minutes = max(
            1, int(self.request.departure_time_window.total_seconds() // 60)
        )
        return [
            from_id,
            to_id,
            "",
            "",
            "",
            "",
            "",
            [],
            [],
            numpy.nan,
            numpy.nan,
            0.0,
            float(travel_time),
            0,
            n_departure_minutes,
        ]


def _to_array(trove_int_list):
    """Copy a Java ``TIntList`` into a numpy array in a single call."""
    return numpy.asarray(trove_int_list.toArray())


def _to_list(trove_int_list):
    """Copy a Java ``TIntList`` into a list of Python ints in a single call."""
    return _to_array(trove_int_list).tolist()


class _GtfsIds:
    """
    Look up the GTFS ids of a transit layer’s routes, stops, and feeds.

    Path templates share most of their routes and stops, so each lookup is
    memoised: every index crosses into Java at most once per instance.
    """

    def __init__(self, transit_layer):
        self._transit_layer = transit_layer
        self._id_only = (
            com.conveyal.r5.transit.TransitLayer.EntityRepresentation.ID_ONLY
        )
        self._routes = {}
        self._route_types = {}
        self._stops = {}
        self._feeds = {}

    def route(self, route):
        """Return the GTFS ``route_id`` of route index ``route``."""
        try:
            return self._routes[route]
        except KeyError:
            route_id = str(self._transit_layer.routeString(route, self._id_only))
            self._routes[route] = route_id
            return route_id

    def route_type(self, route):
        """Return the GTFS ``route_type`` of route index ``route``, as a str."""
        # R5 keeps the parsed route table in ``TransitLayer.routes``, indexed
        # by the same integer ``routeString()`` takes
        try:
            return self._route_types[route]
        except KeyError:
            route_type = str(self._transit_layer.routes.get(route).route_type)
            self._route_types[route] = route_type
            return route_type

    def stop(self, stop):
        """Return the GTFS ``stop_id`` of stop index ``stop``."""
        try:
            return self._stops[stop]
        except KeyError:
            stop_id = str(self._transit_layer.stopString(stop, self._id_only))
            self._stops[stop] = stop_id
            return stop_id

    def feed(self, stop):
        """Return the id of the GTFS feed that stop index ``stop`` belongs to."""
        try:
            return self._feeds[stop]
        except KeyError:
            feed_id = str(self._transit_layer.feedFromStop(stop))
            self._feeds[stop] = feed_id
            return feed_id
