#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.point_to_point.builder.SpeedConfig."""

from .. import util  # noqa: F401

import jpype

import com.conveyal.r5


__all__ = ["SpeedConfig"]


class SpeedConfig(dict):
    """Wrap a com.conveyal.r5.point_to_point.builder.SpeedConfig."""

    DEFAULT_CONFIG = {
        "units": "mph",
        "values": {
            "motorway": 65,
            "motorway_link": 35,
            "trunk": 55,
            "trunk_link": 35,
            "primary": 45,
            "primary_link": 25,
            "secondary": 35,
            "secondary_link": 25,
            "tertiary": 25,
            "tertiary_link": 25,
            "living_street": 5,
        },
    }

    def __init__(self, **kwargs):
        """
        Provide the configuration to load a transport network.

        Arguments
        ---------
        **kwargs : mixed
            Parameters accepted by SpeedConfig. Both snake_case and
            CamelCase are accepted.
            See https://github.com/conveyal/r5/blob/v6.6/src/main/java/com/conveyal/r5/point_to_point/builder/SpeedConfig.java#L10
        """
        super().__init__()
        kwargs = {util.snake_to_camel_case(key): value for key, value in kwargs}
        _config = self.DEFAULT_CONFIG
        if "values" in kwargs:
            _config["values"].update(kwargs["values"])
        if "units" in kwargs:
            _config["units"] = kwargs["units"]
        for key, value in _config.items():
            self[key] = value


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.point_to_point.builder.SpeedConfig", exact=SpeedConfig
)
def _cast_TransportNetworkBuilderConfig(java_class, instance):
    speed_config = com.conveyal.r5.point_to_point.builder.SpeedConfig()
    speed_config.units = instance["units"]
    for key, value in instance["values"].items():
        speed_config.values[key] = value
    return speed_config
