#!/usr/bin/env python3

"""Subclass for TransportNetwork, enables custom cost routing."""
import com.conveyal.r5
from r5py.r5.transport_network import TransportNetwork
from r5py.util.custom_cost_conversions import (
    convert_custom_cost_data_to_custom_cost_instance,
    convert_custom_cost_instances_to_java_list,
    convert_python_dict_to_java_hashmap,
)

__all__ = ["CustomCostTransportNetwork"]


class CustomCostTransportNetwork(TransportNetwork):
    """Inherit from TransportNetwork, adds custom cost data routing functionality."""

    def __init__(self, osm_pbf, custom_cost_data):
        """
        Initialise a transport network with custom costs

        Arguments
        ---------
        osm_pbf : str
            file path of an OpenStreetMap extract in PBF format
        custom_cost_data : List[Dict[str, float]]
            custom cost data(s) to be used in routing.
            str key is osmid, float value is custom costs per edge (way).
            multiple custom cost data can be provided as a list of dicts,
            if multiple custom cost data is provided, all custom cost data will be combined
            for each edge (way).
        """
        # GTFS is currently not supported for custom cost transport network
        super().__init__(osm_pbf, custom_cost_data=custom_cost_data, gtfs=[])

    # "overrides" the base class method
    def add_custom_cost_data_to_network(self, transport_network, custom_cost_data):
        """Custom hook for adding custom cost data to the transport network edges."""
        if not custom_cost_data:
            raise ValueError(
                "custom_cost_data must be provided for custom cost transport network edges."
            )
        vertex_store = com.conveyal.r5.streets.VertexStore(100_000)
        edge_store = com.conveyal.r5.streets.EdgeStore(
            vertex_store, transport_network.streetLayer, 200_000
        )
        transport_network.streetLayer.vertexStore = vertex_store
        transport_network.streetLayer.edgeStore = edge_store
        converted_custom_cost_data = (
            self.convert_python_custom_cost_to_java_custom_cost(custom_cost_data)
        )
        transport_network.streetLayer.edgeStore.costFields = converted_custom_cost_data
        return transport_network

    # used to automatically do the conversion from python to java custom cost data
    def convert_python_custom_cost_to_java_custom_cost(self, custom_cost_data):
        """Convert custom cost python dict items into the Java HashMap (Long, Double) format.

        Arguments:
        ----------
        custom_cost_data : Dict[str, float]
            python custom cost data to be used in routing.
            str key is osmid, float value is custom costs per edge (way)

        Returns:
        --------
        custom_cost_list: jpype.java.util.List
            java list of custom cost instance(s)
        """
        try:
            java_hashmap_custom_cost = convert_python_dict_to_java_hashmap(
                custom_cost_data
            )
            custom_cost_instance = convert_custom_cost_data_to_custom_cost_instance(
                java_hashmap_custom_cost
            )
            custom_cost_list = convert_custom_cost_instances_to_java_list(
                custom_cost_instance
            )
            return custom_cost_list
        except:
            raise ValueError(
                "Failed to convert python custom cost data to java custom cost data. Custom_cost_data must be provided for custom cost transport network"
            )
