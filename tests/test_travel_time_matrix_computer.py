#!/usr/bin/env python3

import pytest  # noqa: F401

import r5py
import r5py.util.exceptions


class TestTravelTimeMatrixInputValidation:
    @pytest.mark.parametrize(
        [
            "origins",
            "expected_error",
        ],
        [
            (
                pytest.lazy_fixture("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_invalid_data(self, transport_network_from_test_files, origins, expected_error):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network_from_test_files,
                origins=origins,
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
        ],
        [(pytest.lazy_fixture("origins_valid_ids"),)],
    )
    def test_origins_valid_data(self, transport_network_from_test_files, origins):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_from_test_files,
            origins=origins,
        )
        del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
            "expected_error",
        ],
        [
            (
                pytest.lazy_fixture("origins_invalid_no_id"),
                pytest.lazy_fixture("origins_invalid_no_id"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_no_id"),
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                r5py.util.exceptions.NoIDColumnError,
            ),
            (
                pytest.lazy_fixture("origins_invalid_duplicate_ids"),
                pytest.lazy_fixture("origins_invalid_no_id"),
                r5py.util.exceptions.NonUniqueIDError,
            ),
        ],
    )
    def test_origins_and_destinations_invalid_data(
        self, transport_network_from_test_files, origins, destinations, expected_error
    ):
        with pytest.raises(expected_error):
            travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
                transport_network_from_test_files,
                origins=origins,
                destinations=destinations,
            )
            del travel_time_matrix_computer

    @pytest.mark.parametrize(
        [
            "origins",
            "destinations",
        ],
        [
            (
                pytest.lazy_fixture("origins_valid_ids"),
                pytest.lazy_fixture("origins_valid_ids"),
            )
        ],
    )
    def test_origins_and_destinations_valid_data(
        self, transport_network_from_test_files, origins, destinations
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network_from_test_files,
            origins=origins,
            destinations=destinations,
        )
        del travel_time_matrix_computer
