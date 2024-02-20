#!/usr/bin/env python3

import geopandas
import pandas
import datetime
import pytest
import pytest_lazy_fixtures

import r5py
import r5py.util.exceptions


class TestTravelTimeMatrixInputValidation:
    def test_departure_time_window_warning(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        with pytest.warns(
            RuntimeWarning,
            match="The provided departure time window is below 5 minutes",
        ):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origin_point,
                destinations=population_grid_points,
                departure_time_window=datetime.timedelta(
                    minutes=3
                ),  # Should throw warning
                departure=departure_datetime,
                transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "expected_error",
        ],
        [
            (
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_invalid_data(
        self,
        transport_network,
        origins,
        departure_datetime,
        expected_error,
    ):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network, origins=origins, departure=departure_datetime
            )
            del travel_time_matrix_computer

    def test_origins_valid_data(
        self,
        transport_network,
        origins_valid_ids,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origins_valid_ids,
            departure=departure_datetime,
        )
        del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
            "expected_error",
        ],
        [
            (
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest_lazy_fixtures.lf("origins_invalid_duplicate_ids"),
                pytest_lazy_fixtures.lf("origins_invalid_no_id"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_and_destinations_invalid_data(
        self,
        transport_network,
        origins,
        destinations,
        departure_datetime,
        expected_error,
    ):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origins,
                destinations=destinations,
                departure=departure_datetime,
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
        ],
        [
            (
                pytest_lazy_fixtures.lf("origins_valid_ids"),
                pytest_lazy_fixtures.lf("origins_valid_ids"),
            )
        ],
    )
    def test_origins_and_destinations_valid_data(
        self,
        transport_network,
        origins,
        destinations,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origins,
            destinations=destinations,
            departure=departure_datetime,
        )
        _ = travel_time_matrix_computer.compute_travel_times()

    def test_try_to_route_without_origins(
        self,
        transport_network,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            departure=departure_datetime,
        )
        with pytest.raises(ValueError, match="No routing origins defined"):
            _ = travel_time_matrix_computer.compute_travel_times()

    def test_try_to_route_without_destinations(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=population_grid_points[0:3],
            departure=departure_datetime,
        )
        _ = travel_time_matrix_computer.compute_travel_times()
        pandas.testing.assert_frame_equal(
            travel_time_matrix_computer.origins,
            travel_time_matrix_computer.destinations,
        )


class TestTravelTimeMatrixComputer:
    def test_travel_time_matrix_initialization(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )
        assert isinstance(
            travel_time_matrix_computer.transport_network, r5py.TransportNetwork
        )
        assert isinstance(travel_time_matrix_computer.origins, geopandas.GeoDataFrame)
        assert isinstance(
            travel_time_matrix_computer.destinations, geopandas.GeoDataFrame
        )

        assert travel_time_matrix_computer.origins.shape == origin_point.shape
        assert (
            travel_time_matrix_computer.destinations.shape
            == population_grid_points.shape
        )

    def test_travel_time_matrix_initialization_with_files(
        self,
        transport_network_files_tuple,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_files_tuple,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )
        assert isinstance(
            travel_time_matrix_computer.transport_network, r5py.TransportNetwork
        )

    def test_all_to_all(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()

        assert isinstance(travel_time_matrix, pandas.DataFrame)
        assert travel_time_matrix.shape == (8464, 3)
        assert travel_time_matrix.columns.to_list() == [
            "from_id",
            "to_id",
            "travel_time",
        ]
        assert travel_time_matrix["from_id"].min() == travel_time_matrix["to_id"].min()
        assert travel_time_matrix["from_id"].max() == travel_time_matrix["to_id"].max()
        assert travel_time_matrix["travel_time"].min() >= 0
        # There can be a bit of fluctuation in the maximum travel time
        assert travel_time_matrix["travel_time"].max() == pytest.approx(50, abs=3)

    def test_one_to_all(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
        assert travel_time_matrix.shape == (92, 3)
        assert travel_time_matrix["from_id"].unique() == [0]
        assert travel_time_matrix["to_id"].min() == 0
        assert travel_time_matrix["to_id"].max() == 91
        # There can be a bit of fluctuation in the maximum travel time
        assert travel_time_matrix["travel_time"].max() == pytest.approx(30, abs=3)

    def test_one_to_all_with_percentiles(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            percentiles=[25, 50, 75],
        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
        assert travel_time_matrix.shape == (92, 5)
        required_cols = ["travel_time_p25", "travel_time_p50", "travel_time_p75"]
        for col in required_cols:
            assert col in travel_time_matrix.columns

        # 75 percentile should always be higher or equal to 25 percentile
        check = (
            travel_time_matrix["travel_time_p75"]
            >= travel_time_matrix["travel_time_p25"]
        )
        assert False not in check.to_list()

    def test_gtfs_date_range_warnings(
        self,
        transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        with pytest.warns(RuntimeWarning, match="Departure time"):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origin_point,
                destinations=population_grid_points,
                departure=datetime.datetime(2021, 2, 22, 8, 30),  # not in GTFS data set
                transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            )
            del travel_time_matrix_computer

    def test_gtfs_date_range_warnings_without_gtfs_file(
        self,
        transport_network_from_test_files_without_gtfs,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        with pytest.warns(RuntimeWarning, match="Departure"):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network_from_test_files_without_gtfs,
                origins=origin_point,
                destinations=population_grid_points,
                departure=departure_datetime,
                transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "snap_to_network",
            "expected_snap_to_network",
        ],
        [
            (
                True,
                True,
            ),
            (
                False,
                False,
            ),
        ],
    )
    def test_snap_to_network_parameter(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        snap_to_network,
        expected_snap_to_network,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            population_grid_points,
            departure=departure_datetime,
            snap_to_network=snap_to_network,
        )
        assert travel_time_matrix_computer.snap_to_network == expected_snap_to_network

    @pytest.mark.parametrize(
        [
            "snap_to_network",
            "expected_travel_times",
        ],
        [
            (
                True,
                pytest_lazy_fixtures.lf("walking_times_snapped"),
            ),
            (
                False,
                pytest_lazy_fixtures.lf("walking_times_not_snapped"),
            ),
        ],
    )
    def test_snap_to_network(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        snap_to_network,
        expected_travel_times,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=population_grid_points,
            departure=departure_datetime,
            snap_to_network=snap_to_network,
            transport_modes=[r5py.TransportMode.WALK],
        )
        travel_times = travel_time_matrix_computer.compute_travel_times()

        travel_times = travel_times.set_index(["from_id", "to_id"]).sort_index()
        expected_travel_times = expected_travel_times.set_index(
            ["from_id", "to_id"]
        ).sort_index()

        pandas.testing.assert_frame_equal(travel_times, expected_travel_times)

    def test_snap_to_network_with_unsnappable_origins(
        self,
        transport_network,
        unsnappable_points,
        population_grid_points,
        departure_datetime,
    ):
        origins = pandas.concat(
            [population_grid_points[-3:], unsnappable_points]
        ).reset_index(drop=False)
        with pytest.warns(
            RuntimeWarning,
            match=(
                "Some (origin|destination) points could not "
                "be snapped to the street network"
            ),
        ):
            travel_time_matrix = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins,
                departure=departure_datetime,
                snap_to_network=True,
                transport_modes=[r5py.TransportMode.WALK],
            )
            _ = travel_time_matrix.compute_travel_times()

    def test_snap_to_network_with_only_unsnappable_origins(
        self,
        transport_network,
        unsnappable_points,
        departure_datetime,
    ):
        with (
            pytest.raises(
                ValueError, match="After snapping, no valid origin points remain"
            ),
            pytest.warns(
                RuntimeWarning,
                match="Some origin points could not be snapped to the street network",
            ),
        ):
            travel_time_matrix = r5py.TravelTimeMatrixComputer(
                transport_network,
                unsnappable_points,
                departure=departure_datetime,
                snap_to_network=True,
                transport_modes=[r5py.TransportMode.WALK],
            )
            _ = travel_time_matrix.compute_travel_times()

    def test_snap_to_network_with_unsnappable_destinations(
        self,
        transport_network,
        population_grid_points,
        unsnappable_points,
        departure_datetime,
    ):
        destinations = pandas.concat(
            [population_grid_points[-3:], unsnappable_points]
        ).reset_index(drop=False)
        with pytest.warns(
            RuntimeWarning,
            match="Some destination points could not be snapped to the street network",
        ):
            travel_time_matrix = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=population_grid_points,
                destinations=destinations,
                departure=departure_datetime,
                snap_to_network=True,
                transport_modes=[r5py.TransportMode.WALK],
            )
            _ = travel_time_matrix.compute_travel_times()

    def test_snap_to_network_with_only_unsnappable_destinations(
        self,
        transport_network,
        population_grid_points,
        unsnappable_points,
        departure_datetime,
    ):
        with (
            pytest.raises(
                ValueError, match="After snapping, no valid destination points remain"
            ),
            pytest.warns(
                RuntimeWarning,
                match="Some destination points could not be snapped to the street network",
            ),
        ):
            travel_time_matrix = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=population_grid_points,
                destinations=unsnappable_points,
                departure=departure_datetime,
                snap_to_network=True,
                transport_modes=[r5py.TransportMode.WALK],
            )
            _ = travel_time_matrix.compute_travel_times()

    @pytest.mark.parametrize("snap_to_network", [True, False])
    def test_travel_time_between_identical_from_and_to_ids(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        snap_to_network,
    ):
        travel_time_matrix = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=population_grid_points,
            transport_modes=[r5py.TransportMode.WALK],
            departure=departure_datetime,
            snap_to_network=snap_to_network,
        ).compute_travel_times()

        assert (
            travel_time_matrix[
                travel_time_matrix["from_id"] == travel_time_matrix["to_id"]
            ].travel_time.max()
            == 0
        )
