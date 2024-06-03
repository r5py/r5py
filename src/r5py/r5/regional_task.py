#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.analyst.cluster.RegionalTask."""

import collections.abc
import datetime
import warnings

import jpype

from .scenario import Scenario
from .transport_mode import TransportMode
from ..util import start_jvm

import java.io
import java.time
import com.conveyal.r5


__all__ = ["RegionalTask"]


start_jvm()


class RegionalTask:
    """Create a RegionalTask, a computing request for R5."""

    def __init__(
        self,
        transport_network,
        origin=None,
        destinations=None,
        departure=datetime.datetime.now(),
        departure_time_window=datetime.timedelta(minutes=10),
        percentiles=[50],
        transport_modes=[TransportMode.TRANSIT],
        access_modes=[TransportMode.WALK],
        egress_modes=None,  # default: access_modes
        max_time=datetime.timedelta(hours=2),
        max_time_walking=datetime.timedelta(hours=2),
        max_time_cycling=datetime.timedelta(hours=2),
        max_time_driving=datetime.timedelta(hours=2),
        speed_walking=3.6,
        speed_cycling=12.0,
        max_public_transport_rides=8,
        max_bicycle_traffic_stress=3,
        breakdown=False,
    ):
        """
        Create a RegionalTask, a computing request for R5.

        A RegionalTask wraps a `com.conveyal.r5.analyst.cluster.RegionalTask`,
        which is used to specify the details of a requested computation.
        RegionalTasks underlie virtually all major computations carried out,
        such as, e.g., `TravelTimeMatrixComputer` or `AccessibilityEstimator`.

        In **r5py**, there is usually no need to explicitely create a
        `RegionalTask`. Rather, the constructors to the computation classes
        (`TravelTimeMatrixComputer`, `AccessibilityEstimator`, ...) accept the
        arguments, and pass them through to an internally handled
        `RegionalTask`.

        Arguments
        ---------
        transport_network : r5py.TransportNetwork
            The street + public transport network to route on
        origin : shapely.geometry.Point
            Point to route from
        destinations : geopandas.GeoDataFrame
            Points to route to, has to have at least an ``id`` column and a
            geometry
        departure : datetime.datetime
            Find public transport connections leaving every minute within
            ``departure_time_window`` after ``departure``. Default: current date
            and time
        departure_time_window : datetime.timedelta
            (see ``departure``) Default: 10 minutes
        percentiles : list[int]
            Return the travel time for these percentiles of all computed trips,
            by travel time. By default, return the median travel time. Default:
            [50]
        transport_modes : list[r5py.TransportMode] or list[str]
            The mode of transport to use for routing. Can be a r5py mode
            enumerable, or a string representation (e.g. "TRANSIT") Default:
            [r5py.TransportMode.TRANSIT] (all public transport)
        access_modes : list[r5py.TransportMode] or list[str]
            Mode of transport to public transport stops. Can be a r5py mode
            object, or a string representation (e.g. "WALK") Default:
            [r5py.TransportMode.WALK]
        egress_modes : list[r5py.TransportMode]
            Mode of transport from public transport stops. Default: access_modes
        max_time : datetime.timedelta
            Maximum trip duration. Default: 2 hours
        max_time_walking : datetime.timedelta
            Maximum time spent walking, potentially including access and egress
            Default: max_time
        max_time_cycling : datetime.timedelta
            Maximum time spent cycling, potentially including access and egress
            Default: max_time
        max_time_driving : datetime.timedelta
            Maximum time spent driving Default: max_time
        speed_walking : float
            Mean walking speed for routing, km/h. Default: 3.6 km/h
        speed_cycling : float
            Mean cycling speed for routing, km/h. Default: 12.0 km/h
        max_public_transport_rides : int
            Use at most ``max_public_transport_rides`` consecutive public
            transport connections. Default: 8
        max_bicycle_traffic_stress : int
            Maximum stress level for cyclist routing, ranges from 1-4 see
            https://docs.conveyal.com/learn-more/traffic-stress Default: 3
        breakdown : bool
            Compute a more detailed breakdown of the routes. Default: False
        """
        self._regional_task = com.conveyal.r5.analyst.cluster.RegionalTask()
        self.scenario = Scenario()

        self.transport_network = transport_network

        self.origin = origin
        self.destinations = destinations

        self.access_modes = access_modes
        self.egress_modes = egress_modes if egress_modes is not None else access_modes
        # last, because extra logic that depends on the others having been set
        self.transport_modes = transport_modes

        self.departure = departure  # transport modes should be set before this line
        self.departure_time_window = departure_time_window
        self.percentiles = percentiles

        self.max_time = max_time
        self.max_time_walking = (
            max_time_walking if max_time_walking is not None else max_time
        )
        self.max_time_cycling = (
            max_time_cycling if max_time_cycling is not None else max_time
        )
        self.max_time_driving = (
            max_time_driving if max_time_driving is not None else max_time
        )

        self.speed_cycling = speed_cycling
        self.speed_walking = speed_walking

        self.max_public_transport_rides = max_public_transport_rides
        self.max_bicycle_traffic_stress = max_bicycle_traffic_stress

        # always record travel times
        self._regional_task.recordTimes = True
        # also report paths, if `breakdown`
        self.breakdown = breakdown

        # a few settings we don’t expose (yet?)
        self._regional_task.makeTauiSite = False
        self._regional_task.oneToOne = False
        self._regional_task.monteCarloDraws = 60
        self._regional_task.recordAccessibility = False

    def __copy__(self):
        """Override `copy.copy()` to properly handle Java classes."""
        # remember all __dict__ except `_regional_task`, which is a Java `Clonable`
        _dict = {k: v for k, v in self.__dict__.items() if k != "_regional_task"}
        # add a clone of the Java object
        _dict["_regional_task"] = self._regional_task.clone()

        # create a new instance, copy over the __dict__ created above
        clone = super().__new__(self.__class__)
        clone.__dict__ = _dict

        return clone

    @property
    def access_modes(self):
        """Route with these modes of transport to reach public transport (r5py.TransportMode)."""
        return self._access_modes

    @access_modes.setter
    def access_modes(self, access_modes):
        # eliminate duplicates, cast to TransportMode (converts str values)
        access_modes = set([TransportMode(mode) for mode in set(access_modes)])
        self._access_modes = access_modes
        self._regional_task.accessModes = RegionalTask._enum_set(
            access_modes, com.conveyal.r5.api.util.LegMode
        )

    @property
    def breakdown(self):
        """Compute a more detailed breakdown of the routes."""
        return self._breakdown

    @breakdown.setter
    def breakdown(self, breakdown):
        self._breakdown = breakdown
        self._regional_task.includePathResults = breakdown

        # R5 has a maximum number of destinations for which it returns detailed
        # information, and it’s set to 5000 by default.
        # The value is a static property of com.conveyal.r5.analyst.cluster.PathResult;
        # static properites of Java classes can be modified in a singleton kind of way
        try:
            num_destinations = len(self.destinations)
        except AttributeError:
            num_destinations = 0
        if (
            num_destinations
            > com.conveyal.r5.analyst.cluster.PathResult.MAX_PATH_DESTINATIONS
        ):
            com.conveyal.r5.analyst.cluster.PathResult.MAX_PATH_DESTINATIONS = (
                num_destinations + 1
            )

    @property
    def departure(self):
        """Find public transport connections leaving within ``departure_time_window`` after ``departure`` (datetime.datetime)."""
        return self._departure

    @departure.setter
    def departure(self, departure):
        # fmt: off
        if (
            [mode for mode in self.transport_modes if mode.is_transit_mode]
            and not self.transport_network.transit_layer.covers(departure)
        ):
            # fmt: on
            warnings.warn(
                f"Departure time {departure} is outside of the time range "
                "covered by currently loaded GTFS data sets.",
                RuntimeWarning,
            )

        self._departure = departure
        self._regional_task.date = java.time.LocalDate.of(
            departure.year, departure.month, departure.day
        )
        # seconds from midnight
        self._regional_task.fromTime = int(
            datetime.timedelta(
                hours=departure.hour, minutes=departure.minute
            ).total_seconds()
        )
        try:
            self._regional_task.toTime = int(
                self._regional_task.fromTime
                + self.departure_time_window.total_seconds()
            )
        except AttributeError:  # departure_time_window has not been set yet
            pass

    @property
    def departure_time_window(self):
        """Find public transport connections leaving within ``departure_time_window`` after ``departure`` (datetime.timedelta).

        **Note:** The value of ``departure_time_window`` should be set with some
        caution. Specifically, setting values near or below the typical headways
        in the studied transit network may lead to routing problems. See `this
        GitHub discussion <https://github.com/r5py/r5py/issues/292>`_ for
        details.
        """
        return self._departure_time_window

    @departure_time_window.setter
    def departure_time_window(self, departure_time_window: datetime.timedelta):
        if departure_time_window.total_seconds() < 300:
            warnings.warn(
                "The provided departure time window is below 5 minutes. This may cause adverse effects with routing.",
                RuntimeWarning,
            )
        self._departure_time_window = departure_time_window
        self._regional_task.toTime = int(
            self._regional_task.fromTime + departure_time_window.total_seconds()
        )

    @property
    def destinations(self):
        """
        Points to route to.

        A ``geopandas.GeoDataFrame`` with a point geometry, and at least
        an ``id`` column (which R5 mangles to ``str``).
        """
        return self._destinations

    @destinations.setter
    def destinations(self, destinations):
        if destinations is not None:
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

            # TODO: figure out whether we could cut this a bit shorter. We should be able
            # to construct the ByteArray fed to java.io.ByteArrayInputStream as a Python `bytes`
            # without the detour via two Java OutputStreams.
            # (but not sure how to distinguish between the writeUTF/writeDouble/etc)

    @property
    def egress_modes(self):
        """Route with these modes of transport to reach the destination from public transport (r5py.TransportMode)."""
        return self._egress_modes

    @egress_modes.setter
    def egress_modes(self, egress_modes):
        # eliminate duplicates, cast to TransportMode (converts str values)
        egress_modes = set([TransportMode(mode) for mode in set(egress_modes)])
        self._egress_modes = egress_modes
        self._regional_task.egressModes = RegionalTask._enum_set(
            egress_modes, com.conveyal.r5.api.util.LegMode
        )

    @property
    def max_bicycle_traffic_stress(self):
        """
        Find routes with this maximum stress level for cyclists.

        Int, in the range 1-4, see https://docs.conveyal.com/learn-more/traffic-stress
        """
        return self._max_bicycle_traffic_stress

    @max_bicycle_traffic_stress.setter
    def max_bicycle_traffic_stress(self, max_bicycle_traffic_stress):
        self._max_bicycle_traffic_stress = max_bicycle_traffic_stress
        self._regional_task.bikeTrafficStress = max_bicycle_traffic_stress

    @property
    def max_public_transport_rides(self):
        """Include at most this many consecutive public transport rides (int)."""
        return self._max_public_transport_rides

    @max_public_transport_rides.setter
    def max_public_transport_rides(self, max_public_transport_rides):
        self._max_public_transport_rides = max_public_transport_rides
        self._regional_task.maxRides = max_public_transport_rides

    @property
    def max_time(self):
        """Restrict trip duration (datetime.timedelta)."""
        return self._max_time

    @max_time.setter
    def max_time(self, max_time):
        self._max_time = max_time
        max_time = int(max_time.total_seconds() / 60)
        self._regional_task.streetTime = max_time
        self._regional_task.maxTripDurationMinutes = max_time
        self._regional_task.maxCarTime = max_time

    @property
    def max_time_cycling(self):
        """
        Restrict routes to at most this duration of cycling (datetime.timedelta).

        Depending on the transport modes specified, this includes times
        on the main leg of the trip, as well as during access and egress.
        """
        return self._max_time_cycling

    @max_time_cycling.setter
    def max_time_cycling(self, max_time_cycling):
        self._max_time_cycling = max_time_cycling
        self._regional_task.maxBikeTime = int(max_time_cycling.total_seconds() / 60)

    @property
    def max_time_driving(self):
        """Restrict routes to at most this duration of driving (datetime.timedelta)."""
        return self._max_time_driving

    @max_time_driving.setter
    def max_time_driving(self, max_time_driving):
        self._max_time_driving = max_time_driving
        self._regional_task.maxCarTime = int(max_time_driving.total_seconds() / 60)

    @property
    def max_time_walking(self):
        """
        Restrict routes to at most this duration of walking (datetime.timedelta).

        Depending on the transport modes specified, this includes times
        on the main leg of the trip, as well as during access and egress.
        """
        return self._max_time_walking

    @max_time_walking.setter
    def max_time_walking(self, max_time_walking):
        self._max_time_walking = max_time_walking
        self._regional_task.maxWalkTime = int(max_time_walking.total_seconds() / 60)

    @property
    def percentiles(self):
        """
        Return the travel time for these percentiles of all computed trips, by travel time.

        By default, return the median travel time.
        (collections.abc.Sequence[int])
        """
        return self._percentiles

    @percentiles.setter
    def percentiles(self, percentiles):
        try:
            assert isinstance(percentiles, collections.abc.Sequence)
            assert len(percentiles) <= 5  # R5 does not allow more than five percentiles
            # (compare https://github.com/r5py/r5py/issues/139 )
        except AssertionError as exception:
            raise ValueError(
                "Maximum number of percentiles allowed is 5"
            ) from exception
        self._percentiles = percentiles
        self._regional_task.percentiles = percentiles

    # TODO: implement a proper balancing mechanism between the different per-mode
    # maximum times, i.e., a sanity check that the different more specific max_times
    # don’t exceed max_time, for instance, but probably also more complex interrelations
    # (this needs some sitting down with pen and paper and a large cup of tea)

    @property
    def origin(self):
        """Set the origin for the routing operation (shapely.geometry.Point)."""
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
        if origin is not None:
            self._origin = origin
            self._regional_task.fromLat = origin.y
            self._regional_task.fromLon = origin.x

    @property
    def scenario(self):
        """Expose the ``RegionalTask``’s ``Scenario`` to Python."""
        return self._regional_task.scenario

    @scenario.setter
    def scenario(self, scenario):
        self._regional_task.scenario = scenario
        self._regional_task.scenarioId = scenario.id

    @property
    def speed_cycling(self):
        """Use this speed for routing for cyclists (km/h, float)."""
        return self._speed_cycling

    @speed_cycling.setter
    def speed_cycling(self, speed_cycling):
        self._speed_cycling = speed_cycling
        self._regional_task.bikeSpeed = speed_cycling / 3600 * 1000  # km/h -> m/s

    @property
    def speed_walking(self):
        """Use this speed for routing pedestrian movement (km/h, float)."""
        return self._speed_walking

    @speed_walking.setter
    def speed_walking(self, speed_walking):
        self._speed_walking = speed_walking
        self._regional_task.walkSpeed = speed_walking / 3600 * 1000  # km/h -> m/s

    @property
    def transport_modes(self):
        """
        Get/set the transport modes used to route the main leg of trips.

        (list[r5py.TransportMode])
        """
        return self._transport_modes

    @transport_modes.setter
    def transport_modes(self, transport_modes):
        # eliminate duplicates, cast to TransportMode (converts str values)
        transport_modes = set([TransportMode(mode) for mode in set(transport_modes)])
        self._transport_modes = transport_modes

        # split them up into direct and transit modes,
        transit_modes = [mode for mode in transport_modes if mode.is_transit_mode]
        direct_modes = [mode for mode in transport_modes if mode.is_street_mode]

        # the different modes underlie certain rules
        # e.g., some direct modes require certain access modes
        # see https://github.com/ipeaGIT/r5r/blob/2e8b9acfd81834f185d95ce53dc5c34beb1315f2/r-package/R/utils.R#L86
        if transit_modes:  # public transport:
            egress_modes = self.egress_modes
            if TransportMode.TRANSIT in transport_modes:
                transit_modes = [mode for mode in TransportMode if mode.is_transit_mode]
            if not direct_modes:
                # only public transport modes passed in,
                # let people walk to and from the stops
                access_modes = direct_modes = [TransportMode.WALK]
            else:
                # otherwise, include the supplied direct modes into access_modes
                access_modes = set(list(self.access_modes) + direct_modes)

        else:  # no public transport
            egress_modes = []  # ignore egress (why?)

            #     # this is weird (the following is the logic implemented in r5r)
            #     # I reckon this is trying to keep the fastest mode only, and
            #     # assumes that car is always faster that bike is always faster than walking
            #     if TransportMode.CAR in transport_modes:
            #         access_modes = direct_modes = [TransportMode.CAR]
            #     elif TransportMode.BICYCLE in transport_modes:
            #         access_modes = direct_modes = [TransportMode.BICYCLE]
            #     elif TransportMode.WALK in transport_modes:
            #         access_modes = direct_modes = [TransportMode.WALK]

            # let’s do that differently (even if potentially more expensive, computationally)
            access_modes = direct_modes

        self.access_modes = access_modes
        self.egress_modes = egress_modes

        self._regional_task.transitModes = RegionalTask._enum_set(
            transit_modes, com.conveyal.r5.api.util.TransitModes
        )
        self._regional_task.directModes = RegionalTask._enum_set(
            direct_modes, com.conveyal.r5.api.util.LegMode
        )

        # pre-compute closest road segments/public transport stops to destination points
        # (for fully-interconnected travel time matrices this also covers all origin points,
        # but potentially this needs to be extended to run also for origins) //TODO

        if self._regional_task.destinationPointSets is not None:
            for mode in direct_modes:
                for destination_point_set in self._regional_task.destinationPointSets:
                    self.transport_network.linkage_cache.getLinkage(
                        destination_point_set,
                        self.transport_network.street_layer,
                        mode,
                    )

    @staticmethod
    def _enum_set(values, java_class):
        # helper function to construct a Java EnumSet out of a list of enum.Enum
        enum_set = java.util.EnumSet.noneOf(java_class)
        for mode in values:
            enum_set.add(java_class.valueOf(mode.value))
        return enum_set


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.analyst.cluster.AnalysisWorkerTask", exact=RegionalTask
)
@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.profile.ProfileRequest", exact=RegionalTask
)
@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.analyst.cluster.RegionalTask", exact=RegionalTask
)
def _cast_RegionalTask(java_class, object_):
    return object_._regional_task.clone()
    # cloned, so we can reuse the Python instance (e.g., with next origin)
