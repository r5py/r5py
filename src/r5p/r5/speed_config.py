#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.point_to_point.builder.SpeedConfig."""

from ..util import config  # noqa: F401

import json

import jpype
import jpype.types

import com.conveyal.r5

from .speed_unit import SpeedUnit


__all__ = ["SpeedConfig"]


adsf = com.conveyal.r5.point_to_point.builder.SpeedConfig.defaultConfig()


class SpeedConfig:
    """Wrap a com.conveyal.r5.point_to_point.builder.SpeedConfig."""
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
        print(1)
        self._config = com.conveyal.r5.point_to_point.builder.SpeedConfig.defaultConfig()
        print(2)
        self.config = dict(self._config.values)
        print(3)

        for key, value in kwargs.items():
            print(4)
            setattr(self, key, value)
            print(5)
        print(6)

    def __getattr__(self, key):
        key = SpeedConfig.snake_to_camel_case(key)
        if key == "units":
            return SpeedUnit(self._config.units.toString())
        return self.config[key]

    def __setattr__(self, key, value):
        key = SpeedConfig.snake_to_camel_case(key)
        if key == "units" and not isinstance(value, SpeedUnit):
            try:
                value = getattr(SpeedUnit, value).value
            except AttributeError:
                value = SpeedUnit.from_string(value).value
            self._config.setattr(key, value)
        else:
            self._config.values[key] = value
        self.config[key] = value

    def update(self, config_update={}):
        for key, value in config_update.items():
            self[key] = value

    @staticmethod
    def snake_to_camel_case(snake_case):
        return ''.join(word.title() for word in snake_case.split('_'))


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.point_to_point.builder.SpeedConfig",
    exact=SpeedConfig
)
def _cast_SpeedConfig(java_class, object_):
    return object_._config
