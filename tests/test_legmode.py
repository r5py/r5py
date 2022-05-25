#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py
import com.conveyal.r5


class TestLegMode:
    @pytest.mark.parametrize(
        ["enum_member", "enum_name"],
        [
            (r5py.LegMode.BICYCLE, "BICYCLE"),
            (r5py.LegMode.BICYCLE_RENT, "BICYCLE_RENT"),
            (r5py.LegMode.CAR, "CAR"),
            (r5py.LegMode.CAR_PARK, "CAR_PARK"),
            (r5py.LegMode.WALK, "WALK"),
        ],
    )
    def test_legmode(self, enum_member, enum_name):
        assert enum_member.name == enum_name
        assert isinstance(enum_member.value, com.conveyal.r5.api.util.LegMode)
        assert enum_member.value == com.conveyal.r5.api.util.LegMode.valueOf(enum_name)
        assert (
            enum_member.name
            == com.conveyal.r5.api.util.LegMode.valueOf(enum_name).name()
        )
