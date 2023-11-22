#!/usr/bin/env python3

"""Subclass for TransportNetwork, enables custom cost routing."""
import com.conveyal.r5
from r5py.r5.transport_network import TransportNetwork
from r5py.util.custom_cost_conversions import (
    convert_java_hashmap_to_python_dict,
    convert_python_custom_costs_to_java_custom_costs,
)
from r5py.util.exceptions import CustomCostDataError
from r5py.util.jvm import start_jvm

__all__ = ["CustomCostTransportNetwork"]

start_jvm()


def r5_supports_custom_costs():
    """
    Check if the R5 java has the GP2 (Green Paths 2) patch i.e. supports custom costs routing.

    Returns:
    --------
    bool: True if using GP2 R5, False otherwise.
    """
    try:
        import com.conveyal.r5.rastercost.CustomCostField  # noqa: F401

        # the import was successful thus using GP2 R5
        return True
    except ImportError:
        # the import was unsuccessful
        return False


class CustomCostTransportNetwork(TransportNetwork):
    """Inherit from TransportNetwork, adds custom cost data routing functionality."""

    def __init__(self, osm_pbf, names, sensitivities, custom_cost_datas):
        """
        Initialise a transport network with custom costs.
        Supports multiple custom costs. Must always have the same number of:
        names, sensitivities, and custom_cost_datas.

        Arguments
        ---------
        osm_pbf : str
            file path of an OpenStreetMap extract in PBF format
        names : List[str]
            name(s) of the custom cost(s)
        sensitivities : List[float] | List[int]
            sensitivities of the custom cost(s)
        custom_cost_datas : List[Dict[str, float]]
            custom cost data(s) to be used in routing.
            str key is osmid, float value is custom costs per edge (way).
            multiple custom cost data can be provided as a list of python dicts,
            when multiple custom cost datas are provided, all of those custom cost datas will be combined
            for each edge (way) during r5 custom cost routing.
        """
        # crash if custom costs are NOT supported in the used version of R5
        # either use TransportNetwork (without custom costs) or change to correct version of R5
        if not r5_supports_custom_costs():
            raise ImportError(
                """Custom costs are not supported in this version of R5.
                Correct (Green Paths 2 / r5_gp2) R5 version can be found here:
                https://github.com/DigitalGeographyLab/r5_gp2.
                """
            )
        self.validate_custom_cost_params(names, sensitivities, custom_cost_datas)
        self.names = names
        self.sensitivities = sensitivities
        self.custom_cost_datas = custom_cost_datas
        # GTFS is currently not supported for custom cost transport network
        super().__init__(osm_pbf, gtfs=[])

    def validate_custom_cost_params(self, names, sensitivities, custom_cost_datas):
        """Validate custom cost parameters."""
        # parameters are lists and non-empty
        params = {
            "names": names,
            "sensitivities": sensitivities,
            "custom_cost_datas": custom_cost_datas,
        }
        for param_name, param_value in params.items():
            if not isinstance(param_value, list):
                raise CustomCostDataError(f"{param_name} must be a list")
            if not param_value:
                raise CustomCostDataError(f"{param_name} must not be empty")

        # lists are of the same length
        if len(set(map(len, params.values()))) != 1:
            raise CustomCostDataError(
                "names, sensitivities, and custom_cost_datas must be of the same length"
            )

        # check individual item types
        for name, sensitivity, custom_cost_data in zip(
            names, sensitivities, custom_cost_datas
        ):
            if not isinstance(name, str):
                raise CustomCostDataError("Names must be strings")
            if not isinstance(sensitivity, (float, int)):
                raise CustomCostDataError("Sensitivities must be floats or integers")
            if not isinstance(custom_cost_data, dict) or not all(
                isinstance(key, str) and isinstance(value, float)
                for key, value in custom_cost_data.items()
            ):
                raise CustomCostDataError(
                    "Custom_cost_datas must be dicts with string keys and float values"
                )

    def add_custom_cost_data_to_network(self, transport_network):
        """Custom hook for adding custom cost data to the transport network edges."""
        vertex_store = com.conveyal.r5.streets.VertexStore(100_000)
        edge_store = com.conveyal.r5.streets.EdgeStore(
            vertex_store, transport_network.streetLayer, 200_000
        )
        transport_network.streetLayer.vertexStore = vertex_store
        transport_network.streetLayer.edgeStore = edge_store
        converted_custom_cost_data = convert_python_custom_costs_to_java_custom_costs(
            self.names, self.sensitivities, self.custom_cost_datas
        )
        transport_network.streetLayer.edgeStore.costFields = converted_custom_cost_data
        self._transport_network = transport_network
        return transport_network

    def _fetch_network_custom_cost_travel_time_product(
        self, method_name, osmids=[], merged=False
    ):
        """
        Retrieve custom cost travel time related product hashmap per osmid from the network edges.
        Ensure that this method is executed post-routing.
        Should not be called directly, use get_base_travel_times or get_additional_travel_times instead.

        Arguments:
        ----------
        method_name : str
            name of the method to be called from the custom cost transport network
            this can be either: getAdditionalTravelTimes or getTravelTimes
            getAdditionalTravelTimes returns the additional travel times from the custom cost instances
            getTravelTimes returns the base travel times from the custom cost instances
            both methods return a Java HashMap with Osmid as key and travel time as value

            note: in getTravelTimes the value is actual seconds but in getAdditionalTravelTimes
            the value more of a cost than actual seconds

        osmids : List[str | int] (optional)
            list of osmids to get travel times for. If not provided, return all travel times.

        merged : bool, default False
            define if the base travel times should be merged into a single dict or not

        Returns:
        --------
        travel_times_per_custom_cost: List[Tuple[str, Dict[str, int]]]
            list of tuples of custom cost name and travel times per custom cost routing

        """
        try:
            cost_fields_list = list(
                self._transport_network.streetLayer.edgeStore.costFields
            )
            travel_times_per_custom_cost = [
                (
                    str(cost_field.getDisplayKey()),
                    convert_java_hashmap_to_python_dict(
                        getattr(cost_field, method_name)()
                    ),
                )
                for cost_field in cost_fields_list
            ]

            # if osmids provided, filter the osm dict value result to only include the osmids provided
            if osmids:
                travel_times_per_custom_cost = [
                    (
                        str(display_key),
                        {
                            str(osmid): osmid_dict[str(osmid)]
                            for osmid in osmids
                            if str(osmid) in osmid_dict.keys()
                        }
                    )
                    for display_key, osmid_dict in travel_times_per_custom_cost
                ]

            # if merged flag is True, merge all results into a single dict
            if merged:
                merged_name = "merged_custom_costs:"
                merged_travel_times = {}
                for name, base_travel_times in travel_times_per_custom_cost:
                    merged_travel_times.update(base_travel_times)
                    merged_name+= f"_{name}"
                # return all base travel times merged in a single dict in a list
                return [(merged_name, merged_travel_times)]
            # return times per custom cost routing
            return travel_times_per_custom_cost
        except:
            raise CustomCostDataError(
                "Failed to get base travel times from custom cost transport network."
            )

    # kept two similar getters for intuitive abstraction, naming and clarity for user

    def get_base_travel_times(self, osmids=[], merged=False):
        """Get base travel times from edges used during routing from custom costs instances.

        Arguments:
        ----------
        osmids : List[str | int] (optional)
            list of osmids to get base travel times for. If not provided, return all base travel times.
        merged : bool, default False
            define if the base travel times should be merged into a single dict or not

        Returns:
        --------
        List[Tuple[str, Dict[str, int]]]
            list of tuples of custom cost name and base travel times
            each tuple represents one custom cost, if merged is True, only one tuple is returned
        """
        return self._fetch_network_custom_cost_travel_time_product(
            "getBaseTraveltimes", osmids, merged
        )

    def get_custom_cost_additional_travel_times(self, osmids=[], merged=False):
        """Get custom cost addition travel times from edges used during routing from custom costs instances.

        Arguments:
        ----------
        osmids : List[str] (optional)
            list of osmids to get additional custom costs for. If not provided, return all base travel times.
        merged : bool, default False
            define if the base travel times should be merged into a single dict or not

        Returns:
        --------
        List[Tuple[str, Dict[str, int]]]
            list of tuples of custom cost name and additional travel timecosts
            each tuple represents one custom cost, if merged is True, only one tuple is returned
        """
        return self._fetch_network_custom_cost_travel_time_product(
            "getcustomCostAdditionalTraveltimes", osmids, merged
        )
