#!/usr/bin/env python3


"""Test whether routing is (more or less) deterministic (https://github.com/r5py/r5py/issues/240)."""


import itertools

import pandas.testing
import pytest

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
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        intermediate_results,
        iteration,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            transport_network,
            population_grid_points,
            departure=departure_datetime,
            snap_to_network=True,
        )
        travel_times = travel_time_matrix_computer.compute_travel_times()

        intermediate_results.append(travel_times)

        for matrix_a, matrix_b in pairwise(intermediate_results):
            # m_a = matrix_a.set_index(["from_id", "to_id"])
            # m_b = matrix_b.set_index(["from_id", "to_id"])
            # m_a["difference"] = m_a.travel_time - m_b.travel_time
            # print(
            #     m_a[m_a.difference != 0],
            #     m_a.difference.describe(),
            #     m_a[(m_a.difference >= 3) | (m_a.difference <= -3)],
            # )

            pandas.testing.assert_frame_equal(
                matrix_a,
                matrix_b,
                check_like=True,
                atol=3,  # tolerance between runs, in minutes
            )
