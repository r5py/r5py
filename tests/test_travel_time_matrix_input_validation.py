#!/usr/bin/env python3

import pytest  # noqa: F401
import pathlib

import geopandas

import r5py
import r5py.util.exceptions


DATA_DIRECTORY = pathlib.Path(__file__).absolute().parent.parent / "docs" / "data"
OSM_PBF = DATA_DIRECTORY / "Helsinki" / "kantakaupunki.osm.pbf"

ORIGINS_INVALID_NO_ID = (
    DATA_DIRECTORY / "test data" / "test_invalid_points_no_id_column.geojson"
)
ORIGINS_INVALID_DUPLICATE_IDS = (
    DATA_DIRECTORY / "test data" / "test_invalid_points_duplicate_ids.geojson"
)


class TestTravelTimeMatrixInputValidation:
    @pytest.mark.parametrize(
        ["geojson_file", "expected_error"],
        [
            (
                ORIGINS_INVALID_NO_ID,
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                ORIGINS_INVALID_DUPLICATE_IDS,
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_non_valid_data(self, geojson_file, expected_error):
        # Just looking at a simple walking system.
        transport_network = r5py.TransportNetwork(OSM_PBF)
        origins = geopandas.read_file(geojson_file)

        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origins,
            )
            del travel_time_matrix_computer
