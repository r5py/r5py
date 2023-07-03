#!/usr/bin/env python3


import pytest
import r5py


class TestTripPlanner:
    def test_trip_planner_initialization(
        self,
        transport_network,
        regional_task,
    ):
        _ = r5py.r5.trip_planner.TripPlanner(transport_network, regional_task)


#
#     def test_transit_access_paths(
#         self,
#         transport_network,
#         regional_task,
#         unsnappable_points,
#     ):
#         for point in unsnappable_points.geometry:
#             regional_task._regional_task.fromLat = point.y
#             regional_task._regional_task.fromLon = point.x
#             trip_planner = r5py.r5.trip_planner.TripPlanner(transport_network, regional_task)
#             with pytest.warns(
#                 RuntimeWarning,
#                 match="Could not find origin",
#             ):
#                 _ = trip_planner.transit_access_paths
#
#     def test_transit_egress_paths(
#         self,
#         transport_network,
#         regional_task,
#         unsnappable_points,
#     ):
#         trip_planner = r5py.r5.trip_planner.TripPlanner(transport_network, regional_task)
#         for point in unsnappable_points.geometry:
#             with pytest.warns(
#                 RuntimeWarning,
#                 match="Could not find destination",
#             ):
#                 trip_planner.request._regional_task.toLat = point.y
#                 trip_planner.request._regional_task.toLon = point.x
#                 _ = trip_planner.transit_egress_paths
#
#     def test_transit_transfer_path(
#         self, transport_network, regional_task,
#         unreachable_stops,
#     ):
#         trip_planner = r5py.r5.trip_planner.TripPlanner(transport_network, regional_task)
#         for stop, next_stop in zip(
#             unreachable_stops,
#             unreachable_stops[1:] + unreachable_stops[1]
#         ):
#             _ = trip_planner.transit_transfer_path(stop, next_stop)
