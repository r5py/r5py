#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.transit.TransportNetwork."""

from ..util import config  # noqa: F401
from .transport_network_builder_config import TransportNetworkBuilderConfig

import jpype
import jpype.types

import com.conveyal.r5
import java.lang
import java.util.ArrayList


__all__ = ["TransportNetwork"]


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
            options accepted by TNBuilderConfig
        """
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
        return self._transport_network.linkageCache

    @property
    def street_layer(self):
        return self._transport_network.streetLayer

    @property
    def timezone(self):
        return self._transport_network.getTimeZone()


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransportNetwork",
    exact=TransportNetwork
)
def _cast_TransportNetwork(java_class, object_):
    return object_._transport_network
