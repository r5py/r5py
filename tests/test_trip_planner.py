#!/usr/bin/env python3


import r5py


class TestTripPlanner:
    def test_trip_planner_initialization(
        self,
        transport_network,
        regional_task,
    ):
        _ = r5py.r5.trip_planner.TripPlanner(transport_network, regional_task)
