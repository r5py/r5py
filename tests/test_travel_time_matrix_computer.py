#!/usr/bin/env python3

import os
import geopandas
import pandas
import datetime
import pytest  # noqa: F401

import r5py
import r5py.util.exceptions


class TestTravelTimeMatrixComputer:
    @pytest.fixture(scope="session")
    def transport_network(self):
        transport_network = r5py.TransportNetwork(OSM_PBF, [GTFS])
        yield transport_network

    @pytest.fixture
    def population_points(self):
        yield geopandas.read_file(POP_POINTS)

    @pytest.fixture
    def origin_point(self):
        data = {"geometry": Point(24.939858, 60.165964),
                "id": 0,
                "name": "Vanha Kirkkopuisto, Helsinki"}
        yield geopandas.GeoDataFrame(data, index=[0], crs="epsg:4326")

    def test_travel_time_matrix_initialization(self, transport_network, population_points, origin_point):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],
        )
        assert isinstance(travel_time_matrix_computer.transport_network, r5py.TransportNetwork)
        assert isinstance(travel_time_matrix_computer.origins, geopandas.GeoDataFrame)
        assert isinstance(travel_time_matrix_computer.destinations, geopandas.GeoDataFrame)

        assert travel_time_matrix_computer.origins.shape == origin_point.shape
        assert travel_time_matrix_computer.destinations.shape == population_points.shape
        assert travel_time_matrix_computer.breakdown is False
        assert travel_time_matrix_computer.breakdown_stat == r5py.BreakdownStat.MEAN

    def test_all_to_all(self, transport_network, population_points):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=population_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],

        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()

        assert isinstance(travel_time_matrix, pandas.DataFrame)
        # TODO: Add more tests

    def test_one_to_all(self, transport_network, population_points, origin_point):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origin_point,
            destinations=population_points,
            departure=datetime.datetime(2022, 2, 22, 8, 30),
            transport_modes=[r5py.TransitMode.TRANSIT, r5py.LegMode.WALK],

        )
        travel_time_matrix = travel_time_matrix_computer.compute_travel_times()

        assert isinstance(travel_time_matrix, pandas.DataFrame)
        # TODO: Add more tests


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
    def test_origins_invalid_data(self, transport_network_from_test_files, origins, expected_error):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network_from_test_files,
                origins=origins,
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
        ],
        [(pytest.lazy_fixture("origins_valid_ids"),)],
    )
    def test_origins_valid_data(self, transport_network_from_test_files, origins):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_from_test_files,
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
        self, transport_network_from_test_files, origins, destinations, expected_error
    ):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network_from_test_files,
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
        self, transport_network_from_test_files, origins, destinations
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_from_test_files,
            origins=origins,
            destinations=destinations,
        )
        del travel_time_matrix_computer
