#!/usr/bin/env python3

from unittest.mock import patch
from r5py.r5.detailed_itineraries_computer import DetailedItinerariesComputer
from r5py.r5.travel_time_matrix_computer import TravelTimeMatrixComputer
from r5py.r5.custom_cost_transport_network import r5_supports_custom_costs
from r5py.util.custom_cost_conversions import (
    convert_custom_cost_instances_to_java_list,
    convert_python_dict_to_java_hashmap,
    convert_custom_cost_segment_weight_factors_to_custom_cost_instance,
)
import pytest
import jpype
import r5py
import r5py.sampledata.helsinki

import com.conveyal.r5


class Test_CustomCostTransportNetwork:
    """Test the CustomCostTransportNetwork and custom cost related logic."""

    # unify routing for tests, scope function so that the routing results aren't cached
    @pytest.fixture(scope="function")
    def custom_cost_routing_results(
        self,
        routing_computer_class,
        origin_point_factory,
        multiple_destination_points,
        custom_cost_transport_network_selector,
        custom_cost_transport_network_zero_values,
        transport_mode,
    ):
        travel_time_matrix_computer_with_custom_values = routing_computer_class(
            custom_cost_transport_network_selector,
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

        if issubclass(routing_computer_class, DetailedItinerariesComputer):
            # DetailedItinerariesComputer logic
            custom_cost_values_router_results = (
                travel_time_matrix_computer_with_custom_values.compute_travel_details()
            )
            zero_cost_values_router_results = (
                travel_time_matrix_computer_with_zero_values.compute_travel_details()
            )
        else:
            # TravelTimeMatrixComputer logic
            custom_cost_values_router_results = (
                travel_time_matrix_computer_with_custom_values.compute_travel_times()
            )
            zero_cost_values_router_results = (
                travel_time_matrix_computer_with_zero_values.compute_travel_times()
            )

        assert not custom_cost_values_router_results.empty
        assert not zero_cost_values_router_results.empty

        # Return a tuple or a dict with the results
        yield custom_cost_values_router_results, zero_cost_values_router_results
        del custom_cost_values_router_results
        del zero_cost_values_router_results

    # check that correct r5 is being used with Green Paths 2 patch, which supports custom costs
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_correct_version_of_r5(self):
        assert r5_supports_custom_costs()

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
    def test_convert_custom_cost_segment_weight_factors_to_custom_cost_instance(
        self, custom_cost_hashmap
    ):
        assert isinstance(custom_cost_hashmap, jpype.java.util.HashMap)
        custom_cost_instance = (
            convert_custom_cost_segment_weight_factors_to_custom_cost_instance(
                "test_name", 1.3, custom_cost_hashmap, True
            )
        )
        assert isinstance(
            custom_cost_instance, com.conveyal.r5.rastercost.CustomCostField
        )
        assert custom_cost_instance.getDisplayKey() == "test_name"
        assert custom_cost_instance.getSensitivityCoefficient() == 1.3
        assert custom_cost_instance.getDisplayValue(12345) == 1.0
        assert custom_cost_instance.getCustomCostFactors().isEmpty() == False

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

    # TEST CUSTOM COST TRANSPORT NETWORK INITIALIZATION AND VALIDATION

    @pytest.mark.parametrize(
        "names, sensitivities, custom_cost_segment_weight_factors, allow_missing_osmids",
        [
            ("test_cost", 1.1, [], True),
            ([], 1.1, [{}], True),
            ("test_cost", [], [{"12345": 1.0, "67890": 1.5}], True),
            ("test_cost", [1], {}, True),
            (
                ["test_cost"],
                1,
                [{"12345": 1.0, "67890": 1.5}, {"12345": 1.0, "67890": 1.5}],
                True,
            ),
            (["name"], [1], ["12345", 67890], True),
            (
                ["name_1"],
                [1.1],
                [{"12345": 1.0, "67890": 1.5}, {"12345": 1.0, "67890": 1.5}],
                True,
            ),
            (
                ["name_1"],
                [1.1, 1.2],
                [{}, {}],
                True,
            ),
            (["name_1", "name_2"], [1.1, 1.2], [{"12345": 1.0, "67890": 1.5}], True),
            # test allow_missing_osmids flag to fail if allow_missing_osmids is False
            (
                ["name_1", "name_2"],
                [1.1, 1.2],
                [{"12345": 1.0, "67890": 1.5}],
                [False, False],
            ),
        ],
    )
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_custom_cost_params_invalid_params(
        self,
        names,
        sensitivities,
        custom_cost_segment_weight_factors,
        allow_missing_osmids,
    ):
        from r5py.util.exceptions import CustomCostDataError

        with patch.object(r5py.CustomCostTransportNetwork, "__del__", lambda x: None):
            with pytest.raises(CustomCostDataError):
                r5py.CustomCostTransportNetwork(
                    r5py.sampledata.helsinki.osm_pbf,
                    names,
                    sensitivities,
                    custom_cost_segment_weight_factors,
                    allow_missing_osmids,
                )

    @pytest.mark.parametrize(
        "names, sensitivities, custom_cost_segment_weight_factors, allow_missing_osmids",
        [
            (["test_cost_1"], 1.1, {"1": 1.1, "2": 1.2}, True),
            (
                ["test_cost_1", "test_cost_2"],
                [1.1, 1.2],
                [{"1": 1.1, "2": 1.2}, {"3": 1.3, "4": 1.4}],
                [True, False],
            ),
        ],
    )
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_single_and_multiple_custom_cost_segment_weight_factors_sets(
        self,
        names,
        sensitivities,
        custom_cost_segment_weight_factors,
        allow_missing_osmids,
    ):
        custom_cost_transport_network = r5py.CustomCostTransportNetwork(
            r5py.sampledata.helsinki.osm_pbf,
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        )
        assert custom_cost_transport_network.names == names
        # CustomCostTransportNetwork should convert params to list so do it here too manually
        if not isinstance(sensitivities, list):
            sensitivities = [sensitivities]
        assert custom_cost_transport_network.sensitivities == sensitivities
        if not isinstance(custom_cost_segment_weight_factors, list):
            custom_cost_segment_weight_factors = [custom_cost_segment_weight_factors]
        assert (
            custom_cost_transport_network.custom_cost_segment_weight_factors
            == custom_cost_segment_weight_factors
        )

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

    # TEST CUSTOM COST ROUTING

    @pytest.mark.parametrize(
        "routing_computer_class",
        [TravelTimeMatrixComputer, DetailedItinerariesComputer],
    )
    @pytest.mark.parametrize(
        "origin_point_factory", ["single_point", "multiple_points"], indirect=True
    )
    @pytest.mark.parametrize(
        "custom_cost_transport_network_selector",
        ["single_cost", "negative_cost", "multiple_cost"],
        indirect=True,
    )
    @pytest.mark.parametrize(
        "transport_mode", [r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]
    )
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_custom_cost_routing(
        self,
        custom_cost_routing_results,
        routing_computer_class,
        custom_cost_transport_network_selector,
    ):
        """Test custom cost routing with both: TravelTimeMatrixComputer and DetailedItinerariesComputer.
        Test TravelTimeMatrixComputer with one-to-many and many-to-many OD-pairs and DetailedItinerariesComputer with one-to-one routing.
        Compare all results with custom cost values and zero custom cost values to verify the applied custom costs during routing.
        Test both active transport modes: walking and cycling.
        """
        # use the results from the fixture
        (
            custom_cost_values_router_results,
            zero_cost_values_router_results,
        ) = custom_cost_routing_results

        travel_times_with_custom_costs = list(
            custom_cost_values_router_results["travel_time"].values
        )
        travel_times_with_zero_costs = list(
            zero_cost_values_router_results["travel_time"].values
        )

        # check that NEGATIVE custom costs are applied correctly
        # i.e. that all the travel times are SHORTER
        if custom_cost_transport_network_selector == "negative_cost":
            assert all(
                a < b
                for a, b in zip(
                    travel_times_with_custom_costs, travel_times_with_zero_costs
                )
            )
        elif (
            custom_cost_transport_network_selector == "single_cost"
            or custom_cost_transport_network_selector == "multiple_cost"
        ):
            # check that POSITIVE custom costs are applied correctly
            # i.e. that all the travel times are LONGER
            assert all(
                a > b
                for a, b in zip(
                    travel_times_with_custom_costs, travel_times_with_zero_costs
                )
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

    @pytest.mark.parametrize(
        "routing_computer_class",
        [TravelTimeMatrixComputer, DetailedItinerariesComputer],
    )
    @pytest.mark.parametrize(
        "origin_point_factory", ["single_point", "multiple_points"], indirect=True
    )
    @pytest.mark.parametrize(
        "custom_cost_transport_network_selector",
        ["single_cost", "negative_cost", "multiple_cost"],
        indirect=True,
    )
    @pytest.mark.parametrize(
        "transport_mode", [r5py.TransportMode.WALK, r5py.TransportMode.BICYCLE]
    )
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_custom_cost_routing_correct_osmids(
        self,
        custom_cost_routing_results,
        origin_point_factory,
        multiple_destination_points,
    ):
        """Test that the custom cost routing results contain correct osmids."""
        (
            custom_cost_values_router_results,
            zero_cost_values_router_results,
        ) = custom_cost_routing_results
        # use the results from the fixture
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

    @pytest.mark.parametrize(
        "method_name",
        ["get_base_travel_times", "get_custom_cost_additional_travel_times"],
    )
    @pytest.mark.parametrize(
        "routing_computer_class",
        [TravelTimeMatrixComputer, DetailedItinerariesComputer],
    )
    # only test multiple points for not having excessive amount of tests, single point is tested in previous tests
    @pytest.mark.parametrize("origin_point_factory", ["multiple_points"], indirect=True)
    @pytest.mark.parametrize(
        "custom_cost_transport_network_selector",
        ["single_cost", "negative_cost", "multiple_cost"],
        indirect=True,
    )
    # test only walking for not having excessive amount of tests
    # travel modes are tested in previous tests
    @pytest.mark.parametrize("transport_mode", [r5py.TransportMode.WALK])
    @pytest.mark.parametrize(
        "osmids", [[], [1000813187, 1000813188], ["1000813187", "1000813188"]]
    )
    @pytest.mark.parametrize("merged", [True, False])
    @pytest.mark.skipif(
        r5_supports_custom_costs() is False,
        reason="R5 version does not support custom costs",
    )
    def test_custom_cost_routing_base_costs_and_custom_costs(
        self,
        method_name,
        custom_cost_transport_network_selector,
        custom_cost_routing_results,
        osmids,
        merged,
    ):
        """Test base travel times and custom cost additional travel times are valid."""
        # route with custom costs
        _, _ = custom_cost_routing_results

        if method_name == "get_base_travel_times":
            base_travel_times = (
                custom_cost_transport_network_selector.get_base_travel_times()
            )
        elif method_name == "get_custom_cost_additional_travel_times":
            base_travel_times = (
                custom_cost_transport_network_selector.get_custom_cost_additional_travel_times()
            )

        # check for correct types
        assert isinstance(base_travel_times, list)
        assert isinstance(base_travel_times[0], tuple)
        assert isinstance(base_travel_times[0][0], str)
        assert isinstance(base_travel_times[0][1], dict)

        # set to variables for easier reading
        FIRST_CUSTOM_COST_NAME = base_travel_times[0][0]
        SECOND_CUSTOM_COST_NAME = (
            base_travel_times[1][0] if len(base_travel_times) >= 2 else None
        )
        FIRST_CUSTOM_COST_VALUES = base_travel_times[0][1]
        SECOND_CUSTOM_COST_VALUES = (
            base_travel_times[1][1] if len(base_travel_times) >= 2 else None
        )

        # see that the expected osmids are to be found in the results
        # check values, osmid filtering and merging results
        if osmids:
            for osmid in osmids:
                assert str(osmid) in FIRST_CUSTOM_COST_VALUES
                if SECOND_CUSTOM_COST_VALUES:
                    assert str(osmid) in SECOND_CUSTOM_COST_VALUES

        if (
            custom_cost_transport_network_selector == "single_cost"
            or custom_cost_transport_network_selector == "negative_cost"
        ):
            # should have one tuple
            assert len(base_travel_times) == 1
            # check the name of 1st custom cost
            if merged:
                assert FIRST_CUSTOM_COST_NAME == "merged_custom_costs:_random_cost_1"
            else:
                assert FIRST_CUSTOM_COST_NAME == "random_cost_1"
            # check that has osmids
            assert len(list(FIRST_CUSTOM_COST_VALUES.items())) > 0
            assert len(list(FIRST_CUSTOM_COST_VALUES.keys())) > 0
            assert len(list(FIRST_CUSTOM_COST_VALUES.values())) > 0

        elif custom_cost_transport_network_selector == "multiple_cost":
            if merged:
                # should have one merged tuple
                assert len(base_travel_times) == 1
                # name should be exactly this
                assert (
                    FIRST_CUSTOM_COST_NAME
                    == "merged_custom_costs:_random_cost_1_random_cost_2"
                )
                # check that has osmids
                assert len(FIRST_CUSTOM_COST_VALUES) > 0
            # should have two tuples
            elif not merged:
                assert len(base_travel_times) == 2
                assert FIRST_CUSTOM_COST_NAME == "random_cost_1"
                assert SECOND_CUSTOM_COST_NAME == "random_cost_2"
                # check that both custom costs have osmids
                assert len(FIRST_CUSTOM_COST_VALUES) > 0
                assert len(SECOND_CUSTOM_COST_VALUES) > 0
                if method_name == "get_base_travel_times":
                    # check that the osmids are same for base traveltimes
                    for osmid, base_travel_time in FIRST_CUSTOM_COST_VALUES.items():
                        # check that if a value with same osmid exists in the other custom cost
                        # it the same as the value in the first custom cost
                        # for base travel times should be same for edges
                        if osmid in SECOND_CUSTOM_COST_VALUES:
                            assert base_travel_time == SECOND_CUSTOM_COST_VALUES[osmid]
                            # check osmid type
                            assert isinstance(osmid, int)
                            assert str(osmid).isdigit()
                elif method_name == "get_custom_cost_additional_travel_times":
                    # check that the osmids are different for addition costs
                    assert FIRST_CUSTOM_COST_VALUES != SECOND_CUSTOM_COST_VALUES
