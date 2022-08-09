#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py
import com.conveyal.r5


class TestTransitMode:
    @pytest.mark.parametrize(
        ["enum_member", "enum_name"],
        [
            (r5py.TransitMode.AIR, "AIR"),
            (r5py.TransitMode.BUS, "BUS"),
            (r5py.TransitMode.CABLE_CAR, "CABLE_CAR"),
            (r5py.TransitMode.FERRY, "FERRY"),
            (r5py.TransitMode.FUNICULAR, "FUNICULAR"),
            (r5py.TransitMode.RAIL, "RAIL"),
            (r5py.TransitMode.SUBWAY, "SUBWAY"),
            (r5py.TransitMode.TRAM, "TRAM"),
            (r5py.TransitMode.TRANSIT, "TRANSIT"),
        ],
    )
    def test_transitmode(self, enum_member, enum_name):
        assert enum_member.name == enum_name
        assert isinstance(enum_member.value, com.conveyal.r5.api.util.TransitModes)
        assert enum_member.value == com.conveyal.r5.api.util.TransitModes.valueOf(
            enum_name
        )
        assert (
            enum_member.name
            == com.conveyal.r5.api.util.TransitModes.valueOf(enum_name).name()
        )
