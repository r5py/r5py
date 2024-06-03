#!/usr/bin/env python3


"""Find detailed routes between two points."""


import copy
import collections
import datetime
import functools
import warnings

import jpype
import pyproj
import shapely

from .access_leg import AccessLeg
from .direct_leg import DirectLeg
from .egress_leg import EgressLeg
from .transfer_leg import TransferLeg
from .transit_leg import TransitLeg
from .transport_mode import TransportMode
from .trip import Trip
from ..util import GoodEnoughEquidistantCrs, start_jvm

import com.conveyal.r5
import gnu.trove.map
import java.lang


__all__ = ["TripPlanner"]


start_jvm()


ACCURATE_GEOMETRIES = com.conveyal.r5.transit.TransitLayer.SAVE_SHAPES
COORDINATE_CORRECTION_FACTOR = com.conveyal.r5.streets.VertexStore.FIXED_FACTOR
R5_CRS = "EPSG:4326"

ONE_MINUTE = datetime.timedelta(minutes=1)
ZERO_SECONDS = datetime.timedelta(seconds=0)


class TripPlanner:
    """Find detailed routes between two points."""

    MAX_ACCESS_TIME = datetime.timedelta(hours=1)
    MAX_EGRESS_TIME = MAX_ACCESS_TIME

    def __init__(self, transport_network, request):
        """
        Find detailed routes between two points.

        Arguments
        =========
        transport_network : r5py.r5.TransportNetwork
            A transport network to route on
        request : r5py.r5.regional_task
            The parameters that should be used when finding a route
        """
        self.transport_network = transport_network
        self.request = request

        EQUIDISTANT_CRS = GoodEnoughEquidistantCrs(self.transport_network.extent)
        self._crs_transformer_function = pyproj.Transformer.from_crs(
            R5_CRS, EQUIDISTANT_CRS
        ).transform

    @property
    def trips(self):
        """
        Detailed routes between two points.

        Returns
        =======
        list[r5py.r5.Trip]
            Detailed routes that meet the requested parameters
        """
        trips = self.direct_paths + self.transit_paths
        return trips

    @property
    def direct_paths(self):
        """
        Detailed routes between two points using direct modes.

        Returns
        =======
        list[r5py.r5.Trip]
            Detailed routes that meet the requested parameters, using direct
            modes (walking, cycling, driving).
        """
        direct_paths = []
        request = copy.copy(self.request)

        direct_modes = [mode for mode in request.transport_modes if mode.is_street_mode]

        for transport_mode in direct_modes:
            # short-circuit identical from_id and to_id:
            if (
                request._regional_task.fromLat == request._regional_task.toLat
                and request._regional_task.fromLon == request._regional_task.toLon
            ):
                lat = request._regional_task.fromLat
                lon = request._regional_task.fromLon
                direct_paths.append(
                    Trip(
                        [
                            DirectLeg(
                                transport_mode,
                                collections.namedtuple(
                                    "StreetSegment",
                                    ["distance", "duration", "geometry"],
                                )(0.0, 0.0, f"LINESTRING({lon} {lat}, {lon} {lat})"),
                            )
                        ]
                    )
                )
            else:
                street_router = com.conveyal.r5.streets.StreetRouter(
                    self.transport_network.street_layer
                )
                street_router.profileRequest = request
                street_router.streetMode = transport_mode

                street_router.setOrigin(
                    request._regional_task.fromLat,
                    request._regional_task.fromLon,
                )
                street_router.setDestination(
                    request._regional_task.toLat,
                    request._regional_task.toLon,
                )

                street_router.route()

                try:
                    router_state = street_router.getState(
                        street_router.getDestinationSplit()
                    )
                    street_segment = self._street_segment_from_router_state(
                        router_state,
                        transport_mode,
                    )
                    direct_paths.append(
                        Trip(
                            [
                                DirectLeg(transport_mode, street_segment),
                            ]
                        )
                    )
                except (
                    java.lang.NullPointerException,
                    java.util.NoSuchElementException,
                ):
                    warnings.warn(
                        f"Could not find route between origin "
                        f"({self.request._regional_task.fromLon}, "
                        f"{self.request._regional_task.fromLat}) "
                        f"and destination ({self.request._regional_task.toLon}, "
                        f"{self.request._regional_task.toLat})",
                        RuntimeWarning,
                    )
        return direct_paths

    def _street_segment_from_router_state(self, router_state, transport_mode):
        """Retrieve a com.conveyal.r5.street.StreetSegment for a route."""
        street_path = com.conveyal.r5.profile.StreetPath(
            router_state,
            self.transport_network,
            False,
        )
        street_segment = com.conveyal.r5.api.util.StreetSegment(
            street_path,
            transport_mode,
            self.transport_network.street_layer,
        )
        return street_segment

    @functools.cached_property
    def transit_paths(self):
        """
        Detailed routes between two points on public transport.

        Returns
        =======
        list[r5py.r5.Trip]
            Detailed routes that meet the requested parameters, on public
            transport.
        """
        transit_paths = []

        # if any transit mode requested:
        if [mode for mode in self.request.transport_modes if mode.is_transit_mode]:
            request = copy.copy(self.request)

            midnight = self.request.departure.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            suboptimal_minutes = max(self.request._regional_task.suboptimalMinutes, 0)
            transit_layer = self.transport_network.transit_layer

            if (
                request._regional_task.fromLat == request._regional_task.toLat
                and request._regional_task.fromLon == request._regional_task.toLon
            ):
                lat = request._regional_task.fromLat
                lon = request._regional_task.fromLon
                transit_paths.append(
                    Trip(
                        [
                            TransitLeg(
                                transport_mode=TransportMode.TRANSIT,
                                departure_time=None,
                                distance=0.0,
                                travel_time=ZERO_SECONDS,
                                wait_time=ZERO_SECONDS,
                                route=None,
                                geometry=shapely.LineString(((lon, lat), (lon, lat))),
                            )
                        ]
                    )
                )
            else:
                # McRapterSuboptimalPathProfileRouter needs this simple callback,
                # this could, of course, be a lambda function, but this way it’s
                # cleaner
                def list_supplier_callback(departure_time):
                    return com.conveyal.r5.profile.SuboptimalDominatingList(
                        suboptimal_minutes
                    )

                transit_router = (
                    com.conveyal.r5.profile.McRaptorSuboptimalPathProfileRouter(
                        self.transport_network,
                        request,
                        self._transit_access_times,
                        self._transit_egress_times,
                        list_supplier_callback,
                        None,
                        True,
                    )
                )
                transit_router.route()

                # `finalStatesByDepartureTime` is a hashmap of lists of router
                # states, indexed by departure times (in seconds since midnight)
                final_states = {
                    (midnight + datetime.timedelta(seconds=departure_time)): state
                    for departure_time, states in zip(
                        transit_router.finalStatesByDepartureTime.keys(),
                        transit_router.finalStatesByDepartureTime.values(),
                    )
                    for state in list(states)  # some departure times yield no results
                }

                # keep another cache layer of shortest access and egress legs
                access_legs_by_stop = {}
                egress_legs_by_stop = {}

                for departure_time, state in final_states.items():
                    trip = Trip()
                    while state:
                        if state.stop == -1:  # EgressLeg
                            try:
                                leg = egress_legs_by_stop[state.back.stop]
                            except KeyError:
                                leg = min(
                                    [
                                        self._transit_egress_paths[transport_mode][
                                            state.back.stop
                                        ]
                                        for transport_mode in self._transit_egress_paths.keys()
                                    ]
                                )
                                egress_legs_by_stop[state.back.stop] = leg
                            leg.wait_time = ZERO_SECONDS
                            leg.departure_time = (
                                midnight
                                + datetime.timedelta(seconds=state.back.time)
                                + ONE_MINUTE
                            )
                            leg.arrival_time = leg.departure_time + leg.travel_time

                        elif state.back is None:  # AccessLeg
                            try:
                                leg = access_legs_by_stop[state.stop]
                            except KeyError:
                                leg = min(
                                    [
                                        self._transit_access_paths[transport_mode][
                                            state.stop
                                        ]
                                        for transport_mode in self._transit_access_paths.keys()
                                    ]
                                )
                                access_legs_by_stop[state.stop] = leg
                            leg.wait_time = ZERO_SECONDS
                            leg.arrival_time = midnight + datetime.timedelta(
                                seconds=state.time
                            )
                            leg.departure_time = leg.arrival_time - leg.travel_time

                        else:
                            if state.pattern == -1:  # TransferLeg
                                departure_stop = state.back.stop
                                arrival_stop = state.stop

                                leg = self._transit_transfer_path(
                                    departure_stop, arrival_stop
                                )

                                leg.departure_time = (
                                    midnight
                                    + datetime.timedelta(seconds=state.back.time)
                                    + ONE_MINUTE
                                )
                                leg.arrival_time = leg.departure_time + leg.travel_time
                                leg.wait_time = (
                                    datetime.timedelta(
                                        seconds=(state.time - state.back.time)
                                    )
                                    - leg.travel_time
                                    + ONE_MINUTE  # the slack added above
                                )

                            else:  # TransitLeg
                                pattern = transit_layer.trip_patterns[state.pattern]
                                route = transit_layer.routes[pattern.routeIndex]
                                transport_mode = TransportMode(
                                    com.conveyal.r5.transit.TransitLayer.getTransitModes(
                                        route.route_type
                                    ).toString()
                                )
                                departure_time = midnight + datetime.timedelta(
                                    seconds=state.boardTime
                                )
                                travel_time = datetime.timedelta(
                                    seconds=(state.time - state.boardTime)
                                )
                                wait_time = datetime.timedelta(
                                    seconds=(state.boardTime - state.back.time)
                                )

                                # ‘hops’ in R5 terminology are the LineStrings
                                # between each pair of consecutive stops of a route
                                hops = list(pattern.getHopGeometries(transit_layer))

                                # select only the ‘hops’ between our stops, and merge
                                # them into one LineString
                                hops = hops[
                                    state.boardStopPosition : state.alightStopPosition
                                ]
                                geometry = shapely.line_merge(
                                    shapely.MultiLineString(
                                        [
                                            shapely.from_wkt(str(geometry.toText()))
                                            for geometry in hops
                                        ]
                                    )
                                )

                                # distance: based on the geometry, which might
                                # be inaccurate.

                                # We do not compute distance values if the
                                # geometry is straight lines between stops
                                # the user can still do that themselves from the
                                # inaccurate geometries: then they at least know
                                # what they committed to.
                                # TODO: add to documentation
                                if ACCURATE_GEOMETRIES:
                                    distance = shapely.ops.transform(
                                        self._crs_transformer_function,
                                        geometry,
                                    ).length
                                else:
                                    distance = None

                                leg = TransitLeg(
                                    transport_mode,
                                    departure_time,
                                    distance,
                                    travel_time,
                                    wait_time,
                                    str(route.route_short_name),
                                    geometry,
                                )

                        # we traverse in reverse order:
                        # add leg to beginning of trip,
                        # then fetch previous state (=leg)
                        trip = leg + trip
                        state = state.back

                    # R5 sometimes reports the same path more than once, skip duplicates
                    if trip not in transit_paths:
                        transit_paths.append(trip)

        return transit_paths

    @functools.cached_property
    def _transit_access_paths(self):
        access_paths = {}

        request = copy.copy(self.request)
        request._regional_task.reverseSearch = False

        street_router = com.conveyal.r5.streets.StreetRouter(
            self.transport_network.street_layer
        )
        street_router.profileRequest = request
        street_router.setOrigin(
            self.request._regional_task.fromLat,
            self.request._regional_task.fromLon,
        )
        street_router.transitStopSearch = True
        street_router.timeLimitSeconds = round(self.MAX_ACCESS_TIME.total_seconds())

        transit_layer = self.transport_network.transit_layer

        for transport_mode in request.access_modes:
            access_paths[transport_mode] = {}

            street_router.streetMode = transport_mode
            street_router.route()
            reached_stops = street_router.getReachedStops()

            for stop in reached_stops.keys():
                router_state = street_router.getStateAtVertex(
                    transit_layer.get_street_vertex_for_stop(stop)
                )
                street_segment = self._street_segment_from_router_state(
                    router_state,
                    transport_mode,
                )
                access_paths[transport_mode][stop] = AccessLeg(
                    transport_mode, street_segment
                )
        return access_paths

    @functools.cached_property
    def _transit_access_times(self):
        """
        Times to reached stops.

        In the format required by McRaptorSuboptimalPathProfileRouter.
        """
        access_times = jpype.JObject(
            {
                com.conveyal.r5.api.util.LegMode
                @ mode: gnu.trove.map.hash.TIntIntHashMap(
                    [stop for stop in reached_stops.keys()],
                    [
                        round(transfer_leg.travel_time.total_seconds())
                        for transfer_leg in reached_stops.values()
                    ],
                )
                for mode, reached_stops in self._transit_access_paths.items()
            },
            "java.util.Map<com.conveyal.r5.LegMode, gnu.trove.map.TIntIntMap>",
        )
        return access_times

    @functools.cached_property
    def _transit_egress_paths(self):
        egress_paths = {}

        request = copy.copy(self.request)
        request._regional_task.reverseSearch = True

        street_router = com.conveyal.r5.streets.StreetRouter(
            self.transport_network.street_layer
        )
        street_router.profileRequest = request
        street_router.setOrigin(
            self.request._regional_task.toLat,
            self.request._regional_task.toLon,
        )
        street_router.transitStopSearch = True
        street_router.timeLimitSeconds = round(self.MAX_EGRESS_TIME.total_seconds())

        transit_layer = self.transport_network.transit_layer

        for transport_mode in request.egress_modes:
            egress_paths[transport_mode] = {}

            street_router.streetMode = transport_mode

            street_router.route()
            reached_stops = street_router.getReachedStops()

            for stop in reached_stops.keys():
                router_state = street_router.getStateAtVertex(
                    transit_layer.get_street_vertex_for_stop(stop)
                )
                street_segment = self._street_segment_from_router_state(
                    router_state,
                    transport_mode,
                )
                egress_paths[transport_mode][stop] = EgressLeg(
                    transport_mode, street_segment
                )
        return egress_paths

    @functools.cached_property
    def _transit_egress_times(self):
        """
        Times to reached stops.

        In the format required by McRaptorSuboptimalPathProfileRouter.
        """
        egress_times = jpype.JObject(
            {
                com.conveyal.r5.api.util.LegMode
                @ mode: gnu.trove.map.hash.TIntIntHashMap(
                    [stop for stop in reached_stops.keys()],
                    [
                        round(transfer_leg.travel_time.total_seconds())
                        for transfer_leg in reached_stops.values()
                    ],
                )
                for mode, reached_stops in self._transit_egress_paths.items()
            },
            "java.util.Map<com.conveyal.r5.LegMode, gnu.trove.map.TIntIntMap>",
        )
        return egress_times

    def _transit_transfer_path(self, from_stop, to_stop):
        """Find a transfer path between two transit stops."""
        self._transfer_paths = {}
        while True:
            try:
                transfer_path = self._transfer_paths[(from_stop, to_stop)]
            except KeyError:
                request = copy.copy(self.request)

                street_router = com.conveyal.r5.streets.StreetRouter(
                    self.transport_network.street_layer
                )
                street_router.profileRequest = request
                street_router.streetMode = TransportMode.WALK

                get_coordinates_for_stop = (
                    self.transport_network.transit_layer._transit_layer.getCoordinateForStopFixed
                )
                from_stop_coordinates = get_coordinates_for_stop(from_stop)
                to_stop_coordinates = get_coordinates_for_stop(to_stop)

                from_lat = from_stop_coordinates.getY() / COORDINATE_CORRECTION_FACTOR
                from_lon = from_stop_coordinates.getX() / COORDINATE_CORRECTION_FACTOR
                to_lat = to_stop_coordinates.getY() / COORDINATE_CORRECTION_FACTOR
                to_lon = to_stop_coordinates.getX() / COORDINATE_CORRECTION_FACTOR

                street_router.setOrigin(from_lat, from_lon)
                street_router.setDestination(to_lat, to_lon)

                street_router.route()

                router_state = street_router.getState(
                    street_router.getDestinationSplit()
                )
                street_segment = self._street_segment_from_router_state(
                    router_state,
                    TransportMode.WALK,
                )

                transfer_path = self._transfer_paths[(from_stop, to_stop)] = (
                    TransferLeg(TransportMode.WALK, street_segment)
                )

                return transfer_path
