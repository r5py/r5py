#!/usr/bin/env python3


"""Fixtures related to routing origins."""


import geopandas
import pytest

from .data_directory import DATA_DIRECTORY


ORIGINS_INVALID_NO_ID = DATA_DIRECTORY / "test_invalid_points_no_id_column.geojson"
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test_invalid_points_duplicate_ids.geojson"
)
ORIGINS_VALID_IDS = DATA_DIRECTORY / "test_valid_points_data.geojson"
SINGLE_VALID_ORIGIN = DATA_DIRECTORY / "test_valid_single_point_data.geojson"


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
