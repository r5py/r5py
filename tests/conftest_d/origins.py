#!/usr/bin/env python3


"""Fixtures related to routing origins."""


import warnings

import geopandas
import pytest

from .data_directory import DATA_DIRECTORY


ORIGINS_INVALID_NO_ID = DATA_DIRECTORY / "test_invalid_points_no_id_column.geojson"
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test_invalid_points_duplicate_ids.geojson"
)
ORIGINS_VALID_IDS = DATA_DIRECTORY / "test_valid_points_data.geojson"
SINGLE_VALID_ORIGIN = DATA_DIRECTORY / "test_valid_single_point_data.geojson"
MULTIPLE_ORIGINS = DATA_DIRECTORY / "test_multiple_origins.geojson"


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


@pytest.fixture()
def multiple_origins():
    """Return a set of multiple origins."""
    origins = geopandas.read_file(MULTIPLE_ORIGINS)
    yield origins
