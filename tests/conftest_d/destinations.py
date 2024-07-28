#!/usr/bin/env python3


"""Fixtures related to the destinations used in routing."""


import geopandas
import pytest
import shapely

from .data_directory import DATA_DIRECTORY


SNAPPED_POPULATION_GRID_POINTS = (
    DATA_DIRECTORY / "test_snapped_population_grid_centroids.geojson"
)


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
def snapped_population_grid_points():
    """Return a `geopandas.GeoDataFrame` that contains grid points snapped to the street network."""
    yield geopandas.read_file(SNAPPED_POPULATION_GRID_POINTS)


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
