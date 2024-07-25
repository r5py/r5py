#!/usr/bin/env python3


"""TransportNetwork with custom impedances."""


import pandas

from .transport_network import TransportNetwork
from ..util import JHashMap
from ..util.exceptions import CustomCostDataError, CustomR5JarRequiredError


__all__ = ["CustomCostTransportNetwork"]


class CustomCostTransportNetwork(TransportNetwork):
    """TransportNetwork with custom impedances."""

    def __init__(
        self,
        osm_pbf,
        gtfs=[],
        custom_costs=pandas.DataFrame(),
        sensitivities={},
        allow_missing_values=True,
        precalculate=True,
    ):
        """
        Initialise a TransportNetwork with custom impedances.

        Supports single or multiple cost factor sets.
        Must always have the same number of:
        names, sensitivities, and custom_cost_segment_weight_factors, and also allow_missing_osmids if multiple provided.
        Multiple datasets so lists of parameters are paired together by "index" order using zip.
        So the first parameters of each parameter list are used together, then the second ones, and so on.

        Arguments
        ---------
        osm_pbf : str | pathlib.Path
            file path of an OpenStreetMap extract in PBF format
        gtfs : str | pathlib.Path | list[str] | list[pathlib.Path]
            path(s) to public transport schedule information in GTFS format
        custom_costs : pandas.DataFrame()
            A DataFrame indexed by OSM IDs, each column is a custom impedance
            that is applied to the respective edges, the column names are used
            the name of the custom costs
        sensitivities : dict[str : float]
            Apply an over-all weight to one or more columns. A dict, the keys
            are column/cost names, the values sensitivity coefficients
        allow_missing_values : bool | List[bool], default True
            Define whether to allow missing values in custom costs.
        precalculate : False or float, default False
            If a positive numeric value, precalculate the transport network
            before routing with this walking or cycling speed (in km/h).
            This potentially speeds up repeated routing for large networks.
        """
        super().__init__(osm_pbf, gtfs)

        try:
            import com.conveyal.r5.rastercost.CustomCostField
        except ImportError:
            raise CustomR5JarRequiredError(
                """Custom costs are not supported in this version of R5.
                Correct (Green Paths 2 patched) R5 version should be found from branch gp2 in
                https://github.com/DigitalGeographyLab/r5. Or by using a release jar from address e.g.
                https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar
                """
            )

        if isinstance(precalculate, (int, float)) and precalculate > 0:
            try:
                import com.conveyal.r5.rastercost.EdgeCustomCostPreCalculator
            except ImportError:
                raise CustomR5JarRequiredError(
                    """Precalculating custom costs are not supported in this version of  R5.
                    Correct (Green Paths 2, and precalculations patched) R5 version should be found from precalculate branch in
                    https://github.com/DigitalGeographyLab/r5. Or by using a release jar from address e.g.
                    https://github.com/DigitalGeographyLab/r5/releases/download/v7.1-gp2-1/r5-v7.1-gp2-2-gd8134d8-all.jar
                    """
                )
                self._transport_network.streetLayer.staticSpeedKmh = precalculate

        for column in custom_costs.columns:
            if column not in sensitivities:
                sensitivities[column] = 1.0

        self.street_layer.cost_fields = [
            com.conveyal.r5.rastercost.CustomCostField(
                column,
                sensitivities[column],
                JHashMap(dict(custom_costs[column])),
                allow_missing_values,
            )
            for column in custom_costs.columns
        ]

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
                    dict(getattr(cost_field, method_name)()),
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

    @property
    def base_travel_times(self):
        """
        Retrieve base travel times.

        Returns
        -------
        pandas.DataFrame
            A data frame containing the columns

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
        return self._fetch_network_custom_cost_travel_time_product("getBaseTraveltimes")

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
