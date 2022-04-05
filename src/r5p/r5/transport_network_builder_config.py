#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.point_to_point.builder.TNBuilderConfig."""

from ..util import config  # noqa: F401

import json
import re

import jpype

import com.conveyal.r5

from .speed_config import SpeedConfig


__all__ = ["TransportNetworkBuilderConfig"]


_IS_CONSTANT_NAME_RE = re.compile(r'[A-Z_]+')


def _is_constant_name(name):
    """Does `name` sound like the name of a constant?"""
    return bool(_IS_CONSTANT_NAME_RE.match(name))


def _snake_to_camel_case(snake_case):
    "Convert `snake_case` to CamelCase spelling."""
    if "_" in snake_case:
        words = snake_case.split("_")
        words = [words[0].lower()] + [word.title() for word in words[1:]]
        camel_case = "".join(words)
    else:
        camel_case = snake_case[0].lower() + snake_case[1:]
    return camel_case


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
            _snake_to_camel_case(key): value
            for key, value in kwargs
        }
        _config = self.DEFAULT_CONFIG | kwargs
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
