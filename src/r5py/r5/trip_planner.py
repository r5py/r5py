#!/usr/bin/env python3


"""Find detailed routes between two points."""


__all__ = ["TripPlanner"]


class TripPlanner:
    """
    Find detailed routes between two points.
    """

    def __init__(self, transport_network, request):
        """
        Find detailed routes between two points.

        Arguments
        =========
        transport_network : r5py.r5.TransportNetwork
            A transport network to route on
        request : r5py.r5.regional_task
            The parameters that should be used when finding a route
        """
        pass

    def plan(self):
        """
        Find detailed routes between two points.

        Returns
        =======
        list[r5py.r5.Trip]
            Detailed routes that meet the requested parameters
        """
        pass
