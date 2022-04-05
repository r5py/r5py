#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.point_to_point.builder.TNBuilderConfig."""

from .. import util  # noqa: F401

import json

import jpype

import com.conveyal.r5

from .speed_config import SpeedConfig


__all__ = ["TransportNetworkBuilderConfig"]


class TransportNetworkBuilderConfig(dict):
    """Wrap a com.conveyal.r5.point_to_point.builder.TNBuilderConfig."""

    DEFAULT_CONFIG = {
        "htmlAnnotations": False,
        "maxHtmlAnnotationsPerFile": 1000,
        "transit": True,
        "useTransfersTxt": False,
        "parentStopLinking": False,
        "stationTransfers": False,
        "subwayAccessTime": com.conveyal.r5.point_to_point.builder.TNBuilderConfig.DEFAULT_SUBWAY_ACCESS_TIME,
        "streets": True,
        "embedRouterConfig": True,
        "areaVisibility": False,
        "matchBusRoutesToStreets": False,
        "fetchElevationUS": False,
        "staticBikeRental": False,
        "staticParkAndRide": True,
        "staticBikeParkAndRide": False,
        "bikeRentalFile": None,
        "speeds": SpeedConfig(),
        "analysisFareCalculator": None,
    }

    def __init__(self, **kwargs):
        """
        Provide the configuration for loading a transport network.

        Arguments
        ---------
        **kwargs : mixed
            Parameters accepted by TNBuilderConfig. Both snake_case and
            CamelCase are accepted.
            See https://github.com/conveyal/r5/blob/v6.6/src/main/java/com/conveyal/r5/point_to_point/builder/TNBuilderConfig.java#L128
        """
        super().__init__()
        kwargs = {
            util.snake_to_camel_case(key): value
            for key, value in kwargs
        }
        _config = self.DEFAULT_CONFIG
        if "speeds" in kwargs:
            _config["speeds"] = SpeedConfig(kwargs["speeds"])
            del kwargs["speeds"]
        _config.update(kwargs)
        for key, value in _config.items():
            self[key] = value


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.point_to_point.builder.TNBuilderConfig",
    exact=TransportNetworkBuilderConfig
)
def _cast_TransportNetworkBuilderConfig(java_class, instance):
    return com.conveyal.r5.common.JsonUtilities.objectMapper.readValue(
        json.dumps(instance),
        com.conveyal.r5.point_to_point.builder.TNBuilderConfig.class_
    )
