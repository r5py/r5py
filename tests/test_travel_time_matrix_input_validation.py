#!/usr/bin/env python3

import pytest  # noqa: F401
import pathlib

import geopandas

import r5py
import r5py.util.exceptions


DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent / "docs" / "data"
OSM_PBF = DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf"

ORIGINS_INVALID_NO_ID = (
    DATA_DIRECTORY / "test data" / "test_invalid_points_no_id_column.geojson"
)
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test data" / "test_invalid_points_duplicate_ids.geojson"
)
ORIGINS_VALID_IDS = DATA_DIRECTORY / "test data" / "test_valid_points_data.geojson"


class TestTravelTimeMatrixInputValidation:
    @pytest.fixture(scope="session")
    def transport_network(self):
        transport_network = r5py.TransportNetwork(OSM_PBF)
        yield transport_network

    @pytest.fixture(scope="session")
    def origins_invalid_no_id(self):
        origins = geopandas.read_file(ORIGINS_INVALID_NO_ID)
        yield origins

    @pytest.fixture(scope="session")
    def origins_invalid_duplicate_ids(self):
        origins = geopandas.read_file(ORIGINS_INVALID_DUPLICATE_IDS)
        yield origins

    @pytest.fixture(scope="session")
    def origins_valid_ids(self):
        origins = geopandas.read_file(ORIGINS_VALID_IDS)
        yield origins

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
    def test_invalid_data(self, transport_network, origins, expected_error):
        # Just looking at a simple walking system.
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
        [
            (
                pytest.lazy_fixture("origins_valid_ids"),
            )
        ]
    )
    def test_valid_data(self, transport_network, origins):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            origins=origins,
        )
        del travel_time_matrix_computer
