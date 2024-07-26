#!/usr/bin/env python3


"""Fixtures describing the expected routing results."""


import geopandas
import pandas
import pytest

from .data_directory import DATA_DIRECTORY


DETAILED_ITINERARIES_BICYCLE = (
    DATA_DIRECTORY / "test_detailed_itineraries_bicycle.gpkg.zip"
)
DETAILED_ITINERARIES_CAR = DATA_DIRECTORY / "test_detailed_itineraries_car.gpkg.zip"
DETAILED_ITINERARIES_TRANSIT = (
    DATA_DIRECTORY / "test_detailed_itineraries_transit.gpkg.zip"
)
DETAILED_ITINERARIES_WALK = DATA_DIRECTORY / "test_detailed_itineraries_walk.gpkg.zip"
WALKING_DETAILS_NOT_SNAPPED = DATA_DIRECTORY / "test_walking_details_not_snapped.csv"
WALKING_DETAILS_SNAPPED = DATA_DIRECTORY / "test_walking_details_snapped.csv"
WALKING_TIMES_NOT_SNAPPED = DATA_DIRECTORY / "test_walking_times_not_snapped.csv"
WALKING_TIMES_SNAPPED = DATA_DIRECTORY / "test_walking_times_snapped.csv"


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
def walking_details_not_snapped():
    """Load expected walking details if snapping is enabled."""
    yield pandas.read_csv(WALKING_DETAILS_NOT_SNAPPED)


@pytest.fixture
def walking_details_snapped():
    """Load expected walking details if snapping is enabled."""
    yield pandas.read_csv(WALKING_DETAILS_SNAPPED)


@pytest.fixture
def walking_times_not_snapped():
    """Load expected walking times if snapping is disabled."""
    yield pandas.read_csv(WALKING_TIMES_NOT_SNAPPED)


@pytest.fixture
def walking_times_snapped():
    """Load expected walking times if snapping is enabled."""
    yield pandas.read_csv(WALKING_TIMES_SNAPPED)
