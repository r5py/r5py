#!/usr/bin/env python3

"""Configuration and fixtures for testing r5py."""

# This is a init file common to all tests. It is automatically sourced
# by pytest et al.

# Define common constants (e.g., paths to test data) and fixtures (e.g.,
# transport network) here.


# explicitly importing fiona before geopandas fixes issue #156
import fiona  # noqa: F401

import datetime
import pathlib
import time
import warnings

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
DETAILED_ITINERARIES_CAR = DATA_DIRECTORY / "test_detailed_itineraries_car.gpkg.zip"
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
def detailed_itineraries_car():
    """Retrieve expected detailed itineraries for driving."""
    yield geopandas.read_file(DETAILED_ITINERARIES_CAR)


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
    # Since geopandas 1.0, it uses pyogrio in the background. pyogrio seems to
    # filter less of the underlying OGR warning messages than what fiona did.
    # Because of that, a warning message bubbles up that states non-unique IDs
    # were corrected (when they, factually, were not corrected)

    # for this fixture, we want to have non-unique values in the "id" column, so
    # let's ignore that warning

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
            message=(
                "Several features with id = 1 have been found. Altering it to be "
                "unique. This warning will not be emitted anymore for this layer"
            ),
        )
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
