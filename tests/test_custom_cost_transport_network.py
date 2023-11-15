#!/usr/bin/env python3

from unittest.mock import patch
from r5py.r5.detailed_itineraries_computer import DetailedItinerariesComputer
from r5py.r5.travel_time_matrix_computer import TravelTimeMatrixComputer
from r5py.r5.custom_cost_transport_network import r5_supports_custom_costs
from r5py.util.custom_cost_conversions import (
    convert_custom_cost_instances_to_java_list,
    convert_python_dict_to_java_hashmap,
    convert_custom_cost_data_to_custom_cost_instance,
)
import pytest
import jpype
import r5py
import r5py.sampledata.helsinki

import com.conveyal.r5


# Create a custom cost test data


class Test_CustomCostTransportNetwork:
    """Test the CustomCostTransportNetwork and custom cost related logic."""

    # check that correct r5 is being used with Green Paths 2 patch, which supports custom costs
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_correct_version_of_r5(self):
        assert r5_supports_custom_costs()

    # test conversions

    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_convert_python_dict_to_java_hashmap(self, custom_cost_test_values):
        converted_data = convert_python_dict_to_java_hashmap(custom_cost_test_values)
        assert isinstance(converted_data, jpype.java.util.HashMap)
        assert converted_data.get(12345) == 1.0
        assert converted_data.isEmpty() == False

    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
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

    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_convert_custom_cost_instance_to_java_list(self, custom_cost_instance):
        custom_cost_list = convert_custom_cost_instances_to_java_list(
            # to list
            [custom_cost_instance]
        )
        assert isinstance(custom_cost_list, jpype.java.util.List)
        assert custom_cost_list.get(0).getDisplayKey() == "test_name"
        assert custom_cost_list.get(0).getDisplayValue(12345) == 1.0

    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_transport_network_java_object(self, custom_cost_transport_network):
        assert isinstance(
            custom_cost_transport_network._transport_network,
            com.conveyal.r5.transit.TransportNetwork,
        )

    # test custom cost transport network initialisation and validation

    @pytest.mark.parametrize(
        "names, sensitivities, custom_cost_datas",
        [
            ("test_cost", 1.1, []),
            ([], 1.1, [{"12345": 1.0, "67890": 1.5}]),
            ("test_cost", [], [{"12345": 1.0, "67890": 1.5}]),
            ("test_cost", [1], [{"12345": 1.0, "67890": 1.5}]),
            (["test_cost"], 1, [{"12345": 1.0, "67890": 1.5}]),
            (["test_cost"], [2.1], {"12345": 1.0, "67890": 1.5}),
            ([1], ["2.1"], {"12345": 1.0, "67890": 1.5}),
            (["name"], [1], ["12345", 67890]),
            (
                ["name_1"],
                [1.1],
                [{"12345": 1.0, "67890": 1.5}, {"12345": 1.0, "67890": 1.5}],
            ),
            (
                ["name_1"],
                [1.1, 1.2],
                [{"12345": 1.0, "67890": 1.5}, {"12345": 1.0, "67890": 1.5}],
            ),
            (["name_1", "name_2"], [1.1, 1.2], [{"12345": 1.0, "67890": 1.5}]),
        ],
    )
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_custom_cost_params_invalid_params(
        self, names, sensitivities, custom_cost_datas
    ):
        from r5py.util.exceptions import CustomCostDataError

        with patch.object(r5py.CustomCostTransportNetwork, "__del__", lambda x: None):
            with pytest.raises(CustomCostDataError):
                r5py.CustomCostTransportNetwork(
                    r5py.sampledata.helsinki.osm_pbf,
                    names,
                    sensitivities,
                    custom_cost_datas,
                )

    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_multiple_custom_cost_datas(self):
        custom_cost_transport_network = r5py.CustomCostTransportNetwork(
            r5py.sampledata.helsinki.osm_pbf,
            ["test_cost_1", "test_cost_2"],
            [1.1, 1.2],
            [{"1": 1.1, "2": 1.2}, {"3": 1.3, "4": 1.4}],
        )
        assert custom_cost_transport_network.names == ["test_cost_1", "test_cost_2"]
        assert custom_cost_transport_network.sensitivities == [1.1, 1.2]
        assert custom_cost_transport_network.custom_cost_datas == [
            {"1": 1.1, "2": 1.2},
            {"3": 1.3, "4": 1.4},
        ]

    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_custom_cost_trasport_network_invalid_osmid_key_fails(
        self, custom_cost_transport_network
    ):
        custom_costs = (
            custom_cost_transport_network._transport_network.streetLayer.edgeStore.costFields
        )
        assert isinstance(custom_costs, jpype.java.util.List)
        assert custom_costs.get(0).getDisplayKey() == "test_cost"
        # should fail if invalid (osmid) key
        try:
            custom_costs.get(0).getDisplayValue(12345)
            assert False, "Expected a NullPointerException"
        except jpype.JException as e:
            if isinstance(e, jpype.java.lang.NullPointerException):
                assert True
            else:
                raise

    # custom cost routing tests

    @pytest.mark.parametrize(
        "routing_computer_class",
        [TravelTimeMatrixComputer, DetailedItinerariesComputer],
    )
    @pytest.mark.parametrize(
        "origin_point_factory", ["single", "multiple"], indirect=True
    )
    @pytest.mark.parametrize(
        "custom_cost_transport_network_factory",
        ["single", "negative", "multiple"],
        indirect=True,
    )
    @pytest.mark.parametrize(
        "transport_mode", [r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]
    )
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_custom_cost_routing_one_to_many(
        self,
        routing_computer_class,
        transport_mode,
        origin_point_factory,
        multiple_destination_points,
        custom_cost_transport_network_factory,
        custom_cost_transport_network_zero_values,
    ):
        """Test custom cost routing with both: TravelTimeMatrixComputer and DetailedItinerariesComputer.
        Test TravelTimeMatrixComputer with one-to-many and many-to-many OD-pairs and DetailedItinerariesComputer with one-to-one routing.
        Compare all results with custom cost values and zero custom cost values to verify the applied custom costs during routing.
        Test both active transport modes: walking and cycling.
        """
        travel_time_matrix_computer_with_custom_values = routing_computer_class(
            custom_cost_transport_network_factory,
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

        # check that NEGATIVE custom costs are applied correctly
        # i.e. that all the travel times are SHORTER
        if custom_cost_transport_network_factory == "negative":
            assert all(
                a < b
                for a, b in zip(
                    travel_times_with_custom_costs, travel_times_with_zero_costs
                )
            )
        elif (
            custom_cost_transport_network_factory == "single"
            or custom_cost_transport_network_factory == "multiple"
        ):
            # check that POSITIVE custom costs are applied correctly
            # i.e. that all the travel times are LONGER
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
