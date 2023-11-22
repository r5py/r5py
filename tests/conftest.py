#!/usr/bin/env python3

# This is a init file common to all tests. It is automatically sourced
# by pytest et al.

# Define common constants (e.g., paths to test data) and fixtures (e.g.,
# transport network) here.


# explicitly importing fiona before geopandas fixes issue #156
import csv
import fiona  # noqa: F401

import datetime
import pathlib
import time

import jpype
import geopandas
import pandas
import pytest
from r5py.util.custom_cost_conversions import (
    convert_custom_cost_data_to_custom_cost_instance,
    convert_custom_cost_instances_to_java_list,
    convert_python_dict_to_java_hashmap,
)
import shapely


# test data
DATA_DIRECTORY = pathlib.Path(__file__).resolve().parent / "data"
ORIGINS_INVALID_NO_ID = DATA_DIRECTORY / "test_invalid_points_no_id_column.geojson"
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test_invalid_points_duplicate_ids.geojson"
)
ORIGINS_VALID_IDS = DATA_DIRECTORY / "test_valid_points_data.geojson"
SINGLE_VALID_ORIGIN = DATA_DIRECTORY / "test_valid_single_point_data.geojson"

R5_JAR_URL = "https://github.com/conveyal/r5/releases/download/v6.9/r5-v6.9-all.jar"
R5_JAR_SHA256 = "a7e1c5ff8786a9fb9191073b8f31a6933b862f44b9ff85b2c00a68c85491274d"
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


# custom cost routing tests related fixtures


@pytest.fixture(scope="session")
def custom_cost_test_values():
    yield {12345: 1.0, 67890: 1.5, 54321: 1.25, 98765: 1.1}


@pytest.fixture(scope="session")
def custom_cost_hashmap(custom_cost_test_values):
    yield convert_python_dict_to_java_hashmap(custom_cost_test_values)


@pytest.fixture(scope="session")
def custom_cost_instance(custom_cost_hashmap):
    yield convert_custom_cost_data_to_custom_cost_instance(
        "test_name", 1.3, custom_cost_hashmap
    )


@pytest.fixture(scope="session")
def custom_cost_list(custom_cost_instance):
    yield convert_custom_cost_instances_to_java_list(custom_cost_instance)


@pytest.fixture(scope="session")
def custom_cost_transport_network(custom_cost_transport_network_from_test_files):
    yield custom_cost_transport_network_from_test_files


@pytest.fixture(scope="session")
def custom_cost_transport_network_from_test_files(osmid_value_dict):
    import r5py

    custom_cost_transport_network = r5py.CustomCostTransportNetwork(
        r5py.sampledata.helsinki.osm_pbf, ["test_cost"], [1.1], [osmid_value_dict]
    )
    yield custom_cost_transport_network

    del custom_cost_transport_network

    time.sleep(0.5)
    jpype.java.lang.System.gc()


# csv reader helper function
def read_osmid_values(csv_file_path, value_generator):
    osmid_values = {}
    with open(csv_file_path, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            osmid, value = row
            osmid_values[osmid] = value_generator(value)
    return osmid_values


# use Helsinki osmid's so that the custom cost values (osmids) are found in the transport network
@pytest.fixture(scope="session")
def osmid_value_dict():
    yield read_osmid_values(
        "tests/data/test_osm_data_custom_cost_kantakaupunki.csv", lambda v: float(v)
    )


@pytest.fixture(scope="session")
def osmid_negative_value_dict():
    yield read_osmid_values(
        "tests/data/test_osm_data_negative_custom_cost_kantakaupunki.csv",
        lambda v: -abs(float(v)),
    )


# run the generator function with a lambda that returns 0.0 to all
@pytest.fixture(scope="session")
def osmid_zero_dict():
    yield read_osmid_values(
        "tests/data/test_osm_data_custom_cost_kantakaupunki.csv", lambda v: 0.0
    )


@pytest.fixture(scope="session")
def single_cost_custom_cost_transport_network(osmid_value_dict):
    import r5py

    # create a network with random values as custom costs
    custom_cost_transport_network = r5py.CustomCostTransportNetwork(
        r5py.sampledata.helsinki.osm_pbf, ["random_cost_1"], [1.2], [osmid_value_dict]
    )
    yield custom_cost_transport_network


@pytest.fixture(scope="session")
def single_cost_negative_custom_cost_transport_network(osmid_negative_value_dict):
    import r5py

    # create a network with random values as custom costs
    custom_cost_transport_network = r5py.CustomCostTransportNetwork(
        r5py.sampledata.helsinki.osm_pbf,
        ["random_cost_1"],
        [1.2],
        [osmid_negative_value_dict],
    )
    yield custom_cost_transport_network


@pytest.fixture(scope="session")
def multi_cost_custom_cost_transport_network(osmid_value_dict):
    import r5py

    # create a network with random values as custom costs
    custom_cost_transport_network = r5py.CustomCostTransportNetwork(
        r5py.sampledata.helsinki.osm_pbf,
        ["random_cost_1", "random_cost_2"],
        [1.1, 1.2],
        [osmid_value_dict, osmid_value_dict],
    )
    yield custom_cost_transport_network


@pytest.fixture(scope="session")
def custom_cost_transport_network_zero_values(osmid_zero_dict):
    import r5py

    # create a network with random values as custom costs
    zero_custom_cost_transport_network = r5py.CustomCostTransportNetwork(
        r5py.sampledata.helsinki.osm_pbf, ["test_name"], [1.3], [osmid_zero_dict]
    )
    yield zero_custom_cost_transport_network


@pytest.fixture(scope="session")
def origin_point_custom_cost():
    yield geopandas.GeoDataFrame(
        {"id": [1], "geometry": [shapely.Point(24.94222, 60.17166)]},
        crs="EPSG:4326",
    )


@pytest.fixture(scope="session")
def multiple_origin_points():
    yield geopandas.GeoDataFrame(
        {
            "id": [1, 2, 3, 4],
            "geometry": [
                shapely.Point(24.95252, 60.17316),
                shapely.Point(24.94742, 60.17466),
                shapely.Point(24.94722, 60.17766),
                shapely.Point(24.94922, 60.17966),
            ],
        },
        crs="EPSG:4326",
    )


@pytest.fixture(scope="session")
def multiple_destination_points():
    yield geopandas.GeoDataFrame(
        {
            "id": [1, 2, 3],
            "geometry": [
                shapely.Point(24.95222, 60.18166),
                shapely.Point(24.94022, 60.17106),
                shapely.Point(24.94258, 60.17400),
            ],
        },
        crs="EPSG:4326",
    )


# fixture factory for shifting between different OD-pairs
# used to test one-to-many and many-to-many routing
@pytest.fixture
def origin_point_factory(request, origin_point_custom_cost, multiple_origin_points):
    if request.param == "single_point":
        yield origin_point_custom_cost
    elif request.param == "multiple_points":
        yield multiple_origin_points


# fixture factory for shifting between different OD-pairs
# used to test one-to-many and many-to-many routing
@pytest.fixture
def custom_cost_transport_network_selector(
    request,
    single_cost_custom_cost_transport_network,
    single_cost_negative_custom_cost_transport_network,
    multi_cost_custom_cost_transport_network,
):
    if request.param == "single_cost":
        yield single_cost_custom_cost_transport_network
    elif request.param == "negative_cost":
        yield single_cost_negative_custom_cost_transport_network
    elif request.param == "multiple_cost":
        yield multi_cost_custom_cost_transport_network
