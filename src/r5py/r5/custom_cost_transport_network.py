#!/usr/bin/env python3

"""Subclass for TransportNetwork, enables custom cost routing."""
import com.conveyal.r5
from r5py.r5.transport_network import TransportNetwork
from r5py.util.custom_cost_conversions import (
    convert_custom_cost_data_to_custom_cost_instance,
    convert_custom_cost_instances_to_java_list,
    convert_python_dict_to_java_hashmap,
)
from r5py.util.exceptions import CustomCostConversionError, CustomCostDataError

__all__ = ["CustomCostTransportNetwork"]


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
        converted_custom_cost_data = (
            self.convert_python_custom_costs_to_java_custom_costs()
        )
        transport_network.streetLayer.edgeStore.costFields = converted_custom_cost_data
        return transport_network

    # used to automatically do the conversion from python to java custom cost data
    def convert_python_custom_costs_to_java_custom_costs(self):
        """Convert custom cost python dict items into the Java HashMap (Long, Double) format.

        Returns:
        --------
        custom_cost_list: jpype.java.util.List
            java list of custom cost instance(s)
        """
        try:
            custom_cost_instances = []
            for name, sensitivity, custom_cost in zip(
                self.names, self.sensitivities, self.custom_cost_datas
            ):
                # convert custom cost item from python dict to java hashmap
                java_hashmap_custom_cost = convert_python_dict_to_java_hashmap(
                    custom_cost
                )
                # convert custom cost params to java customCostField instance
                custom_cost_instance = convert_custom_cost_data_to_custom_cost_instance(
                    name, sensitivity, java_hashmap_custom_cost
                )
                custom_cost_instances.append(custom_cost_instance)
            # convert all java custom cost instances to java list
            custom_cost_list = convert_custom_cost_instances_to_java_list(
                custom_cost_instances
            )
            return custom_cost_list
        except:
            raise CustomCostConversionError(
                "Failed to convert python custom cost data to java custom cost data. Custom_cost_data must be provided for custom cost transport network"
            )
