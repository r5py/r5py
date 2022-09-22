#!/usr/bin/env python3

# This is a init file common to all tests. It is automatically sourced
# by pytest et al.

# Define common constants (e.g., paths to test_data) and fixtures (e.g.,
# transport network) here.


import pathlib

# explicitly importing fiona before geopandas fixes issue #156
import fiona  # noqa: F401
import geopandas
import pytest  # noqa: F401

import r5py

# test_data
DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent / "docs" / "data"
OSM_PBF = DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf"
GTFS = DATA_DIRECTORY / "Helsinki" / "GTFS.zip"
POP_POINTS = DATA_DIRECTORY / "Helsinki" / "population_points_2020.gpkg"

ORIGINS_INVALID_NO_ID = (
    DATA_DIRECTORY / "test_data" / "test_invalid_points_no_id_column.geojson"
)
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test_data" / "test_invalid_points_duplicate_ids.geojson"
)
ORIGINS_VALID_IDS = DATA_DIRECTORY / "test_data" / "test_valid_points_data.geojson"
SINGLE_VALID_ORIGIN = (
    DATA_DIRECTORY / "test_data" / "test_valid_single_point_data.geojson"
)

R5_JAR_URL = "https://github.com/conveyal/r5/releases/download/v6.6/r5-v6.6-all.jar"
R5_JAR_SHA256 = "9e4ceb85a09e750f146f95d98013eb164afac2dfc900a9e68e37ae925b1ec702"
R5_JAR_SHA256_INVALID = "adfadsfadsfadsfasdfasdf"


@pytest.fixture
def data_columns_with_breakdown(scope="session"):
    yield [
        "from_id",
        "to_id",
        "travel_time",
        "routes",
        "board_stops",
        "alight_stops",
        "ride_times",
        "access_time",
        "egress_time",
        "transfer_time",
        "wait_times",
        "total_time",
        "n_iterations",
    ]


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


@pytest.fixture
def origin_point(scope="session"):
    yield geopandas.read_file(SINGLE_VALID_ORIGIN)


@pytest.fixture(scope="session")
def origins_valid_ids():
    origins = geopandas.read_file(ORIGINS_VALID_IDS)
    yield origins


@pytest.fixture(scope="session")
def population_points():
    yield geopandas.read_file(POP_POINTS)


@pytest.fixture(scope="session")
def r5_jar_sha256():
    yield R5_JAR_SHA256


@pytest.fixture(scope="session")
def r5_jar_sha256_invalid():
    yield R5_JAR_SHA256_INVALID


@pytest.fixture(scope="session")
def r5_jar_url():
    yield R5_JAR_URL


@pytest.fixture
def transport_network_files_tuple(scope="session"):
    yield OSM_PBF, [GTFS]


@pytest.fixture(scope="session")
def transport_network_from_test_directory():
    yield r5py.TransportNetwork.from_directory(DATA_DIRECTORY / "Helsinki")


@pytest.fixture(scope="session")
def transport_network_from_test_files():
    transport_network = r5py.TransportNetwork(OSM_PBF, [GTFS])
    yield transport_network
