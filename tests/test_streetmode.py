#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py
import com.conveyal.r5


class TestStreetMode:
    @pytest.mark.parametrize(
        ["enum_member", "enum_name"],
        [
            (r5py.r5.StreetMode.BICYCLE, "BICYCLE"),
            (r5py.r5.StreetMode.CAR, "CAR"),
            (r5py.r5.StreetMode.WALK, "WALK"),
        ],
    )
    def test_streetmode(self, enum_member, enum_name):
        assert enum_member.name == enum_name
        assert isinstance(enum_member.value, com.conveyal.r5.profile.StreetMode)
        assert enum_member.value == com.conveyal.r5.profile.StreetMode.valueOf(
            enum_name
        )
        assert (
            enum_member.name
            == com.conveyal.r5.profile.StreetMode.valueOf(enum_name).name()
        )
