#!/usr/bin/env python3


import sys

import pytest  # noqa: F401

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
            r5py.r5.trip_planner.TripPlanner(
                transport_network,
                regional_task,
            ).plan()
