#!/usr/bin/env python3

import pytest

import r5py
import com.conveyal.r5


class TestJavaCasting:
    @pytest.mark.parametrize(
        ["python_object", "java_class"],
        [
            (r5py.TransportMode.AIR, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.BUS, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.CABLE_CAR, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.FERRY, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.FUNICULAR, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.GONDOLA, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.RAIL, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.SUBWAY, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.TRAM, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.TRANSIT, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.BICYCLE, com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.CAR, com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.WALK, com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.BICYCLE, com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.CAR, com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.WALK, com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.BICYCLE_RENT, com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.CAR_PARK, com.conveyal.r5.api.util.LegMode),
            (
                r5py.ElevationCostFunction.TOBLER,
                com.conveyal.r5.analyst.scenario.RasterCost.CostFunction,
            ),
            (
                r5py.ElevationCostFunction.MINETTI,
                com.conveyal.r5.analyst.scenario.RasterCost.CostFunction,
            ),
        ],
    )
    def test_transport_modes_cast(self, python_object, java_class):
        # see https://jpype.readthedocs.io/en/latest/quickguide.html#classes-objects
        _ = (java_class) @ python_object

    @pytest.mark.parametrize(
        ["python_object", "java_class"],
        [
            (r5py.TransportMode.WALK, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.CAR, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.BICYCLE_RENT, com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.TRAM, com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.BUS, com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.CAR_PARK, com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.TRANSIT, com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.FUNICULAR, com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.GONDOLA, com.conveyal.r5.api.util.LegMode),
        ],
    )
    def test_transport_modes_invalid_cast(self, python_object, java_class):
        # see https://jpype.readthedocs.io/en/latest/quickguide.html#classes-objects
        with pytest.raises(ValueError, match="is not a valid R5"):
            _ = (java_class) @ python_object
