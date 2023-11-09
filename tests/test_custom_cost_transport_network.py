#!/usr/bin/env python3

from r5py.r5.detailed_itineraries_computer import DetailedItinerariesComputer
from r5py.r5.travel_time_matrix_computer import TravelTimeMatrixComputer
from r5py.util.custom_cost_conversions import (
    convert_custom_cost_instances_to_java_list,
    convert_python_dict_to_java_hashmap,
    convert_custom_cost_data_to_custom_cost_instance,
)
import pytest
import jpype
import com.conveyal.r5
import r5py
import r5py.sampledata.helsinki

# Create a custom cost test data


class Test_CustomCostTransportNetwork:
    """Test the CustomCostTransportNetwork and custom cost related logic."""

    def test_convert_python_dict_to_java_hashmap(self, custom_cost_test_values):
        converted_data = convert_python_dict_to_java_hashmap(custom_cost_test_values)
        assert isinstance(converted_data, jpype.java.util.HashMap)
        assert converted_data.get(12345) == 1.0
        assert converted_data.isEmpty() == False

    def test_convert_custom_cost_data_to_custom_cost_instance(
        self, custom_cost_hashmap
    ):
        assert isinstance(custom_cost_hashmap, jpype.java.util.HashMap)
        custom_cost_instance = convert_custom_cost_data_to_custom_cost_instance(
            "test_name", 1.3, custom_cost_hashmap
        )
        assert isinstance(
            custom_cost_instance, com.conveyal.r5.rastercost.CustomCostField
        )
        assert custom_cost_instance.getDisplayKey() == "test_name"
        assert custom_cost_instance.sensitivityCoefficient == 1.3
        assert custom_cost_instance.getDisplayValue(12345) == 1.0
        assert custom_cost_instance.customCostMap.isEmpty() == False

    def test_convert_custom_cost_instance_to_java_list(self, custom_cost_instance):
        custom_cost_list = convert_custom_cost_instances_to_java_list(
            custom_cost_instance
        )
        assert isinstance(custom_cost_list, jpype.java.util.List)
        assert custom_cost_list.get(0).getDisplayKey() == "test_name"
        assert custom_cost_list.get(0).getDisplayValue(12345) == 1.0

    def test_transport_network_java_object(self, custom_cost_transport_network):
        assert isinstance(
            custom_cost_transport_network._transport_network,
            com.conveyal.r5.transit.TransportNetwork,
        )

    def test_custom_cost_trasport_network_streetlayer_edgestore_has_costfields(
        self, custom_cost_transport_network
    ):
        custom_costs = (
            custom_cost_transport_network._transport_network.streetLayer.edgeStore.costFields
        )
        assert isinstance(custom_costs, jpype.java.util.List)
        assert custom_costs.get(0).getDisplayKey() == "test_name"
        assert custom_costs.get(0).getDisplayValue(12345) == 1.0

    @pytest.mark.parametrize(
        "routing_computer_class",
        [TravelTimeMatrixComputer, DetailedItinerariesComputer],
    )
    @pytest.mark.parametrize(
        "origin_point_factory", ["single", "multiple"], indirect=True
    )
    @pytest.mark.parametrize(
        "transport_mode", [r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]
    )
    def test_custom_cost_routing_one_to_many(
        self,
        routing_computer_class,
        transport_mode,
        origin_point_factory,
        multiple_destination_points,
        custom_cost_transport_network_random_values,
        custom_cost_transport_network_zero_values,
    ):
        """Test custom cost routing with both: TravelTimeMatrixComputer and DetailedItinerariesComputer.
        Test TravelTimeMatrixComputer with one-to-many and many-to-many OD-pairs and DetailedItinerariesComputer with one-to-one routing.
        Compare all results with custom cost values and zero custom cost values to verify the applied custom costs during routing.
        Test both active transport modes: walking and cycling.
        """
        travel_time_matrix_computer_with_custom_values = routing_computer_class(
            custom_cost_transport_network_random_values,
            origins=origin_point_factory,
            destinations=multiple_destination_points,
            transport_modes=[transport_mode],
        )

        travel_time_matrix_computer_with_zero_values = routing_computer_class(
            custom_cost_transport_network_zero_values,
            origins=origin_point_factory,
            destinations=multiple_destination_points,
            transport_modes=[transport_mode],
        )

        # different names with different routing computers
        if issubclass(routing_computer_class, DetailedItinerariesComputer):
            # using DetailedItinerariesComputer
            custom_cost_values_router_results = (
                travel_time_matrix_computer_with_custom_values.compute_travel_details()
            )
            zero_cost_values_router_results = (
                travel_time_matrix_computer_with_zero_values.compute_travel_details()
            )
        else:
            # using TravelTimeMatrixComputer
            custom_cost_values_router_results = (
                travel_time_matrix_computer_with_custom_values.compute_travel_times()
            )
            zero_cost_values_router_results = (
                travel_time_matrix_computer_with_zero_values.compute_travel_times()
            )

        assert not custom_cost_values_router_results.empty
        assert not zero_cost_values_router_results.empty

        travel_times_with_custom_costs = list(
            custom_cost_values_router_results["travel_time"].values
        )
        travel_times_with_zero_costs = list(
            zero_cost_values_router_results["travel_time"].values
        )

        # check that all the paths taken with custom costs have longer travel time than paths with zero costs
        assert all(
            a > b
            for a, b in zip(
                travel_times_with_custom_costs, travel_times_with_zero_costs
            )
        )

        osmids_with_custom_costs = custom_cost_values_router_results["osm_ids"].values
        osmids_with_zero_costs = zero_cost_values_router_results["osm_ids"].values

        # check that has correct amount of osmid lists in the results
        # the amount depends on the number of destinations points and if one-to-many or many-to-many
        # in many-to-many the amount of results gain polynomially with the amount of OD pairs
        number_of_origin_points = len(multiple_destination_points) * len(
            origin_point_factory
        )
        assert len(osmids_with_custom_costs) == number_of_origin_points
        assert len(osmids_with_zero_costs) == number_of_origin_points

        # convert java arraylists to python lists
        osmids_with_custom_costs_pylist = [
            list(osmids) for osmids in osmids_with_custom_costs
        ]
        osmids_with_zero_costs_pylist = [
            list(osmids) for osmids in osmids_with_zero_costs
        ]

        # the osmid results should'n be the same when custom costs are applied
        # i.e. should take a different paths/route
        assert osmids_with_custom_costs_pylist != osmids_with_zero_costs_pylist

        # should contain at least one osmid in every osmid list
        for osmids in osmids_with_custom_costs_pylist:
            # can be 0 in detailed itineraries
            assert len(osmids) >= 0

        # check that all the routes are different, no unique routes should exist
        # theoretically there can be same routes if e.g. OD pair is very close to each other
        # but not with current test OD pairs
        assert all(
            osmids_with_custom_costs_pylist[i] != osmids_with_custom_costs_pylist[j]
            for i in range(len(osmids_with_custom_costs_pylist))
            for j in range(i + 1, len(osmids_with_custom_costs_pylist))
        )

        # for detailed itineraries, check also that the geometries are different
        if issubclass(routing_computer_class, DetailedItinerariesComputer):
            osmids_with_custom_costs = list(
                custom_cost_values_router_results["geometry"].values
            )
            osmids_with_zero_costs = list(
                zero_cost_values_router_results["geometry"].values
            )
            assert osmids_with_custom_costs != osmids_with_zero_costs
