#!/usr/bin/env python3


import pandas
import pytest
import pytest_lazy_fixtures  # noqa: F401

import r5py

from .test_custom_cost_transport_network import (  # noqa: F401
    R5_SUPPORTS_CUSTOM_COSTS,
    R5_SUPPORTS_PRECALCULATE_COSTS,
)


@pytest.mark.skipif(
    not R5_SUPPORTS_CUSTOM_COSTS,
    reason="R5 jar does not support custom costs",
)
class Test_CustomCostTravelTimeMatrixComputer:
    """Test the CustomCostTravelTimeMatrix."""

    def test_init(
        self,
        custom_costs_transport_network,
        population_grid_points,
        origin_point,
        departure_datetime,
    ):
        travel_time_matrix_computer = r5py.CustomCostTravelTimeMatrixComputer(
            custom_costs_transport_network,
            origins=origin_point,
            destinations=population_grid_points,
            departure=departure_datetime,
            transport_modes=[r5py.TransportMode.WALK],
        )
        assert isinstance(
            travel_time_matrix_computer, r5py.CustomCostTravelTimeMatrixComputer
        )
        assert isinstance(travel_time_matrix_computer, r5py.TravelTimeMatrixComputer)

    @pytest.mark.parametrize(
        [
            "transport_mode",
            "expected_travel_times",
        ],
        [
            (
                r5py.TransportMode.BICYCLE,
                pytest_lazy_fixtures.lf("custom_costs_travel_times_bicycle"),
            ),
            (
                r5py.TransportMode.CAR,
                pytest_lazy_fixtures.lf("custom_costs_travel_times_car"),
            ),
            (
                r5py.TransportMode.TRANSIT,
                pytest_lazy_fixtures.lf("custom_costs_travel_times_transit"),
            ),
            (
                r5py.TransportMode.WALK,
                pytest_lazy_fixtures.lf("custom_costs_travel_times_walk"),
            ),
        ],
    )
    def test_travel_times(
        self,
        custom_costs_transport_network,
        population_grid_points,
        departure_datetime,
        transport_mode,
        expected_travel_times,
    ):
        travel_time_matrix_computer = r5py.TravelTimeMatrixComputer(
            custom_costs_transport_network,
            origins=population_grid_points,
            departure=departure_datetime,
            transport_modes=[transport_mode],
        )
        travel_times = travel_time_matrix_computer.compute_travel_times()

        travel_times = travel_times.set_index(["from_id", "to_id"]).sort_index()
        expected_travel_times = expected_travel_times.set_index(
            ["from_id", "to_id"]
        ).sort_index()

        travel_times.to_csv(f"/tmp/test_custom_costs_travel_times_{transport_mode.value.lower()}.csv")

        pandas.testing.assert_frame_equal(travel_times, expected_travel_times)
