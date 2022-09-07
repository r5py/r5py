#!/usr/bin/env python3

# This is a init file common to all tests. It is automatically sourced
# by pytest et al.

# Define common constants (e.g., paths to test data) and fixtures (e.g.,
# transport network) here.


import pathlib

import geopandas
import pytest  # noqa: F401

import r5py

# test data
DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent / "docs" / "data"
OSM_PBF = DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf"
GTFS = DATA_DIRECTORY / "Helsinki" / "GTFS.zip"

ORIGINS_INVALID_NO_ID = (
    DATA_DIRECTORY / "test data" / "test_invalid_points_no_id_column.geojson"
)
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test data" / "test_invalid_points_duplicate_ids.geojson"
)
ORIGINS_VALID_IDS = DATA_DIRECTORY / "test data" / "test_valid_points_data.geojson"


@pytest.fixture
def gtfs_timezone_helsinki():
    yield "Europe/Helsinki"


@pytest.fixture(scope="session")
def origins_invalid_no_id():
    origins = geopandas.read_file(ORIGINS_INVALID_NO_ID)
    yield origins


@pytest.fixture(scope="session")
def origins_invalid_duplicate_ids():
    origins = geopandas.read_file(ORIGINS_INVALID_DUPLICATE_IDS)
    yield origins


@pytest.fixture(scope="session")
def origins_valid_ids():
    origins = geopandas.read_file(ORIGINS_VALID_IDS)
    yield origins


@pytest.fixture(scope="session")
def transport_network_from_test_files():
    transport_network = r5py.TransportNetwork(OSM_PBF, [GTFS])
    yield transport_network


@pytest.fixture(scope="session")
def transport_network_from_test_directory():
    yield r5py.TransportNetwork.from_directory(DATA_DIRECTORY / "Helsinki")
