#!/usr/bin/env python3


import pytest  # noqa: F401

import r5py
import com.conveyal.r5


class TestLegMode:
    def test_legmode(self):
        walking = r5py.LegMode.WALK
        assert walking.name == "WALK"
        assert isinstance(walking.value, com.conveyal.r5.api.util.LegMode)
