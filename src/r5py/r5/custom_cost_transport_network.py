#!/usr/bin/env python3

"""Subclass for TransportNetwork, enables custom cost routing."""
import collections
import com.conveyal.r5
from r5py.r5.transport_network import TransportNetwork
from r5py.util.classpath import r5_supports_custom_costs
from r5py.util.custom_cost_conversions import (
    convert_java_hashmap_to_python_dict,
    convert_python_custom_costs_to_java_custom_costs,
)
from r5py.util.exceptions import CustomCostDataError
from r5py.util.jvm import start_jvm

__all__ = ["CustomCostTransportNetwork"]

start_jvm()


class CustomCostTransportNetwork(TransportNetwork):
    """Inherit from TransportNetwork, adds custom cost routing functionality."""

    def __init__(
        self,
        osm_pbf,
        names,
        sensitivities,
        custom_cost_segment_weight_factors,
        allow_missing_osmids=True,
    ):
        """
        Initialise a transport network with custom weighting cost factors.
        Supports single or multiple cost factor sets.
        Must always have the same number of:
        names, sensitivities, and custom_cost_segment_weight_factors, and also allow_missing_osmids if multiple provided.
        Multiple datasets so lists of parameters are paired together by "index" order using zip.
        So the first parameters of each parameter list are used together, then the second ones, and so on.

        Arguments
        ---------
        osm_pbf : str
            File path of an OpenStreetMap extract in PBF format.
        names : str | List[str]
            Single name or multiple names of the custom costs.
        sensitivities : float | int | List[float | int]
            Single or multiple sensitivities of the custom costs.
        custom_cost_segment_weight_factors : Dict[str, float] | List[Dict[str, float]]
            Single or multiple custom cost factors to be used in routing.
            Str key is osmid, float value is custom cost factor per road segment (edge/way).
            Factors will be used to calculate additional seconds per road segment with formula:
            baseTravelTimeSeconds * customCostFactor * sensitivity.
            When multiple custom cost datas are provided, all of those custom cost factors will be combined
            for each road segment during r5 custom cost routing.
        allow_missing_osmids : bool | List[bool], default True
            Define whether to allow missing osmids in routing. Default is True.
            If multiple sets of other data are provided but allow_missing_osmids is not provided,
            will populate default for all custom costs.
            If multiple allow_missing_osmids or are provided, they must be of the same amount as other parameters.
            Using False might be affected by public transit edges if they are added and used in routing.
            If set to False and ANY edges aren't found during routing, routing will throw exception,
            so in most cases the default True should be used.
        """
        # crash if custom costs are NOT supported in the used version of R5
        # either use TransportNetwork (without custom costs) or change to correct version of R5
        if not r5_supports_custom_costs():
            raise RuntimeError(
                """Custom costs are not supported in this version of R5.
                Correct (Green Paths 2 patched) R5 version can be found from branch gp2 in
                https://github.com/DigitalGeographyLab/r5. Or by using a release jar from address e.g.
                https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar
                """
            )

        (
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        ) = self._validate_custom_cost_params(
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        )
        self.names = names
        self.sensitivities = sensitivities
        self.custom_cost_segment_weight_factors = custom_cost_segment_weight_factors
        self.allow_missing_osmids = allow_missing_osmids
        # GTFS is currently not supported for custom cost transport network
        super().__init__(osm_pbf, gtfs=[])

    def convert_params_to_lists(
        self,
        names,
        sensitivities,
        custom_cost_segment_weight_factors,
        allow_missing_osmids,
    ):
        """
        Convert single items into lists if they are not already.

        Arguments:
        ----------
        names : str | collections.abc.Iterable[str]
            Single name or names of the custom costs.
        sensitivities : float | int | collections.abc.Iterable[float | int]
            Single or multiple sensitivities of the custom costs.
        custom_cost_segment_weight_factors : Dict[str, float] | collections.abc.Iterable[Dict[str, float]]
            Single or multiple custom cost factors to be used in routing.
        allow_missing_osmids : bool | collections.abc.Iterable[bool], default True (optional)
            Define whether to allow missing osmids.

        Returns:
        --------
        names : List[str]
        sensitivities : List[float | int]
        custom_cost_segment_weight_factors : List[Dict[str, float]]
        allow_missing_osmids : List[bool]
        """
        if not isinstance(names, collections.abc.Iterable) or isinstance(names, str):
            names = [names]
        if not isinstance(sensitivities, collections.abc.Iterable):
            sensitivities = [sensitivities]
        # needs to be list for dict is iterable
        if not isinstance(
            custom_cost_segment_weight_factors, collections.abc.Iterable
        ) or isinstance(custom_cost_segment_weight_factors, dict):
            custom_cost_segment_weight_factors = [custom_cost_segment_weight_factors]
        if not isinstance(allow_missing_osmids, collections.abc.Iterable):
            allow_missing_osmids = [allow_missing_osmids]
            # if using multiple sets and if optional allow_missing_osmids is not provided,
            # populate the default for all custom costs if many cost dicts provided and only one allow_missing_osmids
            max_len_params = max(
                len(names),
                len(sensitivities),
                len(custom_cost_segment_weight_factors),
            )
            if max_len_params > 1 and len(allow_missing_osmids) == 1:
                allow_missing_osmids = [allow_missing_osmids[0]] * max_len_params
        return (
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        )

    def _validate_custom_cost_params(
        self,
        names,
        sensitivities,
        custom_cost_segment_weight_factors,
        allow_missing_osmids,
    ):
        """
        Validate CustomCostTransportNetwork parameters.
        All parameters are transformed into lists already in convert_params_to_lists method.

        Arguments:
        ----------
        names : List[str]
        sensitivities : List[float | int]
        custom_cost_segment_weight_factors : List[Dict[str, float]]
        allow_missing_osmids : List[bool]

        Raises:
        -------
        CustomCostDataError
            If any of the parameters are not valid.
        """
        (
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        ) = self.convert_params_to_lists(
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        )

        # parameters are lists and non-empty
        params = {
            "names": names,
            "sensitivities": sensitivities,
            "custom_cost_segment_weight_factors": custom_cost_segment_weight_factors,
            "allow_missing_osmids": allow_missing_osmids,
        }
        for param_name, param_value in params.items():
            if not isinstance(param_value, collections.abc.Iterable):
                raise CustomCostDataError(f"{param_name} must be a iterables")
            if not param_value:
                raise CustomCostDataError(f"{param_name} must not be empty")

        # lists are of the same length
        if not (
            len(names)
            == len(sensitivities)
            == len(custom_cost_segment_weight_factors)
            == len(allow_missing_osmids)
        ):
            raise CustomCostDataError(
                "CustomCostTransportNetwork names, sensitivities, and custom_cost_segment_weight_factors must be of the same length, and allow_missing_osmids if multiple provided"
            )

        # check individual item types
        for (
            name,
            sensitivity,
            custom_cost_segment_weight_factor,
            allow_missing_osmid,
        ) in zip(
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        ):
            if not isinstance(name, str):
                raise CustomCostDataError(
                    "CustomCostTransportNetwork names must be strings"
                )
            if not isinstance(sensitivity, (float, int)):
                raise CustomCostDataError(
                    "CustomCostTransportNetwork sensitivities must be floats or integers"
                )
            if (
                len(custom_cost_segment_weight_factor) == 0
                or not isinstance(custom_cost_segment_weight_factor, dict)
                or not all(
                    isinstance(key, str) and isinstance(value, float)
                    for key, value in custom_cost_segment_weight_factor.items()
                )
            ):
                raise CustomCostDataError(
                    "custom_cost_segment_weight_factor must be dicts with string keys and float values"
                )

            if not isinstance(allow_missing_osmid, bool):
                raise CustomCostDataError(
                    "CustomCostTransportNetwork allow_missing_osmids must be bools"
                )

        return (
            names,
            sensitivities,
            custom_cost_segment_weight_factors,
            allow_missing_osmids,
        )

    def add_custom_cost_segment_weight_factors_to_network(self, transport_network):
        """
        Custom hook for adding custom cost data to the transport network road segments.

        Arguments:
        ----------
        transport_network : com.conveyal.r5.transit.TransportNetwork
            R5 transport network object.

        Returns:
        --------
        com.conveyal.r5.transit.TransportNetwork
            R5 transport network object with custom cost factors added to streetLayer.edgeStore.costFields.
        """
        vertex_store = com.conveyal.r5.streets.VertexStore(100_000)
        edge_store = com.conveyal.r5.streets.EdgeStore(
            vertex_store, transport_network.streetLayer, 2_000_000
        )
        transport_network.streetLayer.vertexStore = vertex_store
        transport_network.streetLayer.edgeStore = edge_store
        converted_custom_cost_segment_weight_factors = (
            convert_python_custom_costs_to_java_custom_costs(
                self.names,
                self.sensitivities,
                self.custom_cost_segment_weight_factors,
                self.allow_missing_osmids,
            )
        )
        transport_network.streetLayer.edgeStore.costFields = (
            converted_custom_cost_segment_weight_factors
        )
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
            Name of the method to be called from the custom cost transport network.
            This can be either: getAdditionalTravelTimes or getTravelTimes.
            getAdditionalTravelTimes returns the additional travel times from the custom cost instances,
            getTravelTimes returns the base travel times from the custom cost instances.
            Both methods return a Java HashMap with Osmid as key and travel time as value.

        osmids : List[str | int] (optional)
            list of osmids to get travel times for. If not provided, return all travel times.

        merged : bool, default False
            define if the base travel times should be merged into a single dict or not

        Returns:
        --------
        travel_times_per_custom_cost: List[Tuple[str, Dict[str, int]]]
            list of tuples of custom cost name and travel times per custom cost routing

        Raises:
        -------
        CustomCostDataError
            If failed to get base travel times from custom cost transport network.

        Notes:
        ------
        In getTravelTimes the value is actual seconds but in getAdditionalTravelTimes
        the value more of a cost than actual seconds for it is calculated using baseTravelTimeSeconds * sensitivity * customCostFactor.
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
                        },
                    )
                    for display_key, osmid_dict in travel_times_per_custom_cost
                ]

            # if merged flag is True, merge all results into a single dict
            if merged:
                merged_name = "merged_custom_costs:"
                merged_travel_times = {}
                for name, base_travel_times in travel_times_per_custom_cost:
                    merged_travel_times.update(base_travel_times)
                    merged_name += f"_{name}"
                # return all base travel times merged in a single dict in a list
                return [(merged_name, merged_travel_times)]
            # return times per custom cost routing
            return travel_times_per_custom_cost
        except CustomCostDataError as e:
            raise CustomCostDataError(
                "Failed to get base travel times from custom cost transport network."
            ) from e

    # kept two similar getters for intuitive abstraction, naming and clarity for user

    def get_base_travel_times(self, osmids=[], merged=False):
        """Get base travel times from edges used during routing from custom costs instances.

        Arguments:
        ----------
        osmids : List[str | int] (optional)
            List of osmids to get base travel times for. If not provided, return all base travel times.
        merged : bool, default False
            Define if the base travel times should be merged into a single dict or not.

        Returns:
        --------
        Tuple[str, Dict[str, int]] | List[Tuple[str, Dict[str, int]]]
            List of tuples of custom cost name and base travel times.
            Each tuple represents one custom cost.
            If merged is True, all the used customCosts are merged and only one tuple is returned.
        """
        return self._fetch_network_custom_cost_travel_time_product(
            "getBaseTraveltimes", osmids, merged
        )

    def get_custom_cost_additional_travel_times(self, osmids=[], merged=False):
        """Get custom cost addition travel times from edges used during routing from custom costs instances.

        Arguments:
        ----------
        osmids : List[str] (optional)
            List of osmids to get additional custom costs for. If not provided, return all base travel times.
        merged : bool, default False
            Define if the base travel times should be merged into a single dict or not.

        Returns:
        --------
        Tuple[str, Dict[str, int]] | List[Tuple[str, Dict[str, int]]]
            List of tuples of custom cost name and additional travel timecosts.
            Each tuple represents one custom cost.
            If merged is True, all the used customCosts are merged and only one tuple is returned.
        """
        return self._fetch_network_custom_cost_travel_time_product(
            "getcustomCostAdditionalTraveltimes", osmids, merged
        )
