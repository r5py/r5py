#!/usr/bin/env python3

"""Configuration and fixtures for testing r5py."""

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
    convert_custom_cost_segment_weight_factors_to_custom_cost_instance,
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

R5_JAR_URL = (
    "https://github.com/r5py/r5/releases/download/v7.1-r5py/r5-v7.1-r5py-all.jar"
)
R5_JAR_SHA256 = "cd697b50323fd99977c98039ea317698bcf5fbbdb12b59e3e094ae9443648db2"
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
# vanilla r5 uses mph for car speeds and has turn costs
# DGL r5 and r5_gp2 (Green Paths 2) use km/h and no turn costs
DETAILED_ITINERARIES_CAR_MPH = (
    DATA_DIRECTORY / "test_detailed_itineraries_car_mph.gpkg.zip"
)
DETAILED_ITINERARIES_CAR_KMH = (
    DATA_DIRECTORY / "test_detailed_itineraries_car_kmh.gpkg.zip"
)
DETAILED_ITINERARIES_TRANSIT = (
    DATA_DIRECTORY / "test_detailed_itineraries_transit.gpkg.zip"
)
DETAILED_ITINERARIES_WALK = DATA_DIRECTORY / "test_detailed_itineraries_walk.gpkg.zip"

SAMPLE_DATA_SET_URL = "https://raw.githubusercontent.com/r5py/r5py.sampledata.sao_paulo/main/data/spo_hexgrid.csv"
SAMPLE_DATA_SET_SHA256 = (
    "769660f8f1bc95d2741bbc4225e5e0e77e73461ea8b3e225a58e397b0748bdd4"
)


@pytest.fixture(scope="session")
def departure_datetime():
    """Return the departure time to run tests for."""
    yield datetime.datetime(2022, 2, 22, 8, 30)


@pytest.fixture
def detailed_itineraries_bicycle():
    """Retrieve expected detailed itineraries for cycling."""
    yield geopandas.read_file(DETAILED_ITINERARIES_BICYCLE)


@pytest.fixture
def detailed_itineraries_car_mph():
    yield geopandas.read_file(DETAILED_ITINERARIES_CAR_MPH)


@pytest.fixture
def detailed_itineraries_car_kmh():
    yield geopandas.read_file(DETAILED_ITINERARIES_CAR_KMH)


@pytest.fixture
def detailed_itineraries_transit():
    """Retrieve expected detailed itineraries for public transport."""
    yield geopandas.read_file(DETAILED_ITINERARIES_TRANSIT)


@pytest.fixture
def detailed_itineraries_walk():
    """Retrieve expected detailed itineraries for walking."""
    yield geopandas.read_file(DETAILED_ITINERARIES_WALK)


@pytest.fixture
def not_a_gtfs_file():
    """Return a file path of something that is not a GTFS file."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf


@pytest.fixture
def gtfs_file_path():
    """Return the file path of a GTFS sample data set."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.gtfs


@pytest.fixture
def gtfs_timezone_helsinki():
    """Return the timezone for Helsinki."""
    yield "Europe/Helsinki"


@pytest.fixture()
def origins_invalid_no_id():
    """Return a set of origins that has missing ID values."""
    origins = geopandas.read_file(ORIGINS_INVALID_NO_ID)
    yield origins


@pytest.fixture()
def origins_invalid_duplicate_ids():
    """Return a set of origins that has duplicate ID values."""
    origins = geopandas.read_file(ORIGINS_INVALID_DUPLICATE_IDS)
    yield origins


@pytest.fixture
def origin_point():
    """Return one origin point."""
    yield geopandas.read_file(SINGLE_VALID_ORIGIN)


@pytest.fixture()
def origins_valid_ids():
    """Return a set of origins that has valid ID values."""
    origins = geopandas.read_file(ORIGINS_VALID_IDS)
    yield origins


@pytest.fixture
def osm_pbf_file_path():
    """Return the path of the OSM sample data set."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf


@pytest.fixture(scope="session")
def population_grid():
    """Load the grid point data set."""
    import r5py.sampledata.helsinki

    yield geopandas.read_file(r5py.sampledata.helsinki.population_grid)


@pytest.fixture(scope="session")
def population_grid_points(population_grid):
    """Return the grid point data set in EPSG:4326."""
    population_grid_points = population_grid.copy()
    population_grid_points.geometry = population_grid_points.geometry.to_crs(
        "EPSG:3067"
    ).centroid.to_crs("EPSG:4326")
    yield population_grid_points


@pytest.fixture(scope="session")
def population_grid_points_first_three(population_grid_points):
    """Return the first set of three grid points."""
    yield population_grid_points[0:3]


@pytest.fixture(scope="session")
def population_grid_points_second_three(population_grid_points):
    """Return the second set of three grid points."""
    yield population_grid_points[4:7]


@pytest.fixture(scope="session")
def population_grid_points_four(population_grid_points):
    """Return four grid points."""
    yield population_grid_points[10:14]


@pytest.fixture(scope="session")
def r5_jar_cached():
    """Return a cache path for the R5 jar."""
    from r5py.util.config import Config

    yield str(Config().CACHE_DIR / pathlib.Path(R5_JAR_URL).name)


@pytest.fixture
def r5_jar_cached_invalid():
    """Return an invalid cache path for the R5 jar."""
    yield "/definitely/invalid/path/to/r5.jar"


@pytest.fixture
def r5_jar_sha256():
    """Return the SHA256 hash for the R5 jar."""
    yield R5_JAR_SHA256


@pytest.fixture
def r5_jar_sha256_invalid():
    """Return an invalid SHA256 hash for the R5 jar."""
    yield R5_JAR_SHA256_INVALID


@pytest.fixture
def r5_jar_sha256_github_error_message_when_posting():
    """Return the SHA256 hash of the GitHub error message when accidently POSTing."""
    yield R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING


@pytest.fixture()
def r5_jar_url():
    """Return the URL of the R5 jar."""
    yield R5_JAR_URL


@pytest.fixture
def regional_task(
    population_grid_points,
    transport_network,
    departure_datetime,
):
    """Return an initialised `r5py.RegionalTask`."""
    import r5py

    regional_task = r5py.RegionalTask(
        transport_network,
        population_grid_points.at[1, "geometry"],
        population_grid_points,
        departure=departure_datetime,
    )
    yield regional_task

    # clean up once this fixture has been used
    del regional_task
    time.sleep(0.5)
    jpype.java.lang.System.gc()


@pytest.fixture
def sample_data_set_sha256():
    """Return the SHA256 hash of the sample data at `sample_data_set_url()`."""
    yield SAMPLE_DATA_SET_SHA256


@pytest.fixture
def sample_data_set_url():
    """Return the web address from which a sample data set can be downloaded."""
    yield SAMPLE_DATA_SET_URL


@pytest.fixture(scope="session")
def snapped_population_grid_points():
    """Return a `geopandas.GeoDataFrame` that contains grid points snapped to the street network."""
    yield geopandas.read_file(SNAPPED_POPULATION_GRID_POINTS)


@pytest.fixture
def transport_network_files_tuple():
    """Return a tuple of transport network input test data file paths."""
    import r5py.sampledata.helsinki

    yield r5py.sampledata.helsinki.osm_pbf, [r5py.sampledata.helsinki.gtfs]


@pytest.fixture
def transport_network(transport_network_from_test_files):
    """Return an `r5py.TransportNetwork`."""
    yield transport_network_from_test_files


@pytest.fixture(scope="session")
def transport_network_from_test_directory():
    """Return an `r5py.TransportNetwork` initiated from a directory path."""
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
    """Return an `r5py.TransportNetwork` initiated from test file paths."""
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
    """Return an `r5py.TransportNetwork` initiated without GTFS data."""
    import r5py
    import r5py.sampledata.helsinki

    transport_network = r5py.TransportNetwork(r5py.sampledata.helsinki.osm_pbf, [])
    yield transport_network

    del transport_network

    time.sleep(0.5)
    jpype.java.lang.System.gc()


@pytest.fixture
def unreachable_stops():
    """Return a list of public transport stops that cannot be reached."""
    yield [
        1294132,
        1174101,
        1452601,
    ]


@pytest.fixture
def unsnappable_points():
    """Retrieve a set of points that cannot be snapped to the sample data network."""
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
    """Load expected walking details if snapping is enabled."""
    yield pandas.read_csv(WALKING_DETAILS_SNAPPED)


@pytest.fixture
def walking_details_not_snapped():
    """Load expected walking details if snapping is enabled."""
    yield pandas.read_csv(WALKING_DETAILS_NOT_SNAPPED)


@pytest.fixture
def walking_times_snapped():
    """Load expected walking times if snapping is enabled."""
    yield pandas.read_csv(WALKING_TIMES_SNAPPED)


@pytest.fixture
def walking_times_not_snapped():
    """Load expected walking times if snapping is disabled."""
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
    yield convert_custom_cost_segment_weight_factors_to_custom_cost_instance(
        "test_name", 1.3, custom_cost_hashmap, True
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
        [True, True],
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
