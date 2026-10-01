#!/usr/bin/env python3

import datetime

import geopandas
import numpy
import pandas
import pytest
import shapely

import r5py


def _total(value):
    """Sum a per-leg list column, tolerating scalars and empty lists."""
    if isinstance(value, (list, tuple, numpy.ndarray)):
        return float(numpy.sum(value)) if len(value) else 0.0
    return float(value)


@pytest.fixture(scope="module")
def transit_network():
    """Build the Helsinki sample transport network once for this module."""
    import r5py.sampledata.helsinki

    yield r5py.TransportNetwork(
        r5py.sampledata.helsinki.osm_pbf, [r5py.sampledata.helsinki.gtfs]
    )


class TestExpandedTravelTimeMatrixInputValidation:
    def test_too_many_destinations(
        self,
        transit_network,
        departure_datetime,
    ):
        # more destinations than R5 records path details for
        n = r5py.r5.expanded_travel_time_matrix.MAX_PATH_DESTINATIONS + 1
        points = geopandas.GeoDataFrame(
            {"id": [str(i) for i in range(n)]},
            geometry=[shapely.Point(24.94 + i * 1e-6, 60.17) for i in range(n)],
            crs="EPSG:4326",
        )
        with pytest.raises(ValueError, match="at most"):
            _ = r5py.ExpandedTravelTimeMatrix(
                transit_network,
                origins=points[0:1],
                destinations=points,
                departure=departure_datetime,
            )


class TestExpandedTravelTimeMatrix:
    @pytest.fixture(scope="module")
    def expanded(
        self,
        transit_network,
        population_grid_points,
        departure_datetime,
    ):
        yield r5py.ExpandedTravelTimeMatrix(
            transit_network,
            origins=population_grid_points[0:3],
            destinations=population_grid_points,
            departure=departure_datetime,
            departure_time_window=datetime.timedelta(minutes=60),
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )

    def test_type_and_columns(self, expanded):
        assert isinstance(expanded, pandas.DataFrame)
        assert list(expanded.columns) == r5py.ExpandedTravelTimeMatrix.COLUMNS

    def test_not_empty(self, expanded):
        assert len(expanded) > 0

    def test_dtypes(self, expanded):
        for column in (
            "from_id",
            "to_id",
            "routes",
            "route_types",
            "board_stops",
            "feed_ids",
        ):
            assert pandas.api.types.is_string_dtype(expanded[column])
        for column in (
            "access_time",
            "egress_time",
            "transfer_time",
            "total_time",
        ):
            assert expanded[column].dtype == float
        for column in ("n_rides", "n_iterations"):
            assert expanded[column].dtype == int
        # per-leg components are kept as (Python) lists
        assert all(isinstance(v, list) for v in expanded["ride_time"])
        assert all(isinstance(v, list) for v in expanded["wait_time"])

    def test_components_reconcile_to_total(self, expanded):
        # for every row, the components add up to the reported total time
        transit = expanded[expanded["n_rides"] > 0]
        assert len(transit) > 0
        reconstructed = (
            transit["ride_time"].map(_total)
            + transit["wait_time"].map(_total)
            + transit["access_time"]
            + transit["egress_time"]
            + transit["transfer_time"]
        )
        numpy.testing.assert_allclose(
            reconstructed.to_numpy(),
            transit["total_time"].to_numpy(),
            atol=1e-6,
        )

    def test_n_rides_matches_path_identity(self, expanded):
        transit = expanded[expanded["n_rides"] > 0]
        # routes / stops / in-vehicle lists have one entry per ride
        assert (transit["routes"].str.split("|").map(len) == transit["n_rides"]).all()
        assert (transit["ride_time"].map(len) == transit["n_rides"]).all()
        assert (
            transit["board_stops"].str.split("|").map(len) == transit["n_rides"]
        ).all()
        assert (
            transit["route_types"].str.split("|").map(len) == transit["n_rides"]
        ).all()

    def test_route_types_are_gtfs_codes(self, expanded):
        transit = expanded[expanded["n_rides"] > 0]
        assert len(transit) > 0
        codes = {
            int(code) for entry in transit["route_types"] for code in entry.split("|")
        }
        # every leg reports a parseable GTFS route_type, either a basic code
        # (0–12) or an extended one (100–1799); the Helsinki fixture uses
        # extended codes for its buses (700-series)
        assert codes
        assert all(0 <= code <= 12 or 100 <= code <= 1799 for code in codes)

    def test_walk_only_rows_have_no_transit(self, expanded):
        walk_only = expanded[expanded["n_rides"] == 0]
        # walk-only (direct) templates carry no route identity and no rides
        assert (walk_only["routes"] == "").all()
        assert (walk_only["route_types"] == "").all()
        assert walk_only["ride_time"].map(_total).eq(0.0).all()

    def test_n_iterations_positive(self, expanded):
        assert (expanded["n_iterations"] > 0).all()

    def test_direct_paths_without_transit(
        self,
        transit_network,
        population_grid_points,
        departure_datetime,
    ):
        # R5 records path details only in its transit search, which it skips
        # without transit modes: direct paths are reported nevertheless
        kwargs = dict(
            origins=population_grid_points[0:1],
            destinations=population_grid_points[0:10],
            departure=departure_datetime,
            departure_time_window=datetime.timedelta(minutes=10),
            transport_modes=[r5py.TransportMode.WALK],
        )
        expanded = r5py.ExpandedTravelTimeMatrix(transit_network, **kwargs)
        travel_times = r5py.TravelTimeMatrix(transit_network, **kwargs)

        assert list(expanded.columns) == r5py.ExpandedTravelTimeMatrix.COLUMNS
        assert len(expanded) == travel_times["travel_time"].notna().sum()
        assert (expanded["n_rides"] == 0).all()
        assert (expanded["routes"] == "").all()
        assert (expanded["n_iterations"] == 10).all()

        # TravelTimeMatrix reports 0 for an origin’s own location, R5 does not
        travel_times = travel_times.astype({"from_id": str, "to_id": str})
        merged = expanded.merge(travel_times, on=["from_id", "to_id"])
        merged = merged[merged["from_id"] != merged["to_id"]]
        assert len(merged) > 0
        assert (merged["total_time"] == merged["travel_time"]).all()

    def test_minimum_not_slower_than_mean(
        self,
        transit_network,
        population_grid_points,
        departure_datetime,
    ):
        kwargs = dict(
            origins=population_grid_points[0:3],
            destinations=population_grid_points,
            departure=departure_datetime,
            departure_time_window=datetime.timedelta(minutes=60),
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )
        mean = r5py.ExpandedTravelTimeMatrix(
            transit_network, breakdown_stat=r5py.BreakdownStat.MEAN, **kwargs
        )
        minimum = r5py.ExpandedTravelTimeMatrix(
            transit_network, breakdown_stat=r5py.BreakdownStat.MINIMUM, **kwargs
        )

        # the same path templates are found, only their summaries differ
        pair = ["from_id", "to_id"]
        assert len(mean) == len(minimum)
        assert (
            mean.groupby(pair).size().sort_index()
            == minimum.groupby(pair).size().sort_index()
        ).all()

        # each template’s fastest iteration is no slower than its average, and,
        # hence, neither is the fastest template per pair
        fastest_mean = mean.groupby(pair)["total_time"].min().sort_index()
        fastest_minimum = minimum.groupby(pair)["total_time"].min().sort_index()
        assert (fastest_minimum <= fastest_mean + 1e-6).all()
        assert (fastest_minimum < fastest_mean - 1e-6).any()


class TestBreakdownStat:
    def test_members(self):
        assert set(r5py.BreakdownStat.__members__) == {"MEAN", "MINIMUM"}
