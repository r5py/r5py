#!/usr/bin/env python3


"""Wraps a com.conveyal.r5.transit.TransportNetwork."""


import os.path

import jpype
import jpype.types

from .. import util  # noqa: F401
from .transport_network_builder_config import TransportNetworkBuilderConfig

import com.conveyal.r5
import java.lang
import java.util.ArrayList


__all__ = ["TransportNetwork"]


# TODO: Figure out how to make R5 save the .mapdb elsewhere, and not next
# to the input files (they could well be on a r/o filesystem, or in a dedicate
# data folder that should not be littered with random cache files).


class TransportNetwork:
    """Wrap a com.conveyal.r5.transit.TransportNetwork."""

    def __init__(self, osm_pbf, gtfs=[], build_config={}):
        """
        Load a transport network.

        Arguments
        ---------
        osm_pbf : str
            file path of an OpenStreetMap extract in PBF format
        gtfs : list[str]
            paths to public transport schedule information in GTFS format
        build_json : dict
            options accepted by TNBuilderConfig (including SpeedConfig)
        """
        osm_pbf = os.path.abspath(osm_pbf)
        gtfs = [os.path.abspath(path) for path in gtfs]
        build_config = TransportNetworkBuilderConfig(**build_config)
        self._transport_network = (
            com.conveyal.r5.transit.TransportNetwork.fromFiles(
                java.lang.String(osm_pbf),
                java.util.ArrayList.of(gtfs),
                build_config
            )
        )
        self._transport_network.transitLayer.buildDistanceTables(None)

    @property
    def linkage_cache(self):
        """Expose the `TransportNetwork`’s `linkageCache` to Python."""
        return self._transport_network.linkageCache

    @property
    def street_layer(self):
        """Expose the `TransportNetwork`’s `streetLayer` to Python."""
        return self._transport_network.streetLayer

    @property
    def timezone(self):
        """Determine the timezone of the GTFS data."""
        return self._transport_network.getTimeZone()


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransportNetwork",
    exact=TransportNetwork
)
def _cast_TransportNetwork(java_class, object_):
    return object_._transport_network
