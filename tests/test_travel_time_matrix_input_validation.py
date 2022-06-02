#!/usr/bin/env python3

import os

import geopandas

import pytest  # noqa: F401

import r5py
import r5py.util.exceptions

import com.conveyal.r5

PBF_FILE = os.path.join("tests", "data", "kantakaupunki.osm.pbf")


class TestTravelTimeMatrixInputValidation:
    @pytest.mark.parametrize(
        ["geojson_file", "expected_error"],
        [
            (
                "test_invalid_points_no_id_column.geojson",
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                "test_invalid_points_duplicate_ids.geojson",
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_non_valid_data(self, geojson_file, expected_error):
        # Just looking at a simple walking system.
        transport_network = r5py.TransportNetwork(PBF_FILE)
        origins = geopandas.read_file(os.path.join("tests", "data", geojson_file))

        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network,
                origins=origins,
            )
