#!/usr/bin/env python3

# This is a init file common to all tests. It is automatically sourced
# by pytest et al.

# Define common constants (e.g., paths to test_data) and fixtures (e.g.,
# transport network) here.


# explicitly importing fiona before geopandas fixes issue #156
import fiona  # noqa: F401

import datetime
import geopandas
import pandas
import pathlib
import pytest
import shapely


DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent / "docs" / "data"


OSM_PBF = DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf"
GTFS = DATA_DIRECTORY / "Helsinki" / "GTFS.zip"
POPULATION_GRID = DATA_DIRECTORY / "Helsinki" / "population_grid_2020.gpkg"


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


R5_JAR_URL = "https://github.com/conveyal/r5/releases/download/v6.9/r5-v6.9-all.jar"
R5_JAR_SHA256 = "a7e1c5ff8786a9fb9191073b8f31a6933b862f44b9ff85b2c00a68c85491274d"
R5_JAR_SHA256_INVALID = "adfadsfadsfadsfasdfasdf"
R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING = (
    "14aa2347be79c280e4d0fd3a137fb8f5bf2863261a1e48e1a122df1a52a0f453"
)


SNAPPED_POPULATION_GRID_POINTS = (
    DATA_DIRECTORY / "test_data" / "test_snapped_population_grid_centroids.geojson"
)
WALKING_TIMES_SNAPPED = DATA_DIRECTORY / "test_data" / "test_walking_times_snapped.csv"
WALKING_TIMES_NOT_SNAPPED = (
    DATA_DIRECTORY / "test_data" / "test_walking_times_not_snapped.csv"
)
WALKING_DETAILS_SNAPPED = (
    DATA_DIRECTORY / "test_data" / "test_walking_details_snapped.csv"
)
WALKING_DETAILS_NOT_SNAPPED = (
    DATA_DIRECTORY / "test_data" / "test_walking_details_not_snapped.csv"
)

DETAILED_ITINERARIES_BICYCLE = (
    DATA_DIRECTORY / "test_data" / "test_detailed_itineraries_bicycle.gpkg.zip"
)
DETAILED_ITINERARIES_CAR = (
    DATA_DIRECTORY / "test_data" / "test_detailed_itineraries_car.gpkg.zip"
)
DETAILED_ITINERARIES_TRANSIT = (
    DATA_DIRECTORY / "test_data" / "test_detailed_itineraries_transit.gpkg.zip"
)
DETAILED_ITINERARIES_WALK = (
    DATA_DIRECTORY / "test_data" / "test_detailed_itineraries_walk.gpkg.zip"
)


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
def departure_datetime():
    yield datetime.datetime(2022, 2, 22, 8, 30)


@pytest.fixture(scope="session")
def detailed_itineraries_bicycle():
    yield geopandas.read_file(DETAILED_ITINERARIES_BICYCLE)


@pytest.fixture(scope="session")
def detailed_itineraries_car():
    yield geopandas.read_file(DETAILED_ITINERARIES_CAR)


@pytest.fixture(scope="session")
def detailed_itineraries_transit():
    yield geopandas.read_file(DETAILED_ITINERARIES_TRANSIT)


@pytest.fixture(scope="session")
def detailed_itineraries_walk():
    yield geopandas.read_file(DETAILED_ITINERARIES_WALK)


@pytest.fixture
def gtfs_file():
    yield GTFS


@pytest.fixture
def not_a_gtfs_file():
    yield OSM_PBF


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
def population_grid():
    yield geopandas.read_file(POPULATION_GRID)


@pytest.fixture(scope="session")
def population_grid_points(population_grid):
    population_grid_points = population_grid.copy()
    population_grid_points.geometry = population_grid_points.geometry.to_crs(
        "EPSG:3067"
    ).centroid.to_crs("EPSG:4326")
    yield population_grid_points


@pytest.fixture()
def population_grid_points_first_three(population_grid_points):
    yield population_grid_points[0:3]


@pytest.fixture()
def population_grid_points_second_three(population_grid_points):
    yield population_grid_points[4:7]


@pytest.fixture()
def population_grid_points_four(population_grid_points):
    yield population_grid_points[10:14]


@pytest.fixture(scope="session")
def r5_jar_cached():
    from r5py.util.config import Config

    yield str(Config().CACHE_DIR / pathlib.Path(R5_JAR_URL).name)


@pytest.fixture(scope="session")
def r5_jar_cached_invalid():
    yield "/definitely/invalid/path/to/r5.jar"


@pytest.fixture(scope="session")
def r5_jar_sha256():
    yield R5_JAR_SHA256


@pytest.fixture(scope="session")
def r5_jar_sha256_invalid():
    yield R5_JAR_SHA256_INVALID


@pytest.fixture(scope="session")
def r5_jar_sha256_github_error_message_when_posting():
    yield R5_JAR_SHA256_GITHUB_ERROR_MESSAGE_WHEN_POSTING


@pytest.fixture(scope="session")
def r5_jar_url():
    yield R5_JAR_URL


@pytest.fixture
def regional_task(population_grid_points, departure_datetime):
    import r5py

    transport_network = r5py.TransportNetwork(OSM_PBF, [GTFS])
    regional_task = r5py.RegionalTask(
        transport_network,
        population_grid_points.at[1, "geometry"],
        population_grid_points,
        departure=departure_datetime,
    )
    yield regional_task


@pytest.fixture(scope="session")
def snapped_population_grid_points():
    yield geopandas.read_file(SNAPPED_POPULATION_GRID_POINTS)


@pytest.fixture
def transport_network_files_tuple(scope="session"):
    yield OSM_PBF, [GTFS]


@pytest.fixture(scope="session")
def transport_network(transport_network_from_test_files):
    yield transport_network_from_test_files


@pytest.fixture(scope="session")
def transport_network_from_test_directory():
    import r5py

    yield r5py.TransportNetwork.from_directory(DATA_DIRECTORY / "Helsinki")


@pytest.fixture(scope="session")
def transport_network_from_test_files():
    import r5py

    transport_network = r5py.TransportNetwork(OSM_PBF, [GTFS])
    yield transport_network


@pytest.fixture(scope="session")
def transport_network_from_test_files_without_gtfs():
    import r5py

    transport_network = r5py.TransportNetwork(OSM_PBF, [])
    yield transport_network


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def walking_details_snapped():
    yield pandas.read_csv(WALKING_DETAILS_SNAPPED)


@pytest.fixture(scope="session")
def walking_details_not_snapped():
    yield pandas.read_csv(WALKING_DETAILS_NOT_SNAPPED)


@pytest.fixture(scope="session")
def walking_times_snapped():
    yield pandas.read_csv(WALKING_TIMES_SNAPPED)


@pytest.fixture(scope="session")
def walking_times_not_snapped():
    yield pandas.read_csv(WALKING_TIMES_NOT_SNAPPED)
