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


# Python 3.10+
def pairwise(iterable):
    """pairwise("ABCDEFG") --> AB BC CD DE EF FG ."""
    try:
        return itertools.pairwise(iterable)
    except AttributeError:  # Python<3.10
        a, b = itertools.tee(iterable)
        next(b, None)
        return zip(a, b)


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

        for matrix_a, matrix_b in pairwise(intermediate_results):
            assert (
                matrix_a.set_index(["from_id", "to_id"])
                .sort_index()
                .equals(matrix_b.set_index(["from_id", "to_id"]).sort_index())
            )
