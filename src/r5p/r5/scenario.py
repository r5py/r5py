#!/usr/bin/env python3

"""Wraps a com.conveyal.r5.analyst.scenario.Scenario."""

import jpype

from ..util import config  # noqa: F401

import com.conveyal.r5


__all__ = ["Scenario"]


class Scenario:
    """Wrap a com.conveyal.r5.analyst.scenario.Scenario."""
    def __init__(self):
        """Initialise a most simple Scenario."""
        scenario = com.conveyal.r5.analyst.scenario.Scenario()
        scenario.id = "id"
        self._scenario = scenario

    @property
    def id(self):
        return self._scenario.id


@jpype._jcustomizer.JConversion(
    "com.conveyal.r5.analyst.scenario.Scenario",
    exact=Scenario
)
def _cast_Scenario(java_class, object_):
    return object_._scenario
