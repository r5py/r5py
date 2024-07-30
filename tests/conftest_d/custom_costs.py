#!/usr/bin/env python3


"""Fixtures related to routing with custom costs."""


import pandas
import pytest

from .data_directory import DATA_DIRECTORY
#from .transport_network import osm_pbf_file_path, gtfs_file_path


ORIGINS_INVALID_NO_ID = DATA_DIRECTORY / "test_invalid_points_no_id_column.geojson"


@pytest.fixture(scope="session")
def custom_costs_1():
    """Provide a custom cost data frame."""
    yield pandas.DataFrame({
        "osm_id": [1, 2],
        "custom_cost_1": [1.1, 1.2]
    })


@pytest.fixture(scope="session")
def custom_costs_2():
    """Provide a custom cost data frame."""
    yield pandas.DataFrame({
        "osm_id": [3, 4],
        "custom_cost_2": [1.3, 1.4]
    })


@pytest.fixture(scope="session")
def custom_costs_multiple(
    custom_costs_1,
    custom_costs_2,
):
    """Provide a custom cost data frame with multiple columns."""
    yield custom_costs_1.merge(custom_costs_2, how="outer")


@pytest.fixture(scope="session")
def custom_costs_transport_network(
    osm_pbf_file_path,
    gtfs_file_path,
    custom_costs_1,
):
    import r5py
    yield r5py.CustomCostTransportNetwork(
        osm_pbf_file_path,
        [gtfs_file_path],
        custom_costs_1,
    )
