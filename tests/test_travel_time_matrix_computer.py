#!/usr/bin/env python3

import geopandas
import pandas
import datetime
import pytest  # noqa: F401

import r5py
import r5py.util.exceptions


class TestTravelTimeMatrixInputValidation:
    @pytest.mark.parametrize(
        [
            "origins",
            "expected_error",
        ],
        [
            (
                pytest.lazy_fixture("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_invalid_data(self, transport_network, origins, expected_error):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origins,
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
        ],
        [(pytest.lazy_fixture("origins_valid_ids"),)],
    )
    def test_origins_valid_data(self, transport_network, origins):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origins,
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
                pytest.lazy_fixture("origins_invalid_no_id"),
                pytest.lazy_fixture("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_no_id"),
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                pytest.lazy_fixture("origins_invalid_no_id"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_and_destinations_invalid_data(
        self, transport_network, origins, destinations, expected_error
    ):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origins,
                destinations=destinations,
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
        ],
        [
            (
                pytest.lazy_fixture("origins_valid_ids"),
                pytest.lazy_fixture("origins_valid_ids"),
            )
        ],
    )
    def test_origins_and_destinations_valid_data(
        self, transport_network, origins, destinations
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origins,
            destinations=destinations,
        )
        del travel_time_matrix_computer


class TestTravelTimeMatrixComputer:
    def test_travel_time_matrix_initialization(
        self, transport_network, population_grid_points, origin_point
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
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
        self, transport_network_files_tuple, population_grid_points, origin_point
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_files_tuple,
            origins=origin_point,
            destinations=population_grid_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
        )
        assert isinstance(
            travel_time_matrix_computer.transport_network, r5py.TransportNetwork
        )

    def test_all_to_all(self, transport_network, population_grid_points):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=population_grid_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
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

    def test_one_to_all(self, transport_network, population_grid_points, origin_point):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
        assert travel_time_matrix.shape == (92, 3)
        assert travel_time_matrix["from_id"].unique() == [0]
        assert travel_time_matrix["to_id"].min() == 0
        assert travel_time_matrix["to_id"].max() == 91
        # There can be a bit of fluctuation in the maximum travel time
        assert travel_time_matrix["travel_time"].max() == pytest.approx(30, abs=3)

    def test_one_to_all_with_percentiles(
        self, transport_network, population_grid_points, origin_point
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
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
        self, transport_network, population_grid_points, origin_point
    ):
        with pytest.warns(RuntimeWarning):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origin_point,
                destinations=population_grid_points,
                departure=datetime.datetime(2021, 2, 22, 8, 30),  # not in GTFS data set
                transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
            )
            del travel_time_matrix_computer

    def test_gtfs_date_range_warnings_without_gtfs_file(
        self,
        transport_network_from_test_files_without_gtfs,
        population_grid_points,
        origin_point,
    ):
        with pytest.warns(RuntimeWarning):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network_from_test_files_without_gtfs,
                origins=origin_point,
                destinations=population_grid_points,
                departure=datetime.datetime(2022, 2, 22, 8, 30),
                transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "transport_network_",
            "origins",
            "snap_to_network",
            "expected_snap_to_network",
        ],
        [
            (
                pytest.lazy_fixture("transport_network"),
                pytest.lazy_fixture("population_grid_points"),
                True,
                True,
            ),
            (
                pytest.lazy_fixture("transport_network"),
                pytest.lazy_fixture("population_grid_points"),
                False,
                False,
            ),
        ],
    )
    def test_snap_to_network_parameter(
        self, transport_network_, origins, snap_to_network, expected_snap_to_network
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_, origins, snap_to_network=snap_to_network
        )
        assert travel_time_matrix_computer.snap_to_network == expected_snap_to_network

    @pytest.mark.parametrize(
        [
            "transport_network_",
            "origins",
            "snap_to_network",
            "expected_travel_times",
        ],
        [
            (
                pytest.lazy_fixture("transport_network"),
                pytest.lazy_fixture("population_grid_points"),
                True,
                pytest.lazy_fixture("walking_times_snapped"),
            ),
            (
                pytest.lazy_fixture("transport_network"),
                pytest.lazy_fixture("population_grid_points"),
                False,
                pytest.lazy_fixture("walking_times_not_snapped"),
            ),
        ],
    )
    def test_snap_to_network(
        self, transport_network_, origins, snap_to_network, expected_travel_times
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_, origins, snap_to_network=snap_to_network, transport_modes=[r5py.LegMode.WALK]
        )
        travel_times = travel_time_matrix_computer.compute_travel_times()

        print((travel_times["travel_time"] - expected_travel_times["travel_time"]).describe())
        assert travel_times.equals(expected_travel_times)
