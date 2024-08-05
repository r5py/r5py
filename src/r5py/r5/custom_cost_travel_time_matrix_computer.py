#!/usr/bin/env python3


"""Calculate travel times between many origins and destinations, with custom impedances."""


from .travel_time_matrix_computer import TravelTimeMatrixComputer


__all__ = ["CustomCostTravelTimeMatrixComputer"]


class CustomCostTravelTimeMatrixComputer(TravelTimeMatrixComputer):
    """Compute travel times between many origins and destinations, with custom impedances."""

    def _parse_results(self, from_id, results):
        """
        Parse the results of an R5 TravelTimeMatrix.

        Parse data as returned from `com.conveyal.r5.analyst.TravelTimeComputer.computeTravelTimes()`,
        cast data to Python types, and return as a `pandas.Dataframe`. Because of the way r5py
        and R5 interact, this parses the results of routing from one origin to many (all) destinations.

        Arguments
        ---------
        from_id : mixed
            The value of the ID column of the origin record to report on.
        results : `com.conveyal.r5.OneOriginResult` (Java object)

        Returns
        -------
        pandas.DataFrame
            A data frame containing the columns ``from_id``, ``to_id``,
            ``travel_time``, and ``osm_ids``, where ``travel_time`` is the
            median calculated travel time between ``from_id`` and ``to_id`` or
            ``numpy.nan`` if no connection with the given parameters was found.
            and ``osm_ids`` a list of the OSM edges traversed.

            If non-default ``percentiles`` were requested: one or more columns
            ``travel_time_p{:02d}`` representing the particular percentile of
            travel time.

            For each ``CustomCostField`` passed to
            ``CustomCostTransportNetwork``, another column
            ``additional_{custom_cost_name}`` is added.
        """
        od_matrix = super()._parse_results(from_id, results)

        try:
            od_matrix["osm_ids"] = results.osmIdResults
        except AttributeError:
            pass

        # for cost_field in self.transport_network.street_layer.cost_fields:
        #     costs_per_osm_id = cost_field.getcustomCostAdditionalTraveltimes()
        #     print(costs_per_osm_id)

        return od_matrix
