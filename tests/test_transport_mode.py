#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py
import com.conveyal.r5


class TestTransportMode:
    @pytest.mark.parametrize(
        ["enum_member", "enum_name", "java_type"],
        [
            (r5py.TransportMode.AIR, "AIR", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.BUS, "BUS", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.CABLE_CAR, "CABLE_CAR", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.FERRY, "FERRY", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.FUNICULAR, "FUNICULAR", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.RAIL, "RAIL", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.SUBWAY, "SUBWAY", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.TRAM, "TRAM", com.conveyal.r5.api.util.TransitModes),
            (r5py.TransportMode.TRANSIT, "TRANSIT", com.conveyal.r5.api.util.TransitModes),

            (r5py.TransportMode.BICYCLE, "BICYCLE", com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.CAR, "CAR", com.conveyal.r5.profile.StreetMode),
            (r5py.TransportMode.WALK, "WALK", com.conveyal.r5.profile.StreetMode),

            (r5py.TransportMode.BICYCLE, "BICYCLE", com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.CAR, "CAR", com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.WALK, "WALK", com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.BICYCLE_RENT, "BICYCLE_RENT", com.conveyal.r5.api.util.LegMode),
            (r5py.TransportMode.CAR_PARK, "CAR_PARK", com.conveyal.r5.api.util.LegMode),

        ],
    )
    def test_transportmode(self, enum_member, enum_name, java_type):
        assert enum_member.name == enum_name
        assert enum_member.name == java_type.valueOf(enum_name).name()
