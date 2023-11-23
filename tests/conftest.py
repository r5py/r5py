#!/usr/bin/env python3

# This is a init file common to all tests. It is automatically sourced
# by pytest et al.

# Define common constants (e.g., paths to test data) and fixtures (e.g.,
# transport network) here.


# explicitly importing fiona before geopandas fixes issue #156
import fiona  # noqa: F401

import datetime
import pathlib
import time

import jpype
import geopandas
import pandas
import pytest
import shapely


# test data
DATA_DIRECTORY = pathlib.Path(__file__).resolve().parent / "data"
ORIGINS_INVALID_NO_ID = DATA_DIRECTORY / "test_invalid_points_no_id_column.geojson"
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test_invalid_points_duplicate_ids.geojson"
)
ORIGINS_VALID_IDS = DATA_DIRECTORY / "test_valid_points_data.geojson"
SINGLE_VALID_ORIGIN = DATA_DIRECTORY / "test_valid_single_point_data.geojson"

R5_JAR_URL = (
    "https://github.com/r5py/r5/releases/download/v7.0-r5py/r5-v7.0-r5py-all.jar"
)
R5_JAR_SHA256 = "b061f933862a801f9440266591eb47e6f196c36295d6e7587d69f3e8e7ea1975"
R5_JAR_SHA256_INVALID = "adfadsfadsfadsfasdfasdf"
R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING = (
    "14aa2347be79c280e4d0fd3a137fb8f5bf2863261a1e48e1a122df1a52a0f453"
)

SNAPPED_POPULATION_GRID_POINTS = (
    DATA_DIRECTORY / "test_snapped_population_grid_centroids.geojson"
)

WALKING_TIMES_SNAPPED = DATA_DIRECTORY / "test_walking_times_snapped.csv"
WALKING_TIMES_NOT_SNAPPED = DATA_DIRECTORY / "test_walking_times_not_snapped.csv"
WALKING_DETAILS_SNAPPED = DATA_DIRECTORY / "test_walking_details_snapped.csv"
WALKING_DETAILS_NOT_SNAPPED = DATA_DIRECTORY / "test_walking_details_not_snapped.csv"

DETAILED_ITINERARIES_BICYCLE = (
    DATA_DIRECTORY / "test_detailed_itineraries_bicycle.gpkg.zip"
)
DETAILED_ITINERARIES_CAR = DATA_DIRECTORY / "test_detailed_itineraries_car.gpkg.zip"
DETAILED_ITINERARIES_TRANSIT = (
    DATA_DIRECTORY / "test_detailed_itineraries_transit.gpkg.zip"
)
DETAILED_ITINERARIES_WALK = DATA_DIRECTORY / "test_detailed_itineraries_walk.gpkg.zip"

SAMPLE_DATA_SET_URL = "https://raw.githubusercontent.com/r5py/r5py.sampledata.sao_paulo/main/data/spo_hexgrid.csv"
SAMPLE_DATA_SET_SHA256 = (
    "769660f8f1bc95d2741bbc4225e5e0e77e73461ea8b3e225a58e397b0748bdd4"
)


@pytest.fixture
def data_columns_with_breakdown():
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


@pytest.fixture(scope="session")
def departure_datetime():
    yield datetime.datetime(2022, 2, 22, 8, 30)


@pytest.fixture
def detailed_itineraries_bicycle():
    yield geopandas.read_file(DETAILED_ITINERARIES_BICYCLE)


@pytest.fixture
def detailed_itineraries_car():
    yield geopandas.read_file(DETAILED_ITINERARIES_CAR)


@pytest.fixture
def detailed_itineraries_transit():
    yield geopandas.read_file(DETAILED_ITINERARIES_TRANSIT)


@pytest.fixture
def detailed_itineraries_walk():
    yield geopandas.read_file(DETAILED_ITINERARIES_WALK)


@pytest.fixture
def gtfs_file():
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.gtfs


@pytest.fixture
def not_a_gtfs_file():
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf


@pytest.fixture
def gtfs_file_path():
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.gtfs


@pytest.fixture
def gtfs_timezone_helsinki():
    yield "Europe/Helsinki"


@pytest.fixture()
def origins_invalid_no_id():
    origins = geopandas.read_file(ORIGINS_INVALID_NO_ID)
    yield origins


@pytest.fixture()
def origins_invalid_duplicate_ids():
    origins = geopandas.read_file(ORIGINS_INVALID_DUPLICATE_IDS)
    yield origins


@pytest.fixture
def origin_point():
    yield geopandas.read_file(SINGLE_VALID_ORIGIN)


@pytest.fixture()
def origins_valid_ids():
    origins = geopandas.read_file(ORIGINS_VALID_IDS)
    yield origins


@pytest.fixture
def osm_pbf_file_path():
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf


@pytest.fixture(scope="session")
def population_grid():
    import r5py.sampledata.helsinki

    yield geopandas.read_file(r5py.sampledata.helsinki.population_grid)


@pytest.fixture(scope="session")
def population_grid_points(population_grid):
    population_grid_points = population_grid.copy()
    population_grid_points.geometry = population_grid_points.geometry.to_crs(
        "EPSG:3067"
    ).centroid.to_crs("EPSG:4326")
    yield population_grid_points


@pytest.fixture(scope="session")
def population_grid_points_first_three(population_grid_points):
    yield population_grid_points[0:3]


@pytest.fixture(scope="session")
def population_grid_points_second_three(population_grid_points):
    yield population_grid_points[4:7]


@pytest.fixture(scope="session")
def population_grid_points_four(population_grid_points):
    yield population_grid_points[10:14]


@pytest.fixture(scope="session")
def r5_jar_cached():
    from r5py.util.config import Config

    yield str(Config().CACHE_DIR / pathlib.Path(R5_JAR_URL).name)


@pytest.fixture
def r5_jar_cached_invalid():
    yield "/definitely/invalid/path/to/r5.jar"


@pytest.fixture
def r5_jar_sha256():
    yield R5_JAR_SHA256


@pytest.fixture
def r5_jar_sha256_invalid():
    yield R5_JAR_SHA256_INVALID


@pytest.fixture
def r5_jar_sha256_github_error_message_when_posting():
    yield R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING


@pytest.fixture()
def r5_jar_url():
    yield R5_JAR_URL


@pytest.fixture
def regional_task(
    population_grid_points,
    transport_network,
    departure_datetime,
):
    import r5py

    regional_task = r5py.RegionalTask(
        transport_network,
        population_grid_points.at[1, "geometry"],
        population_grid_points,
        departure=departure_datetime,
    )
    yield regional_task

    del regional_task
    time.sleep(0.5)
    jpype.java.lang.System.gc()


@pytest.fixture
def sample_data_set_sha256():
    yield SAMPLE_DATA_SET_SHA256


@pytest.fixture
def sample_data_set_url():
    yield SAMPLE_DATA_SET_URL


@pytest.fixture(scope="session")
def snapped_population_grid_points():
    yield geopandas.read_file(SNAPPED_POPULATION_GRID_POINTS)


@pytest.fixture
def transport_network_files_tuple():
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf, [r5py.sampledata.helsinki.gtfs]


@pytest.fixture
def transport_network(transport_network_from_test_files):
    yield transport_network_from_test_files


@pytest.fixture(scope="session")
def transport_network_from_test_directory():
    import r5py
    import r5py.sampledata.helsinki
    from .temporary_directory import TemporaryDirectory

    with TemporaryDirectory() as temp_directory:
        (temp_directory / r5py.sampledata.helsinki.osm_pbf.name).symlink_to(
            r5py.sampledata.helsinki.osm_pbf
        )
        (temp_directory / r5py.sampledata.helsinki.gtfs.name).symlink_to(
            r5py.sampledata.helsinki.gtfs
        )

        transport_network = r5py.TransportNetwork.from_directory(temp_directory)
        yield transport_network

        del transport_network

    time.sleep(0.5)
    jpype.java.lang.System.gc()


@pytest.fixture(scope="session")
def transport_network_from_test_files():
    import r5py
    import r5py.sampledata.helsinki

    transport_network = r5py.TransportNetwork(
        r5py.sampledata.helsinki.osm_pbf, [r5py.sampledata.helsinki.gtfs]
    )
    yield transport_network

    del transport_network

    time.sleep(0.5)
    jpype.java.lang.System.gc()


@pytest.fixture(scope="session")
def transport_network_from_test_files_without_gtfs():
    import r5py
    import r5py.sampledata.helsinki

    transport_network = r5py.TransportNetwork(r5py.sampledata.helsinki.osm_pbf, [])
    yield transport_network

    del transport_network

    time.sleep(0.5)
    jpype.java.lang.System.gc()


@pytest.fixture
def unreachable_stops():
    yield [
        1294132,
        1174101,
        1452601,
    ]


@pytest.fixture
def unsnappable_points():
    yield geopandas.GeoDataFrame(
        {
            "id": [1, 2],
            "geometry": [
                shapely.Point(48.20, 16.36),  # far away from Helsinki
                shapely.Point(-0.22, -78.51),  # even further
            ],
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def walking_details_snapped():
    yield pandas.read_csv(WALKING_DETAILS_SNAPPED)


@pytest.fixture
def walking_details_not_snapped():
    yield pandas.read_csv(WALKING_DETAILS_NOT_SNAPPED)


@pytest.fixture
def walking_times_snapped():
    yield pandas.read_csv(WALKING_TIMES_SNAPPED)


@pytest.fixture
def walking_times_not_snapped():
    yield pandas.read_csv(WALKING_TIMES_NOT_SNAPPED)
