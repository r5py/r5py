#!/usr/bin/env python3


"""Calculate detailed itineraries between many origins and destinations."""


import copy
import warnings

try:
    from warnings import deprecated
except ImportError:  # Python<=3.12
    from typing_extensions import deprecated

import geopandas
import joblib
import pandas

from .base_travel_time_matrix import BaseTravelTimeMatrix
from .trip import Trip
from .trip_planner import ACCURATE_GEOMETRIES, TripPlanner


__all__ = ["DetailedItineraries", "DetailedItinerariesComputer"]


class DetailedItineraries(BaseTravelTimeMatrix):
    """Compute detailed itineraries between many origins and destinations."""

    COLUMNS = ["from_id", "to_id", "option"] + Trip.COLUMNS

    _r5py_attributes = BaseTravelTimeMatrix._r5py_attributes + [
        "all_to_all",
        "od_pairs",
    ]

    def __init__(
        self,
        transport_network,
        origins=None,
        destinations=None,
        snap_to_network=False,
        force_all_to_all=False,
        **kwargs,
    ):
        """
        Compute travel times between many origins and destinations.

        ``r5py.DetailedItineraries`` are child classes of
        ``geopandas.GeoDataFrame`` and support all of their methods and
        properties, see https://geopandas.org/en/stable/docs.html

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
        force_all_to_all : bool, default False
            If ``origins`` and ``destinations`` have the same length, by
            default, ``DetailedItineraries`` finds routes between pairs
            of origins and destinations, i.e., it routes from origin #1 to
            destination #1, origin #2 to destination #2, ... .
            Set ``force_all_to_all=True`` to route from each origin to all
            destinations (this is the default, if ``origins`` and ``destinations``
            have different lengths, or if ``destinations`` is omitted)
        **kwargs : mixed
            Any arguments than can be passed to r5py.RegionalTask:
            ``departure``, ``departure_time_window``, ``percentiles``, ``transport_modes``,
            ``access_modes``, ``egress_modes``, ``max_time``, ``max_time_walking``,
            ``max_time_cycling``, ``max_time_driving``, ``speed_cycling``, ``speed_walking``,
            ``max_public_transport_rides``, ``max_bicycle_traffic_stress``
            Note that not all arguments might make sense in this context, and the
            underlying R5 engine might ignore some of them.
        """
        super().__init__(
            transport_network,
            origins,
            destinations,
            snap_to_network,
            **kwargs,
        )

        if destinations is None:
            self.all_to_all = True
            if self.verbose:
                warnings.warn(
                    "No destinations specified, computing an all-to-all matrix",
                    RuntimeWarning,
                )

        elif len(origins) != len(destinations):
            self.all_to_all = True
            if self.verbose:
                warnings.warn(
                    "Origins and destinations are of different length, computing an all-to-all matrix",
                    RuntimeWarning,
                )
        elif origins.equals(destinations):
            self.all_to_all = True
            if self.verbose:
                warnings.warn(
                    "Origins and destinations are identical, computing an all-to-all matrix",
                    RuntimeWarning,
                )
        else:
            self.all_to_all = force_all_to_all

        data = self._compute()
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=(
                    "You are adding a column named 'geometry' to a GeoDataFrame "
                    "constructed without an active geometry column"
                ),
                category=FutureWarning,
            )
            for column in data.columns:
                self[column] = data[column]
            self.set_geometry("geometry")

        del self.transport_network

    def _compute(self):
        """
        Compute travel times from all origins to all destinations.

        Returns
        -------
        geopandas.GeoDataFrame
            The resulting detailed routes. For each origin/destination pair,
            multiple route alternatives (‘options’) might be reported that each
            consist of one or more segments. Each segment represents one row.
            multiple route alternatives (‘options’) might be reported that each consist of
            one or more segments. Each segment represents one row.

            The data frame comprises of the following columns: `from_id`,
            `to_id`, `option` (`int`), `segment` (`int`), `transport_mode`
            (`r5py.TransportMode`), `departure_time` (`datetime.datetime`),
            `distance` (`float`, metres), `travel_time` (`datetime.timedelta`),
            `wait_time` (`datetime.timedelta`), `feed` (`str`, the feed name
            used), `agency_id` (`str` the public transport agency identifier),
            `route_id` (`str`, public transport route ID), `start_stop_id`
            (`str`, the GTFS stop_id for boarding), `end_stop_id` (`str`, the
            GTFS stop_id for alighting), `geometry` (`shapely.LineString`)
        """
        self._prepare_origins_destinations()

        # warn if public transport routes are requested, but R5 has been
        # compiled with `TransitLayer.SAVE_SHAPES = false`.
        if [
            mode for mode in self.request.transport_modes if mode.is_transit_mode
        ] and not ACCURATE_GEOMETRIES:
            warnings.warn(
                (
                    "R5 has been compiled with "
                    "`TransitLayer.SAVE_SHAPES = false` (the default). "
                    "The geometries of public transport routes are "
                    "inaccurate (straight lines between stops), and "
                    "distances can not be computed."
                ),
                RuntimeWarning,
            )

        # loop over all origin/destination pairs, modify the request, and
        # compute times, distance, and other details for each trip
        with joblib.Parallel(
            prefer="threads",
            verbose=(10 * self.verbose),  # joblib has a funny verbosity scale
            n_jobs=self.NUM_THREADS,
        ) as parallel:
            matrices = parallel(
                joblib.delayed(self._travel_details_per_od_pair)(from_id, to_id)
                for _, (from_id, to_id) in self.od_pairs.iterrows()
            )
            od_matrix = pandas.concat(
                [matrix.astype(matrices[0].dtypes) for matrix in matrices],
                ignore_index=True,
            )

        od_matrix = geopandas.GeoDataFrame(od_matrix, crs=self._origins_crs)
        return od_matrix

    def _prepare_origins_destinations(self):
        """Make sure we received enough information to route from origins to destinations."""
        super()._prepare_origins_destinations()

        if self.all_to_all:
            # manually create a list of all all-to-all permutations
            self.od_pairs = self.origins[["id"]].join(
                self.destinations[["id"]],
                how="cross",
                lsuffix="_origin",
                rsuffix="_destination",
            )
        else:
            # origins and destinations are same length, run one-to-one routing
            self.od_pairs = pandas.DataFrame(
                {
                    "id_origin": self.origins.id.values,
                    "id_destination": self.destinations.id.values,
                }
            )

    def _travel_details_per_od_pair(self, from_id, to_id):
        origin = self.origins[self.origins.id == from_id]
        destination = self.destinations[self.destinations.id == to_id]

        request = copy.copy(self.request)
        request._regional_task.fromLat = origin.geometry.item().y
        request._regional_task.fromLon = origin.geometry.item().x
        request._regional_task.toLat = destination.geometry.item().y
        request._regional_task.toLon = destination.geometry.item().x

        trip_planner = TripPlanner(self.transport_network, request)
        trips = trip_planner.trips

        # fmt: off
        trips = [
            [from_id, to_id, option] + segment
            for option, trip in enumerate(trips)
            for segment in trip.as_table()
        ]
        # fmt: on

        return pandas.DataFrame(trips, columns=self.COLUMNS)


@deprecated(
    "Use `DetailedItineraries` instead, `DetailedItinerariesComputer will be deprecated in a future release."
)
class DetailedItinerariesComputer:
    """Compute detailed itineraries between many origins and destinations."""

    def __init__(self, *args, **kwargs):
        """Compute detailed itineraries between many origins and destinations."""
        self._detailed_itineraries = DetailedItineraries(*args, **kwargs)

    def compute_travel_details(self):
        """
        Compute travel times from all origins to all destinations.

        Returns
        -------
        geopandas.GeoDataFrame
            The resulting detailed routes. For each origin/destination pair,
            multiple route alternatives (‘options’) might be reported that each consist of
            one or more segments. Each segment represents one row.
            The data frame comprises of the following columns: `from_id`,
            `to_id`, `option` (`int`), `segment` (`int`), `transport_mode`
            (`r5py.TransportMode`), `departure_time` (`datetime.datetime`),
            `distance` (`float`, metres), `travel_time` (`datetime.timedelta`),
            `wait_time` (`datetime.timedelta`), `route` (`str`, public transport
            route number or name), `geometry` (`shapely.LineString`)
            TODO: Add description of output data frame columns and format
        """
        return self._detailed_itineraries
