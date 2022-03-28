#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.point_to_point.builder.TNBuilderConfig."""

from ..util import config  # noqa: F401

import json

import jpype
import jpype.types

import com.conveyal.r5

from .speed_config import SpeedConfig


__all__ = ["TransportNetworkBuilderConfig"]


class TransportNetworkBuilderConfig:
    """Wrap a com.conveyal.r5.point_to_point.builder.TNBuilderConfig."""
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
        self._config = com.conveyal.r5.point_to_point.builder.TNBuilderConfig.defaultConfig()
        self.config = json.loads(str(self._config.toString()))

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, key):
        key = TransportNetworkBuilderConfig.snake_to_camel_case(key)
        if key == "speeds":
            return SpeedConfig(self.config["speeds"])
        return self.config[key]

    def __setattr__(self, key, value):
        key = TransportNetworkBuilderConfig.snake_to_camel_case(key)
        self.config[key] = value
        self._config.setattr(key, value)

    def update(self, config_update={}):
        for key, value in config_update.items():
            self[key] = value

    @staticmethod
    def snake_to_camel_case(snake_case):
        return ''.join(word.title() for word in snake_case.split('_'))


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.point_to_point.builder.TNBuilderConfig",
    exact=TransportNetworkBuilderConfig
)
def _cast_TransportNetworkBuilderConfig(java_class, object_):
    return object_._config
