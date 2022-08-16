#!/usr/bin/env python3


import pytest  # noqa: F401

import geopandas
import pathlib

import r5py


# test data sets
DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent / "docs" / "data"
OSM_PBF = DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf"
GTFS = DATA_DIRECTORY / "Helsinki" / "GTFS.zip"
POPULATION_GRID_POINTS = DATA_DIRECTORY / "Helsinki" / "population_points_2020.gpkg"


class TestRegionalTask:
    @pytest.fixture(scope="session")
    def blank_regional_task(self):
        transport_network = r5py.TransportNetwork(OSM_PBF, [GTFS])
        grid_points = geopandas.read_file(POPULATION_GRID_POINTS)
        regional_task = r5py.RegionalTask(
            transport_network,
            grid_points.at[1, "geometry"],
            grid_points,
        )
        yield regional_task

    @pytest.mark.parametrize(
        ["regional_task", "percentiles"],
        [
            (pytest.lazy_fixture("blank_regional_task"), []),
            (pytest.lazy_fixture("blank_regional_task"), [50]),
            (pytest.lazy_fixture("blank_regional_task"), [33, 66]),
            (pytest.lazy_fixture("blank_regional_task"), [25, 50, 75]),
            (pytest.lazy_fixture("blank_regional_task"), [20, 40, 60, 80]),
            (pytest.lazy_fixture("blank_regional_task"), [16, 33, 50, 66, 83]),
        ],
    )
    def test_allowed_number_of_percentiles(self, regional_task, percentiles):
        regional_task.percentiles = percentiles

    @pytest.mark.parametrize(
        ["regional_task", "percentiles"],
        [
            (
                pytest.lazy_fixture("blank_regional_task"),
                [10, 20, 30, 40, 50, 60, 70, 90],
            ),
            (
                pytest.lazy_fixture("blank_regional_task"),
                [i for i in range(101)],
            ),
        ],
    )
    def test_out_of_range_percentiles(self, regional_task, percentiles):
        with pytest.raises(
            ValueError, match="Maximum number of percentiles allowed is 5"
        ):
            regional_task.percentiles = percentiles

    # TODO: all other methods and attributes!
