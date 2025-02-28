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
    yield {}


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
    @pytest.mark.parametrize(
        "transport_modes",
        [
            (r5py.TransportMode.WALK,),
            (r5py.TransportMode.BICYCLE,),
            (r5py.TransportMode.CAR,),
            (r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK),
        ],
    )
    @pytest.mark.parametrize("iteration", range(5))
    def test_public_transport_travel_time_matrices(
        self,
        transport_network,
        population_grid_points,
        departure_datetime,
        transport_modes,
        intermediate_results,
        iteration,
    ):
        # subset to keep test comparison data sets small
        origins = population_grid_points[::5].copy()

        travel_times = r5py.TravelTimeMatrix(
            transport_network,
            origins,
            departure=departure_datetime,
            transport_modes=transport_modes,
            snap_to_network=True,
        )

        if transport_modes in intermediate_results:
            previous_results = intermediate_results[transport_modes]
            pandas.testing.assert_frame_equal(
                travel_times,
                previous_results,
                check_like=True,
            )
        intermediate_results[transport_modes] = travel_times.copy()
