#!/usr/bin/env python3


"""Test whether routing is (more or less) deterministic (https://github.com/r5py/r5py/issues/240)."""


import itertools

import pytest  # noqa: F401

import r5py


@pytest.fixture(scope="module")
def intermediate_results():
    # will be modified in each iteration,
    # used to compare results across computation runs
    yield []


class TestDeterministicBehaviour:
    @pytest.mark.parametrize("iteration", range(10))
    def test_public_transport_travel_time_matrices(
        self, transport_network, population_grid_points, intermediate_results, iteration
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            population_grid_points,
        )
        travel_times = travel_time_matrix_computer.compute_travel_times()

        intermediate_results.append(travel_times)

        for matrix_a, matrix_b in itertools.pairwise(intermediate_results):
            assert (
                matrix_a.set_index(["from_id", "to_id"])
                .sort_index()
                .equals(matrix_b.set_index(["from_id", "to_id"]).sort_index())
            )
