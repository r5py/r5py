#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.analyst.cluster.RegionalTask."""

import datetime

import jpype

from ..util import config  # noqa: F401
from . import LegMode, Scenario, StreetMode, TransitMode

import java.io
import java.time
import com.conveyal.r5


__all__ = ["RegionalTask"]


class RegionalTask:
    """Wrap a com.conveyal.r5.analyst.cluster.RegionalTask."""
    def __init__(
            self,

            transport_network,

            origin,
            destinations,

            departure=datetime.datetime.now(),
            departure_time_window=datetime.timedelta(hours=1),

            transport_modes=[TransitMode.TRANSIT],
            access_modes=[LegMode.WALK],
            egress_modes=[],  # default: access_modes

            max_time=datetime.timedelta(hours=2),
            max_time_walking=datetime.timedelta(hours=2),
            max_time_cycling=datetime.timedelta(hours=2),
            max_time_driving=datetime.timedelta(hours=2),

            speed_walking=3.6,
            speed_cycling=12.0,

            max_public_transport_rides=8,
            max_bicycle_traffic_stress=4,
    ):
        """
        Create a RegionalTask.

        Arguments
        ---------
        transport_network : r5p.r5.TransportNetwork
            The street + public transport network to route on
        origin : shapely.geometry.Point
            Point to route from
        destinations : geopandas.GeoDataFrame
            Points to route to, has to have at least an `id` column
            and a geometry
        departure : datetime.datetime
            Find public transport connections leaving within
            `departure_time_window` after departure.
            Default: current date and time
        departure_time_window : datetime.timedelta
            (see `departure`)
            Default: 1 hour
        transport_modes : list[r5p.r5.TransitMode | r5p.r5.LegMode]
            The mode of transport to use for routing.
            Default: [r5p.r5.TransitMode.TRANSIT] (all public transport)
        access_modes : list[r5p.r5.LegMode]
            Mode of transport to public transport stops.
            Default: [r5p.r5.LegMode.WALK]
        egress_modes : list[r5p.r5.LegMode]
            Mode of transport from public transport stops.
            Default: access_modes
        max_time : datetime.timedelta
            Maximum trip duration.
            Default: 2 hours
        max_time_walking : datetime.timedelta
            Maximum time spent walking, potentially including access and egress
            Default: 2 hours
        max_time_cycling
            Maximum time spent cycling, potentially including access and egress
            Default: 2 hours
        max_time_driving
            Maximum time spent driving, potentially including access and egress
            Default: 2 hours
        speed_walking : float
            Mean walking speed for routing, km/h.
            Default: 3.6 km/h
        speed_cycling : float
            Mean cycling speed for routing, km/h.
            Default: 12.0 km/h
        max_public_transport_rides : int
            Use at most `max_public_transport_rides` consecutive public transport
            connections. Default: 8
        max_bicycle_traffic_stress : int
            Maximum stress level for cyclist routing, ranges from 1-4
            see https://docs.conveyal.com/learn-more/traffic-stress
            Default: 3
        """
        self._regional_task = com.conveyal.r5.analyst.cluster.RegionalTask()
        self.scenario = Scenario()

        self.transport_network = transport_network

        self.origin = origin
        self.destinations = destinations

        self.departure = departure
        self.departure_time_window = departure_time_window

        self.transport_modes = transport_modes
        self.access_modes = access_modes
        if egress_modes:
            self.egress_modes = egress_modes
        else:
            self.egress_modes = access_modes

        self.max_time = max_time
        self.max_time_walking = max_time_walking
        self.max_time_cycling = max_time_cycling
        self.max_time_driving = max_time_driving

        self.speed_cycling = speed_cycling
        self.speed_walking = speed_walking

        self.max_public_transport_rides = max_public_transport_rides
        self.max_bicycle_traffic_stress = max_bicycle_traffic_stress

    @property
    def access_modes(self):
        return self._access_modes

    @access_modes.setter
    def access_modes(self, access_modes):
        self._access_modes = access_modes
        self._regional_task.accessModes = RegionalTask._enum_set(
            access_modes,
            com.conveyal.r5.api.util.LegMode
        )

    @property
    def departure(self):
        return self._departure

    @departure.setter
    def departure(self, departure):
        self._departure = departure
        self._regional_task.date = java.time.LocalDate.of(
            departure.year, departure.month, departure.day
        )
        # seconds from midnight
        self._regional_task.fromTime = int(
            datetime.timedelta(
                hours=departure.hour,
                minutes=departure.minute
            ).total_seconds()
        )
        try:
            self._regional_task.toTime = (
                self._regional_task.fromTime
                + self.departure_time_window.total_seconds()
            )
        except AttributeError:  # departure_time_window has not been set yet
            pass

    @property
    def departure_time_window(self):
        return self._departure_time_window

    @departure_time_window.setter
    def departure_time_window(self, departure_time_window):
        self._departure_time_window = departure_time_window
        self._regional_task.toTime = (
            self._regional_task.fromTime
            + departure_time_window.total_seconds()
        )

    @property
    def destinations(self):
        return self._destinations

    @destinations.setter
    def destinations(self, destinations):
        """
        Set destinations geometries.

        Arguments:
        ----------
        destinations : geopandas.GeoDataFrame
            Points to route to, has to have at least an `id` column
            and a geometry
        """
        self._destinations = destinations

        # wrap destinations in a few layers of streams (yeah, Java)
        output_stream = java.io.ByteArrayOutputStream()
        data_output_stream = java.io.DataOutputStream(output_stream)

        # first: number of destinations
        data_output_stream.writeInt(len(destinations))

        # then, data columns, one by one, then still ‘opportunties’
        for id_ in destinations.id.astype(str):
            data_output_stream.writeUTF(id_)
        for lat in destinations.geometry.y:
            data_output_stream.writeDouble(lat)
        for lon in destinations.geometry.x:
            data_output_stream.writeDouble(lon)
        for _ in range(len(destinations)):
            data_output_stream.writeDouble(0)  # ‘opportunities’

        # convert to input stream, then into a point set
        destinations_point_set = com.conveyal.r5.analyst.FreeFormPointSet(
            java.io.ByteArrayInputStream(output_stream.toByteArray())
        )

        self._regional_task.destinationPointSets = [destinations_point_set]

    @property
    def egress_modes(self):
        return self._egress_modes

    @egress_modes.setter
    def egress_modes(self, egress_modes):
        self._egress_modes = egress_modes
        self._regional_task.egressModes = RegionalTask._enum_set(
            egress_modes,
            com.conveyal.r5.api.util.LegMode
        )

    @property
    def max_bicycle_traffic_stress(self):
        return self._max_bicycle_traffic_stress

    @max_bicycle_traffic_stress.setter
    def max_bicycle_traffic_stress(self, max_bicycle_traffic_stress):
        self._max_bicycle_traffic_stress = max_bicycle_traffic_stress
        self._regional_task.bikeTrafficStress = max_bicycle_traffic_stress

    @property
    def max_public_transport_rides(self):
        return self._max_public_transport_rides

    @max_public_transport_rides.setter
    def max_public_transport_rides(self, max_public_transport_rides):
        self._max_public_transport_rides = max_public_transport_rides
        self._regional_task.maxRides = max_public_transport_rides

    @property
    def max_time(self):
        return self._max_time

    @max_time.setter
    def max_time(self, max_time):
        self._max_time = max_time
        self._regional_task.maxTripDurationMinutes = int(
            max_time.total_seconds() / 60
        )

    @property
    def max_time_cycling(self):
        return self._max_time_cycling

    @max_time_cycling.setter
    def max_time_cycling(self, max_time_cycling):
        self._max_time_cycling = max_time_cycling
        self._regional_task.maxBikeTime = int(
            max_time_cycling.total_seconds() / 60
        )

    @property
    def max_time_driving(self):
        return self._max_time_driving

    @max_time_driving.setter
    def max_time_driving(self, max_time_driving):
        self._max_time_driving = max_time_driving
        self._regional_task.maxCarTime = int(
            max_time_driving.total_seconds() / 60
        )

    @property
    def max_time_walking(self):
        return self._max_time_walking

    @max_time_walking.setter
    def max_time_walking(self, max_time_walking):
        self._max_time_walking = max_time_walking
        self._regional_task.maxWalkTime = int(
            max_time_walking.total_seconds() / 60
        )

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, origin):
        """
        Set origin geometry.

        Arguments:
        ----------
        origin : shapely.geometry.Point
            Point to route from
        """
        self._origin = origin
        self._regional_task.fromLat = origin.y
        self._regional_task.FromLon = origin.x

    @property
    def scenario(self):
        return self._regional_task.scenario

    @scenario.setter
    def scenario(self, scenario):
        self._regional_task.scenario = scenario
        self._regional_task.scenarioId = scenario.id

    @property
    def speed_cycling(self):
        return self._speed_cycling

    @speed_cycling.setter
    def speed_cycling(self, speed_cycling):
        self._speed_cycling = speed_cycling
        self._regional_task.walkSpeed = speed_cycling / 3600 * 1000  # km/h -> m/s

    @property
    def speed_walking(self):
        return self._speed_walking

    @speed_walking.setter
    def speed_walking(self, speed_walking):
        self._speed_walking = speed_walking
        self._regional_task.walkSpeed = speed_walking / 3600 * 1000  # km/h -> m/s

    @property
    def transport_modes(self):
        return self._transport_modes

    @transport_modes.setter
    def transport_modes(self, transport_modes):
        self._transport_modes = transport_modes
        transit_modes = [
            mode
            for mode in transport_modes
            if isinstance(mode, TransitMode)
        ]
        self._regional_task.transitModes(
            transit_modes,
            com.conveyal.r5.api.util.LegMode
        )
        direct_modes = [
            mode
            for mode in transport_modes
            if isinstance(mode, StreetMode)
        ]
        self._regional_task.directModes = RegionalTask._enum_set(
            direct_modes,
            com.conveyal.r5.api.util.LegMode  # (!) on purpose (see below)
        )
        # StreetMode is a subset of LegMode.
        # com.conveyal.r5.analyst.TravelTimeComputer expects LegModes

        for mode in direct_modes:
            for destination_point_set in self._regional_task.destinationPointSets:
                self._transport_network.linkageCache.getLinkage(
                    destination_point_set,
                    self._transport_network.streetLayer,
                    mode.value
                )

    @staticmethod
    def _enum_set(values, java_class):
        enum_set = java.util.EnumSet.noneOf(java_class)
        for mode in values:
            enum_set.add(mode.value)
        return enum_set


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.analyst.cluster.RegionalTask",
    exact=RegionalTask
)
def _cast_RegionalTask(java_class, object_):
    return object_._regional_task
