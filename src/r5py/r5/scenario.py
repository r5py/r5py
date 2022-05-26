#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.analyst.scenario.Scenario."""

import jpype

from ..util import start_jvm

import com.conveyal.r5


__all__ = ["Scenario"]


start_jvm()


class Scenario:
    """Wrap a com.conveyal.r5.analyst.scenario.Scenario."""

    def __init__(self):
        """Initialise a most simple Scenario."""
        scenario = com.conveyal.r5.analyst.scenario.Scenario()
        scenario.id = "id"
        self._scenario = scenario

    @property
    def id(self):
        """Retrieve the Java Scenario’s instance’s ID."""
        return self._scenario.id


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.analyst.scenario.Scenario", exact=Scenario
)
def _cast_Scenario(java_class, object_):
    return object_._scenario
