#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.transit.TransportNetwork."""

import tempfile

import jpype

import com.conveyal.r5


__all__ = ["TransportNetwork"]


class TransportNetwork:
    """Wrap a com.conveyal.r5.transit.TransportNetwork."""
    def __init__(self, osm_pbf, gtfs=[]):
        """
        Load a transport network.

        Arguments
        ---------
        osm_pbf : str
            file path of an OpenStreetMap extract in PBF format
        gtfs : list[str]
            paths to public transport schedule information in GTFS format
        """
        with tempfile.NamedTemporaryFile(suffix=".json") as build_config:
            # TODO: actually configure build-config.json
            build_config.write(
                str(
                    com.conveyal.r5.point_to_point.builder
                        .TNBuilderConfig.defaultConfig()
                )
            )
            self._transport_network = (
                com.conveyal.r5.transit.TransportNetwork.fromFiles(
                    osm_pbf,
                    gtfs,
                    build_config.name
                )
            )
        self._transport_network.transitLayer.buildDistanceTables(None)

    @property
    def timezone(self):
        return self._transport_network.getTimeZone()


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.transit.TransportNetwork",
    exact=TransportNetwork
)
def _cast_TransportNetwork(java_class, object_):
    return object_._transport_network
