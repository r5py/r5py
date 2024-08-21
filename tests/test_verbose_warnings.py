#!/usr/bin/env python3


import sys

import pytest

import r5py


class TestVerboseWarnings:
    @pytest.fixture
    def setup_verbose_mode(self):
        original_sys_argv = sys.argv.copy()
        sys.argv.append("--verbose")
        yield
        sys.argv = original_sys_argv

    def test_trip_planner_warn_if_origin_or_destination_not_found(
        self,
        transport_network,
        regional_task,
        setup_verbose_mode,
    ):
        regional_task.transport_modes = [r5py.TransportMode.WALK]

        regional_task.fromLat = 48.20
        regional_task.fromLon = 16.37
        regional_task.toLat = 0
        regional_task.toLon = -78.5

        with pytest.warns(RuntimeWarning, match="Could not find"):
            _ = r5py.r5.trip_planner.TripPlanner(
                transport_network,
                regional_task,
            ).trips

    def test_detailed_itineraries_warn_no_destinations_all_to_all(
        self,
        transport_network,
        population_grid_points_first_three,
        departure_datetime,
        setup_verbose_mode,
    ):
        with (
            pytest.warns(
                RuntimeWarning,
                match="No destinations specified, computing an all-to-all matrix",
            ),
            pytest.warns(
                RuntimeWarning,
                match="No routing destinations defined, using origins as destinations, too.",
            ),
        ):
            r5py.DetailedItineraries(
                transport_network=transport_network,
                origins=population_grid_points_first_three,
                departure=departure_datetime,
                transport_modes=[r5py.TransportMode.WALK],
            )

    def test_detailed_itineraries_warn_diff_length_all_to_all(
        self,
        transport_network,
        population_grid_points_first_three,
        population_grid_points_four,
        departure_datetime,
        setup_verbose_mode,
    ):
        with pytest.warns(
            RuntimeWarning,
            match="Origins and destinations are of different length, computing an all-to-all matrix",
        ):
            r5py.DetailedItineraries(
                transport_network=transport_network,
                origins=population_grid_points_first_three,
                destinations=population_grid_points_four,
                departure=departure_datetime,
                transport_modes=[r5py.TransportMode.WALK],
            )

    def test_travel_time_matrix_warn_no_destinations(
        self,
        transport_network,
        population_grid_points_first_three,
        departure_datetime,
        setup_verbose_mode,
    ):
        with pytest.warns(
            RuntimeWarning,
            match="No routing destinations defined, using origins as destinations, too.",
        ):
            r5py.TravelTimeMatrix(
                transport_network,
                origins=population_grid_points_first_three,
                departure=departure_datetime,
            )

    def test_detailed_itineraries_warn_origins_equal_to_destinations(
        self,
        transport_network,
        population_grid_points_first_three,
        departure_datetime,
        setup_verbose_mode,
    ):
        with pytest.warns(
            RuntimeWarning,
            match="Origins and destinations are identical, computing an all-to-all matrix",
        ):
            detailed_itineraries_computer = r5py.DetailedItineraries(
                transport_network=transport_network,
                origins=population_grid_points_first_three,
                destinations=population_grid_points_first_three,
                departure=departure_datetime,
                transport_modes=[r5py.TransportMode.WALK],
            )
        assert detailed_itineraries_computer.all_to_all
