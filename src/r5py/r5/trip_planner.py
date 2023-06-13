#!/usr/bin/env python3


"""Find detailed routes between two points."""


import copy
import datetime
import collections
import warnings

from .direct_leg import DirectLeg
from .transfer_leg import TransferLeg
from .trip import Trip
from ..util import start_jvm

import com.conveyal.r5
import java.util


__all__ = ["TripPlanner"]


start_jvm()


class TripPlanner:
    """
    Find detailed routes between two points.
    """

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

    def plan(self):
        """
        Find detailed routes between two points.

        Returns
        =======
        list[r5py.r5.Trip]
            Detailed routes that meet the requested parameters
        """
        # TODO: catch from_id == to_id cases and short-circuit them
        trips = []
        if [mode for mode in self.request.transport_modes if mode.is_street_mode]:
            trips += self._find_direct_paths()
        if [mode for mode in self.request.transport_modes if mode.is_transit_mode]:
            trips += self._find_transit_paths()
        return trips

    def _find_direct_paths(self):
        direct_paths = []

        direct_modes = [
            mode for mode in self.request.transport_modes if mode.is_street_mode
        ]

        for transport_mode in direct_modes:
            # short-circuit identical from_id and to_id:
            if (
                self.request._regional_task.fromLat == self.request._regional_task.toLat
                and self.request._regional_task.fromLon
                == self.request._regional_task.toLon
            ):
                lat = self.request._regional_task.fromLat
                lon = self.request._regional_task.fromLon
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
                street_router.profileRequest = self.request
                street_router.streetMode = transport_mode

                # fmt: off
                if (
                    street_router.setOrigin(self.request._regional_task.fromLat, self.request._regional_task.fromLon)
                    and street_router.setDestination(self.request._regional_task.toLat, self.request._regional_task.toLon)
                ):
                    # fmt: on
                    street_router.route()
                    router_state = street_router.getState(street_router.getDestinationSplit())
                    try:
                        street_path = com.conveyal.r5.profile.StreetPath(
                            router_state,
                            self.transport_network,
                            False,
                        )
                    except java.util.NoSuchElementException:
                        continue
                    street_segment = com.conveyal.r5.api.util.StreetSegment(
                        street_path,
                        transport_mode,
                        self.transport_network.street_layer,
                    )

                    direct_paths.append(
                        Trip([
                            DirectLeg(transport_mode, street_segment),
                        ])
                    )
                else:
                    warnings.warn(
                        (
                            f"Could not find "
                            f"origin ({self.request.fromLon}, {self.request.fromLat}) "
                            f"or destination ({self.request.toLon}, {self.request.toLat})"
                        ),
                        RuntimeWarning,
                    )
        return direct_paths

    def _find_transit_paths(self):
        access_paths = self._find_transit_access_paths()
        print(
            access_paths,
            # [list(v.keys()) for v in access_paths.values()],
            # [list(v.values()) for v in access_paths.values()]
        )
        return []

    def _find_transit_access_paths(self):
        access_paths = {}

        request = copy.copy(self.request)
        request._regional_task.reverseSearch = False

        street_router = com.conveyal.r5.streets.StreetRouter(
            self.transport_network.street_layer
        )
        street_router.profileRequest = self.request

        transit_layer = self.transport_network.transit_layer

        for transport_mode in request.access_modes:
            access_paths[transport_mode] = {}

            street_router.streetMode = transport_mode
            street_router.transitStopSearch = True
            street_router.timeLimitSeconds = round(self.MAX_ACCESS_TIME.total_seconds())

            if street_router.setOrigin(
                self.request._regional_task.fromLat,
                self.request._regional_task.fromLon,
            ):
                street_router.route()
                reached_stops = street_router.getReachedStops()

                for stop in reached_stops.keys():
                    router_state = street_router.getStateAtVertex(
                        transit_layer.get_street_vertex_for_stop(stop)
                    )
                    try:
                        street_path = com.conveyal.r5.profile.StreetPath(
                            router_state,
                            self.transport_network,
                            False,
                        )
                    except java.util.NoSuchElementException:
                        warnings.warn(
                            (
                                f"Failed to look up street path/street segment "
                                f"to access public transport stop {stop}, skipping."
                            ),
                            RuntimeWarning
                        )
                        continue

                    street_segment = com.conveyal.r5.api.util.StreetSegment(
                        street_path,
                        transport_mode,
                        self.transport_network.street_layer,
                    )

                    access_paths[transport_mode][stop] = TransferLeg(
                        transport_mode, street_segment
                    )

            else:
                warnings.warn(
                    (
                        f"Could not find "
                        f"origin ({self.request.fromLon}, {self.request.fromLat}) "
                    ),
                    RuntimeWarning,
                )
        return access_paths
